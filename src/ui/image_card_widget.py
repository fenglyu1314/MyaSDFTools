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

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

from ..core.image_manager import MAX_IMAGES
from .window_styles import LayoutConstants


class ImageCardWidget(QFrame):
    """图像卡片组件 - 响应式版本"""

    # 信号定义
    remove_requested = Signal(str)   # 图像路径

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self._card_size = (110, 130)  # 参考区域2的尺寸，稍微增加高度容纳删除按钮

        self._setup_size_policy()
        self._setup_styles()
        self._init_ui()
        self._load_thumbnail()

        # 强制设置固定尺寸，参考区域2的设置方式
        self.setFixedSize(110, 130)

    def _setup_size_policy(self):
        """设置尺寸策略"""
        policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(policy)

        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)

    def _setup_styles(self):
        """设置样式"""
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #DDDDDD;
                border-radius: 6px;
            }
            QFrame:hover {
                border: 2px solid #2196F3;
                background-color: #F8F9FA;
            }
        """)
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(LayoutConstants.SPACING_TINY, LayoutConstants.SPACING_TINY,
                                 LayoutConstants.SPACING_TINY, LayoutConstants.SPACING_TINY)
        layout.setSpacing(LayoutConstants.SPACING_TINY)

        # 缩略图区域 - 动态尺寸
        self.thumbnail_label = QLabel()
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
        self.filename_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: bold;
                color: #333333;
                background-color: #F5F5F5;
                border-radius: 3px;
                padding: 2px 4px;
                margin: 1px;
            }
        """)
        layout.addWidget(self.filename_label)


        
        # 删除按钮 - 响应式尺寸
        self.remove_btn = QPushButton("删除")
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
                min-height: 20px;
                min-width: 50px;
                max-width: 80px;
            }
            QPushButton:hover {
                background-color: #E64A19;
            }
            QPushButton:pressed {
                background-color: #D84315;
            }
        """)
        layout.addWidget(self.remove_btn, 0, Qt.AlignHCenter)
        
        # 连接信号
        self.remove_btn.clicked.connect(self._on_remove_clicked)

    def set_card_size(self, width: int, height: int):
        """设置卡片尺寸（响应式调整）"""
        self._card_size = (width, height)
        self.setFixedSize(width, height)

        # 调整缩略图尺寸（保持一定比例）
        thumbnail_size = min(width - 2 * LayoutConstants.SPACING_TINY,
                           height - 40)  # 减去文件名和按钮的空间
        thumbnail_size = max(thumbnail_size, 40)  # 最小尺寸
        self.thumbnail_label.setFixedSize(thumbnail_size, thumbnail_size)

        # 调整按钮尺寸 - 修复宽度计算
        button_width = min(width - 2 * LayoutConstants.SPACING_TINY, 80)  # 增加最大宽度到80px
        button_width = max(button_width, 50)  # 设置最小宽度50px
        self.remove_btn.setFixedSize(button_width, 20)

    def get_card_size(self) -> tuple[int, int]:
        """获取当前卡片尺寸"""
        return self._card_size
    
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


class ImageCardsContainer(QWidget):
    """图像卡片容器 - 简化版本，直接使用QWidget"""

    # 信号定义
    images_changed = Signal()  # 图像列表改变
    image_removed = Signal(str)  # 图像被移除（供事件处理器同步后端状态）

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_cards = []  # 存储图像卡片
        self.max_images = MAX_IMAGES    # 最大图像数量

        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        # 卡片从左侧依次排列，空余空间留在右侧
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(1, 5, 1, 5)  # 与区域2完全一致的边距
        self.layout.setSpacing(4)  # 与区域2完全一致的间距
        # 左对齐：卡片按顺序贴左排布，删除某张后其余卡片位置可预期，
        # 不会因整体居中而左右移动，便于连续快速删除
        self.layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    
    def add_image(self, image_path: str) -> bool:
        """添加图像卡片"""
        # 检查数量限制
        if len(self.image_cards) >= self.max_images:
            print(f"❌ 图像卡片数量已达上限({self.max_images}张)")
            return False

        # 检查是否已存在（避免重复添加）
        for card in self.image_cards:
            if card.get_image_path() == image_path:
                print(f"⚠️ 图像卡片已存在: {image_path}")
                return False

        # 创建图像卡片
        card = ImageCardWidget(image_path)
        card.remove_requested.connect(self._remove_image)

        # 添加到布局
        self.layout.addWidget(card)
        self.image_cards.append(card)

        self.images_changed.emit()
        print(f"✅ 成功添加图像卡片: {image_path}")
        return True
    
    def _remove_image(self, image_path: str, notify: bool = True):
        """移除图像卡片

        Args:
            image_path: 图像路径
            notify: 是否发出 image_removed 信号。UI 同步（后端已先行删除）时传 False，
                    避免回环触发。
        """
        for i, card in enumerate(self.image_cards):
            if card.get_image_path() == image_path:
                # 从布局中移除
                self.layout.removeWidget(card)
                card.deleteLater()

                # 从列表中移除
                self.image_cards.pop(i)

                self.images_changed.emit()
                if notify:
                    self.image_removed.emit(image_path)
                print(f"✅ 移除图像卡片: {Path(image_path).name}")
                break
    

    

    
    def clear(self, notify: bool = True):
        """清空所有图像卡片"""
        removed_paths = [card.get_image_path() for card in self.image_cards]

        for card in self.image_cards:
            self.layout.removeWidget(card)
            card.deleteLater()

        self.image_cards.clear()
        self.images_changed.emit()

        if notify:
            for path in removed_paths:
                self.image_removed.emit(path)

        print("✅ 清空所有图像卡片")
    
    def get_images_data(self) -> list:
        """获取所有图像数据"""
        return [card.get_image_path() for card in self.image_cards]
    
    def get_image_count(self) -> int:
        """获取图像数量"""
        return len(self.image_cards)
