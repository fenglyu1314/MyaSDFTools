#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的C++实现测试
测试核心算法是否正确实现
"""

import numpy as np
import time
import sys
import os

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_python_sdf():
    """测试Python版本的SDF算法"""
    print("=== 测试Python版本SDF算法 ===")
    
    try:
        from core.sdf_generator import SDFGenerator
        
        # 创建测试图像
        test_image = create_test_image()
        
        # 保存测试图像
        from PIL import Image
        img = Image.fromarray((test_image * 255).astype(np.uint8))
        img.save("test_image.png")
        print("✓ 测试图像已保存: test_image.png")
        
        # 测试SDF生成
        generator = SDFGenerator()
        
        start_time = time.time()
        sdf_result, computation_time = generator.compute_single_sdf(
            "test_image.png",
            threshold=0.5,
            normalize=True,
            invert=False,
            sdf_direction="both",
            max_distance=100
        )
        total_time = time.time() - start_time
        
        print(f"✓ Python SDF计算完成")
        print(f"  - 计算时间: {computation_time:.3f}s")
        print(f"  - 总时间: {total_time:.3f}s")
        print(f"  - 结果形状: {sdf_result.shape}")
        print(f"  - 值范围: [{sdf_result.min():.3f}, {sdf_result.max():.3f}]")
        
        # 保存SDF结果
        sdf_img = Image.fromarray((sdf_result * 255).astype(np.uint8))
        sdf_img.save("test_sdf_python.png")
        print("✓ Python SDF结果已保存: test_sdf_python.png")
        
        return sdf_result
        
    except Exception as e:
        print(f"❌ Python SDF测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_cpp_sdf():
    """测试C++版本的SDF算法"""
    print("\n=== 测试C++版本SDF算法 ===")
    
    try:
        import sdf_core
        print("✓ C++扩展模块导入成功")
        
        # 获取版本信息
        version = sdf_core.get_version()
        print(f"✓ C++版本: {version}")
        
        # 创建测试图像数据
        test_image = create_test_image()
        height, width = test_image.shape
        image_data = test_image.flatten().tolist()
        
        # 测试SDF计算
        start_time = time.time()
        sdf_result = sdf_core.compute_single_sdf(
            image_data, width, height, 0.5, True
        )
        computation_time = time.time() - start_time
        
        # 转换回numpy数组
        sdf_array = np.array(sdf_result, dtype=np.float32).reshape(height, width)
        
        print(f"✓ C++ SDF计算完成")
        print(f"  - 计算时间: {computation_time:.3f}s")
        print(f"  - 结果形状: {sdf_array.shape}")
        print(f"  - 值范围: [{sdf_array.min():.3f}, {sdf_array.max():.3f}]")
        
        # 保存SDF结果
        from PIL import Image
        sdf_img = Image.fromarray((sdf_array * 255).astype(np.uint8))
        sdf_img.save("test_sdf_cpp.png")
        print("✓ C++ SDF结果已保存: test_sdf_cpp.png")
        
        return sdf_array
        
    except ImportError:
        print("❌ C++扩展模块未找到，请先编译C++扩展")
        return None
    except Exception as e:
        print(f"❌ C++ SDF测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_test_image():
    """创建测试图像"""
    # 创建一个简单的圆形图像
    size = 100
    center = size // 2
    radius = 30
    
    image = np.zeros((size, size), dtype=np.float32)
    
    for y in range(size):
        for x in range(size):
            distance = np.sqrt((x - center)**2 + (y - center)**2)
            if distance <= radius:
                image[y, x] = 1.0
    
    return image

def compare_results(python_result, cpp_result):
    """比较Python和C++结果"""
    print("\n=== 结果比较 ===")
    
    if python_result is None or cpp_result is None:
        print("❌ 无法比较结果，某个实现失败")
        return
    
    # 计算差异
    diff = np.abs(python_result - cpp_result)
    max_diff = np.max(diff)
    mean_diff = np.mean(diff)
    
    print(f"✓ 最大差异: {max_diff:.6f}")
    print(f"✓ 平均差异: {mean_diff:.6f}")
    
    # 判断是否一致
    tolerance = 0.01  # 1%的容差
    if max_diff < tolerance:
        print("✅ 结果一致！C++实现正确")
    else:
        print("⚠️ 结果存在差异，需要进一步检查")
    
    # 保存差异图像
    from PIL import Image
    diff_img = Image.fromarray((diff * 255).astype(np.uint8))
    diff_img.save("test_diff.png")
    print("✓ 差异图像已保存: test_diff.png")

def main():
    """主测试函数"""
    print("SDF算法C++实现测试")
    print("=" * 50)
    
    # 测试Python版本
    python_result = test_python_sdf()
    
    # 测试C++版本
    cpp_result = test_cpp_sdf()
    
    # 比较结果
    compare_results(python_result, cpp_result)
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()
