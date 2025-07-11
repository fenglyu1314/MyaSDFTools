#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像卡片组件

显示单张图像的卡片，包含：
- 100x100缩略图预览
- 文件名显示
- 删除按钮
"""

import os
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame
)
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QPixmap, QPainter, QPen, QFont, QDrag


class ImageCardWidget(QFrame):
    """图像卡片组件"""

    # 信号定义
    remove_requested = Signal(str)   # 图像路径

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.drag_start_position = None

        self.setFixedSize(115, 135)  # 调整尺寸让8个卡片更好地填充区域
        self.setAcceptDrops(True)  # 接受拖拽
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        # 使用系统主题颜色，添加背景色区分
        self.setStyleSheet("""
            QFrame {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 5px;
            }
            QFrame:hover {
                border: 1px solid #2196F3;
                background-color: palette(alternate-base);
            }
        """)

        self._init_ui()
        self._load_thumbnail()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)  # 减少间距

        # 缩略图区域 (85x85)
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(85, 85)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                border: 1px solid palette(mid);
                background-color: palette(base);
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
        # 使用全局样式，只设置必要的属性
        self.filename_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: bold;
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

    def mousePressEvent(self, event):
        """鼠标按下事件 - 记录拖拽起始位置"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 开始拖拽"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        if not self.drag_start_position:
            return

        # 检查是否移动了足够的距离来开始拖拽
        if ((event.position().toPoint() - self.drag_start_position).manhattanLength() <
            10):  # 10像素的拖拽阈值
            return

        # 创建拖拽操作
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(f"image_card:{self.image_path}")
        drag.setMimeData(mime_data)

        # 创建拖拽时的缩略图
        pixmap = self.grab()
        drag.setPixmap(pixmap)

        # 执行拖拽
        drop_action = drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if event.mimeData().hasText() and event.mimeData().text().startswith("image_card:"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """拖拽放下事件"""
        if event.mimeData().hasText() and event.mimeData().text().startswith("image_card:"):
            source_path = event.mimeData().text().replace("image_card:", "")
            target_path = self.image_path

            # 通知父容器进行位置交换
            parent_container = self.parent()
            if hasattr(parent_container, 'swap_images'):
                parent_container.swap_images(source_path, target_path)

            event.acceptProposedAction()
        else:
            event.ignore()
