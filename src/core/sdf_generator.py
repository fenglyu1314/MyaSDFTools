#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SDF生成器

实现SDF算法的Python版本，包括：
- 单张图像SDF生成
- 多张图像混合SDF生成
- 8SSEDT算法实现
- 性能监控
"""

import time
import math
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
from PIL import Image
import cv2

class SDFGenerator:
    """SDF生成器类"""
    
    def __init__(self):
        self.last_computation_time = 0.0
        self.use_cpp_backend = False
        
        # 尝试导入C++后端
        try:
            import sdf_core
            self.cpp_backend = sdf_core
            self.use_cpp_backend = True
            print("使用C++后端进行SDF计算")
        except ImportError:
            print("C++后端不可用，使用Python实现")
    
    def compute_single_sdf(self, 
                          image_path: str, 
                          threshold: float = 0.5,
                          normalize: bool = True,
                          invert: bool = False) -> Tuple[np.ndarray, float]:
        """
        计算单张图像的SDF
        
        Args:
            image_path: 图像文件路径
            threshold: 二值化阈值 (0.0-1.0)
            normalize: 是否归一化到[0,1]
            invert: 是否反转内外区域
            
        Returns:
            (sdf_result, computation_time)
        """
        start_time = time.time()
        
        try:
            # 加载和预处理图像
            image_data = self._load_and_preprocess_image(image_path, threshold)
            
            if self.use_cpp_backend:
                # 使用C++后端
                sdf_result = self._compute_sdf_cpp(image_data, normalize, invert)
            else:
                # 使用Python实现
                sdf_result = self._compute_sdf_python(image_data, normalize, invert)
            
            computation_time = time.time() - start_time
            self.last_computation_time = computation_time
            
            return sdf_result, computation_time
            
        except Exception as e:
            raise RuntimeError(f"SDF计算失败: {str(e)}")
    
    def compute_multi_sdf(self,
                         image_paths: List[str],
                         angles: Optional[List[float]] = None,
                         threshold: float = 0.5,
                         normalize: bool = True) -> Tuple[np.ndarray, float]:
        """
        计算多张图像的混合SDF
        
        Args:
            image_paths: 图像文件路径列表
            angles: 对应的光照角度列表 (度数)
            threshold: 二值化阈值
            normalize: 是否归一化
            
        Returns:
            (mixed_sdf_result, computation_time)
        """
        start_time = time.time()
        
        if not image_paths:
            raise ValueError("图像路径列表不能为空")
        
        # 如果没有提供角度，自动计算等角度分布
        if angles is None:
            angles = self._calculate_even_angles(len(image_paths))
        elif len(angles) != len(image_paths):
            raise ValueError("角度数量必须与图像数量相同")
        
        try:
            # 计算每张图像的SDF
            sdf_images = []
            for image_path in image_paths:
                sdf_result, _ = self.compute_single_sdf(image_path, threshold, normalize)
                sdf_images.append(sdf_result)
            
            # 混合多个SDF
            mixed_sdf = self._blend_multiple_sdfs(sdf_images, angles)
            
            computation_time = time.time() - start_time
            self.last_computation_time = computation_time
            
            return mixed_sdf, computation_time
            
        except Exception as e:
            raise RuntimeError(f"多图SDF计算失败: {str(e)}")
    
    def _load_and_preprocess_image(self, image_path: str, threshold: float) -> np.ndarray:
        """加载和预处理图像"""
        # 使用PIL加载图像
        image = Image.open(image_path)
        
        # 转换为灰度图
        if image.mode != 'L':
            image = image.convert('L')
        
        # 转换为numpy数组
        image_array = np.array(image, dtype=np.float32) / 255.0
        
        # 二值化
        binary_image = (image_array > threshold).astype(np.float32)
        
        return binary_image
    
    def _compute_sdf_cpp(self, binary_image: np.ndarray, normalize: bool, invert: bool) -> np.ndarray:
        """使用C++后端计算SDF"""
        height, width = binary_image.shape
        
        # 将numpy数组转换为列表
        image_data = binary_image.flatten().tolist()
        
        # 调用C++函数
        sdf_result = self.cpp_backend.compute_single_sdf(
            image_data, width, height, 0.5, normalize
        )
        
        # 转换回numpy数组
        result = np.array(sdf_result, dtype=np.float32).reshape(height, width)
        
        if invert:
            result = 1.0 - result
        
        return result
    
    def _compute_sdf_python(self, binary_image: np.ndarray, normalize: bool, invert: bool) -> np.ndarray:
        """使用Python实现计算SDF (8SSEDT算法简化版)"""
        height, width = binary_image.shape
        
        # 计算内部和外部的距离变换
        inside_mask = binary_image > 0.5
        outside_mask = ~inside_mask
        
        # 使用OpenCV的距离变换
        inside_dist = cv2.distanceTransform(
            inside_mask.astype(np.uint8), 
            cv2.DIST_L2, 
            cv2.DIST_MASK_PRECISE
        )
        
        outside_dist = cv2.distanceTransform(
            outside_mask.astype(np.uint8), 
            cv2.DIST_L2, 
            cv2.DIST_MASK_PRECISE
        )
        
        # 计算有向距离场
        # 标准SDF: 物体外部为正值，内部为负值
        # 但为了显示方便，我们让物体内部为较大值
        sdf = outside_dist - inside_dist
        
        if normalize:
            # 归一化到[0,1]范围
            min_val, max_val = sdf.min(), sdf.max()
            if max_val > min_val:
                sdf = (sdf - min_val) / (max_val - min_val)
            else:
                sdf = np.ones_like(sdf) * 0.5
        
        if invert:
            sdf = 1.0 - sdf
        
        return sdf.astype(np.float32)
    
    def _calculate_even_angles(self, num_images: int) -> List[float]:
        """计算等角度分布"""
        if num_images <= 0:
            return []
        
        angle_step = 360.0 / num_images
        return [i * angle_step for i in range(num_images)]
    
    def _blend_multiple_sdfs(self, sdf_images: List[np.ndarray], angles: List[float]) -> np.ndarray:
        """混合多个SDF图像"""
        if not sdf_images:
            raise ValueError("SDF图像列表不能为空")
        
        # 确保所有图像尺寸相同
        height, width = sdf_images[0].shape
        for sdf in sdf_images[1:]:
            if sdf.shape != (height, width):
                raise ValueError("所有SDF图像必须具有相同的尺寸")
        
        # 简单的平均混合 (后续可以实现更复杂的混合算法)
        result = np.zeros((height, width), dtype=np.float32)
        
        for sdf_image in sdf_images:
            result += sdf_image
        
        result /= len(sdf_images)
        
        return result
    
    def preview_lighting(self, 
                        sdf_data: np.ndarray, 
                        light_angle: float) -> np.ndarray:
        """
        根据光照角度预览SDF效果
        
        Args:
            sdf_data: SDF数据
            light_angle: 光照角度 (0-360度)
            
        Returns:
            预览效果图像
        """
        # 简单的光照效果模拟
        # 将SDF值作为光照强度
        angle_rad = math.radians(light_angle)
        
        # 创建光照方向向量
        light_dir_x = math.cos(angle_rad)
        light_dir_y = math.sin(angle_rad)
        
        # 计算梯度 (法向量)
        grad_y, grad_x = np.gradient(sdf_data)
        
        # 归一化梯度
        grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        grad_magnitude = np.maximum(grad_magnitude, 1e-8)  # 避免除零
        
        norm_grad_x = grad_x / grad_magnitude
        norm_grad_y = grad_y / grad_magnitude
        
        # 计算光照强度 (点积)
        lighting = norm_grad_x * light_dir_x + norm_grad_y * light_dir_y
        
        # 将光照强度映射到[0,1]
        lighting = (lighting + 1.0) * 0.5
        
        # 结合SDF值和光照效果
        result = sdf_data * lighting
        
        return np.clip(result, 0.0, 1.0)
    
    def get_last_computation_time(self) -> float:
        """获取最后一次计算时间"""
        return self.last_computation_time
    
    def get_version_info(self) -> Dict[str, Any]:
        """获取版本信息"""
        info = {
            'python_version': '0.1.0',
            'backend': 'C++' if self.use_cpp_backend else 'Python',
            'algorithms': ['8SSEDT', 'OpenCV Distance Transform']
        }
        
        if self.use_cpp_backend:
            try:
                info['cpp_version'] = self.cpp_backend.get_version_info()
            except:
                pass
        
        return info
