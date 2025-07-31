#include "hik_robot_cam.hpp"
#include <opencv2/opencv.hpp>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

// 辅助函数:将 cv::Mat 转换为 numpy array
py::array_t<unsigned char> cv_mat_to_numpy(const cv::Mat &input)
{
    cv::Mat output;

    // 判断输入图像的通道数
    if (input.channels() == 1) {
        // 单通道图像，重复通道到三通道
        cv::cvtColor(input, output, cv::COLOR_GRAY2BGR); // 灰度转BGR
    } else if (input.channels() == 3) {
        // 三通道图像（例如BGR），直接使用
        output = input;
    } else if (input.channels() == 4) {
        // 四通道图像（例如BGRA），去掉alpha通道
        cv::cvtColor(input, output, cv::COLOR_BGRA2BGR);
    } else {
        // 如果是其他通道数的图像，可以根据需要扩展
        throw std::runtime_error("不支持的图像通道数");
    }

    // 转换为 NumPy 数组并返回
    return py::array_t<unsigned char>({output.rows, output.cols, 3}, output.data);
}

PYBIND11_MODULE(hik_robot_cam, m)
{
    m.doc() = "海康工业相机Python接口模块"; // 模块文档字符串

    // 绑定相机配置结构体
    py::class_<hik_robot::CameraConfig>(m, "CameraConfig")
        .def(py::init<>())
        .def_readwrite("exposure_time", &hik_robot::CameraConfig::exposure_time, "曝光时间")
        .def_readwrite("frame_rate", &hik_robot::CameraConfig::frame_rate, "帧率")
        .def_readwrite("gain", &hik_robot::CameraConfig::gain, "增益");

    // 绑定相机类
    py::class_<hik_robot::Camera>(m, "HikRobotCamera")
        .def(py::init<const std::string &>(), "初始化相机，需要传入IP地址")
        .def("open", &hik_robot::Camera::open, "打开相机")
        .def("close", &hik_robot::Camera::close, "关闭相机")
        .def("start_stream", &hik_robot::Camera::startStream, "开始图像采集")
        .def("stop_stream", &hik_robot::Camera::stopStream, "停止图像采集")
        .def("configure", &hik_robot::Camera::configure, "配置相机参数")
        .def("is_open", &hik_robot::Camera::isOpen, "检查相机是否已打开")
        .def("is_streaming", &hik_robot::Camera::isStreaming, "检查是否正在采集图像")
        .def("width", &hik_robot::Camera::width, "获取图像宽度")
        .def("height", &hik_robot::Camera::height, "获取图像高度")
        .def("frame_rate", &hik_robot::Camera::frameRate, "获取当前帧率")
        // ROI功能
        .def("set_roi", &hik_robot::Camera::setROI, py::arg("offset_x"), py::arg("offset_y"), py::arg("width"),
             py::arg("height"),
             "设置ROI区域\n"
             "参数:\n"
             "  offset_x: ROI区域左上角X坐标\n"
             "  offset_y: ROI区域左上角Y坐标\n"
             "  width: ROI区域宽度\n"
             "  height: ROI区域高度")
        .def("get_roi", &hik_robot::Camera::getROI, "获取当前ROI设置，返回元组(offset_x, offset_y, width, height)")
        .def("reset_roi", &hik_robot::Camera::resetROI, "重置ROI为最大区域")
        // 修改后的捕获函数，动态处理图像的通道
        .def(
            "capture", [](hik_robot::Camera &self) { return cv_mat_to_numpy(self.capture()); }, "捕获一帧图像")
        // 支持Python的上下文管理器
        .def("__enter__",
             [](hik_robot::Camera &self) {
                 self.open();
                 return &self;
             })
        .def("__exit__", [](hik_robot::Camera &self, py::object, py::object, py::object) { self.close(); });

    // 注册异常类
    py::register_exception<hik_robot::CameraException>(m, "CameraException");
}
