#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
预览图像组件

基础的图像显示组件，支持：
- 图像显示和缩放
- 鼠标拖拽和滚轮缩放
- 网格显示
- 自适应窗口大小
"""

import math
from typing import Optional

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor


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
        self.fit_to_window_mode = True  # 自适应窗口大小

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
        if self.fit_to_window_mode and pixmap:
            self._fit_to_window()

        self._update_display()

    def set_zoom(self, zoom: float):
        """设置缩放比例"""
        self.zoom_factor = max(0.1, min(5.0, zoom))
        self.fit_to_window_mode = False  # 手动缩放时禁用自适应
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
        self.fit_to_window_mode = True

        if self.original_pixmap:
            self._fit_to_window()

        self._update_display()

    def fit_to_window(self):
        """适应窗口大小"""
        self.fit_to_window_mode = True
        if self.original_pixmap:
            self._fit_to_window()
            self._update_display()

    def actual_size(self):
        """显示实际大小"""
        self.zoom_factor = 1.0
        self.fit_to_window_mode = False
        self.offset_x = 0
        self.offset_y = 0
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

        # 发射缩放改变信号
        self.zoom_changed.emit(self.zoom_factor)

    def _draw_grid(self, pixmap: QPixmap) -> QPixmap:
        """在图像上绘制网格"""
        grid_pixmap = QPixmap(pixmap)
        painter = QPainter(grid_pixmap)
        
        # 设置网格样式
        pen = QPen(QColor(200, 200, 200, 128))  # 半透明灰色
        pen.setWidth(1)
        painter.setPen(pen)

        # 网格间距
        grid_size = max(20, int(20 * self.zoom_factor))

        # 绘制垂直线
        for x in range(0, pixmap.width(), grid_size):
            painter.drawLine(x, 0, x, pixmap.height())

        # 绘制水平线
        for y in range(0, pixmap.height(), grid_size):
            painter.drawLine(0, y, pixmap.width(), y)

        painter.end()
        return grid_pixmap

    def mousePressEvent(self, event):
        """鼠标按下事件 - 开始拖拽"""
        if event.button() == Qt.LeftButton and self.original_pixmap:
            self.last_mouse_pos = event.position()
            self.dragging = True
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖拽图像"""
        if self.dragging and self.last_mouse_pos:
            # 计算鼠标移动距离
            delta = event.position() - self.last_mouse_pos
            
            # 更新偏移量
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            
            # 更新鼠标位置
            self.last_mouse_pos = event.position()
            
            # 禁用自适应模式
            self.fit_to_window_mode = False
            
            # 更新显示
            self._update_display()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件 - 结束拖拽"""
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
                self.fit_to_window_mode = False  # 手动缩放时禁用自适应

                # 更新显示
                self._update_display()

    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)

        # 如果启用自适应，重新计算缩放
        if self.fit_to_window_mode and self.original_pixmap:
            self._fit_to_window()
            self._update_display()

    def clear(self):
        """清空显示"""
        self.original_pixmap = None
        self.current_pixmap = None
        self._show_placeholder()
