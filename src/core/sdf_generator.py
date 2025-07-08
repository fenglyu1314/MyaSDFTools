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
                         normalize: bool = True,
                         blend_mode: str = "weighted") -> Tuple[np.ndarray, float]:
        """
        计算多张图像的混合SDF

        Args:
            image_paths: 图像文件路径列表
            angles: 对应的光照角度列表 (度数)
            threshold: 二值化阈值
            normalize: 是否归一化
            blend_mode: 混合模式 ("weighted", "average", "max", "min")

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
            mixed_sdf = self._blend_multiple_sdfs(sdf_images, angles, blend_mode)
            
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
    
    def _blend_multiple_sdfs(self, sdf_images: List[np.ndarray], angles: List[float], blend_mode: str = "weighted") -> np.ndarray:
        """
        混合多个SDF图像

        支持多种混合策略：
        - weighted: 基于角度权重的智能混合 (推荐)
        - average: 简单平均混合
        - max: 取最大值混合
        - min: 取最小值混合
        """
        if not sdf_images:
            raise ValueError("SDF图像列表不能为空")

        if len(sdf_images) != len(angles):
            raise ValueError("SDF图像数量必须与角度数量相同")

        # 确保所有图像尺寸相同
        height, width = sdf_images[0].shape
        for sdf in sdf_images[1:]:
            if sdf.shape != (height, width):
                raise ValueError("所有SDF图像必须具有相同的尺寸")

        # 如果只有一张图像，直接返回
        if len(sdf_images) == 1:
            return sdf_images[0].copy()

        # 根据混合模式选择策略
        if blend_mode == "weighted":
            return self._blend_weighted(sdf_images, angles)
        elif blend_mode == "average":
            return self._blend_average(sdf_images)
        elif blend_mode == "max":
            return self._blend_max(sdf_images)
        elif blend_mode == "min":
            return self._blend_min(sdf_images)
        else:
            # 默认使用加权混合
            return self._blend_weighted(sdf_images, angles)

    def _blend_weighted(self, sdf_images: List[np.ndarray], angles: List[float]) -> np.ndarray:
        """基于角度权重的混合"""
        height, width = sdf_images[0].shape

        # 计算角度权重
        angle_weights = self._calculate_angle_weights(angles)

        # 基于权重的混合
        result = np.zeros((height, width), dtype=np.float32)

        for sdf_image, weight in zip(sdf_images, angle_weights):
            result += sdf_image * weight

        return result

    def _blend_average(self, sdf_images: List[np.ndarray]) -> np.ndarray:
        """简单平均混合"""
        height, width = sdf_images[0].shape
        result = np.zeros((height, width), dtype=np.float32)

        for sdf_image in sdf_images:
            result += sdf_image

        result /= len(sdf_images)
        return result

    def _blend_max(self, sdf_images: List[np.ndarray]) -> np.ndarray:
        """取最大值混合"""
        result = sdf_images[0].copy()

        for sdf_image in sdf_images[1:]:
            result = np.maximum(result, sdf_image)

        return result

    def _blend_min(self, sdf_images: List[np.ndarray]) -> np.ndarray:
        """取最小值混合"""
        result = sdf_images[0].copy()

        for sdf_image in sdf_images[1:]:
            result = np.minimum(result, sdf_image)

        return result

    def _calculate_angle_weights(self, angles: List[float]) -> List[float]:
        """
        计算角度权重

        基于角度分布的均匀性计算权重，确保角度分布越均匀，混合效果越好

        Args:
            angles: 角度列表 (度数)

        Returns:
            权重列表，总和为1.0
        """
        if not angles:
            return []

        if len(angles) == 1:
            return [1.0]

        # 将角度标准化到[0, 360)范围
        normalized_angles = [(angle % 360.0) for angle in angles]

        # 计算角度间隔
        sorted_angles = sorted(normalized_angles)

        # 计算每个角度的权重
        weights = []
        n = len(angles)

        for i, angle in enumerate(normalized_angles):
            # 找到当前角度在排序列表中的位置
            sorted_index = sorted_angles.index(angle)

            # 计算前后角度间隔
            prev_angle = sorted_angles[(sorted_index - 1) % n]
            next_angle = sorted_angles[(sorted_index + 1) % n]

            # 计算角度间隔 (考虑360度循环)
            prev_gap = self._angle_difference(angle, prev_angle)
            next_gap = self._angle_difference(next_angle, angle)

            # 基于间隔计算权重 (间隔越大，权重越高)
            gap_factor = (prev_gap + next_gap) / 2.0

            # 基础权重 + 间隔调整
            base_weight = 1.0 / n
            gap_adjustment = gap_factor / 180.0  # 标准化到[0,2]

            weight = base_weight * (0.5 + gap_adjustment)
            weights.append(weight)

        # 归一化权重
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            weights = [1.0 / n] * n

        return weights

    def _angle_difference(self, angle1: float, angle2: float) -> float:
        """
        计算两个角度之间的最小差值 (考虑360度循环)

        Args:
            angle1: 角度1 (度数)
            angle2: 角度2 (度数)

        Returns:
            最小角度差值 (0-180度)
        """
        diff = abs(angle1 - angle2)
        return min(diff, 360.0 - diff)

    def preview_lighting(self,
                        sdf_data: np.ndarray,
                        light_angle: float,
                        lighting_intensity: float = 1.0,
                        ambient_light: float = 0.3) -> np.ndarray:
        """
        根据光照角度预览SDF效果

        参考shader算法实现正确的SDF光照效果

        Args:
            sdf_data: SDF数据
            light_angle: 光照角度 (0-360度)
            lighting_intensity: 光照强度 (0.0-2.0)
            ambient_light: 环境光强度 (0.0-1.0)

        Returns:
            预览效果图像
        """
        # 将角度转换为0-1范围的光照参数
        # 0度 = 0.0, 180度 = 0.5, 360度 = 1.0
        light_param = (light_angle % 360.0) / 360.0

        # 定义方向向量 (参考shader中的front_dir和right_dir)
        front_dir = np.array([0.0, 0.0, 1.0])  # 正面方向
        right_dir = np.array([1.0, 0.0, 0.0])  # 右方向

        # 根据light_param计算光照方向
        # 将0-1映射到完整的光照方向
        angle_rad = light_param * 2 * math.pi
        light_dir = np.array([
            math.cos(angle_rad),
            math.sin(angle_rad),
            0.5  # Z分量，控制光照的"深度"
        ])

        # 归一化光照方向
        light_dir = light_dir / np.linalg.norm(light_dir)

        # 计算点积 (参考shader算法)
        RdotL = np.dot(right_dir, light_dir)
        FdotL = np.dot(front_dir, light_dir)

        # 应用shader中的FdotL变换
        FdotL = ((-FdotL + 1.0) * 0.5) * ((-FdotL + 1.0) * 0.5)

        # 根据RdotL决定采样方向
        if RdotL < 0:
            # 正常采样
            sdf_sample = sdf_data
        else:
            # 镜像采样 (翻转X轴)
            sdf_sample = np.fliplr(sdf_data)

        # 应用step函数 (参考shader: FdotL < sdf_col)
        # 这里我们使用smooth step来获得更好的视觉效果
        shadow_mask = self._smooth_step(FdotL, sdf_sample, 0.1)

        # 计算最终光照效果
        # 基础亮度
        base_lighting = ambient_light + (1.0 - ambient_light) * lighting_intensity

        # 应用阴影
        final_lighting = base_lighting * shadow_mask

        # 结合原始SDF数据
        result = sdf_data * final_lighting

        return np.clip(result, 0.0, 1.0)

    def _smooth_step(self, edge: float, value: np.ndarray, smoothness: float = 0.1) -> np.ndarray:
        """
        平滑step函数，避免硬边缘

        Args:
            edge: 阈值
            value: 输入值
            smoothness: 平滑度

        Returns:
            平滑的step结果
        """
        # 计算平滑的step函数
        t = np.clip((value - edge + smoothness) / (2 * smoothness), 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)  # 平滑插值
    
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
