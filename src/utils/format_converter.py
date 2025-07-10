#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像格式转换器

处理numpy数组和PIL图像之间的转换，以及数据类型标准化
"""

import numpy as np
from PIL import Image
from typing import Union

class FormatConverter:
    """图像格式转换器
    
    负责处理numpy数组和PIL图像之间的转换，
    以及数据类型的标准化处理。
    """

    @staticmethod
    def numpy_to_pil(array: np.ndarray) -> Image.Image:
        """将numpy数组转换为PIL图像

        Args:
            array: numpy数组，支持2D(灰度)或3D(RGB/RGBA)

        Returns:
            PIL图像对象

        Raises:
            ValueError: 不支持的数组形状或数据类型
        """
        if array is None or array.size == 0:
            raise ValueError("输入数组为空")

        # 标准化数据类型和范围
        array = FormatConverter._normalize_array(array)

        # 根据形状确定图像模式
        if len(array.shape) == 2:
            return Image.fromarray(array, mode='L')
        elif len(array.shape) == 3:
            channels = array.shape[2]
            if channels == 3:
                return Image.fromarray(array, mode='RGB')
            elif channels == 4:
                return Image.fromarray(array, mode='RGBA')
            else:
                raise ValueError(f"不支持的通道数: {channels}")
        else:
            raise ValueError(f"不支持的数组形状: {array.shape}")

    @staticmethod
    def _normalize_array(array: np.ndarray) -> np.ndarray:
        """标准化数组到uint8格式
        
        Args:
            array: 输入数组
            
        Returns:
            标准化后的uint8数组
        """
        if array.dtype in (np.float32, np.float64):
            # 浮点数组，检查范围并转换
            if array.max() <= 1.0 and array.min() >= 0.0:
                return (array * 255).astype(np.uint8)
            else:
                # 超出[0,1]范围，进行裁剪
                array = np.clip(array, 0, 1)
                return (array * 255).astype(np.uint8)
        elif array.dtype == np.uint8:
            return array
        else:
            # 其他整数类型，直接转换
            return array.astype(np.uint8)
    
    @staticmethod
    def pil_to_numpy(image: Image.Image, normalize: bool = True) -> np.ndarray:
        """将PIL图像转换为numpy数组
        
        Args:
            image: PIL图像
            normalize: 是否归一化到[0,1]
            
        Returns:
            numpy数组
        """
        array = np.array(image)
        
        if normalize and array.dtype == np.uint8:
            array = array.astype(np.float32) / 255.0
        
        return array

    @staticmethod
    def get_image_info(image: Union[np.ndarray, Image.Image]) -> dict:
        """获取图像信息
        
        Args:
            image: 图像
            
        Returns:
            图像信息字典
        """
        if isinstance(image, np.ndarray):
            height, width = image.shape[:2]
            channels = image.shape[2] if len(image.shape) > 2 else 1
            dtype = str(image.dtype)
            size = image.size
        else:
            width, height = image.size
            channels = len(image.getbands())
            dtype = image.mode
            size = width * height * channels
        
        return {
            'width': width,
            'height': height,
            'channels': channels,
            'dtype': dtype,
            'size': size
        }
