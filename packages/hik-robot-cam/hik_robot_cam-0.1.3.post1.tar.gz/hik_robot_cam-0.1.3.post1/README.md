# HikRobotCamera

`HikRobotCamera` 是一个高性能的 Python 库，专为海康威视工业相机设计。基于 C++ 和 pybind11 实现，提供了完整的相机控制功能，包括图像采集、参数配置、ROI 设置等。

## ✨ 特性

- 🚀 **高性能**: 基于 C++ 实现，提供高效的图像采集性能
- 🔧 **易于使用**: 简洁的 Python API，支持上下文管理器
- 📷 **功能完整**: 支持相机配置、ROI 设置、实时图像采集
- 🛡️ **线程安全**: 内置线程安全机制，支持多线程环境
- 📝 **类型提示**: 完整的类型注解，提供良好的开发体验

## 📁 项目结构

```
├── CMakeLists.txt               # 项目构建配置文件
├── codec/                       # C++ 核心实现
│   ├── bindings.cpp             # Python 绑定代码
│   ├── cli/                     # 命令行工具
│   │   ├── CMakeLists.txt       # CLI 构建配置
│   │   └── main.cpp             # CLI 主程序
│   ├── hik_robot_cam.cpp        # 相机核心实现
│   └── hik_robot_cam.hpp        # 相机头文件
├── example/                     # 示例代码
│   ├── example_camera.py        # 相机管理器示例
│   ├── test_roi.py              # ROI 功能示例
│   └── test_show.py             # 图像显示示例
├── python_bindings/             # Python 绑定
│   ├── __init__.py              # 包初始化
│   └── hik_robot_cam.pyi        # 类型提示文件
├── pyproject.toml               # 项目配置
├── uv.lock                      # 依赖锁定文件
└── README.md                    # 项目文档
```

## 🚀 快速开始

### 系统要求

- Python 3.8 或更高版本
- CMake 3.10 或更高版本
- Linux x86_64 系统
- 海康威视工业相机

### 安装步骤

#### 1. 安装海康威视 SDK

首先需要安装海康威视机器视觉 SDK。可以从官网下载或使用内网地址：

