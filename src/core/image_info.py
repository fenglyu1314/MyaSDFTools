#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像信息类

负责单个图像文件的信息管理和元数据提取
"""

import os
import hashlib
from pathlib import Path
from PIL import Image

class ImageInfo:
    """图像信息类
    
    负责管理单个图像文件的基本信息，包括文件属性、
    图像尺寸、格式信息和文件哈希值。
    """
    
    def __init__(self, file_path: str):
        """初始化图像信息
        
        Args:
            file_path: 图像文件路径
        """
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
            # 检查文件是否存在
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"文件不存在: {self.file_path}")

            # 文件信息
            self.file_size = os.path.getsize(self.file_path)

            # 图像信息
            with Image.open(self.file_path) as img:
                self.width, self.height = img.size
                self.format = img.format or "Unknown"
                self.mode = img.mode

                # 计算通道数
                self.channels = self._get_channel_count(img)

            # 计算文件哈希
            self.hash = self._calculate_hash()

        except Exception as e:
            print(f"❌ 加载图像信息失败 {self.file_path}: {e}")

    def _get_channel_count(self, img: Image.Image) -> int:
        """获取图像通道数
        
        Args:
            img: PIL图像对象
            
        Returns:
            通道数
        """
        mode_channels = {
            'L': 1,      # 灰度
            'RGB': 3,    # RGB
            'RGBA': 4,   # RGBA
            'CMYK': 4,   # CMYK
            'P': 1,      # 调色板
        }

        return mode_channels.get(img.mode, len(img.getbands()) if hasattr(img, 'getbands') else 1)
    
    def _calculate_hash(self) -> str:
        """计算文件哈希值
        
        Returns:
            MD5哈希值字符串
        """
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
        """检查图像是否有效
        
        Returns:
            图像是否有效
        """
        return (self.width > 0 and self.height > 0 and 
                os.path.exists(self.file_path))
    
    def get_size_string(self) -> str:
        """获取尺寸字符串
        
        Returns:
            格式化的尺寸字符串
        """
        return f"{self.width}×{self.height}"
    
    def get_file_size_string(self) -> str:
        """获取文件大小字符串
        
        Returns:
            格式化的文件大小字符串
        """
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
