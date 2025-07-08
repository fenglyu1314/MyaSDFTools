#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像卡片组件

显示单张图像的卡片，包含：
- 100x100缩略图预览
- 文件名显示
- 角度输入框
- 删除按钮
"""

import os
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QSpinBox, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont

class ImageCardWidget(QFrame):
    """图像卡片组件"""
    
    # 信号定义
    angle_changed = Signal(str, int)  # 图像路径, 新角度
    remove_requested = Signal(str)   # 图像路径
    
    def __init__(self, image_path: str, angle: int = 0, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.angle = angle
        
        self.setFixedSize(120, 180)  # 卡片固定大小
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
            }
            QFrame:hover {
                border: 1px solid #2196F3;
            }
        """)
        
        self._init_ui()
        self._load_thumbnail()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 缩略图区域 (100x100)
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(100, 100)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                border: 1px solid #DDDDDD;
                background-color: #F8F8F8;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.thumbnail_label, 0, Qt.AlignHCenter)
        
        # 文件名显示
        filename = Path(self.image_path).name
        if len(filename) > 12:
            filename = filename[:9] + "..."
        
        self.filename_label = QLabel(filename)
        self.filename_label.setAlignment(Qt.AlignCenter)
        self.filename_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: bold;
                color: #333333;
            }
        """)
        layout.addWidget(self.filename_label)
        
        # 角度输入区域
        angle_layout = QHBoxLayout()
        angle_layout.setContentsMargins(0, 0, 0, 0)
        angle_layout.setSpacing(3)
        
        angle_label = QLabel("角度:")
        angle_label.setStyleSheet("font-size: 10px; color: #666666;")
        angle_layout.addWidget(angle_label)
        
        self.angle_spinbox = QSpinBox()
        self.angle_spinbox.setRange(0, 359)
        self.angle_spinbox.setValue(self.angle)
        self.angle_spinbox.setSuffix("°")
        self.angle_spinbox.setFixedWidth(60)
        self.angle_spinbox.setStyleSheet("""
            QSpinBox {
                font-size: 10px;
                border: 1px solid #CCCCCC;
                border-radius: 2px;
                padding: 2px;
            }
        """)
        angle_layout.addWidget(self.angle_spinbox)
        
        layout.addLayout(angle_layout)
        
        # 删除按钮
        self.remove_btn = QPushButton("×")
        self.remove_btn.setFixedSize(20, 20)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
            QPushButton:pressed {
                background-color: #D32F2F;
            }
        """)
        layout.addWidget(self.remove_btn, 0, Qt.AlignHCenter)
        
        # 连接信号
        self.angle_spinbox.valueChanged.connect(self._on_angle_changed)
        self.remove_btn.clicked.connect(self._on_remove_clicked)
    
    def _load_thumbnail(self):
        """加载缩略图"""
        try:
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                # 缩放到100x100，保持宽高比
                scaled_pixmap = pixmap.scaled(
                    100, 100, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.thumbnail_label.setPixmap(scaled_pixmap)
            else:
                self.thumbnail_label.setText("无法\n加载图像")
                self.thumbnail_label.setStyleSheet(self.thumbnail_label.styleSheet() + """
                    QLabel {
                        color: #FF5722;
                        font-size: 10px;
                    }
                """)
        except Exception as e:
            print(f"加载缩略图失败: {e}")
            self.thumbnail_label.setText("加载\n失败")
            self.thumbnail_label.setStyleSheet(self.thumbnail_label.styleSheet() + """
                QLabel {
                    color: #FF5722;
                    font-size: 10px;
                }
            """)
    
    def _on_angle_changed(self, value):
        """角度改变处理"""
        self.angle = value
        self.angle_changed.emit(self.image_path, value)
    
    def _on_remove_clicked(self):
        """删除按钮点击处理"""
        self.remove_requested.emit(self.image_path)
    
    def get_angle(self) -> int:
        """获取当前角度"""
        return self.angle_spinbox.value()
    
    def set_angle(self, angle: int):
        """设置角度"""
        self.angle_spinbox.blockSignals(True)
        self.angle_spinbox.setValue(angle)
        self.angle = angle
        self.angle_spinbox.blockSignals(False)
    
    def get_image_path(self) -> str:
        """获取图像路径"""
        return self.image_path


class ImageCardsContainer(QWidget):
    """图像卡片容器"""
    
    # 信号定义
    images_changed = Signal()  # 图像列表改变
    angle_changed = Signal(str, int)  # 图像角度改变
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_cards = []  # 存储图像卡片
        self.max_images = 10   # 最大图像数量
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        self.layout.addStretch()  # 左对齐
    
    def add_image(self, image_path: str, angle: int = None) -> bool:
        """添加图像卡片"""
        if len(self.image_cards) >= self.max_images:
            return False
        
        # 自动分配角度
        if angle is None:
            angle = self._calculate_auto_angle()
        
        # 创建图像卡片
        card = ImageCardWidget(image_path, angle)
        card.angle_changed.connect(self.angle_changed.emit)
        card.remove_requested.connect(self._remove_image)
        
        # 添加到布局
        self.layout.insertWidget(len(self.image_cards), card)
        self.image_cards.append(card)
        
        self.images_changed.emit()
        return True
    
    def _remove_image(self, image_path: str):
        """移除图像卡片"""
        for i, card in enumerate(self.image_cards):
            if card.get_image_path() == image_path:
                # 从布局中移除
                self.layout.removeWidget(card)
                card.deleteLater()
                
                # 从列表中移除
                self.image_cards.pop(i)
                
                # 重新分配角度
                self._redistribute_angles()
                
                self.images_changed.emit()
                break
    
    def _calculate_auto_angle(self) -> int:
        """计算自动分配的角度"""
        count = len(self.image_cards) + 1
        if count == 1:
            return 0
        return int(360 / count * len(self.image_cards))
    
    def _redistribute_angles(self):
        """重新分配所有角度"""
        count = len(self.image_cards)
        if count == 0:
            return
        
        for i, card in enumerate(self.image_cards):
            if count == 1:
                angle = 0
            else:
                angle = int(360 / count * i)
            card.set_angle(angle)
    
    def clear(self):
        """清空所有图像卡片"""
        for card in self.image_cards:
            self.layout.removeWidget(card)
            card.deleteLater()
        
        self.image_cards.clear()
        self.images_changed.emit()
    
    def get_images_data(self) -> list:
        """获取所有图像数据"""
        return [(card.get_image_path(), card.get_angle()) for card in self.image_cards]
    
    def get_image_count(self) -> int:
        """获取图像数量"""
        return len(self.image_cards)
