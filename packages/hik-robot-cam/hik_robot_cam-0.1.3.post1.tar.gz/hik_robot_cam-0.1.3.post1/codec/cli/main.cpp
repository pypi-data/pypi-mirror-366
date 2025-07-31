#include "hik_robot_cam.hpp"
#include <chrono>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <opencv2/opencv.hpp>
#include <string>
#include <thread>

// 帧率计算器类
class FpsCounter
{
public:
    void update()
    {
        auto now = std::chrono::steady_clock::now();
        if (last_time_ == std::chrono::steady_clock::time_point{}) {
            last_time_ = now;
            return;
        }

        frame_count_++;
        auto diff = std::chrono::duration_cast<std::chrono::seconds>(now - last_time_).count();
        if (diff >= 1) {
            current_fps_ = static_cast<double>(frame_count_) / static_cast<double>(diff);
            frame_count_ = 0;
            last_time_ = now;
        }
    }

    double getFps() const { return current_fps_; }

private:
    std::chrono::steady_clock::time_point last_time_;
    int frame_count_ = 0;
    double current_fps_ = 0.0;
};

void printUsage(const char *program_name)
{
    std::cout << "用法: " << program_name << " [选项]\n"
              << "选项:\n"
              << "  -h, --help           显示此帮助信息\n"
              << "  -i, --ip <IP>        指定相机IP地址 (默认: 192.168.1.100)\n"
              << "  -g, --gui            启用GUI实时显示模式 (默认)\n"
              << "  -v, --video          录制5秒视频模式\n"
              << "\n示例:\n"
              << "  " << program_name << " --gui --ip 192.168.1.200\n"
              << "  " << program_name << " --video\n";
}

