#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mya SDF Tools - 二次元脸部SDF生成工具

主要功能:
- 单张图像SDF生成
- 多角度图像混合SDF生成  
- 实时光照效果预览
- 高性能C++算法支持
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
    
    # 尝试导入C++扩展模块
    try:
        import sdf_core
        HAS_CPP_EXTENSION = True
    except ImportError:
        HAS_CPP_EXTENSION = False
        print("警告: C++扩展模块未找到，将使用Python实现 (性能较低)")
        
except ImportError as e:
    print(f"模块导入错误: {e}")
    HAS_CPP_EXTENSION = False

# 公开的API
__all__ = [
    'SDFGenerator',
    'ImageManager', 
    'MainWindow',
    'HAS_CPP_EXTENSION',
    '__version__'
]

def get_version_info():
    """获取版本信息"""
    info = {
        'version': __version__,
        'cpp_extension': HAS_CPP_EXTENSION,
        'description': __description__
    }
    
    if HAS_CPP_EXTENSION:
        try:
            import sdf_core
            info['cpp_version'] = sdf_core.get_version_info()
        except:
            pass
            
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
