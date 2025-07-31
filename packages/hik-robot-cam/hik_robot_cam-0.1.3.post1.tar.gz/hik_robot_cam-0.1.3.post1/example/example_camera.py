import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager
from threading import Event, RLock, Thread
from typing import Optional

import numpy as np
from hik_robot_cam import CameraConfig, HikRobotCamera

logger = logging.getLogger(__name__)


class CameraError(Exception):
    """相机操作异常."""

    pass


class Camera:
    """海康机器人相机管理器.

    支持单例模式，自动管理相机资源和引用计数
    线程安全的帧获取和配置更新
    """

    # 类变量
    instances: dict[str, "Camera"] = {}
    instances_lock = RLock()

    # 默认配置
    DEFAULT_FRAME_RATE = 30
    DEFAULT_EXPOSURE_TIME = 2000.0
    DEFAULT_GAIN = 0.0
    DEFAULT_FRAME_SIZE = (480, 640, 3)

    def __new__(cls, camera_id: str, *args, **kwargs) -> "Camera":
        """单例模式实现."""
        with cls.instances_lock:
            if camera_id not in cls.instances:
                instance = super().__new__(cls)
                cls.instances[camera_id] = instance
            return cls.instances[camera_id]

    def __init__(
        self,
        camera_id: str,
        uri: str,
        exposure_time: float = DEFAULT_EXPOSURE_TIME,
        frame_rate: float = DEFAULT_FRAME_RATE,
        gain: float = DEFAULT_GAIN,
    ):
        # 防止重复初始化
        if hasattr(self, "initialized"):
            return

        self.id = camera_id
        self.uri = uri

        # 相机配置
        self.config = self._create_config(exposure_time, frame_rate, gain)

        # 线程同步
        self.frame_lock = RLock()
        self.state_lock = RLock()
        self.stop_event = Event()

        # 状态管理
        self.current_frame = np.zeros(self.DEFAULT_FRAME_SIZE, dtype=np.uint8)
        self.running = False
        self.ref_count = 0
        self.thread: Thread | None = None

        # 标记已初始化
        self.initialized = True

        logger.info(f"Camera {camera_id} initialized with URI: {uri}")

    @classmethod
    def get_instance(cls, camera_id: str) -> Optional["Camera"]:
        """获取已存在的相机实例."""
        with cls.instances_lock:
            return cls.instances.get(camera_id)

    @classmethod
    def list_cameras(cls) -> list[str]:
        """列出所有相机ID."""
        with cls.instances_lock:
            return list(cls.instances.keys())

    @property
    def is_running(self) -> bool:
        with self.state_lock:
            return self.running

    @property
    def ref_count_safe(self) -> int:
        with self.state_lock:
            return self.ref_count

    @property
    def config_copy(self) -> CameraConfig:
        """获取当前配置的副本."""
        return self._copy_config(self.config)

    def _create_config(self, exposure_time: float, frame_rate: float, gain: float) -> CameraConfig:
        """创建相机配置."""
        config = CameraConfig()
        config.exposure_time = exposure_time
        config.frame_rate = frame_rate
        config.gain = gain
        return config

    def _copy_config(self, config: CameraConfig) -> CameraConfig:
        """复制配置对象."""
        new_config = CameraConfig()
        new_config.exposure_time = config.exposure_time
        new_config.frame_rate = config.frame_rate
        new_config.gain = config.gain
        return new_config

    def _capture_loop(self) -> None:
        """相机捕获循环."""
        camera = None
        thread_name = f"Camera-{self.id}"

        try:
            camera = HikRobotCamera(self.uri)

            with camera:
                camera.configure(self.config)
                camera.start_stream()

                frame_interval = 1.0 / self.config.frame_rate

                while not self.stop_event.is_set():
                    try:
                        frame = camera.capture()
                        if frame is not None:
                            with self.frame_lock:
                                self.current_frame = frame
                    except Exception as e:
                        print(f"{thread_name} frame capture failed: {e}")

                    # 可中断的等待
                    if self.stop_event.wait(timeout=frame_interval):
                        break

                # camera.stop_stream()

        except Exception as e:
            raise CameraError(f"Camera capture failed: {e}") from e
        finally:
            if camera:
                try:
                    camera.stop_stream()
                except Exception as e:
                    print(f"{thread_name} stop stream error: {e}")
        self.running = False

    def update_config(
        self,
        exposure_time: float | None = None,
        frame_rate: float | None = None,
        gain: float | None = None,
    ) -> None:
        """更新相机配置.

        注意: 配置更新需要重启相机才能生效
        """
        if exposure_time is not None:
            self.config.exposure_time = exposure_time
        if frame_rate is not None:
            self.config.frame_rate = frame_rate
        if gain is not None:
            self.config.gain = gain

        logger.info(f"Camera {self.id} config updated")

    def start(self) -> None:
        """启动相机."""
        with self.state_lock:
            self.ref_count += 1

            if not self.running:
                self.stop_event.clear()
                self.running = True

                self.thread = Thread(target=self._capture_loop, daemon=True, name=f"Camera-{self.id}")
                self.thread.start()

                logger.info(f"Camera {self.id} started (ref_count: {self.ref_count})")
            else:
                logger.debug(f"Camera {self.id} already running (ref_count: {self.ref_count})")

    def stop(self) -> None:
        """停止相机."""

        with self.state_lock:
            if self.ref_count > 0:
                self.ref_count -= 1

            if self.ref_count == 0 and self.running:
                self.stop_event.set()

                if self.thread and self.thread.is_alive():
                    self.thread.join(timeout=3.0)

                    if self.thread.is_alive():
                        logger.warning(f"Camera {self.id} thread did not stop gracefully")

                self.thread = None
                logger.info(f"Camera {self.id} stopped")
            else:
                logger.debug(f"Camera {self.id} ref_count decreased to {self.ref_count}")

    def restart(self) -> None:
        """重启相机（保持引用计数）."""
        with self.state_lock:
            if self.running:
                temp_refs = self.ref_count
                self.ref_count = 1  # 临时设置为1以确保停止
                self.stop()

                # 等待完全停止
                time.sleep(0.1)

                self.ref_count = temp_refs
                self.start()

                logger.info(f"Camera {self.id} restarted")

    def read(self) -> np.ndarray:
        """读取当前帧."""
        if not self.is_running:
            logger.warning(f"Camera {self.id} is not running")
            return np.zeros(self.DEFAULT_FRAME_SIZE, dtype=np.uint8)

        with self.frame_lock:
            return self.current_frame.copy()

    @contextmanager
    def capture_context(self):
        """上下文管理器，自动管理相机启停."""
        self.start()
        try:
            yield self
        finally:
            self.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def __iter__(self) -> Iterator[np.ndarray]:
        return self

    def __next__(self) -> np.ndarray:
        if not self.is_running:
            raise StopIteration("Camera is not running")
        return self.read()

    def __repr__(self) -> str:
        return f"Camera(id='{self.id}', uri='{self.uri}', running={self.is_running}, ref_count={self.ref_count_safe})"


# 便利函数
def create_camera(camera_id: str, uri: str, **config_kwargs) -> Camera:
    """创建或获取相机实例."""
    return Camera(camera_id, uri, **config_kwargs)


def get_camera(camera_id: str) -> Camera | None:
    """获取已存在的相机实例."""
    return Camera.get_instance(camera_id)


def list_all_cameras() -> list[str]:
    """列出所有相机ID."""
    return Camera.list_cameras()


if __name__ == "__main__":
    camera = create_camera(camera_id="1", uri="192.168.1.66")
    camera.start()

    time.sleep(1)
    print("=" * 50)
    camera.stop()
