#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
预览控制组件

提供预览相关的控制界面：
- 光照角度控制
- 光照强度控制
- 环境光控制
- 缩放控制
- 视图控制按钮
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal


class LightingControlWidget(QWidget):
    """光照控制组件"""
    
    angle_changed = Signal(int)
    intensity_changed = Signal(int)
    ambient_changed = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        # 光照角度控制
        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel("光照角度:"))
        
        self.angle_slider = QSlider(Qt.Horizontal)
        self.angle_slider.setRange(-180, 180)
        self.angle_slider.setValue(0)
        self.angle_slider.valueChanged.connect(self.angle_changed.emit)
        angle_layout.addWidget(self.angle_slider)
        
        self.angle_value_label = QLabel("0°")
        self.angle_value_label.setMinimumWidth(60)
        angle_layout.addWidget(self.angle_value_label)
        
        layout.addLayout(angle_layout)
        
        # 光照强度控制
        intensity_layout = QHBoxLayout()
        intensity_layout.addWidget(QLabel("光照强度:"))
        
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(0, 200)  # 0.0 - 2.0
        self.intensity_slider.setValue(100)  # 默认1.0
        self.intensity_slider.valueChanged.connect(self.intensity_changed.emit)
        intensity_layout.addWidget(self.intensity_slider)
        
        self.intensity_value_label = QLabel("1.0")
        self.intensity_value_label.setMinimumWidth(60)
        intensity_layout.addWidget(self.intensity_value_label)
        
        layout.addLayout(intensity_layout)
        
        # 环境光控制
        ambient_layout = QHBoxLayout()
        ambient_layout.addWidget(QLabel("环境光:"))
        
        self.ambient_slider = QSlider(Qt.Horizontal)
        self.ambient_slider.setRange(0, 100)  # 0.0 - 1.0
        self.ambient_slider.setValue(30)  # 默认0.3
        self.ambient_slider.valueChanged.connect(self.ambient_changed.emit)
        ambient_layout.addWidget(self.ambient_slider)
        
        self.ambient_value_label = QLabel("0.3")
        self.ambient_value_label.setMinimumWidth(60)
        ambient_layout.addWidget(self.ambient_value_label)
        
        layout.addLayout(ambient_layout)
    
    def get_angle(self) -> int:
        """获取光照角度"""
        return self.angle_slider.value()
    
    def get_intensity(self) -> float:
        """获取光照强度"""
        return self.intensity_slider.value() / 100.0
    
    def get_ambient(self) -> float:
        """获取环境光"""
        return self.ambient_slider.value() / 100.0
    
    def set_angle(self, angle: int):
        """设置光照角度"""
        self.angle_slider.setValue(angle)
    
    def set_intensity(self, intensity: float):
        """设置光照强度"""
        self.intensity_slider.setValue(int(intensity * 100))
    
    def set_ambient(self, ambient: float):
        """设置环境光"""
        self.ambient_slider.setValue(int(ambient * 100))


class ViewControlWidget(QWidget):
    """视图控制组件"""
    
    fit_to_window = Signal()
    actual_size = Signal()
    reset_view = Signal()
    zoom_changed = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        # 缩放控制
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("缩放:"))
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 500)  # 10% - 500%
        self.zoom_slider.setValue(100)  # 默认100%
        self.zoom_slider.valueChanged.connect(self.zoom_changed.emit)
        zoom_layout.addWidget(self.zoom_slider)
        
        self.zoom_value_label = QLabel("100%")
        self.zoom_value_label.setMinimumWidth(60)
        zoom_layout.addWidget(self.zoom_value_label)
        
        layout.addLayout(zoom_layout)
        
        # 视图控制按钮
        button_layout = QHBoxLayout()
        
        self.fit_btn = QPushButton("适应窗口")
        self.fit_btn.clicked.connect(self.fit_to_window.emit)
        button_layout.addWidget(self.fit_btn)
        
        self.actual_btn = QPushButton("实际大小")
        self.actual_btn.clicked.connect(self.actual_size.emit)
        button_layout.addWidget(self.actual_btn)
        
        self.reset_btn = QPushButton("重置视图")
        self.reset_btn.clicked.connect(self.reset_view.emit)
        button_layout.addWidget(self.reset_btn)
        
        layout.addLayout(button_layout)
    
    def get_zoom_factor(self) -> float:
        """获取缩放因子"""
        return self.zoom_slider.value() / 100.0
    
    def set_zoom_factor(self, factor: float):
        """设置缩放因子"""
        self.zoom_slider.setValue(int(factor * 100))
        self.zoom_value_label.setText(f"{int(factor * 100)}%")


class PreviewControlPanel(QWidget):
    """预览控制面板"""
    
    # 光照控制信号
    angle_changed = Signal(int)
    intensity_changed = Signal(int)
    ambient_changed = Signal(int)
    
    # 视图控制信号
    fit_to_window = Signal()
    actual_size = Signal()
    reset_view = Signal()
    zoom_changed = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(10)
        
        # 光照控制
        self.lighting_control = LightingControlWidget()
        layout.addWidget(self.lighting_control)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # 视图控制
        self.view_control = ViewControlWidget()
        layout.addWidget(self.view_control)
    
    def _connect_signals(self):
        """连接信号"""
        # 光照控制信号
        self.lighting_control.angle_changed.connect(self.angle_changed.emit)
        self.lighting_control.intensity_changed.connect(self.intensity_changed.emit)
        self.lighting_control.ambient_changed.connect(self.ambient_changed.emit)
        
        # 视图控制信号
        self.view_control.fit_to_window.connect(self.fit_to_window.emit)
        self.view_control.actual_size.connect(self.actual_size.emit)
        self.view_control.reset_view.connect(self.reset_view.emit)
        self.view_control.zoom_changed.connect(self.zoom_changed.emit)
    
    def get_lighting_params(self) -> dict:
        """获取光照参数"""
        return {
            'angle': self.lighting_control.get_angle(),
            'intensity': self.lighting_control.get_intensity(),
            'ambient': self.lighting_control.get_ambient()
        }
    
    def set_lighting_params(self, params: dict):
        """设置光照参数"""
        if 'angle' in params:
            self.lighting_control.set_angle(params['angle'])
        if 'intensity' in params:
            self.lighting_control.set_intensity(params['intensity'])
        if 'ambient' in params:
            self.lighting_control.set_ambient(params['ambient'])
    
    def get_zoom_factor(self) -> float:
        """获取缩放因子"""
        return self.view_control.get_zoom_factor()
    
    def set_zoom_factor(self, factor: float):
        """设置缩放因子"""
        self.view_control.set_zoom_factor(factor)
    
    def update_angle_display(self, angle: int):
        """更新角度显示"""
        direction_hint = self._get_direction_hint(angle)
        self.lighting_control.angle_value_label.setText(f"{angle}° ({direction_hint})")
    
    def update_intensity_display(self, value: int):
        """更新强度显示"""
        intensity = value / 100.0
        self.lighting_control.intensity_value_label.setText(f"{intensity:.1f}")
    
    def update_ambient_display(self, value: int):
        """更新环境光显示"""
        ambient = value / 100.0
        self.lighting_control.ambient_value_label.setText(f"{ambient:.1f}")
    
    def update_zoom_display(self, value: int):
        """更新缩放显示"""
        zoom_factor = value / 100.0
        self.view_control.zoom_value_label.setText(f"{int(zoom_factor * 100)}%")
    
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
