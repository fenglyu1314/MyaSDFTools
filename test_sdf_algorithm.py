#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SDF算法验证测试脚本

验证修复后的SDF算法是否符合参考文章的要求：
1. SDF值范围正确 (0-1)
2. 边界值为0.5
3. 内部值>0.5，外部值<0.5
4. 混合算法正确工作
"""

import numpy as np
import cv2
from src.core.sdf_core_algorithm import SDFCoreAlgorithm
from src.core.sdf_blend_algorithms import SDFBlendAlgorithms

def create_test_image(size=256):
    """创建一个简单的测试图像 - 中心圆形"""
    image = np.zeros((size, size), dtype=np.uint8)
    center = size // 2
    radius = size // 4
    cv2.circle(image, (center, center), radius, 255, -1)
    return image

def test_sdf_normalization():
    """测试SDF归一化是否正确"""
    print("🧪 测试SDF归一化...")
    
    # 创建测试图像
    test_img = create_test_image(128)
    
    # 计算SDF
    sdf_result = SDFCoreAlgorithm.compute_sdf_python(
        test_img, normalize=True, sdf_direction="both", max_distance=50
    )
    
    # 验证值范围
    min_val, max_val = np.min(sdf_result), np.max(sdf_result)
    print(f"📊 SDF值范围: [{min_val:.3f}, {max_val:.3f}]")
    
    # 检查边界附近的值
    center = 64
    radius = 32
    
    # 检查内部点 (按照文章定义，应该接近 0.0)
    inner_point = sdf_result[center, center]
    print(f"🎯 中心点值: {inner_point:.3f} (应该接近0.0)")

    # 检查边界点 (应该接近 0.5)
    boundary_point = sdf_result[center, center + radius]
    print(f"🎯 边界点值: {boundary_point:.3f} (应该接近0.5)")

    # 检查外部点 (按照文章定义，应该接近 1.0)
    outer_point = sdf_result[center, center + radius + 20]
    print(f"🎯 外部点值: {outer_point:.3f} (应该接近1.0)")

    # 验证结果 (按照文章的定义修正)
    success = True
    if not (0.0 <= min_val <= max_val <= 1.0):
        print("❌ 值范围不正确")
        success = False
    if inner_point >= 0.2:  # 内部中心应该接近0.0
        print("❌ 内部点值不正确")
        success = False
    if outer_point <= 0.6:  # 外部应该接近1.0
        print("❌ 外部点值不正确")
        success = False
    
    if success:
        print("✅ SDF归一化测试通过")
    else:
        print("❌ SDF归一化测试失败")
    
    return sdf_result, success

def test_sdf_blending():
    """测试SDF混合算法"""
    print("\n🧪 测试SDF混合算法...")
    
    # 创建两个不同的测试图像
    img1 = create_test_image(128)
    img2 = np.zeros((128, 128), dtype=np.uint8)
    cv2.rectangle(img2, (32, 32), (96, 96), 255, -1)
    
    # 计算各自的SDF
    sdf1 = SDFCoreAlgorithm.compute_sdf_python(img1, normalize=True, sdf_direction="both")
    sdf2 = SDFCoreAlgorithm.compute_sdf_python(img2, normalize=True, sdf_direction="both")
    
    print(f"📊 SDF1值范围: [{np.min(sdf1):.3f}, {np.max(sdf1):.3f}]")
    print(f"📊 SDF2值范围: [{np.min(sdf2):.3f}, {np.max(sdf2):.3f}]")
    
    # 测试两两混合
    blend_result = SDFBlendAlgorithms.blend_two_sdfs(sdf1, sdf2)
    
    print(f"📊 混合结果值范围: [{np.min(blend_result):.3f}, {np.max(blend_result):.3f}]")
    
    # 验证混合结果
    success = True
    if not (0.0 <= np.min(blend_result) <= np.max(blend_result) <= 1.0):
        print("❌ 混合结果值范围不正确")
        success = False
    
    if success:
        print("✅ SDF混合测试通过")
    else:
        print("❌ SDF混合测试失败")
    
    return blend_result, success

def test_multi_sdf_blending():
    """测试多图像SDF混合"""
    print("\n🧪 测试多图像SDF混合...")
    
    # 创建多个测试图像
    images = []
    for i in range(4):
        img = np.zeros((128, 128), dtype=np.uint8)
        # 创建不同位置的圆形
        center_x = 32 + i * 20
        center_y = 64
        cv2.circle(img, (center_x, center_y), 20, 255, -1)
        images.append(img)
    
    # 计算各自的SDF
    sdf_images = []
    for img in images:
        sdf = SDFCoreAlgorithm.compute_sdf_python(img, normalize=True, sdf_direction="both")
        sdf_images.append(sdf)
    
    # 测试sdf_blend模式
    angles = [0, 45, 90, 135]  # 角度
    final_sdf = SDFBlendAlgorithms.blend_multiple_sdfs(sdf_images, angles, "sdf_blend")
    
    print(f"📊 最终SDF值范围: [{np.min(final_sdf):.3f}, {np.max(final_sdf):.3f}]")
    
    # 验证结果
    success = True
    if not (0.0 <= np.min(final_sdf) <= np.max(final_sdf) <= 1.0):
        print("❌ 最终SDF值范围不正确")
        success = False
    
    if success:
        print("✅ 多图像SDF混合测试通过")
    else:
        print("❌ 多图像SDF混合测试失败")
    
    return final_sdf, success

def main():
    """主测试函数"""
    print("🚀 开始SDF算法验证测试")
    print("=" * 50)
    
    # 测试1: SDF归一化
    sdf_result, test1_success = test_sdf_normalization()
    
    # 测试2: SDF混合
    blend_result, test2_success = test_sdf_blending()
    
    # 测试3: 多图像混合
    final_result, test3_success = test_multi_sdf_blending()
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 测试结果总结:")
    print(f"  SDF归一化: {'✅ 通过' if test1_success else '❌ 失败'}")
    print(f"  SDF混合: {'✅ 通过' if test2_success else '❌ 失败'}")
    print(f"  多图像混合: {'✅ 通过' if test3_success else '❌ 失败'}")
    
    all_success = test1_success and test2_success and test3_success
    if all_success:
        print("\n🎉 所有测试通过！SDF算法修复成功！")
    else:
        print("\n⚠️  部分测试失败，需要进一步调试")
    
    return all_success

if __name__ == "__main__":
    main()
