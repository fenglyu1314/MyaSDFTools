#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试角度分布计算
"""

def test_angle_distribution(count):
    """测试180度均匀分布计算"""
    if count <= 0:
        return []
    if count == 1:
        return [0]
    
    angles = []
    for i in range(count):
        angle = int(180 / count * i)
        angles.append(angle)
    return angles

def test_precise_angle_distribution(count):
    """测试精确的180度均匀分布计算（保留小数）"""
    if count <= 0:
        return []
    if count == 1:
        return [0.0]
    
    angles = []
    for i in range(count):
        angle = 180.0 / count * i
        angles.append(angle)
    return angles

if __name__ == "__main__":
    print("=== 整数角度分布测试 ===")
    for n in range(1, 9):
        angles = test_angle_distribution(n)
        print(f'{n}张图像: {angles}')
    
    print("\n=== 精确角度分布测试 ===")
    for n in range(1, 9):
        angles = test_precise_angle_distribution(n)
        print(f'{n}张图像: {[f"{a:.1f}" for a in angles]}')
    
    print("\n=== 8张图像详细分析 ===")
    count = 8
    step = 180.0 / count
    print(f"角度间隔: {step:.1f}度")
    angles = test_precise_angle_distribution(count)
    for i, angle in enumerate(angles):
        print(f"图像{i+1}: {angle:.1f}° (整数: {int(angle)}°)")
