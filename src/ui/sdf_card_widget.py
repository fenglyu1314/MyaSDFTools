#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SDF结果卡片组件

显示单张SDF生成结果的卡片，包含：
- 100x100 SDF预览图
- 生成状态显示
- 计算耗时显示
"""

import time
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont, QPainter, QPen, QColor


class SDFPlaceholderCardWidget(QWidget):
    """SDF占位卡片组件 - 显示等待生成SDF的占位符"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(110, 120)  # 与SDFCardWidget相同的尺寸

        # 设置基础样式，不包含边框（边框通过paintEvent绘制）
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                border-radius: 5px;
            }
        """)

        # 用于跟踪悬停状态
        self.is_hovered = False

        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # 等待图标 - 使用简约的圆点
        wait_label = QLabel("⟳")
        wait_label.setAlignment(Qt.AlignCenter)
        wait_label.setStyleSheet("""
            QLabel {
                font-size: 40px;
                color: #CCCCCC;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(wait_label)

        # 提示文字
        hint_label = QLabel("等待生成")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #999999;
                background: transparent;      
                border: none;
            }
        """)
        layout.addWidget(hint_label)

    def enterEvent(self, event):
        """鼠标进入事件"""
        self.is_hovered = True
        self.update()  # 触发重绘
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.is_hovered = False
        self.update()  # 触发重绘
        super().leaveEvent(event)

    def paintEvent(self, event):
        """自定义绘制事件 - 绘制虚线边框"""
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 设置虚线画笔
        pen = QPen()
        pen.setStyle(Qt.DashLine)
        pen.setWidth(2)

        if self.is_hovered:
            pen.setColor(QColor("#CCCCCC"))  # 悬停时稍微深一点
        else:
            pen.setColor(QColor("#DDDDDD"))  # 正常时浅灰色

        painter.setPen(pen)

        # 绘制虚线边框（留出一些边距）
        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.drawRoundedRect(rect, 5, 5)

        painter.end()


class SDFCardWidget(QFrame):
    """SDF结果卡片组件"""
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.sdf_data = None
        self.generation_time = 0.0
        self.status = "waiting"  # waiting, generating, completed, failed
        
        self.setFixedSize(110, 120)  # 缩小卡片尺寸避免重叠
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        self.setStyleSheet("""
            QFrame {
                background-color: #E0E0E0;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
            }
        """)
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # SDF预览区域 (80x80)
        self.sdf_preview_label = QLabel()
        self.sdf_preview_label.setFixedSize(80, 80)
        self.sdf_preview_label.setAlignment(Qt.AlignCenter)
        self.sdf_preview_label.setStyleSheet("""
            QLabel {
                border: 1px solid #CCCCCC;
                background-color: #F5F5F5;
                border-radius: 3px;
                color: #666666;
                font-size: 11px;
            }
        """)
        self.sdf_preview_label.setText("等待\n生成")
        layout.addWidget(self.sdf_preview_label, 0, Qt.AlignHCenter)
        
        # 状态显示区域
        self.status_label = QLabel("等待生成")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #333333;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.status_label)
    
    def set_status(self, status: str, message: str = ""):
        """设置状态"""
        self.status = status
        
        if status == "waiting":
            self.status_label.setText("等待生成")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #333333;
                    font-weight: bold;
                }
            """)
            self.sdf_preview_label.setText("等待\n生成")
            
        elif status == "generating":
            self.status_label.setText("生成中...")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #2196F3;
                    font-weight: bold;
                }
            """)
            self.sdf_preview_label.setText("生成中\n...")
            
        elif status == "completed":
            time_text = f"✓ {self.generation_time:.2f}s" if self.generation_time > 0 else "✓ 完成"
            self.status_label.setText(time_text)
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #4CAF50;
                    font-weight: bold;
                }
            """)
            
        elif status == "failed":
            self.status_label.setText("❌ 失败")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #FF5722;
                    font-weight: bold;
                }
            """)
            self.sdf_preview_label.setText("生成\n失败")
    
    def set_sdf_preview(self, sdf_image: QPixmap):
        """设置SDF预览图"""
        if not sdf_image.isNull():
            # 缩放到80x80，保持宽高比，确保完整显示
            scaled_pixmap = sdf_image.scaled(
                80, 80,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.sdf_preview_label.setPixmap(scaled_pixmap)
            # 确保图像居中显示
            self.sdf_preview_label.setAlignment(Qt.AlignCenter)
        else:
            self.sdf_preview_label.setText("预览\n失败")
    
    def set_generation_time(self, time_seconds: float):
        """设置生成耗时"""
        self.generation_time = time_seconds
        if self.status == "completed":
            self.status_label.setText(f"✓ {time_seconds:.2f}s")
    
    def get_image_path(self) -> str:
        """获取对应的图像路径"""
        return self.image_path
    
    def get_status(self) -> str:
        """获取当前状态"""
        return self.status


class SDFCardsContainer(QWidget):
    """SDF结果卡片容器"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sdf_cards = []  # 存储SDF卡片
        self.placeholder_cards = []  # 存储占位卡片
        self.max_cards = 8  # 最大卡片数量

        self._init_ui()
        self._init_placeholders()  # 初始显示8个占位卡片
    
    def _init_ui(self):
        """初始化UI"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 0, 15, 0)  # 左右边距让卡片居中，与图像导入区域保持一致
        self.layout.setSpacing(10)  # 稍微增加间距，让卡片横向位置更好地对齐区域1
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中对齐，与图像导入区域保持一致

    def _init_placeholders(self):
        """初始化8个占位卡片"""
        for i in range(self.max_cards):
            placeholder = SDFPlaceholderCardWidget()
            self.placeholder_cards.append(placeholder)
            self.layout.addWidget(placeholder)
    
    def add_sdf_card(self, image_path: str) -> SDFCardWidget:
        """添加SDF卡片 - 替换对应位置的占位卡片"""
        # 检查数量限制
        if len(self.sdf_cards) >= self.max_cards:
            print(f"❌ SDF卡片数量已达上限({self.max_cards}张)")
            return None

        # 检查是否已存在
        for card in self.sdf_cards:
            if card.get_image_path() == image_path:
                return card

        # 找到第一个可用的占位卡片位置
        insert_index = len(self.sdf_cards)
        if insert_index < len(self.placeholder_cards):
            # 移除对应位置的占位卡片
            placeholder = self.placeholder_cards[insert_index]
            self.layout.removeWidget(placeholder)
            placeholder.hide()

        # 创建新卡片
        card = SDFCardWidget(image_path)

        # 插入到正确位置
        self.layout.insertWidget(insert_index, card)
        self.sdf_cards.append(card)

        return card
    
    def remove_sdf_card(self, image_path: str):
        """移除SDF卡片 - 恢复占位卡片"""
        for i, card in enumerate(self.sdf_cards):
            if card.get_image_path() == image_path:
                # 从布局中移除
                self.layout.removeWidget(card)
                card.deleteLater()

                # 从列表中移除
                self.sdf_cards.pop(i)

                # 重新排列剩余的卡片和占位卡片
                self._rearrange_cards()
                break

    def _rearrange_cards(self):
        """重新排列SDF卡片和占位卡片"""
        # 清空布局中的所有组件
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().hide()

        # 重新添加SDF卡片
        for i, card in enumerate(self.sdf_cards):
            self.layout.insertWidget(i, card)
            card.show()

        # 添加剩余的占位卡片
        for i in range(len(self.sdf_cards), self.max_cards):
            if i < len(self.placeholder_cards):
                placeholder = self.placeholder_cards[i]
                self.layout.insertWidget(i, placeholder)
                placeholder.show()
    
    def get_sdf_card(self, image_path: str) -> Optional[SDFCardWidget]:
        """获取指定图像的SDF卡片"""
        for card in self.sdf_cards:
            if card.get_image_path() == image_path:
                return card
        return None
    
    def clear(self):
        """清空所有SDF卡片 - 恢复所有占位卡片"""
        for card in self.sdf_cards:
            self.layout.removeWidget(card)
            card.deleteLater()

        self.sdf_cards.clear()

        # 重新排列，显示所有占位卡片
        self._rearrange_cards()
    
    def update_cards_from_images(self, images_data: list):
        """根据图像数据更新SDF卡片"""
        # 获取当前图像路径列表
        current_image_paths = [data[0] for data in images_data]

        # 移除不再存在的卡片
        cards_to_remove = []
        for card in self.sdf_cards:
            if card.get_image_path() not in current_image_paths:
                cards_to_remove.append(card.get_image_path())

        for image_path in cards_to_remove:
            self.remove_sdf_card(image_path)

        # 添加新的卡片
        for image_path, angle in images_data:
            if not self.get_sdf_card(image_path):
                self.add_sdf_card(image_path)

        # 重新排列卡片顺序以匹配images_data的顺序
        self._rearrange_cards_by_order(current_image_paths)

    def _rearrange_cards_by_order(self, desired_order: list):
        """根据指定顺序重新排列卡片"""
        if not desired_order:
            return

        # 创建一个按新顺序排列的卡片列表
        new_card_order = []
        for image_path in desired_order:
            card = self.get_sdf_card(image_path)
            if card:
                new_card_order.append(card)

        # 如果顺序没有变化，直接返回
        if new_card_order == self.sdf_cards:
            return

        # 更新卡片列表
        self.sdf_cards = new_card_order

        # 重新排列所有卡片和占位卡片
        self._rearrange_cards()

        print(f"🔄 SDF卡片重新排序: {[Path(card.get_image_path()).name for card in self.sdf_cards]}")
    
    def get_card_count(self) -> int:
        """获取卡片数量"""
        return len(self.sdf_cards)
    
    def set_all_status(self, status: str):
        """设置所有卡片的状态"""
        for card in self.sdf_cards:
            card.set_status(status)