int main(int argc, char *argv[])
{
    // 默认参数
    std::string camera_ip = "192.168.1.100";
    bool gui_mode = true;
    bool video_mode = false;

    // 解析命令行参数
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            printUsage(argv[0]);
            return 0;
        } else if (strcmp(argv[i], "-i") == 0 || strcmp(argv[i], "--ip") == 0) {
            if (i + 1 < argc) {
                camera_ip = argv[++i];
            } else {
                std::cerr << "错误: --ip 选项需要指定IP地址\n";
                return -1;
            }
        } else if (strcmp(argv[i], "-g") == 0 || strcmp(argv[i], "--gui") == 0) {
            gui_mode = true;
            video_mode = false;
        } else if (strcmp(argv[i], "-v") == 0 || strcmp(argv[i], "--video") == 0) {
            video_mode = true;
            gui_mode = false;
        } else {
            std::cerr << "错误: 未知选项 " << argv[i] << "\n";
            printUsage(argv[0]);
            return -1;
        }
    }

    try {
        // 创建相机实例
        hik_robot::Camera camera(camera_ip);

        // 配置相机参数
        hik_robot::CameraConfig config;
        config.exposure_time = 5000.0f; // 设置曝光时间
        config.frame_rate = 30.0f;      // 设置目标帧率
        config.gain = 0.0f;             // 设置增益

        // 打开相机并开始采集
        camera.open();
        camera.configure(config);
        camera.startStream();

        // 打印相机信息
        std::cout << "相机初始化成功:\n"
                  << "- 相机IP: " << camera_ip << "\n"
                  << "- 目标帧率: " << camera.frameRate() << " fps\n"
                  << "- 分辨率: " << camera.width() << "x" << camera.height() << "\n"
                  << "- 模式: " << (gui_mode ? "GUI实时显示" : "录制5秒视频") << "\n";

        if (gui_mode) {
            // GUI模式：实时显示
            std::cout << "启动GUI模式，按 'q'、'Q' 或 ESC 退出...\n";

            // 创建窗口和帧率计数器
            cv::namedWindow("相机预览", cv::WINDOW_NORMAL);
            FpsCounter fps_counter;

            // 主循环
            while (true) {
                auto start = std::chrono::steady_clock::now();
                cv::Mat frame;

                try {
                    // 捕获图像
                    frame = camera.capture();

                    // 更新帧率计数器
                    fps_counter.update();

                    // 在图像上显示实时帧率
                    std::stringstream ss;
                    ss << std::fixed << std::setprecision(1) << "FPS: " << fps_counter.getFps();
                    cv::putText(frame, ss.str(), cv::Point(10, 30), cv::FONT_HERSHEY_SIMPLEX, 1.0,
                                cv::Scalar(0, 255, 0), 2);

                    // 显示图像
                    cv::imshow("相机预览", frame);
                } catch (const hik_robot::CameraException &e) {
                    std::cerr << "采集图像错误: " << e.what() << std::endl;
                    break;
                }

                // 检查键盘输入
                int key = cv::waitKey(1);
                if (key == 'q' || key == 'Q' || key == 27) { // q, Q 或 ESC
                    // 保存采集图像
                    if (!frame.empty()) {
                        cv::imwrite("capture.jpg", frame);
                        std::cout << "已保存当前帧到 capture.jpg\n";
                    }
                    break;
                }

                // 按目标帧率控制循环
                auto elapsed = std::chrono::steady_clock::now() - start;
                auto target_duration =
                    std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::seconds(1)) / camera.frameRate();

                if (elapsed < target_duration) {
                    std::this_thread::sleep_for(target_duration - elapsed);
                }
            }
        } else if (video_mode) {
            // 视频录制模式：录制5秒视频
            std::cout << "启动视频录制模式，将录制5秒视频...\n";

            // 设置视频编码器
            cv::VideoWriter video_writer;
            std::string filename = "recorded_video.mp4";
            int fourcc = cv::VideoWriter::fourcc('m', 'p', '4', 'v');
            cv::Size frame_size(camera.width(), camera.height());
            double fps = camera.frameRate();

            bool writer_initialized = false;
            auto start_time = std::chrono::steady_clock::now();
            auto duration = std::chrono::seconds(5);

            FpsCounter fps_counter;
            int frame_count = 0;

            while (std::chrono::steady_clock::now() - start_time < duration) {
                cv::Mat frame;

                try {
                    // 捕获图像
                    frame = camera.capture();

                    // 初始化视频写入器（使用第一帧的实际尺寸）
                    if (!writer_initialized && !frame.empty()) {
                        frame_size = cv::Size(frame.cols, frame.rows);
                        video_writer.open(filename, fourcc, fps, frame_size);
                        if (!video_writer.isOpened()) {
                            std::cerr << "无法创建视频文件: " << filename << std::endl;
                            break;
                        }
                        writer_initialized = true;
                        std::cout << "开始录制视频: " << filename << " (" << frame_size.width << "x"
                                  << frame_size.height << ")\n";
                    }

                    // 写入视频帧
                    if (writer_initialized && !frame.empty()) {
                        video_writer.write(frame);
                        frame_count++;

                        // 更新帧率计数器
                        fps_counter.update();

                        // 显示进度
                        auto elapsed = std::chrono::steady_clock::now() - start_time;
                        auto elapsed_sec =
                            std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count() / 1000.0;
                        std::cout << "\r录制进度: " << std::fixed << std::setprecision(1) << elapsed_sec
                                  << "/5.0秒, 帧数: " << frame_count << ", FPS: " << fps_counter.getFps() << std::flush;
                    }
                } catch (const hik_robot::CameraException &e) {
                    std::cerr << "\n采集图像错误: " << e.what() << std::endl;
                    break;
                }

                // 控制帧率
                std::this_thread::sleep_for(std::chrono::milliseconds(static_cast<int>(1000.0 / fps)));
            }

            // 释放视频写入器
            if (writer_initialized) {
                video_writer.release();
                std::cout << "\n视频录制完成: " << filename << " (共 " << frame_count << " 帧)\n";
            }
        }

        // 停止采集和关闭相机
        camera.stopStream();
        camera.close();

        // 清理窗口（如果使用了GUI模式）
        if (gui_mode) {
            cv::destroyAllWindows();
        }

        std::cout << "程序正常退出\n";
    } catch (const hik_robot::CameraException &e) {
        std::cerr << "相机错误: " << e.what() << std::endl;
        return -1;
    } catch (const std::exception &e) {
        std::cerr << "程序错误: " << e.what() << std::endl;
        return -1;
    }

    return 0;
}
