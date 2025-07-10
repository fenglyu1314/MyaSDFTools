#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化的C++扩展编译脚本
只编译简单的SDF实现用于测试
"""

import os
import sys
from pybind11.setup_helpers import Pybind11Extension, build_ext
import pybind11
from setuptools import setup

# 简单版本的源文件
cpp_sources = [
    "src/cpp/simple_sdf.cpp"
]

# 包含目录
include_dirs = [
    pybind11.get_include()
]

# 编译选项
compile_args = []
if sys.platform == "win32":
    compile_args.extend([
        "/O2",           # 优化
        "/std:c++17",    # C++17标准
        "/EHsc"          # 异常处理
    ])
else:
    compile_args.extend([
        "-O3",
        "-std=c++17"
    ])

# 定义扩展模块
ext_modules = [
    Pybind11Extension(
        "sdf_core",
        sources=cpp_sources,
        include_dirs=include_dirs,
        cxx_std=17,
        extra_compile_args=compile_args,
    ),
]

if __name__ == "__main__":
    # 检查源文件是否存在
    print("检查源文件...")
    for source in cpp_sources:
        if not os.path.exists(source):
            print(f"错误: 源文件不存在: {source}")
            sys.exit(1)
        else:
            print(f"✓ {source}")
    
    print("开始编译简化版C++扩展模块...")
    
    # 直接调用setup进行编译
    setup(
        name="sdf_core",
        ext_modules=ext_modules,
        cmdclass={"build_ext": build_ext},
        zip_safe=False,
        python_requires=">=3.7",
    )
