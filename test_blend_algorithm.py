#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试改进的多图混合算法

验证新的混合策略是否正常工作
"""

import sys
import os
import numpy as np
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.sdf_generator import SDFGenerator
from utils.image_utils import ImageUtils

def create_test_images():
    """创建测试图像"""
    # 创建简单的测试图像
    size = 128
    
    # 图像1: 左侧亮
    img1 = np.zeros((size, size), dtype=np.uint8)
    img1[:, :size//2] = 255
    
    # 图像2: 右侧亮  
    img2 = np.zeros((size, size), dtype=np.uint8)
    img2[:, size//2:] = 255
    
    # 图像3: 上侧亮
    img3 = np.zeros((size, size), dtype=np.uint8)
    img3[:size//2, :] = 255
    
    # 图像4: 下侧亮
    img4 = np.zeros((size, size), dtype=np.uint8)
    img4[size//2:, :] = 255
    
    # 保存测试图像
    test_dir = Path("temp")
    test_dir.mkdir(exist_ok=True)
    
    from PIL import Image
    
    Image.fromarray(img1).save(test_dir / "test_left.png")
    Image.fromarray(img2).save(test_dir / "test_right.png") 
    Image.fromarray(img3).save(test_dir / "test_top.png")
    Image.fromarray(img4).save(test_dir / "test_bottom.png")
    
    return [
        str(test_dir / "test_left.png"),
        str(test_dir / "test_right.png"),
        str(test_dir / "test_top.png"),
        str(test_dir / "test_bottom.png")
    ]

def test_blend_modes():
    """测试不同的混合模式"""
    print("🧪 测试改进的多图混合算法")
    print("=" * 50)
    
    # 创建测试图像
    print("📁 创建测试图像...")
    image_paths = create_test_images()
    
    # 设置角度
    angles = [0, 90, 180, 270]  # 四个方向
    
    # 初始化SDF生成器
    generator = SDFGenerator()
    
    # 测试不同混合模式
    blend_modes = ["weighted", "average", "max", "min"]
    
    for mode in blend_modes:
        print(f"\n🔄 测试混合模式: {mode}")
        
        try:
            # 计算混合SDF
            sdf_result, computation_time = generator.compute_multi_sdf(
                image_paths=image_paths,
                angles=angles,
                threshold=0.5,
                normalize=True,
                blend_mode=mode
            )
            
            print(f"  ✅ 计算成功")
            print(f"  ⏱️  计算时间: {computation_time:.3f}s")
            print(f"  📊 结果形状: {sdf_result.shape}")
            print(f"  📈 值域: [{sdf_result.min():.3f}, {sdf_result.max():.3f}]")
            
            # 保存结果
            result_path = f"temp/blend_result_{mode}.png"
            ImageUtils.save_sdf_as_image(sdf_result, result_path)
            print(f"  💾 结果已保存: {result_path}")
            
        except Exception as e:
            print(f"  ❌ 计算失败: {str(e)}")

def test_angle_weights():
    """测试角度权重计算"""
    print("\n🧮 测试角度权重计算")
    print("=" * 50)
    
    generator = SDFGenerator()
    
    # 测试不同角度分布
    test_cases = [
        ([0, 90, 180, 270], "均匀分布"),
        ([0, 45, 90], "不均匀分布"),
        ([0, 10, 20], "密集分布"),
        ([0], "单角度"),
        ([0, 180], "对称分布")
    ]
    
    for angles, description in test_cases:
        print(f"\n📐 {description}: {angles}")
        
        try:
            weights = generator._calculate_angle_weights(angles)
            print(f"  权重: {[f'{w:.3f}' for w in weights]}")
            print(f"  权重和: {sum(weights):.3f}")
            
            # 验证权重和为1
            if abs(sum(weights) - 1.0) < 1e-6:
                print("  ✅ 权重归一化正确")
            else:
                print("  ❌ 权重归一化错误")
                
        except Exception as e:
            print(f"  ❌ 计算失败: {str(e)}")

def main():
    """主函数"""
    print("🎨 SDF工具 - 混合算法测试")
    print("=" * 60)
    
    try:
        # 测试混合模式
        test_blend_modes()
        
        # 测试角度权重
        test_angle_weights()
        
        print("\n🎉 所有测试完成！")
        print("\n💡 查看 temp/ 目录中的结果图像")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
