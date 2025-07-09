#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
核心功能测试

测试SDF工具的核心功能是否正常工作
"""

import sys
import os
import tempfile
import numpy as np
from pathlib import Path
from PIL import Image

# 添加src目录到Python路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """测试模块导入"""
    print("🧪 测试模块导入...")
    
    try:
        # 测试核心模块
        from core.sdf_generator import SDFGenerator
        from core.image_manager import ImageManager
        from core.config_manager import ConfigManager
        print("  ✅ 核心模块导入成功")

        # 测试工具模块
        from utils.file_utils import FileUtils
        from utils.image_utils import ImageUtils
        from utils.math_utils import MathUtils
        print("  ✅ 工具模块导入成功")

        # 测试UI模块
        from ui.main_window import MainWindow
        print("  ✅ UI模块导入成功")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ 模块导入失败: {e}")
        return False

def test_sdf_generator():
    """测试SDF生成器"""
    print("🧪 测试SDF生成器...")
    
    try:
        from core.sdf_generator import SDFGenerator
        
        # 创建测试图像
        test_image_path = create_test_image()
        
        # 创建SDF生成器
        generator = SDFGenerator()
        print(f"  ✅ SDF生成器创建成功 (C++后端: {'是' if generator.use_cpp_backend else '否'})")
        
        # 测试单张图像SDF生成
        sdf_result, computation_time = generator.compute_single_sdf(test_image_path)
        
        if sdf_result is not None and sdf_result.size > 0:
            print(f"  ✅ 单张SDF生成成功 ({computation_time:.3f}s)")
            print(f"     SDF形状: {sdf_result.shape}")
            print(f"     数值范围: [{sdf_result.min():.3f}, {sdf_result.max():.3f}]")
        else:
            print("  ❌ SDF生成失败")
            return False
        
        # 清理测试文件
        os.unlink(test_image_path)
        
        return True
        
    except Exception as e:
        print(f"  ❌ SDF生成器测试失败: {e}")
        return False

def test_image_manager():
    """测试图像管理器"""
    print("🧪 测试图像管理器...")
    
    try:
        from core.image_manager import ImageManager
        
        # 创建测试图像
        test_image_path = create_test_image()
        
        # 创建图像管理器
        manager = ImageManager()
        print("  ✅ 图像管理器创建成功")
        
        # 测试图像加载
        image_info = manager.add_image(test_image_path)
        
        if image_info and image_info.is_valid():
            print(f"  ✅ 图像加载成功")
            print(f"     尺寸: {image_info.get_size_string()}")
            print(f"     格式: {image_info.format}")
            print(f"     文件大小: {image_info.get_file_size_string()}")
        else:
            print("  ❌ 图像加载失败")
            return False
        
        # 清理测试文件
        os.unlink(test_image_path)
        
        return True
        
    except Exception as e:
        print(f"  ❌ 图像管理器测试失败: {e}")
        return False

def test_config_manager():
    """测试配置管理器"""
    print("🧪 测试配置管理器...")
    
    try:
        from core.config_manager import ConfigManager
        
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
        
        # 创建配置管理器
        config = ConfigManager(config_path)
        print("  ✅ 配置管理器创建成功")
        
        # 测试配置保存
        config.ui.window_width = 1920
        config.ui.window_height = 1080
        
        if config.save():
            print("  ✅ 配置保存成功")
        else:
            print("  ❌ 配置保存失败")
            return False
        
        # 测试配置加载
        new_config = ConfigManager(config_path)
        if new_config.ui.window_width == 1920 and new_config.ui.window_height == 1080:
            print("  ✅ 配置加载成功")
        else:
            print("  ❌ 配置加载失败")
            return False
        
        # 清理测试文件
        os.unlink(config_path)
        
        return True
        
    except Exception as e:
        print(f"  ❌ 配置管理器测试失败: {e}")
        return False

def test_gui_creation():
    """测试GUI创建"""
    print("🧪 测试GUI创建...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from ui.main_window import MainWindow
        
        # 创建应用程序实例
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 创建主窗口
        window = MainWindow()
        print("  ✅ 主窗口创建成功")
        
        # 检查窗口基本属性
        if window.windowTitle():
            print(f"  ✅ 窗口标题: {window.windowTitle()}")
        
        # 不显示窗口，只测试创建
        window.close()
        
        return True
        
    except Exception as e:
        print(f"  ❌ GUI创建测试失败: {e}")
        return False

def create_test_image() -> str:
    """创建测试图像"""
    # 创建一个简单的测试图像
    size = 128
    image = np.ones((size, size), dtype=np.uint8) * 255
    
    # 在中心画一个黑色圆形
    center = size // 2
    radius = size // 4
    y, x = np.ogrid[:size, :size]
    mask = (x - center)**2 + (y - center)**2 <= radius**2
    image[mask] = 0
    
    # 保存为临时文件
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        temp_path = f.name
    
    Image.fromarray(image, mode='L').save(temp_path)
    return temp_path

def main():
    """主测试函数"""
    print("🚀 SDF工具核心功能测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("SDF生成器", test_sdf_generator),
        ("图像管理器", test_image_manager),
        ("配置管理器", test_config_manager),
        ("GUI创建", test_gui_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[{passed + 1}/{total}] {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有核心功能测试通过！")
        print("\n启动应用程序:")
        print("  python main.py")
    else:
        print("⚠️ 部分测试失败，请检查错误信息。")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
