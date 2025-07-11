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
    remove_requested = Signal(str)   # 图像路径

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path

        self.setFixedSize(110, 130)  # 删除角度后减少高度
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
        layout.setSpacing(3)  # 减少间距

        # 缩略图区域 (80x80)
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(80, 80)
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
        self.filename_label.setFixedHeight(16)  # 固定高度
        self.filename_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: bold;
                color: #333333;
            }
        """)
        layout.addWidget(self.filename_label)


        
        # 删除按钮 - 改为更小的按钮
        self.remove_btn = QPushButton("删除")
        self.remove_btn.setFixedSize(70, 20)  # 减少尺寸
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
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
        self.remove_btn.clicked.connect(self._on_remove_clicked)
    
    def _load_thumbnail(self):
        """加载缩略图"""
        try:
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                # 缩放到80x80，保持宽高比，确保完整显示
                scaled_pixmap = pixmap.scaled(
                    80, 80,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.thumbnail_label.setPixmap(scaled_pixmap)
                # 确保图像居中显示
                self.thumbnail_label.setAlignment(Qt.AlignCenter)
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
    
    def _on_remove_clicked(self):
        """删除按钮点击处理"""
        self.remove_requested.emit(self.image_path)
    
    def get_image_path(self) -> str:
        """获取图像路径"""
        return self.image_path
