#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
性能测试脚本
测试修复后的C++实现性能
"""

import numpy as np
import time
import sys
import os
from PIL import Image

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_test_image(size):
    """创建指定大小的测试图像"""
    center = size // 2
    radius = size // 4
    
    image = np.zeros((size, size), dtype=np.float32)
    
    for y in range(size):
        for x in range(size):
            distance = np.sqrt((x - center)**2 + (y - center)**2)
            if distance <= radius:
                image[y, x] = 1.0
    
    return image

def test_performance():
    """测试不同尺寸图像的性能"""
    sizes = [100, 200, 400, 512]
    
    print("SDF算法性能测试")
    print("=" * 60)
    print(f"{'尺寸':<10} {'Python时间':<12} {'C++时间':<12} {'加速比':<10}")
    print("-" * 60)
    
    for size in sizes:
        # 创建测试图像
        test_image = create_test_image(size)
        
        # 保存测试图像
        img = Image.fromarray((test_image * 255).astype(np.uint8))
        test_path = f"test_{size}x{size}.png"
        img.save(test_path)
        
        try:
            # 测试Python版本
            from core.sdf_generator import SDFGenerator
            generator = SDFGenerator()
            
            # 强制使用Python实现
            generator.use_cpp_backend = False
            start_time = time.time()
            python_result, _ = generator.compute_single_sdf(test_path)
            python_time = time.time() - start_time
            
            # 测试C++版本
            try:
                import sdf_core
                
                height, width = test_image.shape
                image_data = test_image.flatten().tolist()
                
                start_time = time.time()
                cpp_result = sdf_core.compute_single_sdf(image_data, width, height, 0.5, True)
                cpp_time = time.time() - start_time
                
                # 计算加速比
                if cpp_time > 0:
                    speedup = python_time / cpp_time
                else:
                    speedup = float('inf')
                
                print(f"{size}x{size:<5} {python_time:<12.3f} {cpp_time:<12.3f} {speedup:<10.1f}x")
                
            except ImportError:
                print(f"{size}x{size:<5} {python_time:<12.3f} {'N/A':<12} {'N/A':<10}")
                
        except Exception as e:
            print(f"{size}x{size:<5} 错误: {e}")
        
        # 清理测试文件
        if os.path.exists(test_path):
            os.remove(test_path)
    
    print("-" * 60)

def test_real_image():
    """测试真实图像的性能"""
    print("\n真实图像性能测试")
    print("=" * 40)
    
    # 检查是否有测试图像
    test_files = ["test_image.png"]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"测试文件: {test_file}")
            
            try:
                from core.sdf_generator import SDFGenerator
                generator = SDFGenerator()
                
                # 测试Python版本
                generator.use_cpp_backend = False
                start_time = time.time()
                python_result, python_comp_time = generator.compute_single_sdf(test_file)
                python_total_time = time.time() - start_time
                
                # 测试C++版本
                generator.use_cpp_backend = True
                start_time = time.time()
                cpp_result, cpp_comp_time = generator.compute_single_sdf(test_file)
                cpp_total_time = time.time() - start_time
                
                print(f"Python版本:")
                print(f"  - 计算时间: {python_comp_time:.3f}s")
                print(f"  - 总时间: {python_total_time:.3f}s")
                print(f"C++版本:")
                print(f"  - 计算时间: {cpp_comp_time:.3f}s")
                print(f"  - 总时间: {cpp_total_time:.3f}s")
                
                if cpp_comp_time > 0:
                    speedup = python_comp_time / cpp_comp_time
                    print(f"加速比: {speedup:.1f}x")
                
                # 验证结果一致性
                diff = np.abs(python_result - cpp_result)
                max_diff = np.max(diff)
                print(f"最大差异: {max_diff:.6f}")
                
            except Exception as e:
                print(f"测试失败: {e}")
        else:
            print(f"测试文件不存在: {test_file}")

if __name__ == "__main__":
    test_performance()
    test_real_image()
