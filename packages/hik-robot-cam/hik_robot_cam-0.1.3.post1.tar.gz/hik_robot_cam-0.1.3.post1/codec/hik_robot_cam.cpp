#include "hik_robot_cam.hpp"
#include <regex>
#include <sstream>
#include <thread>

namespace hik_robot
{

namespace
{
// IP地址格式验证正则表达式
const std::regex kIpRegex("^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\."
                          "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\."
                          "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\."
                          "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$");
} // namespace

Camera::Camera(const std::string &ip) : ip_(ip) { validateIp(ip); }

Camera::~Camera()
{
    try {
        if (isStreaming()) {
            stopStream();
        }
        if (isOpen()) {
            close();
        }
    } catch (...) {
        // 确保析构函数不抛出异常
    }
}

void Camera::validateIp(const std::string &ip)
{
    if (ip.empty() || !std::regex_match(ip, kIpRegex)) {
        throw CameraException("无效的IP地址: " + ip);
    }
}

void Camera::open()
{
    std::lock_guard<std::recursive_mutex> lock(mutex_);

    if (isOpen()) {
        return;
    }

    // 枚举设备列表
    MV_CC_DEVICE_INFO_LIST device_list;
    memset(&device_list, 0, sizeof(MV_CC_DEVICE_INFO_LIST));

    int result = MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, &device_list);
    checkResult(result, "设备枚举失败");

    if (device_list.nDeviceNum == 0) {
        throw CameraException("未找到设备");
    }

    // 查找指定IP的设备
    int device_index = findDevice(device_list);
    if (device_index == -1) {
        throw CameraException("未找到IP为" + ip_ + "的设备");
    }

    // 创建相机句柄
    result = MV_CC_CreateHandle(&handle_, device_list.pDeviceInfo[device_index]);
    checkResult(result, "创建句柄失败");

    // 打开设备
    result = MV_CC_OpenDevice(handle_);
    if (result != MV_OK) {
        MV_CC_DestroyHandle(handle_);
        handle_ = nullptr;
        throw CameraException("打开设备失败");
    }

    // 设置网口相机的最优包大小
    if (device_list.pDeviceInfo[device_index]->nTLayerType == MV_GIGE_DEVICE) {
        int packet_size = MV_CC_GetOptimalPacketSize(handle_);
        if (packet_size > 0) {
            result = MV_CC_SetIntValueEx(handle_, "GevSCPSPacketSize", packet_size);
            checkResult(result, "设置包大小失败");
        }
    }

    updateROILimits();
    updateResolution();
}

void Camera::close()
{
    std::lock_guard<std::recursive_mutex> lock(mutex_);

    if (!isOpen()) {
        return;
    }

    // 确保停止采集
    if (is_streaming_) {
        stopStream();
    }

    // 关闭设备
    int result = MV_CC_CloseDevice(handle_);
    checkResult(result, "关闭设备失败");

    // 销毁句柄
    result = MV_CC_DestroyHandle(handle_);
    checkResult(result, "销毁句柄失败");

    handle_ = nullptr;
    is_streaming_ = false;
}

void Camera::startStream()
{
    std::lock_guard<std::recursive_mutex> lock(mutex_);

    if (!isOpen()) {
        throw CameraException("相机未打开");
    }

    if (is_streaming_) {
        return;
    }

    // 设置触发模式为关闭
    int result = MV_CC_SetEnumValue(handle_, "TriggerMode", MV_TRIGGER_MODE_OFF);
    checkResult(result, "设置触发模式失败");

    // 设置采集模式为连续采集
    result = MV_CC_SetEnumValue(handle_, "AcquisitionMode", MV_ACQ_MODE_CONTINUOUS);
    checkResult(result, "设置采集模式失败");

    // 开始取流
    result = MV_CC_StartGrabbing(handle_);
    checkResult(result, "开始取流失败");

    is_streaming_ = true;
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
}

void Camera::stopStream()
{
    std::lock_guard<std::recursive_mutex> lock(mutex_);

    if (!is_streaming_) {
        return;
    }

    // 停止采集
    int result = MV_CC_StopGrabbing(handle_);
    checkResult(result, "停止采集失败");

    is_streaming_ = false;
}

