#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
单张SDF视觉效果测试脚本

验证修复后的SDF是否显示为"反色"效果
"""

import numpy as np
import cv2
from src.core.sdf_core_algorithm import SDFCoreAlgorithm

def create_simple_test_image():
    """创建一个简单的测试图像 - 白色背景上的黑色圆形"""
    size = 256
    image = np.ones((size, size), dtype=np.uint8) * 255  # 白色背景
    
    # 在中心画一个黑色圆形
    center = (size // 2, size // 2)
    radius = size // 4
    cv2.circle(image, center, radius, 0, -1)  # 黑色圆形
    
    return image

def test_sdf_visual_effect():
    """测试SDF的视觉效果"""
    print("🧪 测试单张SDF视觉效果...")
    
    # 创建测试图像
    test_img = create_simple_test_image()
    print(f"📊 原始图像: 白色背景(255) + 黑色圆形(0)")
    
    # 计算SDF
    sdf_result = SDFCoreAlgorithm.compute_sdf_python(
        test_img, normalize=True, sdf_direction="both", max_distance=50
    )
    
    # 分析SDF结果
    center = 128
    radius = 64
    
    # 检查关键位置的值
    center_val = sdf_result[center, center]  # 圆形中心（原图黑色）
    boundary_val = sdf_result[center, center + radius]  # 边界
    outer_val = sdf_result[center, center + radius + 20]  # 外部（原图白色）
    
    print(f"🎯 圆形中心值: {center_val:.3f} (原图黑色区域)")
    print(f"🎯 边界值: {boundary_val:.3f} (边界)")
    print(f"🎯 外部值: {outer_val:.3f} (原图白色区域)")
    
    # 统计SDF值分布
    inside_mask = test_img < 128  # 原图黑色区域
    outside_mask = test_img >= 128  # 原图白色区域
    
    inside_sdf_mean = np.mean(sdf_result[inside_mask])
    outside_sdf_mean = np.mean(sdf_result[outside_mask])
    
    print(f"📊 原图黑色区域的SDF平均值: {inside_sdf_mean:.3f}")
    print(f"📊 原图白色区域的SDF平均值: {outside_sdf_mean:.3f}")
    
    # 验证"反色"效果
    print("\n🔍 验证反色效果:")
    if inside_sdf_mean < outside_sdf_mean:
        print("✅ 正确！原图黑色区域 → SDF较暗值")
        print("✅ 正确！原图白色区域 → SDF较亮值")
        print("🎉 SDF显示为反色效果，符合文章要求！")
        return True
    else:
        print("❌ 错误！SDF没有显示为反色效果")
        return False

def test_compare_with_original():
    """对比修复前后的效果"""
    print("\n🧪 对比修复前后的效果...")
    
    # 创建测试图像
    test_img = create_simple_test_image()
    
    # 使用修复后的算法
    sdf_fixed = SDFCoreAlgorithm.compute_sdf_python(
        test_img, normalize=True, sdf_direction="both", max_distance=50
    )
    
    # 模拟修复前的算法（内外颠倒）
    inside_mask = test_img < 128
    outside_mask = test_img >= 128
    
    inside_dist = cv2.distanceTransform(
        inside_mask.astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE
    )
    outside_dist = cv2.distanceTransform(
        outside_mask.astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE
    )
    
    # 修复前的错误归一化（内部亮，外部暗）
    inside_max = np.max(inside_dist) if np.max(inside_dist) > 0 else 1.0
    outside_max = np.max(outside_dist) if np.max(outside_dist) > 0 else 1.0
    
    sdf_old = np.full_like(inside_dist, 0.5, dtype=np.float32)
    if np.any(inside_mask):
        normalized_inside = inside_dist[inside_mask] / inside_max * 0.5
        sdf_old[inside_mask] = 0.5 + normalized_inside  # 内部亮
    if np.any(outside_mask):
        normalized_outside = outside_dist[outside_mask] / outside_max * 0.5
        sdf_old[outside_mask] = 0.5 - normalized_outside  # 外部暗
    
    # 对比结果
    center = 128
    
    old_center = sdf_old[center, center]
    new_center = sdf_fixed[center, center]
    
    old_outer = sdf_old[center, center + 80]
    new_outer = sdf_fixed[center, center + 80]
    
    print(f"📊 修复前 - 圆形中心: {old_center:.3f}, 外部: {old_outer:.3f}")
    print(f"📊 修复后 - 圆形中心: {new_center:.3f}, 外部: {new_outer:.3f}")
    
    if new_center < new_outer and old_center > old_outer:
        print("✅ 修复成功！内外关系已正确反转")
        return True
    else:
        print("❌ 修复可能有问题")
        return False

def main():
    """主测试函数"""
    print("🚀 开始单张SDF视觉效果验证")
    print("=" * 50)
    
    # 测试1: 基本视觉效果
    test1_success = test_sdf_visual_effect()
    
    # 测试2: 对比修复前后
    test2_success = test_compare_with_original()
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 视觉效果测试结果:")
    print(f"  反色效果验证: {'✅ 通过' if test1_success else '❌ 失败'}")
    print(f"  修复前后对比: {'✅ 通过' if test2_success else '❌ 失败'}")
    
    if test1_success and test2_success:
        print("\n🎉 单张SDF视觉效果修复成功！")
        print("💡 现在单张SDF应该显示为反色效果：")
        print("   - 原图黑色区域 → SDF显示较暗")
        print("   - 原图白色区域 → SDF显示较亮")
    else:
        print("\n⚠️  视觉效果可能还有问题")
    
    return test1_success and test2_success

if __name__ == "__main__":
    main()
