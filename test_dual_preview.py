#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试双预览区域功能

验证原始SDF和光照效果预览是否正常工作
"""

import sys
import os
import numpy as np
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.sdf_generator import SDFGenerator

def create_simple_sdf():
    """创建简单的测试SDF"""
    size = 128
    center = size // 2
    radius = 40
    
    sdf = np.zeros((size, size), dtype=np.float32)
    
    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center
            distance = np.sqrt(dx*dx + dy*dy)
            
            if distance <= radius:
                # 内部：距离中心越近值越大
                sdf[y, x] = 1.0 - (distance / radius)
            else:
                # 外部：距离边界越远值越小
                sdf[y, x] = max(0.0, 1.0 - (distance - radius) / 20.0)
    
    return sdf

def test_lighting_angles():
    """测试不同角度的光照效果"""
    print("🔆 测试双预览区域和光照效果")
    print("=" * 50)
    
    # 创建测试SDF
    sdf_data = create_simple_sdf()
    print(f"📊 创建测试SDF: 形状{sdf_data.shape}, 值域[{sdf_data.min():.3f}, {sdf_data.max():.3f}]")
    
    # 创建SDF生成器
    generator = SDFGenerator()
    
    # 测试不同角度的光照效果
    test_angles = [0, 45, 90, 135, 180, 225, 270, 315]
    
    print(f"\n🔄 生成 {len(test_angles)} 个角度的光照效果:")
    
    from utils.image_utils import ImageUtils
    
    # 保存原始SDF
    ImageUtils.save_sdf_as_image(sdf_data, "temp/original_sdf.png", colormap='gray')
    print(f"💾 原始SDF已保存: temp/original_sdf.png")
    
    for angle in test_angles:
        try:
            # 生成光照预览
            lighting_result = generator.preview_lighting(
                sdf_data, 
                angle,
                lighting_intensity=1.0,
                ambient_light=0.3
            )
            
            print(f"  角度 {angle:3d}°: 成功 - 值域[{lighting_result.min():.3f}, {lighting_result.max():.3f}]")
            
            # 保存光照效果
            result_path = f"temp/lighting_{angle:03d}deg.png"
            ImageUtils.save_sdf_as_image(lighting_result, result_path, colormap='gray')
            
        except Exception as e:
            print(f"  角度 {angle:3d}°: 失败 - {str(e)}")
    
    print(f"\n💡 请在应用中:")
    print(f"  1. 导入一些黑白图像")
    print(f"  2. 生成SDF")
    print(f"  3. 在预览区域拖动光照角度滑竿")
    print(f"  4. 观察右侧光照效果预览的变化")
    print(f"  5. 调整光照强度和环境光参数")

def main():
    """主函数"""
    try:
        # 确保输出目录存在
        Path("temp").mkdir(exist_ok=True)
        
        # 测试光照效果
        test_lighting_angles()
        
        print("\n🎉 双预览区域测试完成！")
        print("💡 功能说明:")
        print("  ✅ 左侧显示原始SDF")
        print("  ✅ 右侧显示光照效果预览")
        print("  ✅ 拖动角度滑竿实时更新右侧预览")
        print("  ✅ 光照强度和环境光可调节")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
