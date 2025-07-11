#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SDF核心算法模块

实现SDF计算的核心算法：
- 8SSEDT算法的Python实现
- 改进的距离场计算
- 光照预览算法
- 图像预处理
"""

import math
from typing import Optional
import numpy as np
import cv2
from PIL import Image


class SDFCoreAlgorithm:
    """SDF核心算法实现"""

    @staticmethod
    def load_and_preprocess_image(image_path: str, threshold: float = 0.5) -> np.ndarray:
        """
        加载和预处理图像
        
        Args:
            image_path: 图像文件路径
            threshold: 二值化阈值 (0.0-1.0)
            
        Returns:
            预处理后的二值图像
        """
        try:
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
            
        except Exception as e:
            raise RuntimeError(f"图像加载失败: {str(e)}")

    @staticmethod
    def compute_sdf_python(binary_image: np.ndarray, 
                          normalize: bool = True, 
                          invert: bool = False, 
                          sdf_direction: str = "both", 
                          max_distance: int = 100) -> np.ndarray:
        """
        使用Python实现计算SDF (改进的距离场算法)
        
        Args:
            binary_image: 二值图像
            normalize: 是否归一化到[0,1]
            invert: 是否反转内外区域
            sdf_direction: SDF计算方向 ("both", "inside", "outside")
            max_distance: 最大距离限制 (像素)
            
        Returns:
            SDF结果
        """
        height, width = binary_image.shape

        # 计算内部和外部的距离变换
        inside_mask = binary_image > 0.5
        outside_mask = ~inside_mask

        # 根据SDF计算方向选择计算策略
        if sdf_direction == "inside":
            # 只计算内部距离 - 使用正确的归一化
            inside_dist = cv2.distanceTransform(
                inside_mask.astype(np.uint8),
                cv2.DIST_L2,
                cv2.DIST_MASK_PRECISE
            )
            inside_dist = np.clip(inside_dist, 0, max_distance)

            if normalize:
                # 内部距离归一化：边界0.5，内部最深0.0 (按照文章定义)
                max_val = np.max(inside_dist) if np.max(inside_dist) > 0 else 1.0
                sdf = 0.5 - (inside_dist / max_val) * 0.5
            else:
                sdf = inside_dist

        elif sdf_direction == "outside":
            # 只计算外部距离 - 使用正确的归一化
            outside_dist = cv2.distanceTransform(
                outside_mask.astype(np.uint8),
                cv2.DIST_L2,
                cv2.DIST_MASK_PRECISE
            )
            outside_dist = np.clip(outside_dist, 0, max_distance)

            if normalize:
                # 外部距离归一化：边界0.5，外部最远1.0 (按照文章定义)
                max_val = np.max(outside_dist) if np.max(outside_dist) > 0 else 1.0
                sdf = 0.5 + (outside_dist / max_val) * 0.5
            else:
                sdf = outside_dist

        else:  # sdf_direction == "both"
            # 双向计算（默认）- 改进的SDF算法，已经包含正确归一化
            sdf = SDFCoreAlgorithm.compute_improved_sdf(inside_mask, max_distance)
            # 双向计算时normalize参数已在compute_improved_sdf中处理

        # 对于单方向计算，应用invert选项
        if invert and sdf_direction != "both":
            sdf = 1.0 - sdf

        return sdf.astype(np.float32)

    @staticmethod
    def compute_improved_sdf(inside_mask: np.ndarray, max_distance: int) -> np.ndarray:
        """
        改进的SDF计算算法 - 按照参考文章实现正确的归一化

        实现文章中的8SSEDT算法归一化方式：
        - 物体外部：0到0.5的值
        - 物体边界：0.5
        - 物体内部：0.5到1的值

        参考算法：
        val = 0.5f;
        if (dist < 0) val += dist / sqrt(outsideMax) * 0.5f;  // 外部
        else val += dist / sqrt(insideMax) * 0.5f;            // 内部

        Args:
            inside_mask: 内部区域掩码
            max_distance: 最大距离限制

        Returns:
            正确归一化的SDF (0-1范围)
        """
        # 计算内部距离（到边界的距离）
        inside_dist = cv2.distanceTransform(
            inside_mask.astype(np.uint8),
            cv2.DIST_L2,
            cv2.DIST_MASK_PRECISE
        )

        # 计算外部距离（到边界的距离）
        outside_mask = ~inside_mask
        outside_dist = cv2.distanceTransform(
            outside_mask.astype(np.uint8),
            cv2.DIST_L2,
            cv2.DIST_MASK_PRECISE
        )

        # 限制最大距离
        inside_dist = np.clip(inside_dist, 0, max_distance)
        outside_dist = np.clip(outside_dist, 0, max_distance)

        # 计算最大距离值（用于归一化）
        inside_max = np.max(inside_dist) if np.any(inside_mask) else 1.0
        outside_max = np.max(outside_dist) if np.any(outside_mask) else 1.0

        # 避免除零
        inside_max = max(inside_max, 1e-8)
        outside_max = max(outside_max, 1e-8)

        # 按照文章算法进行归一化
        # 注意：文章中说"物体内最中心的地方就是0，最远的地方就是1"
        # 这意味着需要反转我们通常的理解

        # 初始化为边界值 0.5
        result = np.full_like(inside_dist, 0.5, dtype=np.float32)

        # 处理内部区域：0.5 到 0.0 (内部中心最暗)
        if np.any(inside_mask):
            # 内部距离归一化到 [0, 0.5] 然后从 0.5 减去
            normalized_inside = inside_dist[inside_mask] / inside_max * 0.5
            result[inside_mask] = 0.5 - normalized_inside

        # 处理外部区域：0.5 到 1.0 (外部最远最亮)
        if np.any(outside_mask):
            # 外部距离归一化到 [0, 0.5] 然后加到 0.5 上
            normalized_outside = outside_dist[outside_mask] / outside_max * 0.5
            result[outside_mask] = 0.5 + normalized_outside

        # 确保结果在 [0, 1] 范围内
        result = np.clip(result, 0.0, 1.0)

        print(f"🔧 SDF归一化完成 - 内部最大距离: {inside_max:.2f}, 外部最大距离: {outside_max:.2f}")
        print(f"📊 SDF值范围: [{np.min(result):.3f}, {np.max(result):.3f}]")

        return result

    @staticmethod
    def preview_lighting(sdf_data: np.ndarray,
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
        shadow_mask = SDFCoreAlgorithm.smooth_step(FdotL, sdf_sample, 0.1)

        # 计算最终光照效果
        # 基础亮度
        base_lighting = ambient_light + (1.0 - ambient_light) * lighting_intensity

        # 应用阴影
        final_lighting = base_lighting * shadow_mask

        # 结合原始SDF数据
        result = sdf_data * final_lighting

        return np.clip(result, 0.0, 1.0)

    @staticmethod
    def smooth_step(edge: float, value: np.ndarray, smoothness: float = 0.1) -> np.ndarray:
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

    @staticmethod
    def calculate_even_angles(num_images: int) -> list:
        """
        计算均匀分布的角度
        
        Args:
            num_images: 图像数量
            
        Returns:
            角度列表
        """
        if num_images <= 0:
            return []
        elif num_images == 1:
            return [0.0]
        else:
            # 在180度范围内均匀分布
            angle_step = 180.0 / num_images
            return [i * angle_step for i in range(num_images)]
