#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像管理器

负责图像文件的管理，包括：
- 图像加载和验证
- 格式转换
- 缓存管理
- 元数据提取
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
from PIL import Image
import hashlib

class ImageInfo:
    """图像信息类"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = Path(file_path).name
        self.file_size = 0
        self.width = 0
        self.height = 0
        self.channels = 0
        self.format = ""
        self.mode = ""
        self.hash = ""
        
        self._load_info()
    
    def _load_info(self):
        """加载图像信息"""
        try:
            # 文件信息
            self.file_size = os.path.getsize(self.file_path)
            
            # 图像信息
            with Image.open(self.file_path) as img:
                self.width, self.height = img.size
                self.format = img.format or "Unknown"
                self.mode = img.mode
                
                # 计算通道数
                if self.mode == 'L':
                    self.channels = 1
                elif self.mode == 'RGB':
                    self.channels = 3
                elif self.mode == 'RGBA':
                    self.channels = 4
                else:
                    self.channels = len(img.getbands()) if hasattr(img, 'getbands') else 1
            
            # 计算文件哈希
            self.hash = self._calculate_hash()
            
        except Exception as e:
            print(f"加载图像信息失败 {self.file_path}: {e}")
    
    def _calculate_hash(self) -> str:
        """计算文件哈希值"""
        try:
            with open(self.file_path, 'rb') as f:
                file_hash = hashlib.md5()
                chunk = f.read(8192)
                while chunk:
                    file_hash.update(chunk)
                    chunk = f.read(8192)
                return file_hash.hexdigest()
        except:
            return ""
    
    def is_valid(self) -> bool:
        """检查图像是否有效"""
        return (self.width > 0 and self.height > 0 and 
                os.path.exists(self.file_path))
    
    def get_size_string(self) -> str:
        """获取尺寸字符串"""
        return f"{self.width}×{self.height}"
    
    def get_file_size_string(self) -> str:
        """获取文件大小字符串"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"

