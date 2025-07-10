#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
C++扩展编译脚本
使用pybind11直接编译，不依赖CMake
"""

import os
import sys
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11
from setuptools import setup, Extension

# 源文件列表
cpp_sources = [
    "src/cpp/sdf_core.cpp",
    "src/cpp/sdf_algorithms.cpp", 
    "src/cpp/bindings.cpp"
]

# 包含目录
include_dirs = [
    "src/cpp/include",
    pybind11.get_include()
]

# 编译选项
compile_args = []
link_args = []

if sys.platform == "win32":
    # Windows编译选项
    compile_args.extend([
        "/O2",           # 优化
        "/std:c++17",    # C++17标准
        "/EHsc",         # 异常处理
        "/bigobj"        # 大对象文件
    ])
else:
    # Linux/Mac编译选项
    compile_args.extend([
        "-O3",
        "-std=c++17",
        "-ffast-math"
    ])

# 定义扩展模块
ext_modules = [
    Pybind11Extension(
        "sdf_core",
        sources=cpp_sources,
        include_dirs=include_dirs,
        cxx_std=17,
        extra_compile_args=compile_args,
        extra_link_args=link_args,
    ),
]

def build_cpp_extension():
    """编译C++扩展"""
    print("开始编译C++扩展模块...")
    
    # 检查源文件是否存在
    for source in cpp_sources:
        if not os.path.exists(source):
            print(f"错误: 源文件不存在: {source}")
            return False
    
    try:
        setup(
            name="sdf_core",
            ext_modules=ext_modules,
            cmdclass={"build_ext": build_ext},
            zip_safe=False,
            python_requires=">=3.7",
        )
        print("✅ C++扩展编译成功")
        return True
        
    except Exception as e:
        print(f"❌ C++扩展编译失败: {e}")
        return False

if __name__ == "__main__":
    # 检查源文件是否存在
    print("检查源文件...")
    for source in cpp_sources:
        if not os.path.exists(source):
            print(f"错误: 源文件不存在: {source}")
            sys.exit(1)
        else:
            print(f"✓ {source}")

    print("开始编译C++扩展模块...")

    # 直接调用setup进行编译
    setup(
        name="sdf_core",
        ext_modules=ext_modules,
        cmdclass={"build_ext": build_ext},
        zip_safe=False,
        python_requires=">=3.7",
    )
