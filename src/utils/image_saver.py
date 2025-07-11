#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像保存器

处理图像保存、SDF保存、颜色映射等功能
"""

import numpy as np
from PIL import Image
from typing import Union
import cv2
from .format_converter import FormatConverter

class ImageSaver:
    """图像保存器
    
    负责处理图像的保存功能，包括普通图像保存、
    SDF数据保存和颜色映射应用。
    """

    @staticmethod
    def save_sdf_as_image(sdf_data: np.ndarray,
                         file_path: str,
                         colormap: str = 'gray',
                         quality: int = 95) -> bool:
        """将SDF数据保存为图像

        Args:
            sdf_data: SDF数据 (numpy数组)
            file_path: 保存路径
            colormap: 颜色映射 ('viridis', 'plasma', 'jet', 'gray')
            quality: 图像质量

        Returns:
            是否保存成功
        """
        try:
            # 确保数据在[0,1]范围内
            normalized_data = np.clip(sdf_data, 0.0, 1.0)

            if colormap.lower() == 'gray':
                # 灰度图像
                image_uint8 = (normalized_data * 255).astype(np.uint8)
                pil_image = Image.fromarray(image_uint8, mode='L')
            else:
                # 彩色映射
                colored_image = ImageSaver.apply_colormap(normalized_data, colormap)
                pil_image = Image.fromarray(colored_image, mode='RGB')

            # 保存图像
            return ImageSaver.save_image(pil_image, file_path, quality)

        except Exception as e:
            print(f"保存SDF图像失败: {str(e)}")
            return False

    @staticmethod
    def apply_colormap(image: np.ndarray, colormap: str = 'viridis') -> np.ndarray:
        """应用颜色映射
        
        Args:
            image: 输入灰度图像
            colormap: 颜色映射名称
            
        Returns:
            彩色图像
        """
        # 确保图像在[0,255]范围内
        if image.max() <= 1.0:
            image_uint8 = (image * 255).astype(np.uint8)
        else:
            image_uint8 = image.astype(np.uint8)
        
        # 应用OpenCV颜色映射
        colormap_dict = {
            'viridis': cv2.COLORMAP_VIRIDIS,
            'plasma': cv2.COLORMAP_PLASMA,
            'inferno': cv2.COLORMAP_INFERNO,
            'magma': cv2.COLORMAP_MAGMA,
            'jet': cv2.COLORMAP_JET,
            'hot': cv2.COLORMAP_HOT,
            'cool': cv2.COLORMAP_COOL,
            'spring': cv2.COLORMAP_SPRING,
            'summer': cv2.COLORMAP_SUMMER,
            'autumn': cv2.COLORMAP_AUTUMN,
            'winter': cv2.COLORMAP_WINTER
        }
        
        cv_colormap = colormap_dict.get(colormap.lower(), cv2.COLORMAP_VIRIDIS)
        colored_image = cv2.applyColorMap(image_uint8, cv_colormap)
        
        # OpenCV使用BGR，转换为RGB
        return cv2.cvtColor(colored_image, cv2.COLOR_BGR2RGB)
    
    @staticmethod
    def save_image(image: Union[np.ndarray, Image.Image], 
                  file_path: str, 
                  quality: int = 95) -> bool:
        """保存图像
        
        Args:
            image: 图像数据
            file_path: 保存路径
            quality: 质量 (对JPEG有效)
            
        Returns:
            是否成功
        """
        try:
            if isinstance(image, np.ndarray):
                pil_image = FormatConverter.numpy_to_pil(image)
            else:
                pil_image = image
            
            # 根据文件扩展名确定保存参数
            file_path_lower = file_path.lower()
            if file_path_lower.endswith(('.jpg', '.jpeg')):
                pil_image.save(file_path, 'JPEG', quality=quality)
            elif file_path_lower.endswith('.png'):
                pil_image.save(file_path, 'PNG')
            else:
                pil_image.save(file_path)
            
            return True
            
        except Exception as e:
            print(f"保存图像失败 {file_path}: {e}")
            return False
