#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
预览组件 - 重构后的简化版本

显示SDF结果和实时预览，职责明确：
- 协调预览图像组件和控制组件
- 处理SDF数据转换和显示
- 管理光照效果预览
"""

from typing import Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from .preview_image_widget import PreviewImageWidget
from .preview_controls import PreviewControlPanel


class PreviewWidget(QWidget):
    """SDF预览组件 - 重构后的简化版本"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sdf_result = None
        
        # 预览图像组件将在_init_ui中创建
        self.sdf_preview_image = None
        self.lighting_preview_image = None
        self.control_panel = None

        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(5)

        # 控制面板
        self.control_panel = PreviewControlPanel()
        layout.addWidget(self.control_panel)

        # 预览区域 - 使用标签页
        preview_tabs = self._create_preview_tabs()
        layout.addWidget(preview_tabs)

    def _create_preview_tabs(self) -> QWidget:
        """创建预览标签页"""
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #CCCCCC;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F5F5F5;
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #CCCCCC;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
        """)

        # SDF预览标签页
        sdf_area = self._create_sdf_preview_area()
        tab_widget.addTab(sdf_area, "原始SDF")

        # 光照效果预览标签页
        lighting_area = self._create_lighting_preview_area()
        tab_widget.addTab(lighting_area, "光照效果")

        return tab_widget

    def _create_sdf_preview_area(self) -> QWidget:
        """创建SDF预览区域"""
        area = QWidget()
        layout = QVBoxLayout(area)
        layout.setContentsMargins(3, 3, 3, 3)

        # SDF预览图像
        self.sdf_preview_image = PreviewImageWidget()
        layout.addWidget(self.sdf_preview_image)

        return area

    def _create_lighting_preview_area(self) -> QWidget:
        """创建光照效果预览区域"""
        area = QWidget()
        layout = QVBoxLayout(area)
        layout.setContentsMargins(3, 3, 3, 3)

        # 光照预览图像
        self.lighting_preview_image = PreviewImageWidget()
        layout.addWidget(self.lighting_preview_image)

        return area

    def _connect_signals(self):
        """连接信号"""
        if self.control_panel:
            # 光照控制信号
            self.control_panel.angle_changed.connect(self._on_angle_changed)
            self.control_panel.intensity_changed.connect(self._on_intensity_changed)
            self.control_panel.ambient_changed.connect(self._on_ambient_changed)
            
            # 视图控制信号
            self.control_panel.fit_to_window.connect(self._on_fit_window)
            self.control_panel.actual_size.connect(self._on_actual_size)
            self.control_panel.reset_view.connect(self._on_reset_view)
            self.control_panel.zoom_changed.connect(self._on_zoom_changed)

        # 预览图像缩放信号
        if self.sdf_preview_image:
            self.sdf_preview_image.zoom_changed.connect(self._on_preview_zoom_changed)
        if self.lighting_preview_image:
            self.lighting_preview_image.zoom_changed.connect(self._on_preview_zoom_changed)
    
    def set_sdf_result(self, sdf_result):
        """设置SDF结果"""
        print(f"🔧 设置SDF结果: 类型={type(sdf_result)}")

        self.sdf_result = sdf_result

        # 更新原始SDF预览
        if isinstance(sdf_result, QPixmap):
            # 如果是QPixmap，直接显示
            print("📷 显示QPixmap到原始SDF预览")
            if self.sdf_preview_image:
                self.sdf_preview_image.set_pixmap(sdf_result)
        else:
            # 如果是numpy数组，转换后显示
            if hasattr(sdf_result, 'shape') and self.sdf_preview_image:
                print(f"🔢 转换numpy数组到原始SDF预览: 形状={sdf_result.shape}")
                pixmap = self._numpy_to_pixmap(sdf_result)
                if pixmap:
                    self.sdf_preview_image.set_pixmap(pixmap)
                    print("✅ 原始SDF预览更新成功")
                else:
                    print("❌ 转换QPixmap失败")

        # 更新光照效果预览
        print("🔆 开始更新光照效果预览")
        self._update_lighting_preview()

    def clear(self):
        """清空预览"""
        self.sdf_result = None
        if self.sdf_preview_image:
            self.sdf_preview_image.clear()
        if self.lighting_preview_image:
            self.lighting_preview_image.clear()

    def reset_view(self):
        """重置视图"""
        if self.control_panel:
            self.control_panel.lighting_control.set_angle(0)
        if self.sdf_preview_image:
            self.sdf_preview_image.reset_view()
        if self.lighting_preview_image:
            self.lighting_preview_image.reset_view()

    def fit_to_window(self):
        """适应窗口大小"""
        if self.sdf_preview_image:
            self.sdf_preview_image.fit_to_window()
        if self.lighting_preview_image:
            self.lighting_preview_image.fit_to_window()

    def actual_size(self):
        """显示实际大小"""
        if self.sdf_preview_image:
            self.sdf_preview_image.actual_size()
        if self.lighting_preview_image:
            self.lighting_preview_image.actual_size()

    def _on_angle_changed(self, value):
        """角度变化处理"""
        if self.control_panel:
            self.control_panel.update_angle_display(value)
        self._update_lighting_preview()

    def _on_intensity_changed(self, value):
        """光照强度变化处理"""
        if self.control_panel:
            self.control_panel.update_intensity_display(value)
        self._update_lighting_preview()

    def _on_ambient_changed(self, value):
        """环境光变化处理"""
        if self.control_panel:
            self.control_panel.update_ambient_display(value)
        self._update_lighting_preview()
    
    def _on_zoom_changed(self, value):
        """缩放变化处理"""
        if self.control_panel:
            self.control_panel.update_zoom_display(value)
        
        zoom_factor = value / 100.0
        # 同时缩放两个预览区域
        if self.sdf_preview_image:
            self.sdf_preview_image.set_zoom(zoom_factor)
        if self.lighting_preview_image:
            self.lighting_preview_image.set_zoom(zoom_factor)

    def _on_fit_window(self):
        """适应窗口按钮处理"""
        self.fit_to_window()

    def _on_actual_size(self):
        """实际大小按钮处理"""
        self.actual_size()

    def _on_reset_view(self):
        """重置视图按钮处理"""
        self.reset_view()

    def _on_preview_zoom_changed(self, zoom_factor):
        """预览图像缩放改变"""
        if self.control_panel:
            self.control_panel.set_zoom_factor(zoom_factor)

    def _update_lighting_preview(self):
        """更新光照效果预览"""
        if not self.sdf_result or not self.lighting_preview_image:
            return

        try:
            # 如果sdf_result是numpy数组，使用SDF生成器的预览功能
            if hasattr(self.sdf_result, 'shape'):
                print(f"🔢 处理numpy数组: 形状={self.sdf_result.shape}")

                try:
                    from ..core.sdf_generator import SDFGenerator
                except ImportError:
                    # 如果相对导入失败，尝试绝对导入
                    import sys
                    from pathlib import Path
                    sys.path.insert(0, str(Path(__file__).parent.parent))
                    from core.sdf_generator import SDFGenerator
                
                generator = SDFGenerator()

                # 获取当前光照参数
                if self.control_panel:
                    params = self.control_panel.get_lighting_params()
                    light_angle = params['angle']
                    lighting_intensity = params['intensity']
                    ambient_light = params['ambient']
                else:
                    light_angle = 0
                    lighting_intensity = 1.0
                    ambient_light = 0.3

                print(f"🔆 光照参数: 角度={light_angle}°, 强度={lighting_intensity:.1f}, 环境光={ambient_light:.1f}")

                # 生成光照预览效果
                lighting_result = generator.preview_lighting(
                    self.sdf_result,
                    light_angle,
                    lighting_intensity,
                    ambient_light
                )

                if lighting_result is not None:
                    # 转换为QPixmap并显示
                    lighting_pixmap = self._numpy_to_pixmap(lighting_result)
                    if lighting_pixmap:
                        self.lighting_preview_image.set_pixmap(lighting_pixmap)
                        print("✅ 光照效果预览更新成功")
                    else:
                        print("❌ 光照效果转换QPixmap失败")
                else:
                    print("❌ 光照效果生成失败")

        except Exception as e:
            print(f"❌ 更新光照预览失败: {e}")

    def _numpy_to_pixmap(self, numpy_array) -> QPixmap:
        """将numpy数组转换为QPixmap"""
        try:
            try:
                from ..utils.image_utils import ImageUtils
            except ImportError:
                # 如果相对导入失败，尝试绝对导入
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from utils.image_utils import ImageUtils

            # 确保数据在[0,1]范围内
            normalized_data = numpy_array.copy()
            if normalized_data.max() > 1.0 or normalized_data.min() < 0.0:
                normalized_data = (normalized_data - normalized_data.min()) / (normalized_data.max() - normalized_data.min())

            # 转换为PIL图像
            pil_image = ImageUtils.numpy_to_pil(normalized_data)
            
            # 转换为QPixmap
            return ImageUtils.pil_to_qpixmap(pil_image)

        except Exception as e:
            print(f"❌ numpy转QPixmap失败: {e}")
            return QPixmap()
