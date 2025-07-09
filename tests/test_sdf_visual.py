#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SDF可视化测试脚本

创建测试图像并验证SDF生成是否正确
"""

import sys
import os
import numpy as np
from pathlib import Path
from PIL import Image

# 添加src目录到Python路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def create_test_images():
    """创建多种测试图像"""
    temp_dir = project_root / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    # 1. 简单方形
    square_img = np.ones((256, 256), dtype=np.uint8) * 255
    square_img[64:192, 64:192] = 0  # 中心黑色方块
    Image.fromarray(square_img, mode='L').save(temp_dir / "square.png")
    print("✓ 创建方形测试图像")
    
    # 2. 圆形
    circle_img = np.ones((256, 256), dtype=np.uint8) * 255
    center = 128
    radius = 64
    y, x = np.ogrid[:256, :256]
    mask = (x - center)**2 + (y - center)**2 <= radius**2
    circle_img[mask] = 0
    Image.fromarray(circle_img, mode='L').save(temp_dir / "circle.png")
    print("✓ 创建圆形测试图像")
    
    # 3. 复杂形状 - 脸部轮廓模拟
    face_img = np.ones((256, 256), dtype=np.uint8) * 255
    # 脸部外轮廓（椭圆）
    center_x, center_y = 128, 128
    a, b = 80, 100  # 椭圆参数
    y, x = np.ogrid[:256, :256]
    face_mask = ((x - center_x)/a)**2 + ((y - center_y)/b)**2 <= 1
    face_img[face_mask] = 0
    
    # 添加一些内部特征（眼睛、嘴巴区域保持白色）
    # 左眼
    eye_mask1 = ((x - 100)/15)**2 + ((y - 100)/10)**2 <= 1
    face_img[eye_mask1] = 255
    
    # 右眼
    eye_mask2 = ((x - 156)/15)**2 + ((y - 100)/10)**2 <= 1
    face_img[eye_mask2] = 255
    
    # 嘴巴
    mouth_mask = ((x - 128)/25)**2 + ((y - 160)/8)**2 <= 1
    face_img[mouth_mask] = 255
    
    Image.fromarray(face_img, mode='L').save(temp_dir / "face.png")
    print("✓ 创建脸部轮廓测试图像")
    
    return [
        str(temp_dir / "square.png"),
        str(temp_dir / "circle.png"),
        str(temp_dir / "face.png")
    ]

def test_sdf_generation():
    """测试SDF生成"""
    print("\n测试SDF生成...")
    
    try:
        from src.core.sdf_generator import SDFGenerator
        
        # 创建测试图像
        test_images = create_test_images()
        
        # 创建SDF生成器
        generator = SDFGenerator()
        print(f"SDF生成器初始化完成 (C++后端: {'启用' if generator.use_cpp_backend else '禁用'})")
        
        # 测试每个图像
        for i, image_path in enumerate(test_images):
            print(f"\n处理图像 {i+1}: {Path(image_path).name}")
            
            # 生成SDF
            sdf_result, computation_time = generator.compute_single_sdf(
                image_path, 
                threshold=0.5, 
                normalize=True
            )
            
            if sdf_result is not None:
                print(f"  ✓ SDF生成成功")
                print(f"  - 计算时间: {computation_time:.3f}s")
                print(f"  - SDF形状: {sdf_result.shape}")
                print(f"  - 数值范围: [{sdf_result.min():.3f}, {sdf_result.max():.3f}]")
                
                # 保存SDF结果
                sdf_image = (sdf_result * 255).astype(np.uint8)
                output_path = project_root / "temp" / f"sdf_{Path(image_path).stem}.png"
                Image.fromarray(sdf_image, mode='L').save(output_path)
                print(f"  - SDF保存到: {output_path}")
            else:
                print(f"  ✗ SDF生成失败")
                return False
        
        return True
        
    except Exception as e:
        print(f"SDF生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multi_sdf():
    """测试多图SDF混合"""
    print("\n测试多图SDF混合...")
    
    try:
        from src.core.sdf_generator import SDFGenerator
        
        # 创建测试图像
        test_images = create_test_images()
        
        # 创建SDF生成器
        generator = SDFGenerator()
        
        # 测试多图混合
        angles = [0, 120, 240]  # 三个角度
        
        mixed_sdf, computation_time = generator.compute_multi_sdf(
            test_images,
            angles=angles,
            threshold=0.5,
            normalize=True,
            blend_mode="weighted"
        )
        
        if mixed_sdf is not None:
            print(f"  ✓ 多图SDF混合成功")
            print(f"  - 计算时间: {computation_time:.3f}s")
            print(f"  - 混合SDF形状: {mixed_sdf.shape}")
            print(f"  - 数值范围: [{mixed_sdf.min():.3f}, {mixed_sdf.max():.3f}]")
            
            # 保存混合结果
            mixed_image = (mixed_sdf * 255).astype(np.uint8)
            output_path = project_root / "temp" / "mixed_sdf_result.png"
            Image.fromarray(mixed_image, mode='L').save(output_path)
            print(f"  - 混合SDF保存到: {output_path}")
            
            return True
        else:
            print(f"  ✗ 多图SDF混合失败")
            return False
        
    except Exception as e:
        print(f"多图SDF测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🎨 SDF可视化测试")
    print("=" * 50)
    
    tests = [
        ("SDF生成", test_sdf_generation),
        ("多图SDF混合", test_multi_sdf),
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
        print("🎉 所有可视化测试通过！")
        print(f"\n生成的测试文件位于: {project_root / 'temp'}")
    else:
        print("⚠️ 部分测试失败，请检查错误信息。")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
