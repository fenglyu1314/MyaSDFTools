#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11

# C++扩展模块配置
ext_modules = [
    Pybind11Extension(
        "sdf_core",
        [
            "src/cpp/sdf_core.cpp",
            "src/cpp/sdf_algorithms.cpp",
            "src/cpp/bindings.cpp",
        ],
        include_dirs=[
            # pybind11头文件路径
            pybind11.get_include(),
            # 项目头文件路径
            "src/cpp/include",
        ],
        language='c++',
        cxx_std=17,
    ),
]

setup(
    name="mya_sdf_tools",
    version="0.1.0",
    author="Mya",
    description="二次元脸部SDF生成工具",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    python_requires=">=3.8",
    install_requires=[
        "PySide6>=6.5.0",
        "Pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "pybind11>=2.11.0",
        "scipy>=1.11.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "sdf-tool=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C++",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
