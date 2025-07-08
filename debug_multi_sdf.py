#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试多图SDF生成问题

检查多张图像是否正确参与SDF计算
"""

import sys
import os
import numpy as np
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.sdf_generator import SDFGenerator

def create_test_images():
    """创建测试图像"""
    from PIL import Image
    
    # 创建简单的测试图像
    size = 64
    
    # 图像1: 左侧亮 (0度光照)
    img1 = np.zeros((size, size), dtype=np.uint8)
    img1[:, :size//2] = 255
    
    # 图像2: 上侧亮 (90度光照)  
    img2 = np.zeros((size, size), dtype=np.uint8)
    img2[:size//2, :] = 255
    
    # 图像3: 右侧亮 (180度光照)
    img3 = np.zeros((size, size), dtype=np.uint8)
    img3[:, size//2:] = 255
    
    # 保存测试图像
    test_dir = Path("temp")
    test_dir.mkdir(exist_ok=True)
    
    Image.fromarray(img1).save(test_dir / "debug_0deg.png")
    Image.fromarray(img2).save(test_dir / "debug_90deg.png") 
    Image.fromarray(img3).save(test_dir / "debug_180deg.png")
    
    return [
        str(test_dir / "debug_0deg.png"),
        str(test_dir / "debug_90deg.png"),
        str(test_dir / "debug_180deg.png")
    ]

def debug_single_vs_multi():
    """对比单图和多图SDF生成"""
    print("🔍 调试多图SDF生成问题")
    print("=" * 50)
    
    # 创建测试图像
    image_paths = create_test_images()
    angles = [0, 90, 180]
    
    generator = SDFGenerator()
    
    print(f"📁 测试图像: {len(image_paths)} 张")
    print(f"📐 角度设置: {angles}")
    
    # 测试单张图像SDF
    print("\n🔸 单张图像SDF测试:")
    for i, path in enumerate(image_paths):
        try:
            sdf_result, time_cost = generator.compute_single_sdf(
                path, threshold=0.5, normalize=True
            )
            print(f"  图像{i+1}: 成功 - 形状{sdf_result.shape}, 值域[{sdf_result.min():.3f}, {sdf_result.max():.3f}], 时间{time_cost:.3f}s")
        except Exception as e:
            print(f"  图像{i+1}: 失败 - {str(e)}")
    
    # 测试多张图像混合SDF
    print("\n🔸 多张图像混合SDF测试:")
    
    # 测试不同混合模式
    blend_modes = ["weighted", "average", "max", "min"]
    
    for mode in blend_modes:
        try:
            print(f"\n  混合模式: {mode}")
            sdf_result, time_cost = generator.compute_multi_sdf(
                image_paths=image_paths,
                angles=angles,
                threshold=0.5,
                normalize=True,
                blend_mode=mode
            )
            
            print(f"    ✅ 成功 - 形状{sdf_result.shape}")
            print(f"    📊 值域: [{sdf_result.min():.3f}, {sdf_result.max():.3f}]")
            print(f"    ⏱️  时间: {time_cost:.3f}s")
            
            # 保存结果用于检查
            from utils.image_utils import ImageUtils
            result_path = f"temp/debug_multi_{mode}.png"
            ImageUtils.save_sdf_as_image(sdf_result, result_path)
            print(f"    💾 已保存: {result_path}")
            
        except Exception as e:
            print(f"    ❌ 失败: {str(e)}")
            import traceback
            traceback.print_exc()

def debug_angle_weights():
    """调试角度权重计算"""
    print("\n🧮 角度权重计算调试:")
    print("=" * 30)
    
    generator = SDFGenerator()
    
    test_angles = [0, 90, 180]
    weights = generator._calculate_angle_weights(test_angles)
    
    print(f"角度: {test_angles}")
    print(f"权重: {[f'{w:.3f}' for w in weights]}")
    print(f"权重和: {sum(weights):.3f}")

def main():
    """主函数"""
    try:
        debug_single_vs_multi()
        debug_angle_weights()
        
        print("\n🎉 调试完成！")
        print("💡 请检查 temp/ 目录中的结果图像")
        print("📝 如果多图混合结果与单图结果明显不同，说明多图混合正常工作")
        
    except Exception as e:
        print(f"\n❌ 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
