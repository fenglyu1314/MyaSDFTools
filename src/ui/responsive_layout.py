#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
响应式布局组件

提供自动计算尺寸、自适应内容、动态调整的布局组件
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QSizePolicy
from PySide6.QtCore import Qt, QSize, Signal
from typing import List, Optional, Tuple

from .layout_config import layout_config_manager, AreaConfig, LayoutConfig
from .window_styles import LayoutConstants


class ResponsiveWidget(QWidget):
    """响应式组件基类"""
    
    size_changed = Signal(QSize)  # 尺寸变化信号
    
    def __init__(self, area_name: str, parent=None):
        super().__init__(parent)
        self.area_name = area_name
        self.area_config = layout_config_manager.get_area_config(area_name)
        self.layout_config = layout_config_manager.get_layout_config(area_name)
        
        self._setup_size_policy()
        self._setup_layout()
    
    def _setup_size_policy(self):
        """设置尺寸策略"""
        policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
        # 设置弹性系数
        if self.area_config.flex_grow > 0:
            policy.setHorizontalStretch(int(self.area_config.flex_grow * 10))
            policy.setVerticalStretch(int(self.area_config.flex_grow * 10))
        
        self.setSizePolicy(policy)
    
    def _setup_layout(self):
        """设置布局"""
        # 创建主布局
        if self.layout_config.direction == "horizontal":
            self.main_layout = QHBoxLayout(self)
        else:
            self.main_layout = QVBoxLayout(self)
        
        # 设置间距和边距
        self.main_layout.setSpacing(self.layout_config.spacing)
        self.main_layout.setContentsMargins(*self.area_config.padding)
        
        # 设置对齐方式
        alignment = self._get_alignment()
        if alignment:
            self.main_layout.setAlignment(alignment)
    
    def _get_alignment(self) -> Qt.AlignmentFlag:
        """获取对齐方式"""
        alignment_map = {
            "start": Qt.AlignTop | Qt.AlignLeft,
            "center": Qt.AlignCenter,
            "end": Qt.AlignBottom | Qt.AlignRight,
            "stretch": Qt.AlignJustify
        }
        return alignment_map.get(self.layout_config.alignment, Qt.AlignTop | Qt.AlignLeft)
    
    def sizeHint(self) -> QSize:
        """建议尺寸"""
        # 基于配置计算建议尺寸
        width = max(self.area_config.min_width, 100)
        height = max(self.area_config.min_height, 50)
        
        # 应用宽高比
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
        self._on_resize(event.size())
    
    def _on_resize(self, size: QSize):
        """尺寸变化处理（子类重写）"""
        pass


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
        from .window_styles import WidgetStyles
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


class ResponsiveCardContainer(ResponsiveWidget):
    """响应式卡片容器"""

    def __init__(self, area_name: str, parent=None):
        # 先初始化基本属性
        self.cards = []
        self.max_cards = 8

        # 获取卡片配置
        config_dict = layout_config_manager.get_config(area_name)
        card_config = config_dict.get("card_config", {})
        self.max_cards = card_config.get("max_cards", 8)
        self.card_spacing = card_config.get("card_spacing", LayoutConstants.SPACING_SMALL)

        # 调用父类初始化
        super().__init__(area_name, parent)

        # 重新设置为水平布局（卡片容器必须是水平的）
        self._setup_horizontal_layout()
    
    def _setup_horizontal_layout(self):
        """强制设置为水平布局（卡片容器必须是水平的）"""
        # 移除现有布局
        if hasattr(self, 'main_layout') and self.main_layout:
            # 清理现有布局
            while self.main_layout.count():
                child = self.main_layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)
            self.main_layout.setParent(None)

        # 创建新的水平布局
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setSpacing(self.card_spacing)
        self.main_layout.setContentsMargins(*self.area_config.padding)

        # 不设置特殊对齐，让卡片自然分布
    
    def _on_resize(self, size: QSize):
        """尺寸变化时重新计算卡片布局"""
        self._update_card_sizes(size.width())
    
    def _update_card_sizes(self, container_width: int):
        """更新卡片尺寸"""
        if not self.cards:
            return
        
        # 计算卡片布局
        layout_info = layout_config_manager.calculate_card_layout(self.area_name, container_width)
        card_width, card_height = layout_info["card_size"]
        
        # 更新所有卡片尺寸
        for card in self.cards:
            if hasattr(card, 'setFixedSize'):
                card.setFixedSize(card_width, card_height)
    
    def add_card(self, card_widget):
        """添加卡片"""
        if len(self.cards) < self.max_cards:
            self.cards.append(card_widget)
            self.main_layout.addWidget(card_widget)
            self._update_card_sizes(self.width())
    
    def remove_card(self, card_widget):
        """移除卡片"""
        if card_widget in self.cards:
            self.cards.remove(card_widget)
            self.main_layout.removeWidget(card_widget)
            card_widget.setParent(None)
            self._update_card_sizes(self.width())
    
    def clear_cards(self):
        """清空所有卡片"""
        for card in self.cards[:]:
            self.remove_card(card)
    
    def sizeHint(self) -> QSize:
        """建议尺寸"""
        # 基于卡片数量和尺寸计算建议尺寸
        if not self.cards:
            return super().sizeHint()
        
        # 计算理想的容器尺寸
        layout_info = layout_config_manager.calculate_card_layout(self.area_name, 800)  # 假设800px宽度
        container_width, container_height = layout_info["container_size"]
        
        return QSize(container_width, container_height)


class ResponsivePreviewWidget(ResponsiveWidget):
    """响应式预览组件"""
    
    def __init__(self, area_name: str, parent=None):
        super().__init__(area_name, parent)
        self.preview_widget = None
        self.control_widgets = []
    
    def set_preview_widget(self, widget):
        """设置预览组件"""
        if self.preview_widget:
            self.main_layout.removeWidget(self.preview_widget)
        
        self.preview_widget = widget
        self.main_layout.addWidget(widget, 1)  # 给预览组件更大的拉伸系数
    
    def add_control_widget(self, widget):
        """添加控制组件"""
        self.control_widgets.append(widget)
        self.main_layout.addWidget(widget, 0)  # 控制组件不拉伸
    
    def _on_resize(self, size: QSize):
        """尺寸变化时调整预览组件"""
        if self.preview_widget and hasattr(self.preview_widget, 'setFixedSize'):
            # 计算预览区域可用尺寸
            available_height = size.height()
            for control in self.control_widgets:
                available_height -= control.sizeHint().height()
            available_height -= self.layout_config.spacing * len(self.control_widgets)
            available_height -= sum(self.area_config.padding[0::2])  # 上下边距
            
            # 保持正方形比例
            preview_size = min(size.width() - sum(self.area_config.padding[1::2]), available_height)
            preview_size = max(preview_size, LayoutConstants.MIN_PREVIEW_SIZE)
            
            self.preview_widget.setFixedSize(preview_size, preview_size)
