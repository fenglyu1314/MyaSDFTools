#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像列表组件

显示导入的图像列表，支持：
- 缩略图预览
- 拖拽排序
- 删除图像
- 显示图像信息
"""

import os
from pathlib import Path
from typing import List, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QFrame, QSizePolicy, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QSize, QMimeData
from PySide6.QtGui import QPixmap, QIcon, QAction, QDrag, QPainter

class ImageListItem(QFrame):
    """图像列表项组件"""
    
    remove_requested = Signal(str)  # 请求删除信号
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        self.setFixedHeight(50)  # 减少高度从80px到50px

        self._init_ui()
        self._load_image()
    
    def _init_ui(self):
        """初始化UI - 更紧凑的布局"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)  # 减少边距
        layout.setSpacing(6)  # 减少间距

        # 缩略图标签 - 更小的尺寸
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(40, 40)  # 从64x64减少到40x40
        self.thumbnail_label.setScaledContents(True)
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                border: 1px solid #CCCCCC;
                background-color: #F5F5F5;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.thumbnail_label)

        # 信息区域 - 更紧凑
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)  # 减少间距

        # 文件名 - 更小字体
        self.name_label = QLabel(Path(self.image_path).name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        info_layout.addWidget(self.name_label)

        # 文件信息 - 更小字体
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: #666666; font-size: 10px;")
        info_layout.addWidget(self.info_label)

        info_layout.addStretch()
        layout.addLayout(info_layout)

        layout.addStretch()

        # 删除按钮 - 更小尺寸
        self.remove_btn = QPushButton("×")
        self.remove_btn.setFixedSize(18, 18)  # 从24x24减少到18x18
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                border-radius: 9px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
        """)
        self.remove_btn.clicked.connect(self._on_remove_clicked)
        layout.addWidget(self.remove_btn)
    
    def _load_image(self):
        """加载图像缩略图"""
        try:
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                # 创建缩略图
                thumbnail = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.thumbnail_label.setPixmap(thumbnail)
                
                # 更新信息
                file_size = os.path.getsize(self.image_path)
                size_str = self._format_file_size(file_size)
                self.info_label.setText(f"{pixmap.width()}×{pixmap.height()} | {size_str}")
            else:
                self.thumbnail_label.setText("无法\n加载")
                self.info_label.setText("图像格式错误")
        except Exception as e:
            self.thumbnail_label.setText("加载\n失败")
            self.info_label.setText(f"错误: {str(e)[:20]}...")
    
    def _format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def _on_remove_clicked(self):
        """删除按钮点击"""
        self.remove_requested.emit(self.image_path)

class ImageListWidget(QWidget):
    """图像列表组件"""
    
    images_changed = Signal()  # 图像列表变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_items: List[ImageListItem] = []
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # 列表容器
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.MoveAction)
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.list_widget.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #CCCCCC;
                background-color: white;
                alternate-background-color: #F9F9F9;
            }
            QListWidget::item {
                border: none;
                padding: 2px;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                border: 1px solid #2196F3;
            }
        """)
        layout.addWidget(self.list_widget)
        
        # 空状态提示
        self.empty_label = QLabel("暂无图像\n\n拖拽图像文件到此处\n或点击\"导入图像\"按钮")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("""
            QLabel {
                color: #999999;
                font-size: 14px;
                padding: 40px;
                border: 2px dashed #CCCCCC;
                border-radius: 10px;
                background-color: #FAFAFA;
            }
        """)
        layout.addWidget(self.empty_label)
        
        self._update_empty_state()
    
    def add_image(self, image_path: str):
        """添加图像到列表"""
        # 检查是否已存在
        for item in self.image_items:
            if item.image_path == image_path:
                return
        
        # 创建列表项
        image_item = ImageListItem(image_path)
        image_item.remove_requested.connect(self._remove_image)
        self.image_items.append(image_item)
        
        # 添加到列表组件
        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(0, 50))  # 从80减少到50
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, image_item)
        
        self._update_empty_state()
        self.images_changed.emit()
    
    def remove_image(self, image_path: str):
        """从列表中移除图像"""
        self._remove_image(image_path)
    
    def _remove_image(self, image_path: str):
        """内部移除图像方法"""
        # 找到对应的项
        for i, item in enumerate(self.image_items):
            if item.image_path == image_path:
                # 从列表中移除
                self.image_items.pop(i)
                list_item = self.list_widget.takeItem(i)
                if list_item:
                    self.list_widget.removeItemWidget(list_item)
                break
        
        self._update_empty_state()
        self.images_changed.emit()
    
    def clear(self):
        """清空所有图像"""
        self.image_items.clear()
        self.list_widget.clear()
        self._update_empty_state()
        self.images_changed.emit()
    
    def get_image_paths(self) -> List[str]:
        """获取所有图像路径"""
        return [item.image_path for item in self.image_items]
    
    def get_image_count(self) -> int:
        """获取图像数量"""
        return len(self.image_items)
    
    def _update_empty_state(self):
        """更新空状态显示"""
        has_images = len(self.image_items) > 0
        self.list_widget.setVisible(has_images)
        self.empty_label.setVisible(not has_images)
    
    def contextMenuEvent(self, event):
        """右键菜单"""
        if self.list_widget.itemAt(event.pos()):
            menu = QMenu(self)
            
            # 清空所有
            clear_action = QAction("清空所有图像", self)
            clear_action.triggered.connect(self._confirm_clear_all)
            menu.addAction(clear_action)
            
            menu.exec(event.globalPos())
    
    def _confirm_clear_all(self):
        """确认清空所有图像"""
        if self.image_items:
            reply = QMessageBox.question(
                self, "确认清空", 
                f"确定要清空所有 {len(self.image_items)} 张图像吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.clear()
