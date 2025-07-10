#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像验证器

负责图像文件的格式验证和有效性检查
"""

import os
from pathlib import Path
from typing import List
from .image_info import ImageInfo

class ImageValidator:
    """图像验证器
    
    负责验证图像文件的格式、有效性和一致性检查。
    """
    
    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.tga', '.tiff', '.webp'}
    
    @staticmethod
    def is_supported_format(file_path: str) -> bool:
        """检查文件格式是否支持
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否支持该格式
        """
        suffix = Path(file_path).suffix.lower()
        return suffix in ImageValidator.SUPPORTED_FORMATS
    
    @staticmethod
    def validate_file_exists(file_path: str) -> bool:
        """验证文件是否存在
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件是否存在
        """
        return os.path.exists(file_path)
    
    @staticmethod
    def validate_image_file(file_path: str) -> tuple[bool, str]:
        """验证图像文件
        
        Args:
            file_path: 图像文件路径
            
        Returns:
            (是否有效, 错误信息)
        """
        # 检查文件是否存在
        if not ImageValidator.validate_file_exists(file_path):
            return False, f"文件不存在: {file_path}"
        
        # 检查文件格式
        if not ImageValidator.is_supported_format(file_path):
            return False, f"不支持的文件格式: {file_path}"
        
        # 尝试创建图像信息对象验证
        try:
            image_info = ImageInfo(file_path)
            if not image_info.is_valid():
                return False, f"无效的图像文件: {file_path}"
            return True, ""
        except Exception as e:
            return False, f"图像验证失败: {str(e)}"
    
    @staticmethod
    def validate_images_batch(file_paths: List[str]) -> List[str]:
        """批量验证图像文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            无效文件路径列表
        """
        invalid_files = []
        
        for file_path in file_paths:
            is_valid, error_msg = ImageValidator.validate_image_file(file_path)
            if not is_valid:
                invalid_files.append(file_path)
                print(f"❌ {error_msg}")
        
        return invalid_files
    
    @staticmethod
    def check_size_consistency(image_infos: List[ImageInfo]) -> bool:
        """检查图像尺寸是否一致
        
        Args:
            image_infos: 图像信息列表
            
        Returns:
            尺寸是否一致
        """
        if not image_infos:
            return True
        
        sizes = set((info.width, info.height) for info in image_infos)
        return len(sizes) == 1
    
    @staticmethod
    def get_common_size(image_infos: List[ImageInfo]) -> tuple[int, int] | None:
        """获取最常见的图像尺寸
        
        Args:
            image_infos: 图像信息列表
            
        Returns:
            (width, height) 或 None
        """
        if not image_infos:
            return None
        
        # 统计尺寸频率
        size_count = {}
        for image_info in image_infos:
            size = (image_info.width, image_info.height)
            size_count[size] = size_count.get(size, 0) + 1
        
        # 返回最常见的尺寸
        return max(size_count.items(), key=lambda x: x[1])[0]
