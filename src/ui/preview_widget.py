#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
预览组件

显示SDF结果和实时预览，支持：
- SDF图像显示
- 光照角度控制
- 缩放和平移
- 网格显示
"""

import math
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QCheckBox, QPushButton, QFrame, QScrollArea, QSizePolicy, QSplitter, QTabWidget
)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont

class PreviewImageWidget(QLabel):
    """预览图像显示组件"""

    zoom_changed = Signal(float)  # 缩放改变信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 1px solid #CCCCCC;
                background-color: #F5F5F5;
            }
        """)

        # 预览参数
        self.zoom_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.show_grid = False
        self.fit_to_window = True  # 自适应窗口大小

        # 图像数据
        self.original_pixmap: Optional[QPixmap] = None
        self.current_pixmap: Optional[QPixmap] = None

        # 鼠标交互
        self.last_mouse_pos = None
        self.dragging = False

        # 启用鼠标跟踪和事件
        self.setMouseTracking(True)

        self._show_placeholder()
    
    def _show_placeholder(self):
        """显示占位符"""
        self.setText("SDF预览\n\n生成SDF后将在此显示结果")
        self.setStyleSheet(self.styleSheet() + """
            QLabel {
                color: #999999;
                font-size: 16px;
            }
        """)
    
    def set_pixmap(self, pixmap: QPixmap):
        """设置显示的图像"""
        self.original_pixmap = pixmap
        self.current_pixmap = pixmap

        # 重置视图参数
        self.offset_x = 0
        self.offset_y = 0

        # 如果启用自适应，计算合适的缩放比例
        if self.fit_to_window and pixmap:
            self._fit_to_window()

        self._update_display()

    def set_zoom(self, zoom: float):
        """设置缩放比例"""
        self.zoom_factor = max(0.1, min(5.0, zoom))
        self.fit_to_window = False  # 手动缩放时禁用自适应
        self._update_display()

    def set_grid_visible(self, visible: bool):
        """设置网格显示"""
        self.show_grid = visible
        self._update_display()

    def reset_view(self):
        """重置视图"""
        self.zoom_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.fit_to_window = True

        if self.original_pixmap:
            self._fit_to_window()

        self._update_display()

    def fit_to_window(self):
        """适应窗口大小"""
        self.fit_to_window = True
        if self.original_pixmap:
            self._fit_to_window()
            self._update_display()

    def _fit_to_window(self):
        """计算适应窗口的缩放比例"""
        if not self.original_pixmap:
            return

        # 获取可用空间（减去边距）
        available_width = self.width() - 20
        available_height = self.height() - 20

        # 计算缩放比例
        scale_x = available_width / self.original_pixmap.width()
        scale_y = available_height / self.original_pixmap.height()

        # 使用较小的缩放比例以确保图像完全可见
        self.zoom_factor = min(scale_x, scale_y, 1.0)  # 不超过100%
    
    def _update_display(self):
        """更新显示"""
        if not self.original_pixmap:
            return

        # 应用缩放
        scaled_size = self.original_pixmap.size() * self.zoom_factor
        scaled_pixmap = self.original_pixmap.scaled(
            scaled_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        # 如果需要显示网格，绘制网格
        if self.show_grid:
            scaled_pixmap = self._draw_grid(scaled_pixmap)

        # 创建显示区域
        display_pixmap = QPixmap(self.size())
        display_pixmap.fill(QColor(245, 245, 245))  # 背景色

        painter = QPainter(display_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 计算图像在组件中的位置
        widget_center_x = self.width() / 2
        widget_center_y = self.height() / 2

        image_x = widget_center_x - scaled_pixmap.width() / 2 + self.offset_x
        image_y = widget_center_y - scaled_pixmap.height() / 2 + self.offset_y

        # 绘制图像
        painter.drawPixmap(int(image_x), int(image_y), scaled_pixmap)

        painter.end()

        self.current_pixmap = display_pixmap
        super().setPixmap(display_pixmap)
    
    def _draw_grid(self, pixmap: QPixmap) -> QPixmap:
        """在图像上绘制网格"""
        result = QPixmap(pixmap)
        painter = QPainter(result)
        
        # 设置网格样式
        pen = QPen(QColor(255, 255, 255, 128))
        pen.setWidth(1)
        painter.setPen(pen)
        
        # 绘制网格线
        grid_size = 20 * self.zoom_factor
        width, height = result.width(), result.height()
        
        # 垂直线
        x = 0
        while x < width:
            painter.drawLine(int(x), 0, int(x), height)
            x += grid_size
        
        # 水平线
        y = 0
        while y < height:
            painter.drawLine(0, int(y), width, int(y))
            y += grid_size
        
        painter.end()
        return result

    # 鼠标事件处理
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton and self.original_pixmap:
            self.last_mouse_pos = event.position()
            self.dragging = True
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.dragging and self.last_mouse_pos:
            # 计算鼠标移动距离
            delta = event.position() - self.last_mouse_pos

            # 更新偏移量
            self.offset_x += delta.x()
            self.offset_y += delta.y()

            # 更新显示
            self._update_display()

            # 更新鼠标位置
            self.last_mouse_pos = event.position()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.ArrowCursor)
            self.last_mouse_pos = None

    def wheelEvent(self, event):
        """鼠标滚轮事件 - 缩放"""
        if self.original_pixmap:
            # 获取滚轮滚动方向
            delta = event.angleDelta().y()

            # 计算缩放因子
            zoom_in = delta > 0
            zoom_factor = 1.1 if zoom_in else 0.9

            # 获取鼠标位置
            mouse_pos = event.position()

            # 计算缩放前鼠标在图像中的相对位置
            old_zoom = self.zoom_factor
            new_zoom = max(0.1, min(5.0, old_zoom * zoom_factor))

            if new_zoom != old_zoom:
                # 计算缩放中心偏移
                zoom_ratio = new_zoom / old_zoom

                # 调整偏移量以保持鼠标位置不变
                widget_center_x = self.width() / 2
                widget_center_y = self.height() / 2

                mouse_offset_x = mouse_pos.x() - widget_center_x
                mouse_offset_y = mouse_pos.y() - widget_center_y

                self.offset_x = (self.offset_x - mouse_offset_x) * zoom_ratio + mouse_offset_x
                self.offset_y = (self.offset_y - mouse_offset_y) * zoom_ratio + mouse_offset_y

                # 更新缩放
                self.zoom_factor = new_zoom
                self.fit_to_window = False  # 手动缩放时禁用自适应

                # 发射缩放改变信号
                self.zoom_changed.emit(self.zoom_factor)

                # 更新显示
                self._update_display()

    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)

        # 如果启用自适应，重新计算缩放
        if self.fit_to_window and self.original_pixmap:
            self._fit_to_window()
            self._update_display()

