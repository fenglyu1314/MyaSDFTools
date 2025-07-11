#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
光照预览处理器

专门负责光照效果的计算和预览更新：
- 光照算法实现
- 光照预览更新
- 角度参数处理
"""

import numpy as np
from typing import Optional
from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QPixmap, QImage


class LightingPreviewHandler(QObject):
    """光照预览处理器 - 专门处理光照效果相关逻辑"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_merged_sdf: Optional[np.ndarray] = None

    def set_merged_sdf(self, sdf_data: np.ndarray):
        """设置当前的合并SDF数据"""
        self.current_merged_sdf = sdf_data

    def update_lighting_preview(self, lighting_preview_widget, angle: float, 
                               intensity: float = 1.0, ambient: float = 0.1):
        """更新光照效果预览"""
        if self.current_merged_sdf is None:
            print("❌ 没有SDF数据，无法更新光照预览")
            return

        try:
            # 计算光照效果
            lighting_result = self._apply_lighting_effect(
                self.current_merged_sdf, angle, intensity, ambient
            )

            if lighting_result is not None:
                # 转换为QPixmap并显示
                lighting_pixmap = self._numpy_to_pixmap(lighting_result)
                if not lighting_pixmap.isNull():
                    # 缩放图像以适应预览区域，保持宽高比，显示完整图像
                    preview_size = lighting_preview_widget.size()
                    margin = 4  # 边距
                    scaled_pixmap = lighting_pixmap.scaled(
                        preview_size.width() - margin,
                        preview_size.height() - margin,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    lighting_preview_widget.setPixmap(scaled_pixmap)
                    lighting_preview_widget.setText("")
                    lighting_preview_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    print(f"✅ 光照效果预览更新成功: 角度={angle}°, 尺寸={scaled_pixmap.size().width()}x{scaled_pixmap.size().height()}")
                else:
                    lighting_preview_widget.setText("光照效果\n转换失败")
                    print("❌ 光照效果转换QPixmap失败")
            else:
                lighting_preview_widget.setText("光照效果\n计算失败")
                print("❌ 光照效果计算失败")

        except Exception as e:
            print(f"❌ 更新光照预览失败: {e}")
            lighting_preview_widget.setText("光照效果\n更新失败")

    def _apply_lighting_effect(self, sdf_data: np.ndarray, angle: float, 
                              intensity: float, ambient: float) -> Optional[np.ndarray]:
        """应用光照效果 - 使用shader方式的SDF光照算法"""
        try:
            # 角度范围：-180到180度
            # 将角度映射到0-1范围：-180度=0, 0度=0.5, 180度=1
            light_param = abs(angle / 180.0)

            # 根据角度决定SDF采样方式
            if angle <= 0:
                # 角度<=0时，对SDF进行左右镜像反转
                sdf_sample = np.fliplr(sdf_data)
            else:
                # 0到180度正常比对
                sdf_sample = sdf_data

            # 使用step函数进行比较：light_param < sdf_sample
            shadow_mask = np.where(sdf_sample > light_param, 1.0, 0.0)

            # 直接使用shadow_mask作为结果（纯黑白显示）
            result = shadow_mask

            # 转换为可显示的图像 (0-255)
            result_normalized = np.clip(result * 255, 0, 255).astype(np.uint8)

            # 转换为RGB
            if len(result_normalized.shape) == 2:
                result_rgb = np.stack([result_normalized] * 3, axis=-1)
            else:
                result_rgb = result_normalized

            return result_rgb

        except Exception as e:
            print(f"❌ 应用光照效果失败: {e}")
            return None

    def _numpy_to_pixmap(self, image_array: np.ndarray) -> QPixmap:
        """将numpy数组转换为QPixmap"""
        try:
            # 确保数据类型正确
            if image_array.dtype != np.uint8:
                image_array = np.clip(image_array, 0, 255).astype(np.uint8)

            if len(image_array.shape) == 3:
                # 彩色图像
                height, width, channels = image_array.shape
                if channels == 3:
                    # RGB图像
                    q_image = QImage(image_array.data, width, height, width * 3, QImage.Format.Format_RGB888)
                elif channels == 4:
                    # RGBA图像
                    q_image = QImage(image_array.data, width, height, width * 4, QImage.Format.Format_RGBA8888)
                else:
                    return QPixmap()
            elif len(image_array.shape) == 2:
                # 灰度图像
                height, width = image_array.shape
                q_image = QImage(image_array.data, width, height, width, QImage.Format.Format_Grayscale8)
            else:
                return QPixmap()

            return QPixmap.fromImage(q_image)

        except Exception as e:
            print(f"❌ numpy转QPixmap失败: {e}")
            return QPixmap()
