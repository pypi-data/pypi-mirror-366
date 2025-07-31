#pragma once

#include <MvCameraControl.h>
#include <opencv2/opencv.hpp>
#include <stdexcept>
#include <string>

namespace hik_robot
{

// 相机操作异常类
class CameraException : public std::runtime_error
{
public:
    explicit CameraException(const std::string &message) : std::runtime_error(message) {}
};

// 相机配置结构体
struct CameraConfig {
    float exposure_time = 2000.0f; // 曝光时间，默认10000
    float frame_rate = 30.0f;      // 帧率，默认30fps
    float gain = 0.0f;             // 增益，默认0
};

class Camera
{
public:
    // 构造函数，需要传入相机IP地址
    explicit Camera(const std::string &ip);
    ~Camera();

    // 禁用拷贝构造和赋值操作，确保资源安全
    Camera(const Camera &) = delete;
    Camera &operator=(const Camera &) = delete;

    // 核心操作接口
    void open();        // 打开相机
    void close();       // 关闭相机
    void startStream(); // 开始图像流
    void stopStream();  // 停止图像流
    cv::Mat capture();  // 捕获一帧图像

    // 配置接口
    void configure(const CameraConfig &config);                                             // 配置相机参数
    void setROI(const int offset_x, const int offset_y, const int width, const int height); // 设置ROI区域
    void resetROI();                                                                        // 重置ROI区域
    std::tuple<int, int, int, int> getROI() const;                                          // 获取ROI区域

    // 状态查询接口
    bool isOpen() const noexcept { return handle_ != nullptr; } // 相机是否已打开
    bool isStreaming() const noexcept { return is_streaming_; } // 是否正在采集图像

    // 相机信息查询
    int width() const noexcept { return width_; }   // 图像宽度
    int height() const noexcept { return height_; } // 图像高度
    float frameRate() const;                        // 当前帧率

private:
    // 内部辅助方法
    void validateIp(const std::string &ip);                // IP地址验证
    int findDevice(const MV_CC_DEVICE_INFO_LIST &devices); // 查找设备
    void checkResult(int result,
                     const std::string &operation) const; // 检查操作结果
    bool convertToMat(cv::Mat &image,                     // 转换图像格式到OpenCV
                      const MV_FRAME_OUT_INFO_EX *frame_info, const unsigned char *data) const;
    void updateResolution(); // 更新分辨率信息
    void updateROILimits();  // 更新ROI限制信息

    // 成员变量
    std::string ip_;           // 相机IP地址
    void *handle_{nullptr};    // 相机句柄
    int width_{0};             // 图像宽度
    int height_{0};            // 图像高度
    int max_width_{0};         // 最大图像宽度
    int max_height_{0};        // 最大图像高度
    int offset_x_{0};          // ROI X偏移
    int offset_y_{0};          // ROI Y偏移
    bool is_streaming_{false}; // 采集状态标志

    // 线程同步锁
    mutable std::recursive_mutex mutex_; // 递归互斥锁，保证线程安全
};

} // namespace hik_robot
