#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SDF预览处理器

专门负责SDF预览的更新和管理：
- 单张SDF预览更新
- 合并SDF预览更新
- SDF数据转换
"""

import numpy as np
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QObject
from PySide6.QtGui import QPixmap, QImage


class SDFPreviewHandler(QObject):
    """SDF预览处理器 - 专门处理SDF预览相关逻辑"""

    def __init__(self, parent=None):
        super().__init__(parent)

    def update_single_sdf_card_preview(self, components: dict, image_path: str, 
                                     sdf_result: np.ndarray, computation_time: float):
        """更新单张SDF卡片预览"""
        try:
            sdf_cards_container = components.get('sdf_cards_container')
            if not sdf_cards_container:
                print("❌ 找不到SDF卡片容器")
                return
            
            # 找到对应的SDF卡片
            for card in sdf_cards_container.sdf_cards:
                if card.get_image_path() == image_path:
                    # 转换为预览图像
                    preview_image = self._sdf_to_preview_image(sdf_result)
                    if preview_image is not None:
                        pixmap = self._numpy_to_pixmap(preview_image)
                        if not pixmap.isNull():
                            card.set_sdf_preview(pixmap)
                            card.set_generation_time(computation_time)
                            card.set_status("completed")
                            print(f"✅ 实时更新SDF卡片: {Path(image_path).name}")
                            break
                        else:
                            print(f"❌ SDF卡片预览转换失败: {image_path}")
                    else:
                        print(f"❌ SDF卡片预览生成失败: {image_path}")
                    break
            else:
                print(f"❌ 找不到对应的SDF卡片: {image_path}")
                
        except Exception as e:
            print(f"❌ 更新单张SDF卡片预览失败: {e}")

    def update_merged_sdf_preview(self, components: dict, sdf_result: np.ndarray):
        """更新合并SDF预览"""
        try:
            preview_widget = components.get('merged_sdf_preview')
            if not preview_widget:
                print("❌ 找不到合并SDF预览组件")
                return

            print(f"🔧 更新合并SDF预览: 组件类型={type(preview_widget)}")

            # 转换SDF为可显示的图像
            preview_image = self._sdf_to_preview_image(sdf_result)
            if preview_image is not None:
                pixmap = self._numpy_to_pixmap(preview_image)
                if not pixmap.isNull():
                    # ZoomableImageWidget使用set_image方法，会自动适应窗口
                    if hasattr(preview_widget, 'set_image'):
                        preview_widget.set_image(pixmap)
                        print("✅ 合并SDF预览更新成功（自动适应窗口）")
                    else:
                        print(f"❌ 预览组件没有set_image方法: {dir(preview_widget)}")
                else:
                    print("❌ SDF预览转换QPixmap失败")
            else:
                print("❌ SDF预览数据转换失败")
        except Exception as e:
            print(f"❌ 更新SDF预览失败: {e}")
            import traceback
            traceback.print_exc()

    def set_all_sdf_cards_completed(self, components: dict):
        """设置所有SDF卡片状态为完成"""
        try:
            sdf_cards_container = components.get('sdf_cards_container')
            if sdf_cards_container:
                sdf_cards_container.set_all_status("completed")
                print(f"✅ 设置所有SDF卡片状态为完成")
        except Exception as e:
            print(f"❌ 设置SDF卡片状态失败: {e}")

    def _sdf_to_preview_image(self, sdf_data: np.ndarray) -> Optional[np.ndarray]:
        """将SDF数据转换为预览图像"""
        try:
            if sdf_data is None or sdf_data.size == 0:
                return None

            # 归一化到0-255范围
            normalized = ((sdf_data - sdf_data.min()) / 
                         (sdf_data.max() - sdf_data.min()) * 255).astype(np.uint8)
            
            return normalized

        except Exception as e:
            print(f"❌ SDF转换预览图像失败: {e}")
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
