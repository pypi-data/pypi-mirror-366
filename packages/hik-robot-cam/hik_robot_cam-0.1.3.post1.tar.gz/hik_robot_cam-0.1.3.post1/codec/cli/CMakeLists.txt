cmake_minimum_required(VERSION 3.15)
project(hik_camera_cpp LANGUAGES CXX)

# 设置较低的 C++ 标准版本
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 添加 OpenCV 头文件路径
find_package(OpenCV REQUIRED)
message(STATUS "OpenCV Libs: \n${OpenCV_LIBS}\n")
message(STATUS "OpenCV Headers: \n${OpenCV_INCLUDE_DIRS}\n")

file(GLOB_RECURSE MVS_LIBS "/opt/MVS/lib/64/*so")

# 添加包含目录
include_directories(${OpenCV_INCLUDE_DIRS} ../ /opt/MVS/include/)

# 添加链接库
add_executable(main main.cpp ../hik_robot_cam.cpp)

target_link_libraries(main ${MVS_LIBS} ${OpenCV_LIBS})
