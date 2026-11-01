#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI模块 - 用户界面相关组件

分层约定（每个组件只保留一份实现）:
- main_window.py          主窗口，负责协调各管理器
- ui_layout_manager.py    布局装配
- ui_signal_manager.py    信号连接
- event_handlers.py       事件处理与业务编排
- image_card_widget.py    图像卡片与卡片容器（唯一实现）
- ui_components.py        UI 组件工厂（唯一实现）
"""

from .main_window import MainWindow

__all__ = ['MainWindow']
