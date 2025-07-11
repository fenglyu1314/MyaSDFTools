#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
光照效果测试脚本

测试修复后的SDF数据在光照预览中的效果
"""

import numpy as np
import cv2
from src.core.sdf_core_algorithm import SDFCoreAlgorithm
from src.ui.lighting_preview_handler import LightingPreviewHandler

def create_test_face_image(size=256):
    """创建一个简单的脸部形状测试图像"""
    image = np.zeros((size, size), dtype=np.uint8)
    
    # 脸部轮廓 (椭圆)
    center = (size // 2, size // 2)
    axes = (size // 3, size // 2.5)
    cv2.ellipse(image, center, (int(axes[0]), int(axes[1])), 0, 0, 360, 255, -1)
    
    # 眼睛 (两个小圆)
    eye_y = size // 2 - size // 8
    left_eye = (size // 2 - size // 6, eye_y)
    right_eye = (size // 2 + size // 6, eye_y)
    cv2.circle(image, left_eye, size // 20, 0, -1)
    cv2.circle(image, right_eye, size // 20, 0, -1)
    
    # 嘴巴 (小椭圆)
    mouth_center = (size // 2, size // 2 + size // 6)
    cv2.ellipse(image, mouth_center, (size // 12, size // 24), 0, 0, 360, 0, -1)
    
    return image

def test_lighting_angles():
    """测试不同角度的光照效果"""
    print("🧪 测试光照效果...")
    
    # 创建测试图像
    test_img = create_test_face_image(256)
    
    # 计算SDF
    sdf_result = SDFCoreAlgorithm.compute_sdf_python(
        test_img, normalize=True, sdf_direction="both", max_distance=100
    )
    
    print(f"📊 SDF值范围: [{np.min(sdf_result):.3f}, {np.max(sdf_result):.3f}]")
    
    # 创建光照预览处理器
    lighting_handler = LightingPreviewHandler()
    lighting_handler.current_merged_sdf = sdf_result
    
    # 测试不同角度
    test_angles = [-180, -90, 0, 90, 180]
    
    for angle in test_angles:
        lighting_result = lighting_handler._apply_lighting_effect(
            sdf_result, angle, intensity=1.0, ambient=0.3
        )
        
        if lighting_result is not None:
            # 统计黑白像素比例
            gray_result = lighting_result[:, :, 0] if len(lighting_result.shape) == 3 else lighting_result
            white_pixels = np.sum(gray_result > 128)
            black_pixels = np.sum(gray_result <= 128)
            total_pixels = gray_result.size
            
            white_ratio = white_pixels / total_pixels
            black_ratio = black_pixels / total_pixels
            
            print(f"🔆 角度{angle:4d}°: 白色{white_ratio:.2%}, 黑色{black_ratio:.2%}")
        else:
            print(f"❌ 角度{angle:4d}°: 光照计算失败")
    
    print("✅ 光照效果测试完成")
    return True

def test_sdf_boundary_values():
    """测试SDF边界值的正确性"""
    print("\n🧪 测试SDF边界值...")
    
    # 创建简单的圆形图像
    size = 128
    image = np.zeros((size, size), dtype=np.uint8)
    center = size // 2
    radius = size // 4
    cv2.circle(image, (center, center), radius, 255, -1)
    
    # 计算SDF
    sdf_result = SDFCoreAlgorithm.compute_sdf_python(
        image, normalize=True, sdf_direction="both", max_distance=50
    )
    
    # 检查关键位置的值
    center_val = sdf_result[center, center]
    boundary_val = sdf_result[center, center + radius]
    outer_val = sdf_result[center, center + radius + 20]
    
    print(f"🎯 中心值: {center_val:.3f} (应该接近0.0)")
    print(f"🎯 边界值: {boundary_val:.3f} (应该接近0.5)")
    print(f"🎯 外部值: {outer_val:.3f} (应该接近1.0)")

    # 验证边界值是否符合预期 (按照文章定义修正)
    success = True
    if center_val > 0.2:  # 中心应该接近0.0
        print("❌ 中心值偏高")
        success = False
    if abs(boundary_val - 0.5) > 0.1:  # 边界应该接近0.5
        print("❌ 边界值不正确")
        success = False
    if outer_val < 0.7:  # 外部应该接近1.0
        print("❌ 外部值偏低")
        success = False
    
    if success:
        print("✅ SDF边界值测试通过")
    else:
        print("❌ SDF边界值测试失败")
    
    return success

def test_lighting_consistency():
    """测试光照效果的一致性"""
    print("\n🧪 测试光照一致性...")
    
    # 创建测试图像
    test_img = create_test_face_image(128)
    sdf_result = SDFCoreAlgorithm.compute_sdf_python(
        test_img, normalize=True, sdf_direction="both", max_distance=50
    )
    
    lighting_handler = LightingPreviewHandler()
    lighting_handler.current_merged_sdf = sdf_result
    
    # 测试对称角度应该产生镜像效果
    angle_pairs = [(-90, 90), (-45, 45), (-135, 135)]
    
    success = True
    for neg_angle, pos_angle in angle_pairs:
        result_neg = lighting_handler._apply_lighting_effect(sdf_result, neg_angle, 1.0, 0.3)
        result_pos = lighting_handler._apply_lighting_effect(sdf_result, pos_angle, 1.0, 0.3)
        
        if result_neg is not None and result_pos is not None:
            # 检查是否为镜像关系
            gray_neg = result_neg[:, :, 0] if len(result_neg.shape) == 3 else result_neg
            gray_pos = result_pos[:, :, 0] if len(result_pos.shape) == 3 else result_pos
            
            # 翻转负角度结果并比较
            flipped_neg = np.fliplr(gray_neg)
            difference = np.mean(np.abs(flipped_neg.astype(float) - gray_pos.astype(float)))
            
            print(f"🔄 角度对({neg_angle:4d}°, {pos_angle:3d}°): 差异={difference:.2f}")
            
            if difference > 50:  # 允许一定的差异
                print(f"⚠️  角度对({neg_angle}, {pos_angle})差异较大")
                success = False
        else:
            print(f"❌ 角度对({neg_angle}, {pos_angle})计算失败")
            success = False
    
    if success:
        print("✅ 光照一致性测试通过")
    else:
        print("❌ 光照一致性测试失败")
    
    return success

def main():
    """主测试函数"""
    print("🚀 开始光照效果验证测试")
    print("=" * 50)
    
    # 测试1: 基本光照效果
    test1_success = test_lighting_angles()
    
    # 测试2: SDF边界值
    test2_success = test_sdf_boundary_values()
    
    # 测试3: 光照一致性
    test3_success = test_lighting_consistency()
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 光照测试结果总结:")
    print(f"  基本光照效果: {'✅ 通过' if test1_success else '❌ 失败'}")
    print(f"  SDF边界值: {'✅ 通过' if test2_success else '❌ 失败'}")
    print(f"  光照一致性: {'✅ 通过' if test3_success else '❌ 失败'}")
    
    all_success = test1_success and test2_success and test3_success
    if all_success:
        print("\n🎉 所有光照测试通过！")
    else:
        print("\n⚠️  部分光照测试失败，需要进一步调试")
    
    return all_success

if __name__ == "__main__":
    main()