cv::Mat Camera::capture()
{
    std::lock_guard<std::recursive_mutex> lock(mutex_);

    if (!isStreaming()) {
        throw CameraException("未开始图像采集");
    }

    // 获取一帧图像
    MV_FRAME_OUT frame = {0};
    int result = MV_CC_GetImageBuffer(handle_, &frame, 1000);
    checkResult(result, "获取图像失败");

    cv::Mat image;
    bool convert_success = convertToMat(image, &frame.stFrameInfo, frame.pBufAddr);

    // 释放图像缓存
    MV_CC_FreeImageBuffer(handle_, &frame);

    if (!convert_success) {
        throw CameraException("图像格式转换失败");
    }

    return image;
}

void Camera::configure(const CameraConfig &config)
{
    std::lock_guard<std::recursive_mutex> lock(mutex_);

    if (!isOpen()) {
        throw CameraException("相机未打开");
    }

    // 设置曝光时间
    int result = MV_CC_SetFloatValue(handle_, "ExposureTime", config.exposure_time);
    checkResult(result, "设置曝光时间失败");

    // 设置帧率
    result = MV_CC_SetBoolValue(handle_, "AcquisitionFrameRateEnable", true);
    checkResult(result, "设置帧率使能失败");
    result = MV_CC_SetFloatValue(handle_, "AcquisitionFrameRate", config.frame_rate);
    checkResult(result, "设置帧率失败");

    // 设置增益
    result = MV_CC_SetFloatValue(handle_, "Gain", config.gain);
    checkResult(result, "设置增益失败");
}

float Camera::frameRate() const
{
    std::lock_guard<std::recursive_mutex> lock(mutex_);

    if (!isOpen()) {
        throw CameraException("相机未打开");
    }

    MVCC_FLOATVALUE frame_rate = {0};
    int result = MV_CC_GetFloatValue(handle_, "AcquisitionFrameRate", &frame_rate);
    checkResult(result, "获取帧率失败");

    return frame_rate.fCurValue;
}

bool Camera::convertToMat(cv::Mat &image, const MV_FRAME_OUT_INFO_EX *frame_info, const unsigned char *data) const
{
    if (!frame_info || !data) {
        return false;
    }

    switch (frame_info->enPixelType) {
    case PixelType_Gvsp_Mono8:
        image = cv::Mat(frame_info->nHeight, frame_info->nWidth, CV_8UC1, (void *)data);
        break;

    case PixelType_Gvsp_RGB8_Packed:
        image = cv::Mat(frame_info->nHeight, frame_info->nWidth, CV_8UC3, (void *)data);
        break;

    case PixelType_Gvsp_BayerGR8: {
        cv::Mat temp(frame_info->nHeight, frame_info->nWidth, CV_8UC1, (void *)data);
        cv::cvtColor(temp, image, cv::COLOR_BayerGR2BGR);
    } break;

    case PixelType_Gvsp_BayerRG8: {
        cv::Mat temp(frame_info->nHeight, frame_info->nWidth, CV_8UC1, (void *)data);
        cv::cvtColor(temp, image, cv::COLOR_BayerBG2BGR);
    } break;

    default:
        return false;
    }

    return true;
}

void Camera::updateROILimits()
{
    if (!isOpen()) {
        throw CameraException("相机未打开");
    }

    MVCC_INTVALUE width_max = {0};
    MVCC_INTVALUE height_max = {0};

    int result = MV_CC_GetIntValue(handle_, "WidthMax", &width_max);
    checkResult(result, "获取最大宽度失败");

    result = MV_CC_GetIntValue(handle_, "HeightMax", &height_max);
    checkResult(result, "获取最大高度失败");

    max_width_ = static_cast<int>(width_max.nCurValue);
    max_height_ = static_cast<int>(height_max.nCurValue);
}

void Camera::updateResolution()
{
    if (!isOpen()) {
        throw CameraException("相机未打开");
    }

    MVCC_INTVALUE width_info = {0};
    MVCC_INTVALUE height_info = {0};
    MVCC_INTVALUE offset_x_info = {0};
    MVCC_INTVALUE offset_y_info = {0};

    int result = MV_CC_GetIntValue(handle_, "Width", &width_info);
    checkResult(result, "获取图像宽度失败");

    result = MV_CC_GetIntValue(handle_, "Height", &height_info);
    checkResult(result, "获取图像高度失败");

    result = MV_CC_GetIntValue(handle_, "OffsetX", &offset_x_info);
    if (result != MV_OK) // 如果OffsetX不可用，默认为0
        offset_x_ = 0;
    else
        offset_x_ = static_cast<int>(offset_x_info.nCurValue);

    result = MV_CC_GetIntValue(handle_, "OffsetY", &offset_y_info);
    if (result != MV_OK) // 如果OffsetY不可用，默认为0
        offset_y_ = 0;
    else
        offset_y_ = static_cast<int>(offset_y_info.nCurValue);

    width_ = static_cast<int>(width_info.nCurValue);
    height_ = static_cast<int>(height_info.nCurValue);
}

