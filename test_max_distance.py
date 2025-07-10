#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试最大距离参数是否生效
"""

import numpy as np
import time
import sys
import os
from PIL import Image

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_test_image(size=200):
    """创建测试图像 - 中心有一个小圆"""
    center = size // 2
    radius = 20  # 小圆，这样可以看到距离效果
    
    image = np.zeros((size, size), dtype=np.float32)
    
    for y in range(size):
        for x in range(size):
            distance = np.sqrt((x - center)**2 + (y - center)**2)
            if distance <= radius:
                image[y, x] = 1.0
    
    return image

def test_max_distance_effect():
    """测试不同max_distance值的效果"""
    print("测试最大距离参数效果")
    print("=" * 50)
    
    # 创建测试图像
    test_image = create_test_image(200)
    
    # 保存测试图像
    img = Image.fromarray((test_image * 255).astype(np.uint8))
    img.save("test_max_distance.png")
    print("✓ 测试图像已保存: test_max_distance.png")
    
    # 测试不同的max_distance值
    max_distances = [10, 30, 50, 100]
    
    try:
        import sdf_core
        print("✓ C++扩展模块导入成功")
        
        height, width = test_image.shape
        image_data = test_image.flatten().tolist()
        
        print(f"\n{'最大距离':<10} {'最小值':<10} {'最大值':<10} {'范围':<10} {'计算时间':<10}")
        print("-" * 60)
        
        for max_dist in max_distances:
            start_time = time.time()
            
            # 测试C++版本
            sdf_result = sdf_core.compute_single_sdf(
                image_data, width, height, 0.5, False, max_dist  # normalize=False 以看到原始距离值
            )
            
            computation_time = time.time() - start_time
            
            # 转换回numpy数组
            sdf_array = np.array(sdf_result, dtype=np.float32).reshape(height, width)
            
            min_val = np.min(sdf_array)
            max_val = np.max(sdf_array)
            range_val = max_val - min_val
            
            print(f"{max_dist:<10} {min_val:<10.2f} {max_val:<10.2f} {range_val:<10.2f} {computation_time:<10.3f}s")
            
            # 保存结果图像
            # 归一化到0-255用于保存
            normalized = ((sdf_array - min_val) / (range_val + 1e-6) * 255).astype(np.uint8)
            result_img = Image.fromarray(normalized)
            result_img.save(f"test_sdf_max{max_dist}.png")
            
        print(f"\n✓ 结果图像已保存: test_sdf_max*.png")
        
    except ImportError:
        print("❌ C++扩展模块未找到")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_python_vs_cpp_max_distance():
    """比较Python和C++版本的max_distance效果"""
    print("\n比较Python和C++版本的max_distance效果")
    print("=" * 50)
    
    try:
        from core.sdf_generator import SDFGenerator
        
        # 创建测试图像
        test_image = create_test_image(100)
        img = Image.fromarray((test_image * 255).astype(np.uint8))
        img.save("test_compare.png")
        
        generator = SDFGenerator()
        max_distance = 25
        
        # 测试Python版本
        generator.use_cpp_backend = False
        python_result, python_time = generator.compute_single_sdf(
            "test_compare.png",
            threshold=0.5,
            normalize=False,
            max_distance=max_distance
        )
        
        # 测试C++版本
        generator.use_cpp_backend = True
        cpp_result, cpp_time = generator.compute_single_sdf(
            "test_compare.png",
            threshold=0.5,
            normalize=False,
            max_distance=max_distance
        )
        
        print(f"Python版本:")
        print(f"  - 计算时间: {python_time:.3f}s")
        print(f"  - 值范围: [{python_result.min():.2f}, {python_result.max():.2f}]")
        print(f"  - 最大距离限制: {max_distance}")
        
        print(f"C++版本:")
        print(f"  - 计算时间: {cpp_time:.3f}s")
        print(f"  - 值范围: [{cpp_result.min():.2f}, {cpp_result.max():.2f}]")
        print(f"  - 最大距离限制: {max_distance}")
        
        # 检查是否都遵守了max_distance限制
        python_max_exceeded = np.any(np.abs(python_result) > max_distance + 1)  # +1 for tolerance
        cpp_max_exceeded = np.any(np.abs(cpp_result) > max_distance + 1)
        
        print(f"\n最大距离限制检查:")
        print(f"  - Python版本超出限制: {'是' if python_max_exceeded else '否'}")
        print(f"  - C++版本超出限制: {'是' if cpp_max_exceeded else '否'}")
        
        if not python_max_exceeded and not cpp_max_exceeded:
            print("✅ 两个版本都正确应用了最大距离限制")
        else:
            print("⚠️ 某个版本没有正确应用最大距离限制")
        
        # 计算差异
        diff = np.abs(python_result - cpp_result)
        max_diff = np.max(diff)
        mean_diff = np.mean(diff)
        
        print(f"\n结果比较:")
        print(f"  - 最大差异: {max_diff:.6f}")
        print(f"  - 平均差异: {mean_diff:.6f}")
        
        # 清理测试文件
        if os.path.exists("test_compare.png"):
            os.remove("test_compare.png")
            
    except Exception as e:
        print(f"❌ 比较测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    print("最大距离参数测试")
    print("=" * 50)
    
    # 测试C++版本的max_distance效果
    success = test_max_distance_effect()
    
    if success:
        # 比较Python和C++版本
        test_python_vs_cpp_max_distance()
    
    print("\n测试完成！")
    print("请查看生成的图像文件来验证最大距离效果：")
    print("- test_max_distance.png: 原始测试图像")
    print("- test_sdf_max*.png: 不同最大距离设置的SDF结果")

if __name__ == "__main__":
    main()
