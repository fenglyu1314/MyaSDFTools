#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MVP版本测试脚本

测试基础功能是否正常工作
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        # 测试核心模块
        from src.core.sdf_generator import SDFGenerator
        from src.core.image_manager import ImageManager
        print("✓ 核心模块导入成功")
        
        # 测试工具模块
        from src.utils.file_utils import FileUtils
        from src.utils.image_utils import ImageUtils
        from src.utils.math_utils import MathUtils
        print("✓ 工具模块导入成功")
        
        # 测试UI模块
        from src.ui.main_window import MainWindow
        from src.ui.image_list_widget import ImageListWidget
        from src.ui.preview_widget import PreviewWidget
        from src.ui.parameter_widget import ParameterWidget
        print("✓ UI模块导入成功")
        
        return True
        
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        return False

def test_sdf_generator():
    """测试SDF生成器"""
    print("\n测试SDF生成器...")
    
    try:
        from src.core.sdf_generator import SDFGenerator
        import numpy as np
        from PIL import Image
        
        # 创建SDF生成器
        generator = SDFGenerator()
        print("✓ SDF生成器创建成功")
        
        # 创建测试图像
        test_image = np.ones((256, 256), dtype=np.uint8) * 255
        test_image[64:192, 64:192] = 0  # 中心黑色方块
        
        # 保存测试图像
        os.makedirs("temp", exist_ok=True)
        test_image_path = "temp/test_image.png"
        Image.fromarray(test_image, mode='L').save(test_image_path)
        print("✓ 测试图像创建成功")
        
        # 测试单张SDF生成
        sdf_result, computation_time = generator.compute_single_sdf(test_image_path)
        print(f"✓ 单张SDF生成成功，计算时间: {computation_time:.3f}s")
        print(f"  SDF结果形状: {sdf_result.shape}")
        print(f"  SDF值范围: [{sdf_result.min():.3f}, {sdf_result.max():.3f}]")
        
        # 测试多张SDF生成
        image_paths = [test_image_path, test_image_path]  # 使用相同图像测试
        multi_sdf, multi_time = generator.compute_multi_sdf(image_paths)
        print(f"✓ 多张SDF生成成功，计算时间: {multi_time:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"✗ SDF生成器测试失败: {e}")
        return False

def test_image_manager():
    """测试图像管理器"""
    print("\n测试图像管理器...")
    
    try:
        from src.core.image_manager import ImageManager
        
        # 创建图像管理器
        manager = ImageManager()
        print("✓ 图像管理器创建成功")
        
        # 测试添加图像
        test_image_path = "temp/test_image.png"
        if os.path.exists(test_image_path):
            success = manager.add_image(test_image_path)
            if success:
                print("✓ 图像添加成功")
                
                # 测试获取图像信息
                info = manager.get_image_info(test_image_path)
                if info:
                    print(f"  图像尺寸: {info.get_size_string()}")
                    print(f"  文件大小: {info.get_file_size_string()}")
                
                # 测试统计信息
                stats = manager.get_statistics()
                print(f"  统计信息: {stats}")
                
            else:
                print("✗ 图像添加失败")
                return False
        else:
            print("✗ 测试图像不存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 图像管理器测试失败: {e}")
        return False

def test_ui_creation():
    """测试UI创建"""
    print("\n测试UI创建...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from src.ui.main_window import MainWindow
        
        # 创建应用程序
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        window = MainWindow()
        print("✓ 主窗口创建成功")
        
        # 测试窗口属性
        print(f"  窗口标题: {window.windowTitle()}")
        print(f"  窗口尺寸: {window.size().width()}x{window.size().height()}")
        
        # 不显示窗口，只测试创建
        # window.show()
        
        return True
        
    except Exception as e:
        print(f"✗ UI创建测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖项"""
    print("测试依赖项...")
    
    dependencies = [
        ('PySide6', 'PySide6'),
        ('PIL', 'Pillow'),
        ('numpy', 'numpy'),
        ('cv2', 'opencv-python'),
        ('scipy', 'scipy')
    ]
    
    missing_deps = []
    
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} (缺失)")
            missing_deps.append(package_name)
    
    if missing_deps:
        print(f"\n缺少依赖项: {', '.join(missing_deps)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """主测试函数"""
    print("=" * 50)
    print("SDF工具 MVP版本测试")
    print("=" * 50)
    
    tests = [
        ("依赖项检查", test_dependencies),
        ("模块导入", test_imports),
        ("SDF生成器", test_sdf_generator),
        ("图像管理器", test_image_manager),
        ("UI创建", test_ui_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[{passed + 1}/{total}] {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
            print(f"✓ {test_name} 通过")
        else:
            print(f"✗ {test_name} 失败")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！MVP版本可以运行。")
        print("\n启动应用程序:")
        print("python main.py")
    else:
        print("❌ 部分测试失败，请检查错误信息。")
    
    print("=" * 50)
    
    # 清理临时文件
    try:
        if os.path.exists("temp/test_image.png"):
            os.remove("temp/test_image.png")
        if os.path.exists("temp") and not os.listdir("temp"):
            os.rmdir("temp")
    except:
        pass

if __name__ == "__main__":
    main()
