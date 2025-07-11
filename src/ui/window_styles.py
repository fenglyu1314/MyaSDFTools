#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
窗口样式定义模块

提供统一的主题样式和按钮样式定义
"""

class ThemeStyles:
    """统一的主题样式系统"""

    @staticmethod
    def get_theme_colors():
        """获取主题颜色"""
        # 暂时直接使用原有的检测方式，避免主题管理器的循环依赖问题
        is_dark_theme = ThemeStyles._detect_dark_theme()
        return ThemeStyles._get_color_scheme(is_dark_theme)

    @staticmethod
    def _detect_dark_theme() -> bool:
        """检测是否为深色主题"""
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtGui import QPalette

            app = QApplication.instance()
            if not app:
                return False

            # 尝试使用新的ColorScheme API
            style_hints = app.styleHints()
            if hasattr(style_hints, 'colorScheme') and hasattr(style_hints, 'ColorScheme'):
                color_scheme = style_hints.colorScheme()
                return color_scheme == style_hints.ColorScheme.Dark

            # 回退到调色板检测
            palette = app.palette()
            window_color = palette.color(QPalette.Window)
            return window_color.lightness() < 128

        except Exception:
            return False  # 默认浅色主题

    @staticmethod
    def _get_color_scheme(is_dark: bool) -> dict:
        """获取颜色方案"""
        if is_dark:
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
        else:
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


class ButtonStyles:
    """统一的按钮样式"""

    @staticmethod
    def primary_button(size="normal"):
        """主要按钮样式"""
        colors = ThemeStyles.get_theme_colors()
        height = "36px" if size == "normal" else "32px" if size == "small" else "28px"
        font_size = "14px" if size == "normal" else "13px" if size == "small" else "12px"
        return f"""
            QPushButton {{
                background-color: {colors['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: {font_size};
                font-weight: bold;
                min-height: {height};
                padding: 0px 12px;
            }}
            QPushButton:hover:enabled {{
                background-color: {colors['accent_hover']};
            }}
            QPushButton:pressed:enabled {{
                background-color: {colors['accent_pressed']};
            }}
            QPushButton:disabled {{
                background-color: {colors['bg_tertiary']};
                color: {colors['text_disabled']};
            }}
        """

    @staticmethod
    def success_button(size="normal"):
        """成功按钮样式"""
        colors = ThemeStyles.get_theme_colors()
        height = "36px" if size == "normal" else "32px" if size == "small" else "28px"
        font_size = "14px" if size == "normal" else "13px" if size == "small" else "12px"
        return f"""
            QPushButton {{
                background-color: {colors['success']};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: {font_size};
                font-weight: bold;
                min-height: {height};
                padding: 0px 12px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
            QPushButton:pressed {{
                background-color: #3d8b40;
            }}
        """

    @staticmethod
    def secondary_button(size="normal"):
        """次要按钮样式"""
        colors = ThemeStyles.get_theme_colors()
        height = "36px" if size == "normal" else "32px" if size == "small" else "28px"
        font_size = "14px" if size == "normal" else "13px" if size == "small" else "12px"
        return f"""
            QPushButton {{
                background-color: {colors['bg_tertiary']};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                font-size: {font_size};
                font-weight: bold;
                min-height: {height};
                padding: 0px 12px;
            }}
            QPushButton:hover:enabled {{
                background-color: {colors['bg_secondary']};
            }}
            QPushButton:pressed:enabled {{
                background-color: {colors['border']};
            }}
            QPushButton:disabled {{
                background-color: {colors['bg_tertiary']};
                color: {colors['text_disabled']};
            }}
        """

    @staticmethod
    def danger_button(size="normal"):
        """危险按钮样式"""
        colors = ThemeStyles.get_theme_colors()
        height = "36px" if size == "normal" else "32px" if size == "small" else "28px"
        font_size = "14px" if size == "normal" else "13px" if size == "small" else "12px"
        return f"""
            QPushButton {{
                background-color: {colors['error']};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: {font_size};
                font-weight: bold;
                min-height: {height};
                padding: 0px 12px;
            }}
            QPushButton:hover:enabled {{
                background-color: #d32f2f;
            }}
            QPushButton:pressed:enabled {{
                background-color: #b71c1c;
            }}
            QPushButton:disabled {{
                background-color: {colors['bg_tertiary']};
                color: {colors['text_disabled']};
            }}
        """


class LayoutConstants:
    """布局常量定义"""

    # 基础尺寸单位
    BASE_UNIT = 8  # 基础单位，所有尺寸都是此单位的倍数

    # 间距定义
    SPACING_TINY = BASE_UNIT // 2      # 4px
    SPACING_SMALL = BASE_UNIT          # 8px
    SPACING_MEDIUM = BASE_UNIT * 2     # 16px
    SPACING_LARGE = BASE_UNIT * 3      # 24px

    # 边距定义
    MARGIN_SMALL = BASE_UNIT           # 8px
    MARGIN_MEDIUM = BASE_UNIT * 2      # 16px
    MARGIN_LARGE = BASE_UNIT * 3       # 24px

    # 组件尺寸比例
    CARD_ASPECT_RATIO = 1.18           # 卡片宽高比 (110/130)
    PREVIEW_ASPECT_RATIO = 1.0         # 预览区域宽高比

    # 最小尺寸
    MIN_CARD_SIZE = BASE_UNIT * 10     # 80px
    MIN_BUTTON_HEIGHT = BASE_UNIT * 4  # 32px
    MIN_PREVIEW_SIZE = BASE_UNIT * 25  # 200px


class ResponsiveLayout:
    """响应式布局计算器"""

    @staticmethod
    def calculate_card_size(container_width: int, max_cards: int = 8) -> tuple[int, int]:
        """计算卡片尺寸"""
        # 参考区域2的SDF卡片尺寸，保持一致性
        # 区域1稍微增加高度以容纳删除按钮
        card_width = 110   # 与区域2一致的宽度
        card_height = 130  # 比区域2稍高，容纳删除按钮

        return card_width, card_height

    @staticmethod
    def calculate_container_size(card_count: int, card_size: tuple[int, int]) -> tuple[int, int]:
        """计算容器尺寸"""
        card_width, card_height = card_size

        # 计算容器宽度
        margins = LayoutConstants.MARGIN_SMALL * 2
        spacings = LayoutConstants.SPACING_SMALL * (card_count - 1) if card_count > 1 else 0
        container_width = card_width * card_count + spacings + margins

        # 计算容器高度（卡片高度 + 上下边距）
        container_height = card_height + LayoutConstants.MARGIN_SMALL * 2

        return container_width, container_height

    @staticmethod
    def calculate_preview_size(available_width: int, available_height: int) -> tuple[int, int]:
        """计算预览区域尺寸"""
        # 保持正方形比例，取较小值
        size = min(available_width, available_height)
        size = max(size, LayoutConstants.MIN_PREVIEW_SIZE)
        return size, size

    @staticmethod
    def calculate_button_size(text: str, min_width: int | None = None) -> tuple[int, int]:
        """计算按钮尺寸"""
        # 基于文本长度计算宽度
        text_width = len(text) * LayoutConstants.BASE_UNIT + LayoutConstants.MARGIN_MEDIUM * 2
        width = max(text_width, min_width or LayoutConstants.BASE_UNIT * 20)  # 最小160px
        height = LayoutConstants.MIN_BUTTON_HEIGHT + LayoutConstants.BASE_UNIT  # 40px
        return width, height


class WidgetStyles:
    """通用组件样式"""

    @staticmethod
    def group_box_style():
        """分组框样式"""
        colors = ThemeStyles.get_theme_colors()
        return f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {colors['border']};
                border-radius: 4px;
                margin-top: {LayoutConstants.SPACING_SMALL}px;
                padding-top: {LayoutConstants.SPACING_SMALL}px;
                background-color: {colors['bg_primary']};
                color: {colors['text_primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {LayoutConstants.SPACING_SMALL}px;
                padding: 0 4px 0 4px;
                background-color: {colors['bg_primary']};
            }}
        """

    @staticmethod
    def slider_style():
        """滑竿样式"""
        colors = ThemeStyles.get_theme_colors()
        return f"""
            QSlider::groove:horizontal {{
                border: 1px solid {colors['border']};
                height: 6px;
                background: {colors['bg_secondary']};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {colors['accent']};
                border: 1px solid {colors['border']};
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {colors['accent_hover']};
            }}
        """

    @staticmethod
    def progress_bar_style():
        """进度条样式"""
        colors = ThemeStyles.get_theme_colors()
        return f"""
            QProgressBar {{
                border: 1px solid {colors['border']};
                border-radius: 3px;
                background-color: {colors['bg_secondary']};
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {colors['accent']};
                border-radius: 2px;
            }}
        """
