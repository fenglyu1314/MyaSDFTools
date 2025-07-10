#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
窗口配置管理模块

负责窗口属性设置和配置管理
"""

from pathlib import Path
from PySide6.QtGui import QIcon


class WindowConfiguration:
    """窗口配置管理类"""

    @staticmethod
    def setup_window_properties(window):
        """设置窗口属性"""
        window.setWindowTitle("SDF工具 - 二次元脸部SDF生成")
        
        # 计算窗口总高度：内容区域 + 菜单栏 + 状态栏
        # 内容区域: 775px, 菜单栏: ~28px, 状态栏: ~25px
        total_height = 775 + 28 + 25  # = 828px
        window.setFixedSize(1318, total_height)
        
        # 设置窗口图标
        WindowConfiguration._set_window_icon(window)
        
        # 启用拖拽
        window.setAcceptDrops(True)

    @staticmethod
    def _set_window_icon(window):
        """设置窗口图标"""
        icon_path = Path("assets/icon.png")
        if icon_path.exists():
            window.setWindowIcon(QIcon(str(icon_path)))

    @staticmethod
    def get_default_window_size():
        """获取默认窗口大小"""
        return (1318, 828)

    @staticmethod
    def get_minimum_window_size():
        """获取最小窗口大小"""
        return (1200, 700)

    @staticmethod
    def apply_theme(window, theme_name="default"):
        """应用主题（预留功能）"""
        # 预留主题功能
        pass