class PreviewWidget(QWidget):
    """SDF预览组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sdf_result = None
        self.light_angle = 0.0
        self.lighting_intensity = 1.0
        self.ambient_light = 0.3

        # 预览图像组件将在_init_ui中创建
        self.sdf_preview_image = None
        self.lighting_preview_image = None

        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)  # 减少边距
        layout.setSpacing(5)  # 减少间距

        # 控制面板
        control_panel = self._create_control_panel()
        layout.addWidget(control_panel)

        # 预览区域 - 使用标签页替代分割器
        preview_tabs = self._create_preview_tabs()
        layout.addWidget(preview_tabs)
    
    def _create_control_panel(self) -> QWidget:
        """创建简化的控制面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        panel.setMaximumHeight(60)  # 从120px减少到60px

        layout = QHBoxLayout(panel)  # 改为水平布局
        layout.setContentsMargins(8, 5, 8, 5)  # 减少边距
        layout.setSpacing(10)

        # 光照角度控制 - 紧凑版
        angle_label = QLabel("光照:")
        angle_label.setMinimumWidth(40)  # 减少宽度
        layout.addWidget(angle_label)

        self.angle_slider = QSlider(Qt.Horizontal)
        self.angle_slider.setRange(0, 360)
        self.angle_slider.setValue(0)
        self.angle_slider.setMaximumWidth(150)  # 限制宽度
        layout.addWidget(self.angle_slider)

        self.angle_value_label = QLabel("0°")
        self.angle_value_label.setMinimumWidth(30)  # 减少宽度
        self.angle_value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.angle_value_label)

        # 光照强度控制 - 紧凑版
        intensity_label = QLabel("强度:")
        intensity_label.setMinimumWidth(40)
        layout.addWidget(intensity_label)

        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(0, 200)  # 0.0 到 2.0
        self.intensity_slider.setValue(100)  # 1.0
        self.intensity_slider.setMaximumWidth(100)  # 限制宽度
        layout.addWidget(self.intensity_slider)

        self.intensity_value_label = QLabel("1.0")
        self.intensity_value_label.setMinimumWidth(30)
        self.intensity_value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.intensity_value_label)

        # 环境光控制 - 紧凑版
        ambient_label = QLabel("环境:")
        ambient_label.setMinimumWidth(40)
        layout.addWidget(ambient_label)

        self.ambient_slider = QSlider(Qt.Horizontal)
        self.ambient_slider.setRange(0, 100)  # 0.0 到 1.0
        self.ambient_slider.setValue(30)  # 0.3
        self.ambient_slider.setMaximumWidth(100)  # 限制宽度
        layout.addWidget(self.ambient_slider)

        self.ambient_value_label = QLabel("0.3")
        self.ambient_value_label.setMinimumWidth(30)
        self.ambient_value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.ambient_value_label)

        # 添加弹性空间
        layout.addStretch()
        
        return panel
    
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
        area = QWidget()  # 移除边框

        layout = QVBoxLayout(area)
        layout.setContentsMargins(3, 3, 3, 3)  # 减少边距

        # SDF预览图像 - 直接添加，无需滚动区域
        self.sdf_preview_image = PreviewImageWidget()
        layout.addWidget(self.sdf_preview_image)

        return area

    def _create_lighting_preview_area(self) -> QWidget:
        """创建光照效果预览区域"""
        area = QWidget()  # 移除边框

        layout = QVBoxLayout(area)
        layout.setContentsMargins(3, 3, 3, 3)  # 减少边距

        # 光照预览图像 - 直接添加，无需滚动区域
        self.lighting_preview_image = PreviewImageWidget()
        layout.addWidget(self.lighting_preview_image)

        return area


    
    def _connect_signals(self):
        """连接信号"""
        # 角度滑竿
        self.angle_slider.valueChanged.connect(self._on_angle_changed)

        # 光照控制滑竿
        self.intensity_slider.valueChanged.connect(self._on_intensity_changed)
        self.ambient_slider.valueChanged.connect(self._on_ambient_changed)

        # 连接缩放信号（如果预览图像已创建）
        # 注意：简化版本中移除了缩放滑竿，这里不需要连接信号
    
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
    
    def _create_mock_sdf_image(self):
        """创建模拟的SDF图像"""
        # 创建一个简单的渐变图像作为SDF预览
        pixmap = QPixmap(512, 512)
        pixmap.fill(QColor(128, 128, 128))
        
        painter = QPainter(pixmap)
        
        # 绘制一个简单的圆形SDF效果
        center_x, center_y = 256, 256
        max_radius = 200
        
        for y in range(512):
            for x in range(512):
                dx = x - center_x
                dy = y - center_y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance <= max_radius:
                    # 内部：从中心到边缘的渐变
                    value = int(255 * (1.0 - distance / max_radius))
                    painter.setPen(QColor(value, value, value))
                    painter.drawPoint(x, y)
        
        painter.end()
        
        if self.sdf_preview_image:
            self.sdf_preview_image.set_pixmap(pixmap)

    def clear(self):
        """清空预览"""
        self.sdf_result = None
        if self.sdf_preview_image:
            self.sdf_preview_image.original_pixmap = None
            self.sdf_preview_image.current_pixmap = None
            self.sdf_preview_image._show_placeholder()
        if self.lighting_preview_image:
            self.lighting_preview_image.original_pixmap = None
            self.lighting_preview_image.current_pixmap = None
            self.lighting_preview_image._show_placeholder()

    def reset_view(self):
        """重置视图"""
        self.angle_slider.setValue(0)
        if self.sdf_preview_image:
            self.sdf_preview_image.reset_view()
        if self.lighting_preview_image:
            self.lighting_preview_image.reset_view()
    
    def _on_angle_changed(self, value):
        """角度变化处理"""
        self.light_angle = value

        # 添加方向提示
        direction_hint = self._get_direction_hint(value)
        self.angle_value_label.setText(f"{value}° ({direction_hint})")

        # 实时更新光照效果预览
        self._update_lighting_preview()

    def _get_direction_hint(self, angle: float) -> str:
        """获取角度对应的方向提示"""
        angle = angle % 360
        if angle < 22.5 or angle >= 337.5:
            return "右"
        elif angle < 67.5:
            return "右下"
        elif angle < 112.5:
            return "下"
        elif angle < 157.5:
            return "左下"
        elif angle < 202.5:
            return "左"
        elif angle < 247.5:
            return "左上"
        elif angle < 292.5:
            return "上"
        else:
            return "右上"

    def _on_intensity_changed(self, value):
        """光照强度变化处理"""
        intensity = value / 100.0  # 转换为0.0-2.0范围
        self.intensity_value_label.setText(f"{intensity:.1f}")
        self._update_lighting_preview()

    def _on_ambient_changed(self, value):
        """环境光变化处理"""
        ambient = value / 100.0  # 转换为0.0-1.0范围
        self.ambient_value_label.setText(f"{ambient:.1f}")
        self._update_lighting_preview()
    
    def _on_zoom_changed(self, value):
        """缩放变化处理"""
        zoom_factor = value / 100.0
        self.zoom_value_label.setText(f"{int(zoom_factor * 100)}%")
        # 同时缩放两个预览区域
        if self.sdf_preview_image:
            self.sdf_preview_image.set_zoom(zoom_factor)
        if self.lighting_preview_image:
            self.lighting_preview_image.set_zoom(zoom_factor)

    def _on_grid_toggled(self, checked):
        """网格显示切换 - 简化版本中暂时禁用"""
        # 简化版本中移除了网格控件
        pass

    def _on_fit_window(self):
        """适应窗口按钮处理"""
        if self.sdf_preview_image:
            self.sdf_preview_image.fit_to_window()
        if self.lighting_preview_image:
            self.lighting_preview_image.fit_to_window()

    def _on_actual_size(self):
        """实际大小按钮处理"""
        for preview_image in [self.sdf_preview_image, self.lighting_preview_image]:
            if preview_image:
                preview_image.zoom_factor = 1.0
                preview_image.fit_to_window = False
                preview_image.offset_x = 0
                preview_image.offset_y = 0
                preview_image._update_display()

        # 简化版本中移除了缩放滑竿
        pass

    def _on_reset_view(self):
        """重置视图按钮处理"""
        self.reset_view()

    def fit_to_window(self):
        """适应窗口大小"""
        if self.sdf_preview_image:
            self.sdf_preview_image.fit_to_window = True
            self.sdf_preview_image._fit_to_window()
        if self.lighting_preview_image:
            self.lighting_preview_image.fit_to_window = True
            self.lighting_preview_image._fit_to_window()

    def actual_size(self):
        """显示实际大小"""
        if self.sdf_preview_image:
            self.sdf_preview_image.set_zoom(1.0)
        if self.lighting_preview_image:
            self.lighting_preview_image.set_zoom(1.0)

    def _update_lighting_preview(self):
        """更新光照效果预览"""
        print(f"🔆 _update_lighting_preview 被调用")
        print(f"   SDF结果: {type(self.sdf_result) if self.sdf_result is not None else 'None'}")
        print(f"   光照预览图像: {'存在' if self.lighting_preview_image else '不存在'}")

        if self.sdf_result is None:
            print("⚠️ SDF结果为空，跳过光照预览更新")
            return

        if not self.lighting_preview_image:
            print("⚠️ 光照预览图像组件不存在，跳过更新")
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
                lighting_intensity = self.intensity_slider.value() / 100.0
                ambient_light = self.ambient_slider.value() / 100.0

                print(f"🔆 光照参数: 角度={self.light_angle}°, 强度={lighting_intensity:.1f}, 环境光={ambient_light:.1f}")

                # 生成光照预览效果
                lighting_result = generator.preview_lighting(
                    self.sdf_result,
                    self.light_angle,
                    lighting_intensity,
                    ambient_light
                )

                print(f"🎨 光照结果: 形状={lighting_result.shape}, 值域=[{lighting_result.min():.3f}, {lighting_result.max():.3f}]")

                # 转换为QPixmap并显示到光照预览区域
                pixmap = self._numpy_to_pixmap(lighting_result)
                if pixmap:
                    print(f"🖼️ 设置光照预览QPixmap: 大小={pixmap.size()}")
                    self.lighting_preview_image.set_pixmap(pixmap)
                    print(f"✅ 光照预览更新成功")
                else:
                    print(f"❌ 转换QPixmap失败")
            else:
                print(f"⚠️ SDF结果不是numpy数组: {type(self.sdf_result)}")
                # 如果是QPixmap，也尝试显示到光照预览区域
                if isinstance(self.sdf_result, QPixmap):
                    print("📷 直接显示QPixmap到光照预览区域")
                    self.lighting_preview_image.set_pixmap(self.sdf_result)

        except Exception as e:
            print(f"❌ 更新光照预览失败: {e}")
            import traceback
            traceback.print_exc()

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
            import io
            img_bytes = io.BytesIO()
            pil_image.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(img_bytes.getvalue())
            return pixmap

        except Exception as e:
            print(f"numpy转QPixmap失败: {e}")
            return None
