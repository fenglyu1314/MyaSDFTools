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
    QCheckBox, QPushButton, QFrame, QScrollArea, QSizePolicy
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
        
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 控制面板
        control_panel = self._create_control_panel()
        layout.addWidget(control_panel)
        
        # 预览区域
        preview_area = self._create_preview_area()
        layout.addWidget(preview_area)
    
    def _create_control_panel(self) -> QWidget:
        """创建控制面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        panel.setMaximumHeight(120)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # 光照角度控制
        angle_layout = QHBoxLayout()
        
        angle_label = QLabel("光照角度:")
        angle_label.setMinimumWidth(80)
        angle_layout.addWidget(angle_label)
        
        self.angle_slider = QSlider(Qt.Horizontal)
        self.angle_slider.setRange(0, 360)
        self.angle_slider.setValue(0)
        self.angle_slider.setTickPosition(QSlider.TicksBelow)
        self.angle_slider.setTickInterval(45)
        angle_layout.addWidget(self.angle_slider)
        
        self.angle_value_label = QLabel("0°")
        self.angle_value_label.setMinimumWidth(40)
        self.angle_value_label.setAlignment(Qt.AlignCenter)
        angle_layout.addWidget(self.angle_value_label)
        
        layout.addLayout(angle_layout)
        
        # 视图控制
        view_layout = QHBoxLayout()
        
        # 缩放控制
        zoom_label = QLabel("缩放:")
        zoom_label.setMinimumWidth(80)
        view_layout.addWidget(zoom_label)
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 500)  # 0.1x 到 5.0x
        self.zoom_slider.setValue(100)  # 1.0x
        view_layout.addWidget(self.zoom_slider)
        
        self.zoom_value_label = QLabel("100%")
        self.zoom_value_label.setMinimumWidth(50)
        self.zoom_value_label.setAlignment(Qt.AlignCenter)
        view_layout.addWidget(self.zoom_value_label)
        
        # 网格显示
        self.grid_checkbox = QCheckBox("显示网格")
        view_layout.addWidget(self.grid_checkbox)
        
        # 适应窗口按钮
        self.fit_window_btn = QPushButton("适应窗口")
        self.fit_window_btn.setMaximumWidth(80)
        view_layout.addWidget(self.fit_window_btn)

        # 实际大小按钮
        self.actual_size_btn = QPushButton("实际大小")
        self.actual_size_btn.setMaximumWidth(80)
        view_layout.addWidget(self.actual_size_btn)

        # 重置视图按钮
        self.reset_view_btn = QPushButton("重置视图")
        self.reset_view_btn.setMaximumWidth(80)
        view_layout.addWidget(self.reset_view_btn)
        
        layout.addLayout(view_layout)
        
        return panel
    
    def _create_preview_area(self) -> QWidget:
        """创建预览区域"""
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignCenter)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #CCCCCC;
                background-color: #FAFAFA;
            }
        """)
        
        # 预览图像组件
        self.preview_image = PreviewImageWidget()
        scroll_area.setWidget(self.preview_image)

        # 连接缩放信号
        self.preview_image.zoom_changed.connect(self.update_zoom_slider)
        
        return scroll_area
    
    def _connect_signals(self):
        """连接信号"""
        # 角度滑竿
        self.angle_slider.valueChanged.connect(self._on_angle_changed)
        
        # 缩放滑竿
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
        
        # 网格复选框
        self.grid_checkbox.toggled.connect(self._on_grid_toggled)
        
        # 视图控制按钮
        self.fit_window_btn.clicked.connect(self._on_fit_window)
        self.actual_size_btn.clicked.connect(self._on_actual_size)
        self.reset_view_btn.clicked.connect(self._on_reset_view)
    
    def set_sdf_result(self, sdf_result):
        """设置SDF结果"""
        self.sdf_result = sdf_result

        # 如果传入的是QPixmap，直接显示
        if isinstance(sdf_result, QPixmap):
            self.preview_image.set_pixmap(sdf_result)
        else:
            # 如果是numpy数组，转换为QPixmap
            try:
                from ..utils.image_utils import ImageUtils
                pil_image = ImageUtils.numpy_to_pil(sdf_result)

                # 转换为QPixmap
                import io
                img_bytes = io.BytesIO()
                pil_image.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                pixmap = QPixmap()
                pixmap.loadFromData(img_bytes.getvalue())
                self.preview_image.set_pixmap(pixmap)

            except Exception as e:
                print(f"转换SDF结果显示失败: {e}")
                # 如果转换失败，显示错误信息
                self.preview_image.setText("SDF显示错误\n\n请检查数据格式")
    
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
        
        self.preview_image.set_pixmap(pixmap)
    
    def clear(self):
        """清空预览"""
        self.sdf_result = None
        self.preview_image.original_pixmap = None
        self.preview_image.current_pixmap = None
        self.preview_image._show_placeholder()
    
    def reset_view(self):
        """重置视图"""
        self.angle_slider.setValue(0)
        self.zoom_slider.setValue(100)
        self.grid_checkbox.setChecked(False)
        self.preview_image.reset_view()
    
    def _on_angle_changed(self, value):
        """角度变化处理"""
        self.light_angle = value
        self.angle_value_label.setText(f"{value}°")
        
        # TODO: 根据角度更新SDF预览效果
        # 这里可以实现实时的光照效果预览
    
    def _on_zoom_changed(self, value):
        """缩放变化处理"""
        zoom_factor = value / 100.0
        self.zoom_value_label.setText(f"{int(zoom_factor * 100)}%")
        self.preview_image.set_zoom(zoom_factor)

    def update_zoom_slider(self, zoom_factor):
        """更新缩放滑竿显示"""
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(int(zoom_factor * 100))
        self.zoom_value_label.setText(f"{int(zoom_factor * 100)}%")
        self.zoom_slider.blockSignals(False)
    
    def _on_grid_toggled(self, checked):
        """网格显示切换"""
        self.preview_image.set_grid_visible(checked)
    
    def _on_fit_window(self):
        """适应窗口按钮处理"""
        self.preview_image.fit_to_window()

    def _on_actual_size(self):
        """实际大小按钮处理"""
        self.preview_image.zoom_factor = 1.0
        self.preview_image.fit_to_window = False
        self.preview_image.offset_x = 0
        self.preview_image.offset_y = 0
        self.preview_image._update_display()

        # 更新缩放滑竿
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(100)
        self.zoom_value_label.setText("100%")
        self.zoom_slider.blockSignals(False)

    def _on_reset_view(self):
        """重置视图按钮处理"""
        self.reset_view()
