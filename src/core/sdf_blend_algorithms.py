#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SDF混合算法模块

实现多种SDF混合策略：
- 基于SDF特性的两两混合
- 权重混合
- 简单混合模式（平均、最大、最小）
"""

from typing import List
import numpy as np


class SDFBlendAlgorithms:
    """SDF混合算法实现"""

    def __init__(self):
        """初始化混合算法"""
        pass

    def blend_multiple_sdfs(self, sdf_images: List[np.ndarray],
                           angles: List[float],
                           blend_mode: str = "sdf_blend") -> np.ndarray:
        """
        混合多个SDF图像

        使用确认正确的SDF混合策略：
        - sdf_blend: 基于SDF特性的两两混合 (相邻帧混合算法)

        Args:
            sdf_images: SDF图像列表
            angles: 对应的角度列表 (保留参数兼容性，但不影响混合结果)
            blend_mode: 混合模式 (固定为sdf_blend)

        Returns:
            混合后的SDF
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

        # 使用SDF特性混合 (Python实现)
        return self.blend_sdf_pairwise(sdf_images, angles)

    def blend_sdf_pairwise(self, sdf_images: List[np.ndarray], angles: List[float]) -> np.ndarray:
        """
        基于SDF特性的两两混合算法
        
        实现文章中描述的算法：
        1. 将每两帧进行SDF特性混合
        2. 将所有混合结果相加并归一化
        
        参考算法：
        float SDFA = Sample(A) * 2.0 - 1.0;
        float SDFB = Sample(B) * 2.0 - 1.0;
        
        if(SDFA < 0.0) result = 1.0;           // 在A内部
        else if(SDFB > 0.0) result = 0.0;      // 在B外部
        else result = abs(SDFB) / (abs(SDFB) + SDFA);  // 在A外部且B内部
        
        Args:
            sdf_images: SDF图像列表
            angles: 角度列表
            
        Returns:
            混合后的SDF
        """
        height, width = sdf_images[0].shape
        num_images = len(sdf_images)

        # 存储所有两两混合的结果
        blend_results = []

        print(f"🔄 开始SDF特性混合，共{num_images}张图像")

        # 相邻帧混合（更合理的策略）
        for i in range(num_images - 1):
            sdf_a = sdf_images[i]
            sdf_b = sdf_images[i + 1]

            # 执行两两SDF混合
            blend_result = SDFBlendAlgorithms.blend_two_sdfs(sdf_a, sdf_b)
            blend_results.append(blend_result)

            print(f"  ✅ 混合第{i+1}帧和第{i+2}帧")

        print(f"🎯 SDF相邻帧混合完成，共生成{len(blend_results)}个混合结果")

        # 将所有混合结果相加并归一化
        if blend_results:
            final_result = np.mean(blend_results, axis=0)
        else:
            final_result = sdf_images[0] if sdf_images else np.zeros((height, width))

        print(f"📊 最终混合结果值范围: [{np.min(final_result):.3f}, {np.max(final_result):.3f}]")

        return final_result

    @staticmethod
    def blend_two_sdfs(sdf_a: np.ndarray, sdf_b: np.ndarray) -> np.ndarray:
        """
        两个SDF的特性混合

        实现文章中的核心混合算法

        按照文章的SDF格式：
        - 0.0-0.5: 内部区域 (距离边界越远值越小，中心最暗)
        - 0.5: 边界
        - 0.5-1.0: 外部区域 (距离边界越远值越大，外部最亮)

        Args:
            sdf_a: 第一个SDF (0-1范围)
            sdf_b: 第二个SDF (0-1范围)

        Returns:
            混合结果
        """
        # 将SDF从[0,1]转换到[-1,1]范围
        # 按照文章的定义：0.5 -> 0 (边界), <0.5 -> 负值 (内部), >0.5 -> 正值 (外部)
        SDFA = (sdf_a - 0.5) * 2.0
        SDFB = (sdf_b - 0.5) * 2.0

        # 初始化结果数组
        result = np.zeros_like(sdf_a, dtype=np.float32)

        # 应用混合规则 (注意：现在<0.5是内部，>0.5是外部)
        # 在A内部 (SDFA < 0, 即 sdf_a < 0.5)
        mask_a_inside = SDFA < 0.0
        result[mask_a_inside] = 1.0

        # 在B外部 (SDFB > 0, 即 sdf_b > 0.5)
        mask_b_outside = SDFB > 0.0
        result[mask_b_outside] = 0.0

        # 在A外部且B内部 (SDFA >= 0 and SDFB <= 0)
        mask_transition = (~mask_a_inside) & (~mask_b_outside)
        if np.any(mask_transition):
            abs_SDFB = np.abs(SDFB[mask_transition])
            abs_SDFA = np.abs(SDFA[mask_transition])
            # 避免除零
            denominator = abs_SDFB + abs_SDFA
            safe_mask = denominator > 1e-8
            if np.any(safe_mask):
                transition_indices = np.where(mask_transition)
                safe_indices = np.where(safe_mask)
                result[transition_indices[0][safe_indices], transition_indices[1][safe_indices]] = \
                    abs_SDFB[safe_indices] / denominator[safe_indices]

        print(f"🔄 SDF混合完成 - A内部像素: {np.sum(mask_a_inside)}, B外部像素: {np.sum(mask_b_outside)}, 过渡像素: {np.sum(mask_transition)}")

        return result


