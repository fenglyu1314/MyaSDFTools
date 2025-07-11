#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像缓存管理器

负责图像数据的缓存管理，提高访问性能
"""

import numpy as np
from typing import Dict, Optional, Tuple
from PIL import Image

class ImageCache:
    """图像缓存管理器
    
    负责管理图像数据的内存缓存，使用FIFO策略管理缓存大小。
    """
    
    def __init__(self, max_cache_size: int = 100):
        """初始化缓存管理器
        
        Args:
            max_cache_size: 最大缓存项数量
        """
        self.image_cache: Dict[str, np.ndarray] = {}
        self.max_cache_size = max_cache_size
    
    def get(self, key: str) -> Optional[np.ndarray]:
        """从缓存获取数据
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的图像数据或None
        """
        return self.image_cache.get(key)
    
    def put(self, key: str, data: np.ndarray):
        """添加数据到缓存
        
        Args:
            key: 缓存键
            data: 图像数据
        """
        # 如果缓存已满，移除最旧的项
        if len(self.image_cache) >= self.max_cache_size:
            # 简单的FIFO策略
            oldest_key = next(iter(self.image_cache))
            del self.image_cache[oldest_key]
        
        self.image_cache[key] = data
    
    def remove(self, key: str) -> bool:
        """从缓存移除数据
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功移除
        """
        if key in self.image_cache:
            del self.image_cache[key]
            return True
        return False
    
    def clear(self):
        """清空所有缓存"""
        self.image_cache.clear()
    
    def size(self) -> int:
        """获取缓存大小
        
        Returns:
            当前缓存项数量
        """
        return len(self.image_cache)
    
    def set_max_size(self, size: int):
        """设置最大缓存大小
        
        Args:
            size: 新的最大缓存大小
        """
        self.max_cache_size = max(1, size)
        
        # 如果当前缓存超过新的限制，清理多余的项
        while len(self.image_cache) > self.max_cache_size:
            oldest_key = next(iter(self.image_cache))
            del self.image_cache[oldest_key]
    
    def load_image_data(self, file_path: str, as_grayscale: bool = True) -> Optional[np.ndarray]:
        """加载图像数据（带缓存）
        
        Args:
            file_path: 图像文件路径
            as_grayscale: 是否转换为灰度图
            
        Returns:
            图像数据数组
        """
        # 检查缓存
        cache_key = f"{file_path}_{as_grayscale}"
        cached_data = self.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            # 加载图像
            image = Image.open(file_path)
            
            # 转换为灰度图
            if as_grayscale and image.mode != 'L':
                image = image.convert('L')
            
            # 转换为numpy数组
            image_array = np.array(image, dtype=np.float32)
            
            # 归一化到[0,1]
            if image_array.max() > 1.0:
                image_array = image_array / 255.0
            
            # 添加到缓存
            self.put(cache_key, image_array)
            
            return image_array
            
        except Exception as e:
            print(f"加载图像数据失败 {file_path}: {e}")
            return None
    
    def load_thumbnail(self, file_path: str, size: Tuple[int, int] = (128, 128)) -> Optional[np.ndarray]:
        """加载缩略图（带缓存）
        
        Args:
            file_path: 图像文件路径
            size: 缩略图尺寸
            
        Returns:
            缩略图数据
        """
        cache_key = f"{file_path}_thumb_{size[0]}x{size[1]}"
        
        # 检查缓存
        cached_data = self.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            # 加载并缩放图像
            with Image.open(file_path) as image:
                # 保持宽高比缩放
                image.thumbnail(size, Image.Resampling.LANCZOS)
                
                # 转换为RGB模式以便显示
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # 转换为numpy数组
                thumbnail_array = np.array(image, dtype=np.uint8)
                
                # 添加到缓存
                self.put(cache_key, thumbnail_array)
                
                return thumbnail_array
                
        except Exception as e:
            print(f"加载缩略图失败 {file_path}: {e}")
            return None
