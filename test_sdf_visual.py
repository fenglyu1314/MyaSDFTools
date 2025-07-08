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
import matplotlib.pyplot as plt

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def create_test_images():
    """创建多种测试图像"""
    os.makedirs("temp", exist_ok=True)
    
    # 1. 简单方形
    square_img = np.ones((256, 256), dtype=np.uint8) * 255
    square_img[64:192, 64:192] = 0  # 中心黑色方块
    Image.fromarray(square_img, mode='L').save("temp/square.png")
    print("✓ 创建方形测试图像")
    
    # 2. 圆形
    circle_img = np.ones((256, 256), dtype=np.uint8) * 255
    center = 128
    radius = 64
    y, x = np.ogrid[:256, :256]
    mask = (x - center)**2 + (y - center)**2 <= radius**2
    circle_img[mask] = 0
    Image.fromarray(circle_img, mode='L').save("temp/circle.png")
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
    eye_mask1 = (x - 100)**2 + (y - 100)**2 <= 15**2
    face_img[eye_mask1] = 255
    # 右眼
    eye_mask2 = (x - 156)**2 + (y - 100)**2 <= 15**2
    face_img[eye_mask2] = 255
    # 嘴巴
    mouth_mask = ((x - 128)/25)**2 + ((y - 160)/10)**2 <= 1
    face_img[mouth_mask] = 255
    
    Image.fromarray(face_img, mode='L').save("temp/face.png")
    print("✓ 创建脸部轮廓测试图像")
    
    return ["temp/square.png", "temp/circle.png", "temp/face.png"]

def test_sdf_generation(image_paths):
    """测试SDF生成并可视化结果"""
    from src.core.sdf_generator import SDFGenerator
    
    generator = SDFGenerator()
    
    for i, image_path in enumerate(image_paths):
        print(f"\n测试图像: {image_path}")
        
        try:
            # 生成SDF
            sdf_result, computation_time = generator.compute_single_sdf(
                image_path, threshold=0.5, normalize=True, invert=False
            )
            
            print(f"  计算时间: {computation_time:.3f}s")
            print(f"  SDF形状: {sdf_result.shape}")
            print(f"  SDF值范围: [{sdf_result.min():.3f}, {sdf_result.max():.3f}]")
            
            # 加载原始图像
            original = np.array(Image.open(image_path).convert('L'))
            
            # 创建可视化
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            
            # 原始图像
            axes[0].imshow(original, cmap='gray')
            axes[0].set_title('原始图像')
            axes[0].axis('off')
            
            # SDF结果
            im1 = axes[1].imshow(sdf_result, cmap='viridis')
            axes[1].set_title('SDF结果')
            axes[1].axis('off')
            plt.colorbar(im1, ax=axes[1])
            
            # SDF等高线
            axes[2].contour(sdf_result, levels=10, colors='white')
            axes[2].imshow(sdf_result, cmap='viridis', alpha=0.7)
            axes[2].set_title('SDF等高线')
            axes[2].axis('off')
            
            plt.tight_layout()
            
            # 保存可视化结果
            output_path = f"temp/sdf_test_{i+1}.png"
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"  可视化结果保存到: {output_path}")
            
            # 验证SDF特性
            verify_sdf_properties(sdf_result, original)
            
        except Exception as e:
            print(f"  ✗ SDF生成失败: {e}")

def verify_sdf_properties(sdf_result, original_image):
    """验证SDF的基本特性"""
    print("  验证SDF特性:")
    
    # 1. 检查边界值
    binary_mask = original_image < 128  # 假设阈值为128
    
    # 在物体内部，SDF应该相对较大
    inside_values = sdf_result[binary_mask]
    outside_values = sdf_result[~binary_mask]
    
    if len(inside_values) > 0 and len(outside_values) > 0:
        inside_mean = inside_values.mean()
        outside_mean = outside_values.mean()
        
        print(f"    内部平均值: {inside_mean:.3f}")
        print(f"    外部平均值: {outside_mean:.3f}")
        
        if inside_mean > outside_mean:
            print("    ✓ 内部值大于外部值 (正确)")
        else:
            print("    ✗ 内部值小于外部值 (可能有问题)")
    
    # 2. 检查梯度连续性
    grad_y, grad_x = np.gradient(sdf_result)
    grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
    
    print(f"    梯度幅值范围: [{grad_magnitude.min():.3f}, {grad_magnitude.max():.3f}]")
    
    # 3. 检查值域
    if 0 <= sdf_result.min() and sdf_result.max() <= 1:
        print("    ✓ 值域在[0,1]范围内")
    else:
        print(f"    ✗ 值域超出[0,1]范围: [{sdf_result.min():.3f}, {sdf_result.max():.3f}]")

def analyze_sdf_quality():
    """分析SDF质量"""
    print("\n" + "="*50)
    print("SDF质量分析")
    print("="*50)
    
    print("\n正确的SDF应该具有以下特性:")
    print("1. 在物体边界处值约为0.5（如果归一化到[0,1]）")
    print("2. 物体内部值较大，外部值较小（或相反，取决于符号约定）")
    print("3. 距离边界越远，值的变化越大")
    print("4. 梯度应该指向最近的边界")
    print("5. 等值线应该与物体边界平行")
    
    print("\n如果看到圆形渐变，可能的原因:")
    print("- 测试图像本身就是圆形")
    print("- 算法实现有误")
    print("- 显示/可视化有问题")
    
    print("\n建议检查:")
    print("- 查看生成的可视化图像")
    print("- 对比原始图像和SDF结果")
    print("- 检查SDF值的分布")

def main():
    """主函数"""
    print("SDF可视化测试")
    print("="*30)
    
    # 创建测试图像
    print("创建测试图像...")
    image_paths = create_test_images()
    
    # 测试SDF生成
    print("\n开始SDF测试...")
    test_sdf_generation(image_paths)
    
    # 分析说明
    analyze_sdf_quality()
    
    print(f"\n测试完成！请查看temp/目录下的可视化结果。")
    print("如果matplotlib可用，会生成详细的对比图像。")

if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("请安装: pip install matplotlib")
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
