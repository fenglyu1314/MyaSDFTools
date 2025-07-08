#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建测试图像用于验证光照预览功能
"""

import numpy as np
from PIL import Image
from pathlib import Path

def create_test_image():
    """创建一个简单的测试图像"""
    size = 256
    
    # 创建一个圆形图像
    img = np.zeros((size, size), dtype=np.uint8)
    center = size // 2
    radius = 80
    
    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center
            distance = np.sqrt(dx*dx + dy*dy)
            
            if distance <= radius:
                img[y, x] = 255
    
    # 保存图像
    output_path = Path("temp/test_circle.png")
    output_path.parent.mkdir(exist_ok=True)
    
    Image.fromarray(img).save(output_path)
    print(f"✅ 测试图像已创建: {output_path}")
    
    return str(output_path)

if __name__ == "__main__":
    create_test_image()
