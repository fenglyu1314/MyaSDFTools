#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像处理器

处理图像的各种操作，如调整大小、灰度转换、二值化等
"""

import numpy as np
from PIL import Image
from typing import Tuple, Union
import cv2
from .format_converter import FormatConverter

class ImageProcessor:
    """图像处理器
    
    负责处理图像的各种操作，包括尺寸调整、颜色转换、
    图像增强等功能。
    """

    @staticmethod
    def resize_image(image: Union[np.ndarray, Image.Image], 
                    size: Tuple[int, int], 
                    keep_aspect_ratio: bool = True,
                    method: str = 'lanczos') -> Union[np.ndarray, Image.Image]:
        """调整图像大小
        
        Args:
            image: 输入图像
            size: 目标尺寸 (width, height)
            keep_aspect_ratio: 是否保持宽高比
            method: 插值方法
            
        Returns:
            调整后的图像
        """
        is_numpy = isinstance(image, np.ndarray)
        
        # 转换为PIL图像进行处理
        if is_numpy:
            pil_image = FormatConverter.numpy_to_pil(image)
        else:
            pil_image = image
        
        # 选择插值方法
        resample_methods = {
            'nearest': Image.Resampling.NEAREST,
            'bilinear': Image.Resampling.BILINEAR,
            'bicubic': Image.Resampling.BICUBIC,
            'lanczos': Image.Resampling.LANCZOS
        }
        resample = resample_methods.get(method.lower(), Image.Resampling.LANCZOS)
        
        if keep_aspect_ratio:
            # 保持宽高比
            pil_image.thumbnail(size, resample)
            resized_image = pil_image
        else:
            # 直接调整到指定尺寸
            resized_image = pil_image.resize(size, resample)
        
        # 如果输入是numpy数组，转换回numpy
        if is_numpy:
            return FormatConverter.pil_to_numpy(resized_image, normalize=True)
        else:
            return resized_image
    
    @staticmethod
    def convert_to_grayscale(image: Union[np.ndarray, Image.Image]) -> Union[np.ndarray, Image.Image]:
        """转换为灰度图
        
        Args:
            image: 输入图像
            
        Returns:
            灰度图像
        """
        is_numpy = isinstance(image, np.ndarray)
        
        if is_numpy:
            if len(image.shape) == 2:
                # 已经是灰度图
                return image
            elif len(image.shape) == 3:
                if image.shape[2] == 3:
                    # RGB转灰度
                    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                elif image.shape[2] == 4:
                    # RGBA转灰度
                    rgb = image[:, :, :3]
                    return cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        else:
            # PIL图像
            return image.convert('L')
        
        return image
    
    @staticmethod
    def threshold_image(image: np.ndarray, threshold: float = 0.5, invert: bool = False) -> np.ndarray:
        """图像二值化
        
        Args:
            image: 输入图像
            threshold: 阈值
            invert: 是否反转
            
        Returns:
            二值化图像
        """
        binary = (image > threshold).astype(np.float32)
        
        if invert:
            binary = 1.0 - binary
        
        return binary
    
    @staticmethod
    def normalize_image(image: np.ndarray, target_range: Tuple[float, float] = (0.0, 1.0)) -> np.ndarray:
        """归一化图像
        
        Args:
            image: 输入图像
            target_range: 目标范围
            
        Returns:
            归一化后的图像
        """
        min_val, max_val = image.min(), image.max()
        
        if max_val > min_val:
            # 归一化到[0,1]
            normalized = (image - min_val) / (max_val - min_val)
            
            # 缩放到目标范围
            target_min, target_max = target_range
            normalized = normalized * (target_max - target_min) + target_min
        else:
            # 如果图像是常数，设置为目标范围的中值
            normalized = np.full_like(image, (target_range[0] + target_range[1]) / 2)
        
        return normalized
    
    @staticmethod
    def create_checkerboard(size: Tuple[int, int], 
                           square_size: int = 20,
                           color1: Tuple[int, int, int] = (255, 255, 255),
                           color2: Tuple[int, int, int] = (200, 200, 200)) -> np.ndarray:
        """创建棋盘背景
        
        Args:
            size: 图像尺寸 (width, height)
            square_size: 方格大小
            color1: 颜色1
            color2: 颜色2
            
        Returns:
            棋盘图像
        """
        width, height = size
        image = np.zeros((height, width, 3), dtype=np.uint8)
        
        for y in range(0, height, square_size):
            for x in range(0, width, square_size):
                # 计算方格颜色
                square_x = x // square_size
                square_y = y // square_size
                
                if (square_x + square_y) % 2 == 0:
                    color = color1
                else:
                    color = color2
                
                # 填充方格
                end_x = min(x + square_size, width)
                end_y = min(y + square_size, height)
                image[y:end_y, x:end_x] = color
        
        return image
    
    @staticmethod
    def blend_images(image1: np.ndarray, 
                    image2: np.ndarray, 
                    alpha: float = 0.5) -> np.ndarray:
        """混合两张图像
        
        Args:
            image1: 图像1
            image2: 图像2
            alpha: 混合系数 (0.0-1.0)
            
        Returns:
            混合后的图像
        """
        alpha = np.clip(alpha, 0.0, 1.0)
        return image1 * alpha + image2 * (1.0 - alpha)