class ImageManager:
    """图像管理器"""
    
    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.tga', '.tiff', '.webp'}
    
    def __init__(self):
        self.images: Dict[str, ImageInfo] = {}
        self.image_cache: Dict[str, np.ndarray] = {}
        self.max_cache_size = 100  # 最大缓存图像数量
    
    def add_image(self, file_path: str) -> bool:
        """
        添加图像到管理器
        
        Args:
            file_path: 图像文件路径
            
        Returns:
            是否添加成功
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"文件不存在: {file_path}")
                return False
            
            # 检查文件格式
            if not self.is_supported_format(file_path):
                print(f"不支持的文件格式: {file_path}")
                return False
            
            # 创建图像信息
            image_info = ImageInfo(file_path)
            
            # 验证图像
            if not image_info.is_valid():
                print(f"无效的图像文件: {file_path}")
                return False
            
            # 添加到管理器
            self.images[file_path] = image_info
            print(f"成功添加图像: {image_info.file_name}")
            
            return True
            
        except Exception as e:
            print(f"添加图像失败 {file_path}: {e}")
            return False
    
    def remove_image(self, file_path: str) -> bool:
        """
        从管理器中移除图像
        
        Args:
            file_path: 图像文件路径
            
        Returns:
            是否移除成功
        """
        if file_path in self.images:
            del self.images[file_path]
            
            # 清除缓存
            if file_path in self.image_cache:
                del self.image_cache[file_path]
            
            return True
        
        return False
    
    def clear_all(self):
        """清空所有图像"""
        self.images.clear()
        self.image_cache.clear()
    
    def get_image_info(self, file_path: str) -> Optional[ImageInfo]:
        """获取图像信息"""
        return self.images.get(file_path)
    
    def get_all_images(self) -> List[ImageInfo]:
        """获取所有图像信息"""
        return list(self.images.values())
    
    def get_image_paths(self) -> List[str]:
        """获取所有图像路径"""
        return list(self.images.keys())
    
    def load_image_data(self, file_path: str, as_grayscale: bool = True) -> Optional[np.ndarray]:
        """
        加载图像数据
        
        Args:
            file_path: 图像文件路径
            as_grayscale: 是否转换为灰度图
            
        Returns:
            图像数据数组
        """
        # 检查缓存
        cache_key = f"{file_path}_{as_grayscale}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
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
            self._add_to_cache(cache_key, image_array)
            
            return image_array
            
        except Exception as e:
            print(f"加载图像数据失败 {file_path}: {e}")
            return None
    
    def load_thumbnail(self, file_path: str, size: Tuple[int, int] = (128, 128)) -> Optional[np.ndarray]:
        """
        加载缩略图
        
        Args:
            file_path: 图像文件路径
            size: 缩略图尺寸
            
        Returns:
            缩略图数据
        """
        cache_key = f"{file_path}_thumb_{size[0]}x{size[1]}"
        
        # 检查缓存
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
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
                self._add_to_cache(cache_key, thumbnail_array)
                
                return thumbnail_array
                
        except Exception as e:
            print(f"加载缩略图失败 {file_path}: {e}")
            return None
    
    def validate_images(self) -> List[str]:
        """
        验证所有图像文件
        
        Returns:
            无效图像的路径列表
        """
        invalid_images = []
        
        for file_path, image_info in self.images.items():
            if not os.path.exists(file_path) or not image_info.is_valid():
                invalid_images.append(file_path)
        
        # 移除无效图像
        for file_path in invalid_images:
            self.remove_image(file_path)
        
        return invalid_images
    
    def get_common_size(self) -> Optional[Tuple[int, int]]:
        """
        获取最常见的图像尺寸
        
        Returns:
            (width, height) 或 None
        """
        if not self.images:
            return None
        
        # 统计尺寸频率
        size_count = {}
        for image_info in self.images.values():
            size = (image_info.width, image_info.height)
            size_count[size] = size_count.get(size, 0) + 1
        
        # 返回最常见的尺寸
        return max(size_count.items(), key=lambda x: x[1])[0]
    
    def check_size_consistency(self) -> bool:
        """检查所有图像尺寸是否一致"""
        if not self.images:
            return True
        
        sizes = set((info.width, info.height) for info in self.images.values())
        return len(sizes) == 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取图像统计信息"""
        if not self.images:
            return {}
        
        total_size = sum(info.file_size for info in self.images.values())
        formats = {}
        sizes = {}
        
        for info in self.images.values():
            # 格式统计
            formats[info.format] = formats.get(info.format, 0) + 1
            
            # 尺寸统计
            size = (info.width, info.height)
            sizes[size] = sizes.get(size, 0) + 1
        
        return {
            'total_images': len(self.images),
            'total_size': total_size,
            'formats': formats,
            'sizes': sizes,
            'cache_size': len(self.image_cache)
        }
    
    def is_supported_format(self, file_path: str) -> bool:
        """检查文件格式是否支持"""
        suffix = Path(file_path).suffix.lower()
        return suffix in self.SUPPORTED_FORMATS
    
    def _add_to_cache(self, key: str, data: np.ndarray):
        """添加数据到缓存"""
        # 如果缓存已满，移除最旧的项
        if len(self.image_cache) >= self.max_cache_size:
            # 简单的FIFO策略
            oldest_key = next(iter(self.image_cache))
            del self.image_cache[oldest_key]
        
        self.image_cache[key] = data
    
    def clear_cache(self):
        """清空缓存"""
        self.image_cache.clear()
    
    def set_cache_size(self, size: int):
        """设置缓存大小"""
        self.max_cache_size = max(1, size)
        
        # 如果当前缓存超过新的限制，清理多余的项
        while len(self.image_cache) > self.max_cache_size:
            oldest_key = next(iter(self.image_cache))
            del self.image_cache[oldest_key]
