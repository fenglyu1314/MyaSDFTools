#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像卡片容器

管理多个图像卡片的容器组件
"""

from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt, Signal

from .image_card import ImageCardWidget


class PlaceholderCardWidget(QWidget):
    """占位卡片组件 - 用于提示用户添加图像"""

    # 信号定义
    add_image_requested = Signal()  # 请求添加图像

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(115, 135)
        self.setAcceptDrops(True)
        
        # 简化的占位符样式
        self.setStyleSheet("""
            QWidget {
                background-color: palette(base);
                border: 2px dashed palette(mid);
                border-radius: 5px;
            }
            QWidget:hover {
                border: 2px dashed #2196F3;
                background-color: palette(alternate-base);
            }
        """)

    def mousePressEvent(self, event):
        """点击添加图像"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.add_image_requested.emit()
        super().mousePressEvent(event)


class ImageCardsContainer(QWidget):
    """图像卡片容器"""

    # 信号定义
    images_changed = Signal()  # 图像列表改变
    image_remove_requested = Signal(str)  # 请求删除图像信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_cards = []  # 存储图像卡片
        self.placeholder_cards = []  # 存储占位卡片
        self.max_images = 8    # 最大图像数量改为8张

        self._init_ui()
        self._init_placeholders()  # 初始显示8个占位卡片
    
    def _init_ui(self):
        """初始化UI"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 0, 15, 0)  # 左右边距让卡片居中
        self.layout.setSpacing(7)  # 精确计算的间距让8个卡片平均分布
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中对齐

    def _init_placeholders(self):
        """初始化8个占位卡片"""
        for i in range(self.max_images):
            placeholder = PlaceholderCardWidget()
            placeholder.add_image_requested.connect(self._on_add_image_requested)
            self.placeholder_cards.append(placeholder)
            self.layout.addWidget(placeholder)

    def _on_add_image_requested(self):
        """处理添加图像请求"""
        # 通过父窗口的事件处理器处理导入图像
        parent_window = self.window()
        if hasattr(parent_window, '_handle_import'):
            parent_window._handle_import()

    def add_image(self, image_path: str) -> bool:
        """添加图像卡片 - 替换第一个可用的占位卡片"""
        # 检查数量限制
        if len(self.image_cards) >= self.max_images:
            print(f"❌ 图像卡片数量已达上限({self.max_images}张)")
            return False

        # 检查是否已存在（避免重复添加）
        for card in self.image_cards:
            if card.get_image_path() == image_path:
                print(f"⚠️ 图像卡片已存在: {image_path}")
                return False

        # 找到第一个可用的占位卡片位置
        insert_index = len(self.image_cards)
        if insert_index < len(self.placeholder_cards):
            # 移除对应位置的占位卡片
            placeholder = self.placeholder_cards[insert_index]
            self.layout.removeWidget(placeholder)
            placeholder.hide()

        # 创建图像卡片
        card = ImageCardWidget(image_path)
        card.remove_requested.connect(self._remove_image)

        # 启用拖拽功能
        card.setAcceptDrops(True)

        # 插入到正确位置
        self.layout.insertWidget(insert_index, card)
        self.image_cards.append(card)

        self.images_changed.emit()
        print(f"✅ 成功添加图像卡片: {image_path}")
        return True
    
    def _remove_image(self, image_path: str):
        """移除图像卡片 - 发出删除请求信号"""
        # 发出删除请求信号，让外部处理器处理后端删除
        self.image_remove_requested.emit(image_path)

        # UI层面的删除操作
        for i, card in enumerate(self.image_cards):
            if card.get_image_path() == image_path:
                # 从布局中移除
                self.layout.removeWidget(card)
                card.deleteLater()

                # 从列表中移除
                self.image_cards.pop(i)

                # 重新排列剩余的图像卡片和占位卡片
                self._rearrange_cards()

                self.images_changed.emit()
                break

    def _rearrange_cards(self):
        """重新排列图像卡片和占位卡片"""
        # 清空布局中的所有组件
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().hide()

        # 重新添加图像卡片
        for i, card in enumerate(self.image_cards):
            self.layout.insertWidget(i, card)
            card.show()

        # 添加剩余的占位卡片
        for i in range(len(self.image_cards), self.max_images):
            if i < len(self.placeholder_cards):
                placeholder = self.placeholder_cards[i]
                self.layout.insertWidget(i, placeholder)
                placeholder.show()

    def clear(self):
        """清空所有图像卡片 - 恢复所有占位卡片"""
        for card in self.image_cards:
            self.layout.removeWidget(card)
            card.deleteLater()

        self.image_cards.clear()

        # 重新排列，显示所有占位卡片
        self._rearrange_cards()

        self.images_changed.emit()
    
    def get_images_data(self) -> list:
        """获取所有图像数据"""
        return [card.get_image_path() for card in self.image_cards]

    def get_image_count(self) -> int:
        """获取图像数量"""
        return len(self.image_cards)

    def swap_images(self, source_path: str, target_path: str):
        """交换两个图像的位置"""
        if source_path == target_path:
            return

        # 找到两个图像卡片的索引
        source_index = -1
        target_index = -1

        for i, card in enumerate(self.image_cards):
            if card.get_image_path() == source_path:
                source_index = i
            elif card.get_image_path() == target_path:
                target_index = i

        # 如果找到了两个卡片，交换它们的位置
        if source_index >= 0 and target_index >= 0:
            # 交换列表中的位置
            self.image_cards[source_index], self.image_cards[target_index] = \
                self.image_cards[target_index], self.image_cards[source_index]

            # 重新排列布局
            self._rearrange_cards()

            # 发出变化信号
            self.images_changed.emit()

            print(f"🔄 交换图像位置: {Path(source_path).name} ↔ {Path(target_path).name}")
