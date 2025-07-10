#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像管理器

负责图像文件的管理，提供统一的图像管理接口
"""

from typing import List, Dict, Optional, Tuple, Any
import numpy as np
from .image_info import ImageInfo
from .image_validator import ImageValidator
from .image_cache import ImageCache

class ImageManager:
    """图像管理器

    负责图像文件的统一管理，内部委托给专门的处理器。
    """

    def __init__(self):
        """初始化图像管理器"""
        self.images: Dict[str, ImageInfo] = {}
        self.cache = ImageCache()
        self.validator = ImageValidator()

    def add_image(self, file_path: str) -> bool:
        """添加图像到管理器

        Args:
            file_path: 图像文件路径

        Returns:
            是否添加成功
        """
        try:
            # 验证图像文件
            is_valid, error_msg = self.validator.validate_image_file(file_path)
            if not is_valid:
                print(f"❌ {error_msg}")
                return False

            # 创建图像信息
            image_info = ImageInfo(file_path)

            # 添加到管理器
            self.images[file_path] = image_info
            print(f"✅ 成功添加图像: {image_info.file_name}")

            return True

        except Exception as e:
            print(f"❌ 添加图像失败 {file_path}: {e}")
            return False

    def remove_image(self, file_path: str) -> bool:
        """从管理器中移除图像

        Args:
            file_path: 图像文件路径

        Returns:
            是否移除成功
        """
        if file_path in self.images:
            del self.images[file_path]

            # 清除相关缓存
            cache_keys_to_remove = [key for key in self.cache.image_cache.keys()
                                   if key.startswith(file_path)]
            for key in cache_keys_to_remove:
                self.cache.remove(key)

            return True

        return False

    def clear_all(self):
        """清空所有图像"""
        self.images.clear()
        self.cache.clear()

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
        """加载图像数据（委托给缓存管理器）"""
        return self.cache.load_image_data(file_path, as_grayscale)

    def load_thumbnail(self, file_path: str, size: Tuple[int, int] = (128, 128)) -> Optional[np.ndarray]:
        """加载缩略图（委托给缓存管理器）"""
        return self.cache.load_thumbnail(file_path, size)

    def validate_images(self) -> List[str]:
        """验证所有图像文件

        Returns:
            无效图像的路径列表
        """
        invalid_images = []

        for file_path, image_info in self.images.items():
            if not self.validator.validate_file_exists(file_path) or not image_info.is_valid():
                invalid_images.append(file_path)

        # 移除无效图像
        for file_path in invalid_images:
            self.remove_image(file_path)

        return invalid_images

    def get_common_size(self) -> Optional[Tuple[int, int]]:
        """获取最常见的图像尺寸（委托给验证器）"""
        return self.validator.get_common_size(list(self.images.values()))

    def check_size_consistency(self) -> bool:
        """检查所有图像尺寸是否一致（委托给验证器）"""
        return self.validator.check_size_consistency(list(self.images.values()))

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
            'cache_size': self.cache.size()
        }

    def is_supported_format(self, file_path: str) -> bool:
        """检查文件格式是否支持（委托给验证器）"""
        return self.validator.is_supported_format(file_path)

    def clear_cache(self):
        """清空缓存（委托给缓存管理器）"""
        self.cache.clear()

    def set_cache_size(self, size: int):
        """设置缓存大小（委托给缓存管理器）"""
        self.cache.set_max_size(size)
