#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SDF生成器 - 重构后的简化版本

负责协调各个SDF算法模块：
- 单张图像SDF生成
- 多张图像混合SDF生成
- 性能监控
- 算法选择和参数管理
"""

import time
from typing import List, Tuple, Optional, Dict, Any
import numpy as np

from .sdf_core_algorithm import SDFCoreAlgorithm
from .sdf_blend_algorithms import SDFBlendAlgorithms


class SDFGenerator:
    """SDF生成器类 - 重构后的简化版本
    
    负责协调SDF计算的各个模块，提供统一的接口
    """

    def __init__(self):
        """初始化SDF生成器"""
        self.last_computation_time = 0.0

        # 初始化各个模块
        self.core_algorithm = SDFCoreAlgorithm()
        self.blend_algorithms = SDFBlendAlgorithms()

    def compute_single_sdf(self,
                          image_path: str,
                          threshold: float = 0.5,
                          normalize: bool = True,
                          invert: bool = False,
                          sdf_direction: str = "both",
                          max_distance: int = 100,
                          num_threads: Optional[int] = None) -> Tuple[np.ndarray, float]:
        """
        计算单张图像的SDF
        
        Args:
            image_path: 图像文件路径
            threshold: 二值化阈值 (0.0-1.0)
            normalize: 是否归一化到[0,1]
            invert: 是否反转内外区域
            sdf_direction: SDF计算方向 ("both", "inside", "outside")
            max_distance: 最大距离限制 (像素)
            num_threads: 线程数 (None表示自动)
            
        Returns:
            (sdf_result, computation_time)
        """
        start_time = time.time()
        
        try:
            # 加载和预处理图像
            image_data = self.core_algorithm.load_and_preprocess_image(image_path, threshold)

            # 使用Python实现计算SDF
            sdf_result = self.core_algorithm.compute_sdf_python(
                image_data, normalize, invert, sdf_direction, max_distance
            )
            
            computation_time = time.time() - start_time
            self.last_computation_time = computation_time
            
            return sdf_result, computation_time
            
        except Exception as e:
            raise RuntimeError(f"SDF计算失败: {str(e)}")

    def compute_multi_sdf(self,
                         image_paths: List[str],
                         angles: Optional[List[float]] = None,
                         threshold: float = 0.5,
                         normalize: bool = True,
                         invert: bool = False,
                         blend_mode: str = "sdf_blend",
                         sdf_direction: str = "both",
                         max_distance: int = 100,
                         num_threads: Optional[int] = None) -> Tuple[np.ndarray, float]:
        """
        计算多张图像的混合SDF

        Args:
            image_paths: 图像文件路径列表
            angles: 对应的光照角度列表 (度数)
            threshold: 二值化阈值
            normalize: 是否归一化
            invert: 是否反转内外区域
            blend_mode: 混合模式 (固定为"sdf_blend")
            sdf_direction: SDF计算方向 ("both", "inside", "outside")
            max_distance: 最大距离限制 (像素)
            num_threads: 线程数 (None表示自动)

        Returns:
            (mixed_sdf_result, computation_time)
        """
        start_time = time.time()
        
        if not image_paths:
            raise ValueError("图像路径列表不能为空")
        
        # 如果没有提供角度，自动计算等角度分布
        if angles is None:
            angles = self.core_algorithm.calculate_even_angles(len(image_paths))
        elif len(angles) != len(image_paths):
            raise ValueError("角度数量必须与图像数量相同")
        
        try:
            # 计算每张图像的SDF
            sdf_images = []
            for image_path in image_paths:
                sdf_result, _ = self.compute_single_sdf(
                    image_path, threshold, normalize, invert, sdf_direction, max_distance, num_threads
                )
                sdf_images.append(sdf_result)

            # 混合多个SDF
            mixed_sdf = self.blend_algorithms.blend_multiple_sdfs(sdf_images, angles, blend_mode)
            
            computation_time = time.time() - start_time
            self.last_computation_time = computation_time
            
            return mixed_sdf, computation_time
            
        except Exception as e:
            raise RuntimeError(f"多图SDF计算失败: {str(e)}")

    def preview_lighting(self,
                        sdf_data: np.ndarray,
                        light_angle: float,
                        lighting_intensity: float = 1.0,
                        ambient_light: float = 0.3) -> np.ndarray:
        """
        根据光照角度预览SDF效果
        
        Args:
            sdf_data: SDF数据
            light_angle: 光照角度 (0-360度)
            lighting_intensity: 光照强度 (0.0-2.0)
            ambient_light: 环境光强度 (0.0-1.0)
            
        Returns:
            预览效果图像
        """
        return self.core_algorithm.preview_lighting(
            sdf_data, light_angle, lighting_intensity, ambient_light
        )

    def get_last_computation_time(self) -> float:
        """获取最后一次计算时间"""
        return self.last_computation_time

    def get_version_info(self) -> Dict[str, Any]:
        """获取版本信息"""
        info = {
            'python_version': '0.2.0',
            'backend': 'Python',
            'algorithms': ['OpenCV Distance Transform', 'Improved SDF'],
            'blend_modes': ['sdf_blend']
        }

        return info

    def get_performance_info(self) -> Dict[str, Any]:
        """获取性能信息"""
        performance_info = {
            'last_computation_time': self.last_computation_time,
            'backend': 'C++' if self.cpp_interface.is_available() else 'Python'
        }
        
        # 如果有C++后端，获取性能基准
        if self.cpp_interface.is_available():
            benchmark = self.cpp_interface.benchmark_performance()
            performance_info['cpp_benchmark'] = benchmark
        
        return performance_info

    def validate_backend(self) -> Dict[str, Any]:
        """验证后端功能"""
        validation_info = {
            'python_backend': {
                'available': True,
                'algorithms': ['OpenCV Distance Transform', 'Improved SDF']
            }
        }

        return validation_info
