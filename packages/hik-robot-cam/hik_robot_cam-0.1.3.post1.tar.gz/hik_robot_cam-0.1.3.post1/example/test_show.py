import cv2
import hik_robot_cam


def main():
    # 创建相机实例
    camera = hik_robot_cam.HikRobotCamera("192.168.1.66")

    # 配置相机参数
    config = hik_robot_cam.CameraConfig()
    config.exposure_time = 1000.0  # 设置曝光时间
    config.frame_rate = 30.0  # 设置帧率
    config.gain = 8.0  # 设置增益

    # 使用上下文管理器自动管理资源
    with camera:
        # 配置并开始采集
        camera.configure(config)
        camera.start_stream()

        try:
            # 循环采集图像
            i = 0
            while True:
                i += 1
                frame = camera.capture()

                # 曝光时间写在图像上
                cv2.putText(
                    frame,
                    f"Exposure Time: {config.exposure_time} us",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                )

                cv2.imshow("xx", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                if i % 100 == 0:
                    config.exposure_time += 1000.0  # 每100帧增加曝光时间
                    camera.configure(config)

        finally:
            # 确保正确释放资源
            camera.stop_stream()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
