#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像处理工具

提供图像处理相关的工具函数统一接口
"""

from .format_converter import FormatConverter
from .image_processor import ImageProcessor
from .image_saver import ImageSaver
from typing import Tuple, Union
import numpy as np
from PIL import Image

class ImageUtils:
    """图像处理工具类

    提供图像处理功能的统一接口，内部委托给专门的处理器。
    """

    # 格式转换相关方法
    @staticmethod
    def numpy_to_pil(array: np.ndarray) -> Image.Image:
        """将numpy数组转换为PIL图像"""
        return FormatConverter.numpy_to_pil(array)

    @staticmethod
    def pil_to_numpy(image: Image.Image, normalize: bool = True) -> np.ndarray:
        """将PIL图像转换为numpy数组"""
        return FormatConverter.pil_to_numpy(image, normalize)

    # 图像处理相关方法
    @staticmethod
    def resize_image(image: Union[np.ndarray, Image.Image],
                    size: Tuple[int, int],
                    keep_aspect_ratio: bool = True,
                    method: str = 'lanczos') -> Union[np.ndarray, Image.Image]:
        """调整图像大小"""
        return ImageProcessor.resize_image(image, size, keep_aspect_ratio, method)

    @staticmethod
    def convert_to_grayscale(image: Union[np.ndarray, Image.Image]) -> Union[np.ndarray, Image.Image]:
        """转换为灰度图"""
        return ImageProcessor.convert_to_grayscale(image)

    @staticmethod
    def threshold_image(image: np.ndarray, threshold: float = 0.5, invert: bool = False) -> np.ndarray:
        """图像二值化"""
        return ImageProcessor.threshold_image(image, threshold, invert)

    @staticmethod
    def normalize_image(image: np.ndarray, target_range: Tuple[float, float] = (0.0, 1.0)) -> np.ndarray:
        """归一化图像"""
        return ImageProcessor.normalize_image(image, target_range)

    @staticmethod
    def create_checkerboard(size: Tuple[int, int],
                           square_size: int = 20,
                           color1: Tuple[int, int, int] = (255, 255, 255),
                           color2: Tuple[int, int, int] = (200, 200, 200)) -> np.ndarray:
        """创建棋盘背景"""
        return ImageProcessor.create_checkerboard(size, square_size, color1, color2)

    @staticmethod
    def blend_images(image1: np.ndarray,
                    image2: np.ndarray,
                    alpha: float = 0.5) -> np.ndarray:
        """混合两张图像"""
        return ImageProcessor.blend_images(image1, image2, alpha)

    # 图像保存相关方法
    @staticmethod
    def save_sdf_as_image(sdf_data: np.ndarray,
                         file_path: str,
                         colormap: str = 'gray',
                         quality: int = 95) -> bool:
        """将SDF数据保存为图像"""
        return ImageSaver.save_sdf_as_image(sdf_data, file_path, colormap, quality)

    @staticmethod
    def apply_colormap(image: np.ndarray, colormap: str = 'viridis') -> np.ndarray:
        """应用颜色映射"""
        return ImageSaver.apply_colormap(image, colormap)

    @staticmethod
    def save_image(image: Union[np.ndarray, Image.Image],
                  file_path: str,
                  quality: int = 95) -> bool:
        """保存图像"""
        return ImageSaver.save_image(image, file_path, quality)

    @staticmethod
    def get_image_info(image: Union[np.ndarray, Image.Image]) -> dict:
        """获取图像信息"""
        return FormatConverter.get_image_info(image)
