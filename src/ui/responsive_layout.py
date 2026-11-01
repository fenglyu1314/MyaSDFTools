#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
响应式布局组件

根据 layout_config 自动计算尺寸、自适应内容、动态调整的布局组件。
"""

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtCore import QSize, Signal

from .layout_config import layout_config_manager
from .window_styles import WidgetStyles


class ResponsiveGroupBox(QGroupBox):
    """响应式分组框"""

    size_changed = Signal(QSize)

    def __init__(self, title: str, area_name: str, parent=None):
        super().__init__(title, parent)
        self.area_name = area_name
        self.area_config = layout_config_manager.get_area_config(area_name)
        self.layout_config = layout_config_manager.get_layout_config(area_name)

        self._setup_size_policy()
        self._setup_layout()
        self._apply_styles()

    def _setup_size_policy(self):
        """设置尺寸策略"""
        # 如果设置了固定高度（min_height == max_height），使用Fixed策略
        if (self.area_config.max_height > 0 and
            self.area_config.min_height == self.area_config.max_height):
            # 固定高度的区域（如区域1和区域2）
            policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            self.setFixedHeight(self.area_config.min_height)
        else:
            # 可变高度的区域
            policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        if self.area_config.flex_grow > 0:
            policy.setHorizontalStretch(int(self.area_config.flex_grow * 10))
            if not (self.area_config.max_height > 0 and
                   self.area_config.min_height == self.area_config.max_height):
                policy.setVerticalStretch(int(self.area_config.flex_grow * 10))

        self.setSizePolicy(policy)

    def _setup_layout(self):
        """设置布局"""
        if self.layout_config.direction == "horizontal":
            self.main_layout = QHBoxLayout(self)
        else:
            self.main_layout = QVBoxLayout(self)

        self.main_layout.setSpacing(self.layout_config.spacing)
        self.main_layout.setContentsMargins(*self.area_config.padding)

    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet(WidgetStyles.group_box_style())

    def sizeHint(self) -> QSize:
        """建议尺寸"""
        width = max(self.area_config.min_width, 200)
        height = max(self.area_config.min_height, 100)

        if self.area_config.aspect_ratio:
            if width / height > self.area_config.aspect_ratio:
                width = int(height * self.area_config.aspect_ratio)
            else:
                height = int(width / self.area_config.aspect_ratio)

        return QSize(width, height)

    def minimumSizeHint(self) -> QSize:
        """最小尺寸"""
        return QSize(self.area_config.min_width, self.area_config.min_height)

    def resizeEvent(self, event):
        """尺寸变化事件"""
        super().resizeEvent(event)
        self.size_changed.emit(event.size())
