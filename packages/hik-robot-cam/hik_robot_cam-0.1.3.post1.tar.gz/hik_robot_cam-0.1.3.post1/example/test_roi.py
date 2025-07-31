import time

import cv2
import hik_robot_cam


def main():
    # 创建相机实例
    camera = hik_robot_cam.HikRobotCamera("192.168.1.66")

    # 配置相机参数
    config = hik_robot_cam.CameraConfig()
    config.exposure_time = 5000.0  # 设置曝光时间
    config.frame_rate = 5.0  # 设置帧率
    config.gain = 3.0  # 设置增益

    # 使用上下文管理器自动管理资源
    with camera:
        # 配置并开始采集
        camera.configure(config)
        camera.reset_roi()
        camera.start_stream()

        frame = camera.capture()
        cv2.imwrite("test.jpg", frame)
        camera.stop_stream()

        time.sleep(1)
        # 配置并开始采集
        camera.set_roi(63, 168, 573, 218)
        camera.start_stream()

        frame = camera.capture()
        cv2.imwrite("test_with_roi.jpg", frame)
        camera.stop_stream()


if __name__ == "__main__":
    main()