void Camera::setROI(const int offset_x, const int offset_y, const int width, const int height)
{
    std::lock_guard<std::recursive_mutex> lock(mutex_);

    if (!isOpen() || is_streaming_) {
        throw CameraException(isOpen() ? "相机正在采集，无法设置ROI" : "相机未打开");
    }

    // 验证参数范围
    if (offset_x < 0 || offset_y < 0 || width <= 0 || height <= 0) {
        throw CameraException("ROI参数无效: 偏移量和尺寸必须为正");
    }

    // 计算对齐后的ROI参数
    const uint _width = (width / 16) * 16;
    const uint _height = (height / 16) * 16;
    const uint _offset_x = (offset_x / 16) * 16;
    const uint _offset_y = (offset_y / 16) * 16;

    // 验证ROI是否在有效范围内
    if ((_offset_x + _width) > max_width_ || (_offset_y + _height) > max_height_) {
        throw CameraException("ROI超出传感器范围: 最大宽度=" + std::to_string(max_width_) +
                              ", 最大高度=" + std::to_string(max_height_));
    }

    // 重置ROI参数
    checkResult(MV_CC_SetIntValueEx(handle_, "OffsetX", 0), "重置OffsetX失败");
    checkResult(MV_CC_SetIntValueEx(handle_, "OffsetY", 0), "重置OffsetY失败");
    checkResult(MV_CC_SetIntValueEx(handle_, "Width", max_width_), "设置Width失败");
    checkResult(MV_CC_SetIntValueEx(handle_, "Height", max_height_), "设置Height失败");

    // 设置ROI参数并更新分辨率
    checkResult(MV_CC_SetIntValueEx(handle_, "Width", _width), "设置Width失败");
    checkResult(MV_CC_SetIntValueEx(handle_, "Height", _height), "设置Height失败");
    checkResult(MV_CC_SetIntValueEx(handle_, "OffsetX", _offset_x), "设置OffsetX失败");
    checkResult(MV_CC_SetIntValueEx(handle_, "OffsetY", _offset_y), "设置OffsetY失败");

    updateResolution();
}

std::tuple<int, int, int, int> Camera::getROI() const
{
    std::lock_guard<std::recursive_mutex> lock(mutex_);
    if (!isOpen()) {
        throw CameraException("相机未打开");
    }
    return std::make_tuple(offset_x_, offset_y_, width_, height_);
}

void Camera::resetROI()
{
    std::lock_guard<std::recursive_mutex> lock(mutex_);

    if (!isOpen()) {
        throw CameraException("相机未打开");
    }

    if (is_streaming_) {
        throw CameraException("相机正在采集，无法重置ROI");
    }

    checkResult(MV_CC_SetIntValueEx(handle_, "OffsetX", 0), "重置OffsetX失败");
    checkResult(MV_CC_SetIntValueEx(handle_, "OffsetY", 0), "重置OffsetY失败");
    checkResult(MV_CC_SetIntValueEx(handle_, "Width", max_width_), "设置Width失败");
    checkResult(MV_CC_SetIntValueEx(handle_, "Height", max_height_), "设置Height失败");

    // 更新分辨率信息
    updateResolution();
}

void Camera::checkResult(int result, const std::string &operation) const
{
    if (result != MV_OK) {
        std::stringstream ss;
        ss << operation << " (错误码: 0x" << std::hex << result << ")";
        throw CameraException(ss.str());
    }
}

int Camera::findDevice(const MV_CC_DEVICE_INFO_LIST &devices)
{
    for (unsigned int i = 0; i < devices.nDeviceNum; i++) {
        MV_CC_DEVICE_INFO *device_info = devices.pDeviceInfo[i];
        if (!device_info || device_info->nTLayerType != MV_GIGE_DEVICE) {
            continue;
        }

        // 获取设备IP地址
        int device_ip = device_info->SpecialInfo.stGigEInfo.nCurrentIp;
        std::stringstream ss;
        ss << ((device_ip & 0xff000000) >> 24) << "." << ((device_ip & 0x00ff0000) >> 16) << "."
           << ((device_ip & 0x0000ff00) >> 8) << "." << (device_ip & 0x000000ff);

        if (ss.str() == ip_) {
            return i;
        }
    }
    return -1;
}

} // namespace hik_robot
