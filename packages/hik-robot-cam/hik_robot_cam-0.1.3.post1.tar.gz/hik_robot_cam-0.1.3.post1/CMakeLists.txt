cmake_minimum_required(VERSION 3.15)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

# 设置较低的 C++ 标准版本
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find the module development requirements (requires FindPython from 3.17 or
# scikit-build-core's built-in backport)
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)
message(STATUS "pybind11 version: ${pybind11_VERSION}")
message(STATUS "pybind11_INCLUDE_DIRS: ${pybind11_INCLUDE_DIRS}")
message(STATUS "pybind11_LIBRARIES: ${pybind11_LIBRARIES}")

# 添加 OpenCV 头文件路径
find_package(OpenCV REQUIRED)
message(STATUS "OpenCV Libs: \n${OpenCV_LIBS}\n")
message(STATUS "OpenCV Headers: \n${OpenCV_INCLUDE_DIRS}\n")

# 添加海康工业相机 SDK
file(GLOB_RECURSE MVS_LIBS "/opt/MVS/lib/64/*so")

# 添加包含目录
include_directories(${pybind11_INCLUDE_DIRS} ${OpenCV_INCLUDE_DIRS} ../ /opt/MVS/include/)

# 设置源文件
set(SOURCES
    ${CMAKE_SOURCE_DIR}/codec/hik_robot_cam.cpp
    ${CMAKE_SOURCE_DIR}/codec/bindings.cpp
)

# 设置库目录
link_directories(/usr/local/lib /opt/MVS/lib/64 ${CMAKE_SOURCE_DIR}/codec)

# 创建共享库
pybind11_add_module(hik_robot_cam ${SOURCES})

# 链接库
target_link_libraries(hik_robot_cam PRIVATE ${MVS_LIBS} ${OpenCV_LIBS})

install(TARGETS hik_robot_cam DESTINATION hik_robot_cam)
install(DIRECTORY ${CMAKE_SOURCE_DIR}/python_bindings/ DESTINATION hik_robot_cam)
