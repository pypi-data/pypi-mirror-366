from __future__ import annotations

import numpy as np

class CameraConfig:
    def __init__(self) -> None:
        self.exposure_time: float
        self.frame_rate: float
        self.gain: float

class HikRobotCamera:
    """海康威视工业相机.

    提供与海康威视工业相机交互的方法.
    """

    def __init__(self, host: str) -> None:
        """初始化海康威视工业相机对象.

        Args:
            host (str): 摄像头的IP地址.

        """
        ...

    def open(self) -> None:
        """打开摄像头."""
        ...

    def close(self) -> None:
        """关闭摄像头."""
        ...

    def start_stream(self) -> bool:
        """启动图像采集.

        Returns:
            bool: 是否成功启动图像采集.

        """
        ...

    def stop_stream(self) -> bool:
        """停止图像采集.

        Returns:
            bool: 是否成功停止图像采集.

        """
        ...

    def capture(self) -> np.ndarray:
        """获取摄像头的一帧图像.

        Returns:
            np.ndarray: 一帧图像.

        """
        ...

    def configure(self, config: CameraConfig) -> None:
        """配置相机参数.

        Args:
            config: CameraConfig 对象.

        """
        ...

    def is_open(self) -> bool:
        """检查相机是否已打开.

        Returns:
            bool: 如果相机已打开,返回 True,否则返回 False.

        """
        ...

    def is_streaming(self) -> bool:
        """检查是否正在采集图像.

        Returns:
            bool: 如果相机正在采集图像,返回 True,否则返回 False.

        """
        ...

    def width(self) -> int:
        """获取摄像头的宽度.

        Returns:
            int: 摄像头的宽度.

        """
        ...

    def height(self) -> int:
        """获取摄像头的高度.

        Returns:
            int: 摄像头的高度.

        """
        ...

    def frame_rate(self) -> float:
        """获取摄像头的帧率.

        Returns:
            float: 摄像头的帧率.

        """
        ...
    def set_roi(self, offset_x: int, offset_y: int, width: int, height: int) -> None:
        """设置感兴趣区域(ROI).

        注意: 必须在相机打开但未开始采集时调用此方法.

        Args:
            offset_x (int): ROI区域左上角X坐标
            offset_y (int): ROI区域左上角Y坐标
            width (int): ROI区域宽度
            height (int): ROI区域高度

        Raises:
            CameraException: 如果参数无效或设置失败

        """
        ...

    def get_roi(self) -> tuple[int, int, int, int]:
        """获取当前ROI设置.

        Returns:
            Tuple[int, int, int, int]: (offset_x, offset_y, width, height)

        """
        ...

    def reset_roi(self) -> None:
        """重置ROI为最大区域.

        注意: 必须在相机打开但未开始采集时调用此方法.
        """
        ...
    def __enter__(self) -> HikRobotCamera:
        """支持 Python 的上下文管理器.

        Returns:
            HikRobotCamera: 相机实例.

        """
        ...

    def __exit__(self, exc_type: type | None, exc_value: BaseException | None, traceback: object | None) -> None:
        """支持 Python 的上下文管理器.关闭相机."""
        ...

# 异常类
class CameraException(Exception):
    """相机异常类,用于捕获与相机相关的错误."""

    ...