**官方下载**: [海康机器人官网](https://www.hikrobotics.com/cn/machinevision/service/download/?module=0)

```bash
# 下载 Linux x86_64 版本, 解压并安装
tar -zxvf MVS-3.0.1_x86_64_20240629.tar.gz
cd MVS-3.0.1_x86_64_20240629
sudo ./setup.sh
```

#### 2. 安装 Python 包

```bash
uv add hik-robot-cam
```

#### 3. 验证安装

```python
import hik_robot_cam
print(hik_robot_cam.__version__)  # 显示版本信息
```

## 📖 使用指南

### 基本用法

#### 导入库

```python
from hik_robot_cam import HikRobotCamera, CameraConfig, CameraException
import cv2
import numpy as np
```

#### 创建相机实例

```python
# 使用相机 IP 地址创建实例
camera = HikRobotCamera("192.168.1.100")
```

#### 推荐：使用上下文管理器

使用 `with` 语句可以自动管理相机资源，确保正确释放：

```python
with HikRobotCamera("192.168.1.100") as camera:
    # 配置相机参数
    config = CameraConfig()
    config.exposure_time = 5000.0  # 曝光时间 (μs)
    config.frame_rate = 30.0       # 帧率 (fps)
    config.gain = 1.0              # 增益

    camera.configure(config)

    # 开始采集
    camera.start_stream()

    # 捕获图像
    frame = camera.capture()
    print(f"图像尺寸: {frame.shape}")  # (height, width, channels)

    # 保存图像
    cv2.imwrite("captured_image.jpg", frame)

    # 停止采集
    camera.stop_stream()
    # 相机会在退出 with 块时自动关闭
```

### 高级功能

#### 相机参数配置

```python
# 创建配置对象
config = CameraConfig()
config.exposure_time = 10000.0  # 曝光时间 (微秒)
config.frame_rate = 15.0        # 帧率 (fps)
config.gain = 2.0               # 增益值

# 应用配置
camera.configure(config)
```

#### ROI (感兴趣区域) 设置

ROI 功能允许您只采集图像的特定区域，提高处理效率：

```python
with HikRobotCamera("192.168.1.100") as camera:
    # 设置 ROI: (x偏移, y偏移, 宽度, 高度)
    camera.set_roi(100, 100, 800, 600)

    # 获取当前 ROI 设置
    offset_x, offset_y, width, height = camera.get_roi()
    print(f"当前 ROI: ({offset_x}, {offset_y}, {width}, {height})")

    camera.start_stream()
    frame = camera.capture()  # 只会返回 ROI 区域的图像

    # 重置为全图像
    camera.stop_stream()
    camera.reset_roi()
    camera.start_stream()
```

#### 相机状态查询

```python
# 检查相机状态
print(f"相机已打开: {camera.is_open()}")
print(f"正在采集: {camera.is_streaming()}")

# 获取相机信息
print(f"图像尺寸: {camera.width()} x {camera.height()}")
print(f"当前帧率: {camera.frame_rate()} fps")
```

#### 连续采集示例

```python
with HikRobotCamera("192.168.1.100") as camera:
    camera.start_stream()

    try:
        for i in range(10):
            frame = camera.capture()
            cv2.imwrite(f"frame_{i:03d}.jpg", frame)
            print(f"已保存第 {i+1} 帧")
    except CameraException as e:
        print(f"采集错误: {e}")
    finally:
        camera.stop_stream()
```

### 异常处理

库提供了完善的异常处理机制：

```python
from hik_robot_cam import CameraException

try:
    with HikRobotCamera("192.168.1.100") as camera:
        camera.start_stream()
        frame = camera.capture()
except CameraException as e:
    print(f"相机操作失败: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

## 📚 示例代码

项目提供了多个示例，展示不同的使用场景：

```bash
# ROI 功能演示
python example/test_roi.py

# 图像显示示例
python example/test_show.py

# 相机管理器示例
python example/example_camera.py
```

## 📋 API 参考

### HikRobotCamera 类

| 方法                  | 描述              | 返回值                    |
| --------------------- | ----------------- | ------------------------- |
| `__init__(host: str)` | 初始化相机实例    | None                      |
| `open()`              | 打开相机连接      | None                      |
| `close()`             | 关闭相机连接      | None                      |
| `start_stream()`      | 开始图像采集      | bool                      |
| `stop_stream()`       | 停止图像采集      | bool                      |
| `capture()`           | 捕获一帧图像      | np.ndarray                |
| `configure(config)`   | 配置相机参数      | None                      |
| `set_roi(x, y, w, h)` | 设置感兴趣区域    | None                      |
| `get_roi()`           | 获取当前 ROI 设置 | Tuple[int, int, int, int] |
| `reset_roi()`         | 重置 ROI 为全图   | None                      |
| `is_open()`           | 检查相机是否打开  | bool                      |
| `is_streaming()`      | 检查是否正在采集  | bool                      |
| `width()`             | 获取图像宽度      | int                       |
| `height()`            | 获取图像高度      | int                       |
| `frame_rate()`        | 获取当前帧率      | float                     |

### CameraConfig 类

| 属性            | 类型  | 描述            | 默认值 |
| --------------- | ----- | --------------- | ------ |
| `exposure_time` | float | 曝光时间 (微秒) | 2000.0 |
| `frame_rate`    | float | 帧率 (fps)      | 30.0   |
| `gain`          | float | 增益值          | 0.0    |

## ❓ 常见问题

### Q: 相机连接失败怎么办？

A: 请检查：

- 相机 IP 地址是否正确
- 网络连接是否正常
- 海康 SDK 是否正确安装
- 相机是否被其他程序占用

### Q: 图像采集速度慢怎么优化？

A: 可以尝试：

- 使用 ROI 减少图像尺寸
- 调整曝光时间和帧率
- 确保网络带宽充足

### Q: 支持哪些图像格式？

A: 库返回的图像格式为 BGR 彩色图像 (OpenCV 标准格式)，尺寸为 (height, width, 3)。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！请确保：

- 代码符合项目风格
- 添加适当的测试
- 更新相关文档
