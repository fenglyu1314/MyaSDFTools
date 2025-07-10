#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
可缩放拖拽的图像预览组件

支持功能：
- 鼠标滚轮缩放
- 鼠标拖拽移动
- 适应窗口大小
- 实际大小显示
- 重置视图
"""

from typing import Optional
from PySide6.QtWidgets import QLabel, QScrollArea, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPixmap, QWheelEvent, QMouseEvent, QPaintEvent, QPainter

class ZoomableImageLabel(QLabel):
    """支持缩放拖拽的图像标签"""
    
    # 信号定义
    zoom_changed = Signal(float)  # 缩放比例改变
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 缩放相关
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        # 拖拽相关
        self.dragging = False
        self.last_pan_point = QPoint()
        self.image_offset = QPoint(0, 0)
        
        # 图像相关
        self.original_pixmap = None
        self.scaled_pixmap = None
        
        # 设置属性
        self.setMinimumSize(100, 100)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 1px solid #CCCCCC;
                background-color: #F5F5F5;
            }
        """)
        
        # 启用鼠标跟踪
        self.setMouseTracking(True)
    
    def set_image(self, pixmap: QPixmap):
        """设置图像"""
        if pixmap.isNull():
            self.original_pixmap = None
            self.scaled_pixmap = None
            self.clear()
            return
        
        self.original_pixmap = pixmap
        self.zoom_factor = 1.0
        self.image_offset = QPoint(0, 0)
        self._update_display()
    
    def _update_display(self):
        """更新显示"""
        if not self.original_pixmap:
            return
        
        # 计算缩放后的尺寸
        new_size = self.original_pixmap.size() * self.zoom_factor
        
        # 缩放图像
        self.scaled_pixmap = self.original_pixmap.scaled(
            new_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # 更新显示
        self.update()
        
        # 发送缩放改变信号
        self.zoom_changed.emit(self.zoom_factor)
    
    def paintEvent(self, event: QPaintEvent):
        """绘制事件"""
        if not self.scaled_pixmap:
            super().paintEvent(event)
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 计算绘制位置
        widget_rect = self.rect()
        pixmap_rect = self.scaled_pixmap.rect()
        
        # 居中位置 + 偏移
        x = (widget_rect.width() - pixmap_rect.width()) // 2 + self.image_offset.x()
        y = (widget_rect.height() - pixmap_rect.height()) // 2 + self.image_offset.y()
        
        # 绘制图像
        painter.drawPixmap(x, y, self.scaled_pixmap)
    
    def wheelEvent(self, event: QWheelEvent):
        """鼠标滚轮事件 - 缩放"""
        if not self.original_pixmap:
            return
        
        # 计算缩放因子
        delta = event.angleDelta().y()
        zoom_in = delta > 0
        
        # 缩放步长
        zoom_step = 0.1
        if zoom_in:
            new_zoom = self.zoom_factor * (1 + zoom_step)
        else:
            new_zoom = self.zoom_factor * (1 - zoom_step)
        
        # 限制缩放范围
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))
        
        if new_zoom != self.zoom_factor:
            self.zoom_factor = new_zoom
            self._update_display()
        
        event.accept()
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件 - 开始拖拽"""
        if event.button() == Qt.LeftButton and self.scaled_pixmap:
            self.dragging = True
            self.last_pan_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件 - 拖拽"""
        if self.dragging and self.scaled_pixmap:
            # 计算移动距离
            delta = event.pos() - self.last_pan_point
            self.image_offset += delta
            self.last_pan_point = event.pos()
            
            # 更新显示
            self.update()
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件 - 结束拖拽"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.ArrowCursor)
        
        super().mouseReleaseEvent(event)
    
    def fit_to_window(self):
        """适应窗口大小"""
        if not self.original_pixmap:
            return
        
        # 计算适应窗口的缩放比例
        widget_size = self.size()
        pixmap_size = self.original_pixmap.size()
        
        scale_x = widget_size.width() / pixmap_size.width()
        scale_y = widget_size.height() / pixmap_size.height()
        
        # 选择较小的缩放比例以确保完全显示
        self.zoom_factor = min(scale_x, scale_y) * 0.9  # 留一点边距
        self.zoom_factor = max(self.min_zoom, min(self.max_zoom, self.zoom_factor))
        
        # 重置偏移
        self.image_offset = QPoint(0, 0)
        
        self._update_display()
    
    def actual_size(self):
        """显示实际大小"""
        if not self.original_pixmap:
            return
        
        self.zoom_factor = 1.0
        self.image_offset = QPoint(0, 0)
        self._update_display()
    
    def reset_view(self):
        """重置视图"""
        if not self.original_pixmap:
            return
        
        self.zoom_factor = 1.0
        self.image_offset = QPoint(0, 0)
        self._update_display()
    
    def get_zoom_factor(self) -> float:
        """获取当前缩放比例"""
        return self.zoom_factor
    
    def set_zoom_factor(self, zoom: float):
        """设置缩放比例"""
        zoom = max(self.min_zoom, min(self.max_zoom, zoom))
        if zoom != self.zoom_factor:
            self.zoom_factor = zoom
            self._update_display()


class ZoomableImageWidget(QWidget):
    """可缩放图像组件容器"""
    
    # 信号定义
    zoom_changed = Signal(float)
    
    def __init__(self, parent=None, auto_fit=True):
        super().__init__(parent)
        self.auto_fit = auto_fit  # 是否自动适应窗口

        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建可缩放的图像标签
        self.image_label = ZoomableImageLabel()
        self.image_label.zoom_changed.connect(self.zoom_changed.emit)
        
        layout.addWidget(self.image_label)
    
    def set_image(self, pixmap: QPixmap):
        """设置图像"""
        self.image_label.set_image(pixmap)
        # 如果启用自动适应，设置图像后自动适应窗口
        if self.auto_fit and not pixmap.isNull():
            self.fit_to_window()
    
    def fit_to_window(self):
        """适应窗口大小"""
        self.image_label.fit_to_window()
    
    def actual_size(self):
        """显示实际大小"""
        self.image_label.actual_size()
    
    def reset_view(self):
        """重置视图"""
        self.image_label.reset_view()
    
    def get_zoom_factor(self) -> float:
        """获取当前缩放比例"""
        return self.image_label.get_zoom_factor()
    
    def set_zoom_factor(self, zoom: float):
        """设置缩放比例"""
        self.image_label.set_zoom_factor(zoom)
