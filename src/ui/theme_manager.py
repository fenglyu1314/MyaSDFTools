#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主题管理器

负责动态主题切换和系统主题监听
"""

import platform
from enum import Enum
from typing import Optional, Callable

from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette

from .window_configuration import WindowConfiguration


class ThemeMode(Enum):
    """主题模式枚举"""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class ThemeManager(QObject):
    """主题管理器 - 处理动态主题切换"""
    
    # 主题变化信号
    theme_changed = Signal(str)  # 发送新主题名称
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 当前主题模式
        self._current_mode = ThemeMode.SYSTEM
        self._current_theme = None
        
        # 系统主题监听定时器
        self._system_monitor_timer = QTimer()
        self._system_monitor_timer.timeout.connect(self._check_system_theme)
        self._system_monitor_timer.setInterval(1000)  # 每秒检查一次
        
        # 记录上次检测的系统主题
        self._last_system_theme = None
        
        # 初始化当前主题（延迟到第一次调用时）
        # self._update_current_theme()
        
    def start_monitoring(self):
        """开始监听系统主题变化"""
        if self._current_mode == ThemeMode.SYSTEM:
            self._system_monitor_timer.start()
            print("🎨 开始监听系统主题变化")
    
    def stop_monitoring(self):
        """停止监听系统主题变化"""
        self._system_monitor_timer.stop()
        print("🎨 停止监听系统主题变化")
    
    def set_theme_mode(self, mode: ThemeMode):
        """设置主题模式"""
        if self._current_mode == mode:
            return
            
        old_mode = self._current_mode
        self._current_mode = mode
        
        print(f"🎨 主题模式切换: {old_mode.value} -> {mode.value}")
        
        # 根据新模式更新主题
        self._update_current_theme()
        
        # 管理系统监听
        if mode == ThemeMode.SYSTEM:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def get_current_mode(self) -> ThemeMode:
        """获取当前主题模式"""
        return self._current_mode
    
    def get_current_theme(self) -> str:
        """获取当前主题名称"""
        return self._current_theme
    
    def _update_current_theme(self):
        """更新当前主题"""
        if self._current_mode == ThemeMode.LIGHT:
            new_theme = "light"
        elif self._current_mode == ThemeMode.DARK:
            new_theme = "dark"
        else:  # SYSTEM
            new_theme = "dark" if self._detect_system_dark_theme() else "light"
        
        if new_theme != self._current_theme:
            old_theme = self._current_theme
            self._current_theme = new_theme
            print(f"🎨 主题切换: {old_theme} -> {new_theme}")
            # 暂时禁用信号发送，避免初始化时的错误
            # self.theme_changed.emit(new_theme)
    
    def _check_system_theme(self):
        """检查系统主题变化（定时器回调）"""
        if self._current_mode != ThemeMode.SYSTEM:
            return
            
        current_system_theme = self._detect_system_dark_theme()
        
        if current_system_theme != self._last_system_theme:
            self._last_system_theme = current_system_theme
            print(f"🎨 检测到系统主题变化: {'深色' if current_system_theme else '浅色'}")
            self._update_current_theme()
    
    def _detect_system_dark_theme(self) -> bool:
        """检测系统是否为深色主题"""
        try:
            app = QApplication.instance()
            if not app:
                return False

            # 优先使用系统调色板检测
            palette = app.palette()

            # 检查多个颜色角色来更准确地判断主题
            window_color = palette.color(QPalette.Window)
            base_color = palette.color(QPalette.Base)
            text_color = palette.color(QPalette.WindowText)

            # 综合判断：窗口背景、基础背景都比较暗，或者文字颜色比较亮
            window_dark = window_color.lightness() < 128
            base_dark = base_color.lightness() < 128
            text_light = text_color.lightness() > 128

            # Windows 10/11 特殊处理
            if platform.system() == "Windows":
                try:
                    import winreg
                    # 检查Windows注册表中的主题设置
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                       r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                    apps_use_light_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    winreg.CloseKey(key)
                    return apps_use_light_theme == 0
                except:
                    pass

            # 如果至少两个指标表明是深色主题，则认为是深色
            dark_indicators = sum([window_dark, base_dark, text_light])
            return dark_indicators >= 2

        except Exception:
            return False  # 默认浅色主题
    
    def force_refresh_theme(self):
        """强制刷新主题（用于手动触发）"""
        print("🎨 强制刷新主题")
        self._update_current_theme()
    
    def get_theme_colors(self, theme_name: Optional[str] = None) -> dict:
        """获取指定主题的颜色方案"""
        # 如果还没有初始化主题，先初始化
        if self._current_theme is None:
            self._update_current_theme()

        if theme_name is None:
            theme_name = self._current_theme

        # 使用WindowConfiguration的现有逻辑，但允许强制指定主题
        if theme_name == "dark":
            colors = self._get_dark_color_scheme()
        else:
            colors = self._get_light_color_scheme()

        return colors
    
    def _get_dark_color_scheme(self) -> dict:
        """获取深色主题颜色方案"""
        return {
            'bg_primary': '#2b2b2b',
            'bg_secondary': '#3c3c3c',
            'bg_tertiary': '#4a4a4a',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'text_disabled': '#888888',
            'border': '#555555',
            'accent': '#2196F3',
            'accent_hover': '#1976D2',
            'accent_pressed': '#1565C0',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#F44336'
        }
    
    def _get_light_color_scheme(self) -> dict:
        """获取浅色主题颜色方案"""
        return {
            'bg_primary': '#ffffff',
            'bg_secondary': '#f5f5f5',
            'bg_tertiary': '#eeeeee',
            'text_primary': '#333333',
            'text_secondary': '#666666',
            'text_disabled': '#999999',
            'border': '#cccccc',
            'accent': '#2196F3',
            'accent_hover': '#1976D2',
            'accent_pressed': '#1565C0',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#F44336'
        }


# 全局主题管理器实例
_theme_manager_instance = None

def get_theme_manager() -> ThemeManager:
    """获取全局主题管理器实例"""
    global _theme_manager_instance
    if _theme_manager_instance is None:
        _theme_manager_instance = ThemeManager()
    return _theme_manager_instance
