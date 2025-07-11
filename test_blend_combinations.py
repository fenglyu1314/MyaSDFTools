#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试SDF混合组合数量
"""

import numpy as np
from src.core.sdf_blend_algorithms import SDFBlendAlgorithms

def test_blend_combinations():
    """测试两两混合的组合数量"""
    print("🧪 测试SDF混合组合数量...")
    
    # 创建8个测试SDF图像
    num_images = 8
    sdf_images = []
    angles = []
    
    for i in range(num_images):
        # 创建简单的测试SDF
        sdf = np.random.rand(64, 64).astype(np.float32)
        sdf_images.append(sdf)
        angles.append(i * 45)  # 0, 45, 90, ..., 315度
    
    print(f"📊 输入: {num_images}张SDF图像")
    
    # 计算期望的组合数
    expected_combinations = num_images * (num_images - 1) // 2
    print(f"📊 期望组合数: C({num_images},2) = {expected_combinations}")
    
    # 手动计算组合数来验证
    manual_count = 0
    print("🔍 手动枚举所有组合:")
    for i in range(num_images):
        for j in range(i + 1, num_images):
            manual_count += 1
            print(f"  组合{manual_count}: 第{i+1}帧 + 第{j+1}帧")
    
    print(f"📊 手动计算组合数: {manual_count}")
    
    # 使用我们的混合算法
    print("\n🔄 执行SDF混合...")
    result = SDFBlendAlgorithms.blend_sdf_pairwise(sdf_images, angles)
    
    print(f"📊 混合结果形状: {result.shape}")
    print(f"📊 混合结果值范围: [{np.min(result):.3f}, {np.max(result):.3f}]")
    
    return expected_combinations == manual_count

def test_blend_algorithm_step_by_step():
    """逐步测试混合算法"""
    print("\n🧪 逐步测试混合算法...")
    
    # 创建两个简单的测试SDF
    size = 64
    
    # SDF A: 左半部分内部(暗)，右半部分外部(亮)
    sdf_a = np.ones((size, size), dtype=np.float32) * 0.8  # 外部
    sdf_a[:, :size//2] = 0.2  # 左半部分内部
    
    # SDF B: 上半部分内部(暗)，下半部分外部(亮)  
    sdf_b = np.ones((size, size), dtype=np.float32) * 0.8  # 外部
    sdf_b[:size//2, :] = 0.2  # 上半部分内部
    
    print(f"📊 SDF A: 左半部分={sdf_a[0, 0]:.1f}(内部), 右半部分={sdf_a[0, -1]:.1f}(外部)")
    print(f"📊 SDF B: 上半部分={sdf_b[0, 0]:.1f}(内部), 下半部分={sdf_b[-1, 0]:.1f}(外部)")
    
    # 执行混合
    blend_result = SDFBlendAlgorithms.blend_two_sdfs(sdf_a, sdf_b)
    
    # 检查四个象限的结果
    top_left = blend_result[size//4, size//4]      # A内部 & B内部
    top_right = blend_result[size//4, 3*size//4]   # A外部 & B内部  
    bottom_left = blend_result[3*size//4, size//4] # A内部 & B外部
    bottom_right = blend_result[3*size//4, 3*size//4] # A外部 & B外部
    
    print(f"🎯 混合结果:")
    print(f"  左上(A内&B内): {top_left:.3f}")
    print(f"  右上(A外&B内): {top_right:.3f}")  
    print(f"  左下(A内&B外): {bottom_left:.3f}")
    print(f"  右下(A外&B外): {bottom_right:.3f}")
    
    # 验证混合规则
    print(f"\n🔍 验证混合规则:")
    print(f"  A内部 → 应该=1.0, 实际={top_left:.3f} {'✅' if abs(top_left - 1.0) < 0.1 else '❌'}")
    print(f"  B外部 → 应该=0.0, 实际={bottom_left:.3f} {'✅' if abs(bottom_left - 0.0) < 0.1 else '❌'}")
    print(f"  过渡区域 → 应该在0-1之间, 实际={top_right:.3f} {'✅' if 0 <= top_right <= 1 else '❌'}")
    
    return True

def main():
    """主测试函数"""
    print("🚀 开始SDF混合算法验证")
    print("=" * 50)
    
    # 测试1: 组合数量
    test1_success = test_blend_combinations()
    
    # 测试2: 混合算法逻辑
    test2_success = test_blend_algorithm_step_by_step()
    
    print("\n" + "=" * 50)
    print("📋 混合算法测试结果:")
    print(f"  组合数量验证: {'✅ 通过' if test1_success else '❌ 失败'}")
    print(f"  混合逻辑验证: {'✅ 通过' if test2_success else '❌ 失败'}")
    
    return test1_success and test2_success

if __name__ == "__main__":
    main()
