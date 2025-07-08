#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试实时光照预览功能

验证角度预览功能是否正常工作
"""

import sys
import os
import numpy as np
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.sdf_generator import SDFGenerator

def create_test_sdf():
    """创建测试SDF数据"""
    # 创建一个简单的圆形SDF
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

def test_lighting_preview():
    """测试光照预览功能"""
    print("🔆 测试实时光照预览功能")
    print("=" * 50)
    
    # 创建测试SDF
    sdf_data = create_test_sdf()
    print(f"📊 测试SDF形状: {sdf_data.shape}")
    print(f"📈 SDF值域: [{sdf_data.min():.3f}, {sdf_data.max():.3f}]")
    
    # 创建SDF生成器
    generator = SDFGenerator()
    
    # 测试不同角度的光照效果
    test_angles = [0, 45, 90, 135, 180, 225, 270, 315]
    
    print(f"\n🔄 测试 {len(test_angles)} 个角度的光照效果:")
    
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
            
            # 保存结果
            from utils.image_utils import ImageUtils
            result_path = f"temp/lighting_preview_{angle:03d}deg.png"
            ImageUtils.save_sdf_as_image(lighting_result, result_path, colormap='gray')
            
        except Exception as e:
            print(f"  角度 {angle:3d}°: 失败 - {str(e)}")

def test_lighting_parameters():
    """测试不同光照参数"""
    print(f"\n💡 测试不同光照参数:")
    
    sdf_data = create_test_sdf()
    generator = SDFGenerator()
    
    # 测试不同光照强度
    intensities = [0.5, 1.0, 1.5, 2.0]
    for intensity in intensities:
        try:
            result = generator.preview_lighting(
                sdf_data, 
                45,  # 固定角度
                lighting_intensity=intensity,
                ambient_light=0.3
            )
            print(f"  光照强度 {intensity:.1f}: 值域[{result.min():.3f}, {result.max():.3f}]")
            
            # 保存结果
            from utils.image_utils import ImageUtils
            result_path = f"temp/lighting_intensity_{intensity:.1f}.png"
            ImageUtils.save_sdf_as_image(result, result_path, colormap='gray')
            
        except Exception as e:
            print(f"  光照强度 {intensity:.1f}: 失败 - {str(e)}")
    
    # 测试不同环境光
    ambients = [0.0, 0.2, 0.5, 0.8]
    for ambient in ambients:
        try:
            result = generator.preview_lighting(
                sdf_data, 
                45,  # 固定角度
                lighting_intensity=1.0,
                ambient_light=ambient
            )
            print(f"  环境光 {ambient:.1f}: 值域[{result.min():.3f}, {result.max():.3f}]")
            
            # 保存结果
            from utils.image_utils import ImageUtils
            result_path = f"temp/ambient_light_{ambient:.1f}.png"
            ImageUtils.save_sdf_as_image(result, result_path, colormap='gray')
            
        except Exception as e:
            print(f"  环境光 {ambient:.1f}: 失败 - {str(e)}")

def main():
    """主函数"""
    try:
        # 确保输出目录存在
        Path("temp").mkdir(exist_ok=True)
        
        # 测试光照预览
        test_lighting_preview()
        
        # 测试光照参数
        test_lighting_parameters()
        
        print("\n🎉 光照预览测试完成！")
        print("💡 请查看 temp/ 目录中的结果图像")
        print("📝 不同角度和参数应该产生明显不同的光照效果")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
