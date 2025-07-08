cmake_minimum_required(VERSION 3.16)
project(mya_sdf_tools)

# 设置C++标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 设置编译选项
if(MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /O2 /openmp")
else()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -fopenmp")
endif()

# 查找Python和pybind11
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# 包含目录
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/src/cpp/include
    ${Python_INCLUDE_DIRS}
)

# 源文件
set(CPP_SOURCES
    src/cpp/sdf_core.cpp
    src/cpp/sdf_algorithms.cpp
    src/cpp/bindings.cpp
)

# 头文件
set(CPP_HEADERS
    src/cpp/include/sdf_core.h
    src/cpp/include/sdf_algorithms.h
    src/cpp/include/common.h
)

# 创建pybind11模块
pybind11_add_module(sdf_core ${CPP_SOURCES} ${CPP_HEADERS})

# 设置模块属性
target_compile_definitions(sdf_core PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})

# 链接库
if(WIN32)
    # Windows特定链接
    target_link_libraries(sdf_core PRIVATE ${Python_LIBRARIES})
else()
    # Linux/Mac链接
    target_link_libraries(sdf_core PRIVATE)
endif()

# 设置输出目录
set_target_properties(sdf_core PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# 安装规则
install(TARGETS sdf_core DESTINATION .)

# 测试配置
enable_testing()
add_subdirectory(tests OPTIONAL)
