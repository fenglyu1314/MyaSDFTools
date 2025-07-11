#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主题切换控件

提供用户界面的主题切换功能
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from .theme_manager import ThemeManager, ThemeMode, get_theme_manager


class ThemeSwitcherWidget(QWidget):
    """主题切换控件"""
    
    # 主题模式变化信号
    theme_mode_changed = Signal(object)  # 发送ThemeMode对象
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 获取主题管理器
        self.theme_manager = get_theme_manager()
        
        self._init_ui()
        self._connect_signals()
        
        # 设置初始值
        self._update_combo_selection()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # 主题标签
        theme_label = QLabel("主题:")
        theme_label.setFont(QFont("", 9))
        layout.addWidget(theme_label)
        
        # 主题选择下拉框
        self.theme_combo = QComboBox()
        self.theme_combo.setFixedWidth(80)
        self.theme_combo.setFont(QFont("", 9))
        
        # 添加主题选项
        self.theme_combo.addItem("跟随系统", ThemeMode.SYSTEM)
        self.theme_combo.addItem("浅色", ThemeMode.LIGHT)
        self.theme_combo.addItem("深色", ThemeMode.DARK)
        
        # 设置样式
        self._apply_combo_style()
        
        layout.addWidget(self.theme_combo)
        
        # 设置整体样式
        self.setFixedHeight(25)
    
    def _apply_combo_style(self):
        """应用下拉框样式"""
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: transparent;
                border: 1px solid palette(mid);
                border-radius: 3px;
                padding: 2px 5px;
                font-size: 9px;
            }
            QComboBox:hover {
                border-color: palette(highlight);
            }
            QComboBox::drop-down {
                border: none;
                width: 15px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid palette(text);
                margin-right: 3px;
            }
            QComboBox QAbstractItemView {
                background-color: palette(base);
                border: 1px solid palette(mid);
                selection-background-color: palette(highlight);
                font-size: 9px;
            }
        """)
    
    def _connect_signals(self):
        """连接信号"""
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
    
    def _on_theme_changed(self, index):
        """主题选择变化处理"""
        if index < 0:
            return
            
        # 获取选中的主题模式
        theme_mode = self.theme_combo.itemData(index)
        
        if theme_mode and theme_mode != self.theme_manager.get_current_mode():
            print(f"🎨 用户切换主题模式: {theme_mode.value}")
            
            # 设置主题管理器的模式
            self.theme_manager.set_theme_mode(theme_mode)
            
            # 发送信号
            self.theme_mode_changed.emit(theme_mode)
    
    def _update_combo_selection(self):
        """更新下拉框选择状态"""
        current_mode = self.theme_manager.get_current_mode()
        
        # 查找对应的索引
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current_mode:
                self.theme_combo.blockSignals(True)
                self.theme_combo.setCurrentIndex(i)
                self.theme_combo.blockSignals(False)
                break
    
    def refresh_style(self):
        """刷新样式（主题变化时调用）"""
        self._apply_combo_style()
    
    def get_current_theme_mode(self) -> ThemeMode:
        """获取当前选中的主题模式"""
        current_index = self.theme_combo.currentIndex()
        if current_index >= 0:
            return self.theme_combo.itemData(current_index)
        return ThemeMode.SYSTEM


class CompactThemeSwitcher(QWidget):
    """紧凑型主题切换器 - 用于窗口右上角"""
    
    theme_mode_changed = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 获取主题管理器
        self.theme_manager = get_theme_manager()
        
        self._init_ui()
        self._connect_signals()
        self._update_combo_selection()
    
    def _init_ui(self):
        """初始化紧凑UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 1, 3, 1)
        layout.setSpacing(3)
        
        # 只有下拉框，没有标签
        self.theme_combo = QComboBox()
        self.theme_combo.setFixedSize(70, 20)
        self.theme_combo.setFont(QFont("", 8))
        
        # 添加主题选项（使用更短的文本）
        self.theme_combo.addItem("🔄 系统", ThemeMode.SYSTEM)
        self.theme_combo.addItem("☀️ 浅色", ThemeMode.LIGHT)
        self.theme_combo.addItem("🌙 深色", ThemeMode.DARK)
        
        # 设置紧凑样式
        self._apply_compact_style()
        
        layout.addWidget(self.theme_combo)
        
        # 设置整体尺寸
        self.setFixedSize(76, 22)
    
    def _apply_compact_style(self):
        """应用紧凑样式"""
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #999;
                border-radius: 2px;
                padding: 1px 3px;
                font-size: 8px;
                color: black;
            }
            QComboBox:hover {
                border-color: #0078d4;
                background-color: #f0f0f0;
            }
            QComboBox::drop-down {
                border: none;
                width: 12px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 3px solid black;
                margin-right: 2px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #999;
                selection-background-color: #0078d4;
                color: black;
                font-size: 8px;
            }
        """)
    
    def _connect_signals(self):
        """连接信号"""
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
    
    def _on_theme_changed(self, index):
        """主题选择变化处理"""
        if index < 0:
            return
            
        theme_mode = self.theme_combo.itemData(index)
        
        if theme_mode and theme_mode != self.theme_manager.get_current_mode():
            print(f"🎨 用户切换主题模式: {theme_mode.value}")
            self.theme_manager.set_theme_mode(theme_mode)
            self.theme_mode_changed.emit(theme_mode)
    
    def _update_combo_selection(self):
        """更新下拉框选择状态"""
        current_mode = self.theme_manager.get_current_mode()
        
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current_mode:
                self.theme_combo.blockSignals(True)
                self.theme_combo.setCurrentIndex(i)
                self.theme_combo.blockSignals(False)
                break
    
    def refresh_style(self):
        """刷新样式"""
        self._apply_compact_style()
