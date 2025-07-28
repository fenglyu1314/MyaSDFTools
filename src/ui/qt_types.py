#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Qt类型提示辅助模块

为了解决Pylance对PySide6 Qt枚举值的类型检查问题，
提供常用的Qt枚举值的类型安全导入。

使用方法：
    from .qt_types import Qt_Horizontal, Qt_AlignCenter
    
    # 替代直接使用 Qt.Horizontal
    slider = QSlider(Qt_Horizontal)
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy

# 常用的Qt枚举值
# 方向相关
Qt_Horizontal = Qt.Orientation.Horizontal
Qt_Vertical = Qt.Orientation.Vertical

# 对齐相关
Qt_AlignLeft = Qt.AlignmentFlag.AlignLeft
Qt_AlignRight = Qt.AlignmentFlag.AlignRight
Qt_AlignCenter = Qt.AlignmentFlag.AlignCenter
Qt_AlignTop = Qt.AlignmentFlag.AlignTop
Qt_AlignBottom = Qt.AlignmentFlag.AlignBottom
Qt_AlignHCenter = Qt.AlignmentFlag.AlignHCenter
Qt_AlignVCenter = Qt.AlignmentFlag.AlignVCenter

# 缩放相关
Qt_KeepAspectRatio = Qt.AspectRatioMode.KeepAspectRatio
Qt_IgnoreAspectRatio = Qt.AspectRatioMode.IgnoreAspectRatio
Qt_KeepAspectRatioByExpanding = Qt.AspectRatioMode.KeepAspectRatioByExpanding

# 变换相关
Qt_SmoothTransformation = Qt.TransformationMode.SmoothTransformation
Qt_FastTransformation = Qt.TransformationMode.FastTransformation

# 鼠标按钮
Qt_LeftButton = Qt.MouseButton.LeftButton
Qt_RightButton = Qt.MouseButton.RightButton
Qt_MiddleButton = Qt.MouseButton.MiddleButton

# 键盘修饰符
Qt_NoModifier = Qt.KeyboardModifier.NoModifier
Qt_ShiftModifier = Qt.KeyboardModifier.ShiftModifier
Qt_ControlModifier = Qt.KeyboardModifier.ControlModifier
Qt_AltModifier = Qt.KeyboardModifier.AltModifier

# 窗口状态
Qt_WindowNoState = Qt.WindowState.WindowNoState
Qt_WindowMinimized = Qt.WindowState.WindowMinimized
Qt_WindowMaximized = Qt.WindowState.WindowMaximized
Qt_WindowFullScreen = Qt.WindowState.WindowFullScreen

# 焦点策略
Qt_NoFocus = Qt.FocusPolicy.NoFocus
Qt_TabFocus = Qt.FocusPolicy.TabFocus
Qt_ClickFocus = Qt.FocusPolicy.ClickFocus
Qt_StrongFocus = Qt.FocusPolicy.StrongFocus
Qt_WheelFocus = Qt.FocusPolicy.WheelFocus

# 大小策略
Qt_Fixed = QSizePolicy.Policy.Fixed
Qt_Minimum = QSizePolicy.Policy.Minimum
Qt_Maximum = QSizePolicy.Policy.Maximum
Qt_Preferred = QSizePolicy.Policy.Preferred
Qt_Expanding = QSizePolicy.Policy.Expanding
Qt_MinimumExpanding = QSizePolicy.Policy.MinimumExpanding
Qt_Ignored = QSizePolicy.Policy.Ignored

# 滚动条策略
Qt_ScrollBarAsNeeded = Qt.ScrollBarPolicy.ScrollBarAsNeeded
Qt_ScrollBarAlwaysOff = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
Qt_ScrollBarAlwaysOn = Qt.ScrollBarPolicy.ScrollBarAlwaysOn

# 文本交互标志
Qt_NoTextInteraction = Qt.TextInteractionFlag.NoTextInteraction
Qt_TextSelectableByMouse = Qt.TextInteractionFlag.TextSelectableByMouse
Qt_TextSelectableByKeyboard = Qt.TextInteractionFlag.TextSelectableByKeyboard
Qt_LinksAccessibleByMouse = Qt.TextInteractionFlag.LinksAccessibleByMouse
Qt_LinksAccessibleByKeyboard = Qt.TextInteractionFlag.LinksAccessibleByKeyboard
Qt_TextEditable = Qt.TextInteractionFlag.TextEditable
Qt_TextEditorInteraction = Qt.TextInteractionFlag.TextEditorInteraction
Qt_TextBrowserInteraction = Qt.TextInteractionFlag.TextBrowserInteraction

# 为了向后兼容，也提供原始的Qt对象
QtCore_Qt = Qt

# 导出所有常用的枚举值
__all__ = [
    'Qt_Horizontal', 'Qt_Vertical',
    'Qt_AlignLeft', 'Qt_AlignRight', 'Qt_AlignCenter', 'Qt_AlignTop', 'Qt_AlignBottom',
    'Qt_AlignHCenter', 'Qt_AlignVCenter',
    'Qt_KeepAspectRatio', 'Qt_IgnoreAspectRatio', 'Qt_KeepAspectRatioByExpanding',
    'Qt_SmoothTransformation', 'Qt_FastTransformation',
    'Qt_LeftButton', 'Qt_RightButton', 'Qt_MiddleButton',
    'Qt_NoModifier', 'Qt_ShiftModifier', 'Qt_ControlModifier', 'Qt_AltModifier',
    'Qt_WindowNoState', 'Qt_WindowMinimized', 'Qt_WindowMaximized', 'Qt_WindowFullScreen',
    'Qt_NoFocus', 'Qt_TabFocus', 'Qt_ClickFocus', 'Qt_StrongFocus', 'Qt_WheelFocus',
    'Qt_Fixed', 'Qt_Minimum', 'Qt_Maximum', 'Qt_Preferred', 'Qt_Expanding',
    'Qt_MinimumExpanding', 'Qt_Ignored',
    'Qt_ScrollBarAsNeeded', 'Qt_ScrollBarAlwaysOff', 'Qt_ScrollBarAlwaysOn',
    'Qt_NoTextInteraction', 'Qt_TextSelectableByMouse', 'Qt_TextSelectableByKeyboard',
    'Qt_LinksAccessibleByMouse', 'Qt_LinksAccessibleByKeyboard', 'Qt_TextEditable',
    'Qt_TextEditorInteraction', 'Qt_TextBrowserInteraction',
    'QtCore_Qt'
]
