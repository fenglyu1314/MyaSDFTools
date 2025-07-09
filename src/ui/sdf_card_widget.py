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
from PySide6.QtGui import QPixmap, QFont

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
                background-color: white;
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
                border: 1px solid #DDDDDD;
                background-color: #F8F8F8;
                border-radius: 3px;
                color: #999999;
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
                color: #666666;
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
                    color: #666666;
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
            # 缩放到100x100，保持宽高比
            scaled_pixmap = sdf_image.scaled(
                100, 100, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.sdf_preview_label.setPixmap(scaled_pixmap)
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
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        #self.layout.setSpacing(10)  # 增加间距避免重叠
        self.layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # 左对齐并顶部对齐
    
    def add_sdf_card(self, image_path: str) -> SDFCardWidget:
        """添加SDF卡片"""
        # 检查是否已存在
        for card in self.sdf_cards:
            if card.get_image_path() == image_path:
                return card
        
        # 创建新卡片
        card = SDFCardWidget(image_path)
        
        # 添加到布局
        self.layout.insertWidget(len(self.sdf_cards), card)
        self.sdf_cards.append(card)
        
        return card
    
    def remove_sdf_card(self, image_path: str):
        """移除SDF卡片"""
        for i, card in enumerate(self.sdf_cards):
            if card.get_image_path() == image_path:
                # 从布局中移除
                self.layout.removeWidget(card)
                card.deleteLater()
                
                # 从列表中移除
                self.sdf_cards.pop(i)
                break
    
    def get_sdf_card(self, image_path: str) -> Optional[SDFCardWidget]:
        """获取指定图像的SDF卡片"""
        for card in self.sdf_cards:
            if card.get_image_path() == image_path:
                return card
        return None
    
    def clear(self):
        """清空所有SDF卡片"""
        for card in self.sdf_cards:
            self.layout.removeWidget(card)
            card.deleteLater()
        
        self.sdf_cards.clear()
    
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
    
    def get_card_count(self) -> int:
        """获取卡片数量"""
        return len(self.sdf_cards)
    
    def set_all_status(self, status: str):
        """设置所有卡片的状态"""
        for card in self.sdf_cards:
            card.set_status(status)
