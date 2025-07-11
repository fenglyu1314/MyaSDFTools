#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mya SDF Tools - 二次元脸部SDF生成工具

主要功能:
- 单张图像SDF生成
- 多角度图像混合SDF生成
- 实时光照效果预览
- 高性能Python算法实现
"""

__version__ = "0.1.0"
__author__ = "Mya"
__email__ = ""
__description__ = "二次元脸部SDF生成工具"

# 导入主要模块
try:
    from .core.sdf_generator import SDFGenerator
    from .core.image_manager import ImageManager
    from .ui.main_window import MainWindow

except ImportError as e:
    print(f"模块导入错误: {e}")

# 公开的API
__all__ = [
    'SDFGenerator',
    'ImageManager',
    'MainWindow',
    '__version__'
]

def get_version_info():
    """获取版本信息"""
    info = {
        'version': __version__,
        'description': __description__,
        'backend': 'Python'
    }

    return info

def check_dependencies():
    """检查依赖项是否正确安装"""
    missing_deps = []
    
    try:
        import PySide6
    except ImportError:
        missing_deps.append('PySide6')
        
    try:
        import numpy
    except ImportError:
        missing_deps.append('numpy')
        
    try:
        import PIL
    except ImportError:
        missing_deps.append('Pillow')
        
    try:
        import cv2
    except ImportError:
        missing_deps.append('opencv-python')
    
    if missing_deps:
        print(f"缺少依赖项: {', '.join(missing_deps)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True
