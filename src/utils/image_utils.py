#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像处理工具

提供图像处理相关的工具函数
"""

import numpy as np
from PIL import Image
from typing import Tuple, Optional, Union
import cv2

class ImageUtils:
    """图像处理工具类"""
    
    @staticmethod
    def numpy_to_pil(array: np.ndarray) -> Image.Image:
        """
        将numpy数组转换为PIL图像
        
        Args:
            array: numpy数组
            
        Returns:
            PIL图像
        """
        # 确保数组在正确的范围内
        if array.dtype == np.float32 or array.dtype == np.float64:
            if array.max() <= 1.0:
                array = (array * 255).astype(np.uint8)
            else:
                array = array.astype(np.uint8)
        
        # 处理不同的数组形状
        if len(array.shape) == 2:
            # 灰度图
            return Image.fromarray(array, mode='L')
        elif len(array.shape) == 3:
            if array.shape[2] == 3:
                # RGB图
                return Image.fromarray(array, mode='RGB')
            elif array.shape[2] == 4:
                # RGBA图
                return Image.fromarray(array, mode='RGBA')
        
        raise ValueError(f"不支持的数组形状: {array.shape}")
    
    @staticmethod
    def pil_to_numpy(image: Image.Image, normalize: bool = True) -> np.ndarray:
        """
        将PIL图像转换为numpy数组
        
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
    def resize_image(image: Union[np.ndarray, Image.Image], 
                    size: Tuple[int, int], 
                    keep_aspect_ratio: bool = True,
                    method: str = 'lanczos') -> Union[np.ndarray, Image.Image]:
        """
        调整图像大小
        
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
            pil_image = ImageUtils.numpy_to_pil(image)
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
            return ImageUtils.pil_to_numpy(resized_image, normalize=True)
        else:
            return resized_image
    
    @staticmethod
    def convert_to_grayscale(image: Union[np.ndarray, Image.Image]) -> Union[np.ndarray, Image.Image]:
        """
        转换为灰度图
        
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
        """
        图像二值化
        
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
        """
        归一化图像
        
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
        """
        创建棋盘背景
        
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
        """
        混合两张图像
        
        Args:
            image1: 图像1
            image2: 图像2
            alpha: 混合系数 (0.0-1.0)
            
        Returns:
            混合后的图像
        """
        alpha = np.clip(alpha, 0.0, 1.0)
        return image1 * alpha + image2 * (1.0 - alpha)

    @staticmethod
    def save_sdf_as_image(sdf_data: np.ndarray,
                         file_path: str,
                         colormap: str = 'viridis',
                         quality: int = 95) -> bool:
        """
        将SDF数据保存为图像

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
                colored_image = ImageUtils.apply_colormap(normalized_data, colormap)
                pil_image = Image.fromarray(colored_image, mode='RGB')

            # 保存图像
            return ImageUtils.save_image(pil_image, file_path, quality)

        except Exception as e:
            print(f"保存SDF图像失败: {str(e)}")
            return False

    @staticmethod
    def apply_colormap(image: np.ndarray, colormap: str = 'viridis') -> np.ndarray:
        """
        应用颜色映射
        
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
        """
        保存图像
        
        Args:
            image: 图像数据
            file_path: 保存路径
            quality: 质量 (对JPEG有效)
            
        Returns:
            是否成功
        """
        try:
            if isinstance(image, np.ndarray):
                pil_image = ImageUtils.numpy_to_pil(image)
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
    
    @staticmethod
    def get_image_info(image: Union[np.ndarray, Image.Image]) -> dict:
        """
        获取图像信息
        
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
