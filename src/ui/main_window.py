#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主窗口模块

实现SDF工具的主界面，包含：
- 图像导入区域
- SDF预览区域  
- 参数控制面板
- 菜单栏和状态栏
"""

import sys
import os
import time
from pathlib import Path
from typing import Optional, List, Dict

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QProgressBar, QStatusBar, QMenuBar,
    QFileDialog, QMessageBox, QSplitter, QGroupBox, QSlider,
    QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QTextEdit,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QSize
from PySide6.QtGui import QPixmap, QAction, QIcon, QFont, QDragEnterEvent, QDropEvent

# 导入自定义组件
from .image_list_widget import ImageListWidget
from .preview_widget import PreviewWidget
from .parameter_widget import ParameterWidget
from .image_card_widget import ImageCardsContainer
from .sdf_card_widget import SDFCardsContainer
from .zoomable_image_widget import ZoomableImageWidget

# 导入核心模块
from ..core.sdf_generator import SDFGenerator
from ..core.image_manager import ImageManager
from ..utils.image_utils import ImageUtils

class ThemeStyles:
    """统一的主题样式系统"""

    @staticmethod
    def get_theme_colors():
        """获取主题颜色"""
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
    def warning_button(size="normal"):
        """警告按钮样式"""
        height = "36px" if size == "normal" else "32px" if size == "small" else "28px"
        font_size = "14px" if size == "normal" else "13px" if size == "small" else "12px"
        return f"""
            QPushButton {{
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: {font_size};
                font-weight: bold;
                min-height: {height};
                padding: 0px 12px;
            }}
            QPushButton:hover:enabled {{
                background-color: #F57C00;
            }}
            QPushButton:pressed:enabled {{
                background-color: #E65100;
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
                color: #666666;
            }}
        """

    @staticmethod
    def secondary_button(size="normal"):
        """次要按钮样式"""
        height = "36px" if size == "normal" else "32px" if size == "small" else "24px"
        font_size = "14px" if size == "normal" else "13px" if size == "small" else "11px"
        return f"""
            QPushButton {{
                background-color: #607D8B;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: {font_size};
                font-weight: bold;
                min-height: {height};
                padding: 0px 12px;
            }}
            QPushButton:hover {{
                background-color: #546E7A;
            }}
            QPushButton:pressed {{
                background-color: #455A64;
            }}
        """

class MainWindow(QMainWindow):
    """SDF工具主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SDF工具 - 二次元脸部SDF生成")
        # 设置固定窗口大小，根据各区域实际需求计算
        # 左侧：1000px（区域1+2+4&5横向+按钮），右侧：300px（区域3参数控制），边距和间距：18px
        self.setFixedSize(1318, 775)  # 1000(左侧)+300(右侧)+18(边距和间距) = 1318px，高度保持775px
        
        # 初始化变量
        self.current_images: List[str] = []
        self.sdf_result: Optional[object] = None
        self.computation_time: float = 0.0

        # 批量处理相关
        self.batch_sdf_results: Dict[str, object] = {}  # 存储每张图像的SDF结果
        self.batch_processing: bool = False

        # 新UI相关变量
        self.current_sdf_results: Dict[str, object] = {}  # 存储每张图像的SDF结果
        self.current_merged_sdf: Optional[object] = None  # 存储合并后的SDF

        # 初始化核心组件
        self.sdf_generator = SDFGenerator()
        self.image_manager = ImageManager()
        
        # 设置窗口图标
        self._set_window_icon()
        
        # 初始化UI
        self._init_ui()
        self._init_status_bar()
        self._connect_signals()
        
        # 启用拖拽
        self.setAcceptDrops(True)
        
        # 显示欢迎信息
        self._show_welcome_message()
    
    def _set_window_icon(self):
        """设置窗口图标"""
        icon_path = Path("assets/icon.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
    
    def _init_ui(self):
        """初始化用户界面 - 简化布局，消除多余容器嵌套"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局 - 水平分割，直接添加区域
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)  # 减小边距
        main_layout.setSpacing(8)  # 减小间距

        # 左侧垂直布局 - 直接添加区域，无多余容器
        left_layout = QVBoxLayout()

        # 区域1: 图像导入区域
        image_import_area = self._create_image_import_area()
        image_import_area.setFixedSize(1000, 210)  # 宽度1000px，适合10个100px图像卡片
        left_layout.addWidget(image_import_area)

        # 区域2: SDF结果区域
        sdf_results_area = self._create_sdf_results_area()
        sdf_results_area.setFixedSize(1000, 160)  # 宽度1000px，与区域1保持一致
        left_layout.addWidget(sdf_results_area)

        # 区域4和5: 合并SDF预览和光照效果预览区域 - 横向并排
        preview_areas_layout = QHBoxLayout()
        preview_areas_layout.setSpacing(8)

        # 区域4: 合并SDF预览区域
        merged_sdf_area = self._create_merged_sdf_area()
        merged_sdf_area.setFixedSize(490, 350)  # 调整宽度适应横向布局
        preview_areas_layout.addWidget(merged_sdf_area)

        # 区域5: 光照效果预览区域
        lighting_preview_area = self._create_lighting_preview_area()
        lighting_preview_area.setFixedSize(490, 350)  # 调整宽度适应横向布局，高度与区域4保持一致
        preview_areas_layout.addWidget(lighting_preview_area)

        left_layout.addLayout(preview_areas_layout)

        # 右侧垂直布局 - 区域3参数控制 + 操作按钮
        right_layout = QVBoxLayout()

        # 区域3: 参数控制区域 - 移到右侧，竖向放置
        parameter_area = self._create_parameter_area()
        parameter_area.setFixedSize(300, 580)  # 调整高度为按钮区域留出更多空间
        right_layout.addWidget(parameter_area)

        # 操作按钮区域 - 移到右侧
        button_area = self._create_button_area()
        button_area.setFixedSize(300, 140)  # 增加高度：3个按钮(35*3=105) + 间距(8*2=16) + 边距(10*2=20) = 141px
        right_layout.addWidget(button_area)

        # 直接添加布局到主布局，无多余容器包装
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

    def _create_image_import_area(self) -> QWidget:
        """创建图像导入区域 - 固定尺寸布局"""
        area = QGroupBox("1. 图像导入")
        layout = QVBoxLayout(area)
        layout.setContentsMargins(4, 4, 4, 4)  # 适当的边距

        # 图像卡片容器 - 固定高度确保卡片完整显示
        self.image_cards_container = ImageCardsContainer()
        self.image_cards_container.setFixedHeight(200)  # 调整高度适应新的区域尺寸
        layout.addWidget(self.image_cards_container)

        # 进度条 - 固定位置，避免重叠
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(10)  # 稍微增加高度
        layout.addWidget(self.progress_bar)

        return area

    def _create_sdf_results_area(self) -> QWidget:
        """创建SDF生成结果区域 - 固定尺寸布局"""
        area = QGroupBox("2. SDF生成结果")
        layout = QVBoxLayout(area)
        layout.setContentsMargins(4, 4, 4, 4)  # 适当的边距
        # layout.setSpacing(10)

        # SDF结果卡片容器 - 固定高度确保卡片完整显示
        self.sdf_cards_container = SDFCardsContainer()
        self.sdf_cards_container.setFixedHeight(160)  # 调整高度适应新的区域尺寸
        layout.addWidget(self.sdf_cards_container)

        return area

    def _create_parameter_area(self) -> QWidget:
        """创建参数控制区域 - 仅包含参数，不包含按钮"""
        area = QGroupBox("3. SDF参数控制")
        layout = QVBoxLayout(area)
        layout.setContentsMargins(4, 4, 4, 4)  # 减小边距
        # layout.setSpacing(5)  # 减小间距

        # 参数控制组件 - 直接添加
        self.parameter_widget = ParameterWidget()
        layout.addWidget(self.parameter_widget)

        return area

    def _create_button_area(self) -> QWidget:
        """创建操作按钮区域 - 适应右侧垂直布局，防止重叠"""
        area = QWidget()  # 不使用QGroupBox，减少边距
        layout = QVBoxLayout(area)  # 改为垂直布局适应右侧
        layout.setContentsMargins(10, 10, 10, 10)  # 左右上下边距各10px
        layout.setSpacing(8)  # 按钮间距8px

        # 按钮宽度计算：容器宽度300 - 左右边距20 = 280px
        button_width = 280
        button_height = 35

        self.import_btn = QPushButton("导入图像")
        self.import_btn.setStyleSheet(ButtonStyles.success_button("normal"))
        self.import_btn.setFixedSize(button_width, button_height)
        layout.addWidget(self.import_btn)

        self.generate_btn = QPushButton("生成SDF")
        self.generate_btn.setEnabled(False)
        self.generate_btn.setStyleSheet(ButtonStyles.primary_button("normal"))
        self.generate_btn.setFixedSize(button_width, button_height)
        layout.addWidget(self.generate_btn)

        self.export_btn = QPushButton("导出")
        self.export_btn.setEnabled(False)
        self.export_btn.setStyleSheet(ButtonStyles.secondary_button("normal"))
        self.export_btn.setFixedSize(button_width, button_height)
        layout.addWidget(self.export_btn)

        return area

    def _create_merged_sdf_area(self) -> QWidget:
        """创建合并SDF预览区域 - 最小边距布局"""
        area = QGroupBox("4. 合并SDF预览")
        layout = QVBoxLayout(area)

        # 预览图像区域 - 使用可缩放组件，精确计算尺寸
        self.merged_sdf_preview = ZoomableImageWidget()
        self.merged_sdf_preview.setFixedSize(470, 280)  # 调整为横向布局适合的尺寸
        self.merged_sdf_preview.zoom_changed.connect(self._on_merged_sdf_zoom_changed)
        layout.addWidget(self.merged_sdf_preview)

        # 控制区域 - 紧凑布局
        control_layout = QHBoxLayout()

        # 缩放控制
        control_layout.addWidget(QLabel("缩放:"))
        
        self.fit_btn = QPushButton("适应")
        self.fit_btn.setStyleSheet(ButtonStyles.secondary_button("tiny"))
        self.fit_btn.setFixedSize(50, 25)
        control_layout.addWidget(self.fit_btn)
        
        self.actual_btn = QPushButton("1:1")
        self.actual_btn.setStyleSheet(ButtonStyles.secondary_button("tiny"))
        self.actual_btn.setFixedSize(40, 25)
        control_layout.addWidget(self.actual_btn)
        
        self.reset_btn = QPushButton("重置")
        self.reset_btn.setStyleSheet(ButtonStyles.secondary_button("tiny"))
        self.reset_btn.setFixedSize(50, 25)
        control_layout.addWidget(self.reset_btn)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(50)
        control_layout.addWidget(self.zoom_label)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)

        return area

    def _create_lighting_preview_area(self) -> QWidget:
        """创建光照效果预览区域 - 最小边距布局"""
        area = QGroupBox("5. 光照效果预览")
        layout = QVBoxLayout(area)
        #layout.setContentsMargins(8, 12, 8, 8)  # 最小边距
        #layout.setSpacing(4)  # 最小间距

        # 预览图像区域 - 固定显示，精确计算尺寸
        self.lighting_preview = QLabel("光照效果预览\n\n生成SDF后将在此显示")
        self.lighting_preview.setFixedSize(470, 280)  # 调整为与区域4保持一致的尺寸
        self.lighting_preview.setAlignment(Qt.AlignCenter)

        # 应用主题样式
        colors = ThemeStyles.get_theme_colors()
        self.lighting_preview.setStyleSheet(f"""
            QLabel {{
                border: 1px solid {colors['border']};
                background-color: {colors['bg_secondary']};
                color: {colors['text_disabled']};
                font-size: 14px;
            }}
        """)
        layout.addWidget(self.lighting_preview)

        # 光照控制区域 - 简化为只保留光照角度
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(10, 5, 10, 5)
        control_layout.setSpacing(8)

        # 光照角度 - 范围-180到180
        control_layout.addWidget(QLabel("光照角度:"))
        self.angle_slider = QSlider(Qt.Horizontal)
        self.angle_slider.setRange(-180, 180)
        self.angle_slider.setValue(0)  # 默认0度
        self.angle_slider.setFixedHeight(25)
        control_layout.addWidget(self.angle_slider)
        self.angle_value_label = QLabel("0°")
        self.angle_value_label.setFixedWidth(50)  # 增加宽度以显示负数
        control_layout.addWidget(self.angle_value_label)

        layout.addLayout(control_layout)

        return area


    
    def _create_preview_panel(self) -> QWidget:
        """创建中间预览面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(3, 3, 3, 3)  # 减少边距
        layout.setSpacing(5)  # 减少间距

        # 预览区域标题 - 更紧凑
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(5, 0, 5, 0)

        preview_title = QLabel("SDF预览")
        preview_title.setFont(QFont("Arial", 13, QFont.Bold))  # 减小字体
        title_layout.addWidget(preview_title)

        title_layout.addStretch()

        # 快速操作按钮组 - 更紧凑
        quick_btn_layout = QHBoxLayout()
        quick_btn_layout.setSpacing(3)

        # 适应窗口按钮 - 使用统一样式
        self.fit_btn = QPushButton("适应")
        self.fit_btn.setMaximumWidth(50)
        self.fit_btn.setStyleSheet(ButtonStyles.secondary_button("tiny"))
        quick_btn_layout.addWidget(self.fit_btn)

        # 实际大小按钮 - 使用统一样式
        self.actual_btn = QPushButton("1:1")
        self.actual_btn.setMaximumWidth(40)
        self.actual_btn.setStyleSheet(ButtonStyles.secondary_button("tiny"))
        quick_btn_layout.addWidget(self.actual_btn)

        # 重置按钮 - 使用统一样式
        self.reset_btn = QPushButton("重置")
        self.reset_btn.setMaximumWidth(50)
        self.reset_btn.setStyleSheet(ButtonStyles.secondary_button("tiny"))
        quick_btn_layout.addWidget(self.reset_btn)

        title_layout.addLayout(quick_btn_layout)
        layout.addLayout(title_layout)

        # 预览组件
        self.preview_widget = PreviewWidget()
        layout.addWidget(self.preview_widget)

        # 简化的操作提示
        hint_label = QLabel("💡 滚轮缩放 | 左键拖拽 | 右侧调节参数")
        hint_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 10px;
                padding: 3px 8px;
                background-color: #F8F9FA;
                border: 1px solid #E9ECEF;
                border-radius: 3px;
            }
        """)
        hint_label.setMaximumHeight(20)
        layout.addWidget(hint_label)

        return panel

    def _create_parameter_panel(self) -> QWidget:
        """创建右侧参数控制面板"""
        panel = QWidget()
        # panel.setMaximumWidth(280)  # 限制最大宽度
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(5)

        # 参数控制区域
        self.parameter_widget = ParameterWidget()
        layout.addWidget(self.parameter_widget)

        # 添加弹性空间
        layout.addStretch()

        return panel

    def _init_menu_bar(self):
        """初始化菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        # 导入图像
        import_action = QAction("导入图像(&I)", self)
        import_action.setShortcut("Ctrl+I")
        import_action.setStatusTip("导入图像文件")
        import_action.triggered.connect(self._import_images)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        # 导出SDF
        export_action = QAction("导出SDF(&E)", self)
        export_action.setShortcut("Ctrl+E")
        export_action.setStatusTip("导出SDF结果")
        export_action.setEnabled(False)
        export_action.triggered.connect(self._export_sdf)
        file_menu.addAction(export_action)
        self.export_action = export_action

        file_menu.addSeparator()

        # 退出
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("退出程序")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")

        # 清空图像
        clear_action = QAction("清空图像(&C)", self)
        clear_action.setShortcut("Ctrl+Delete")
        clear_action.setStatusTip("清空所有导入的图像")
        clear_action.triggered.connect(self._clear_images)
        edit_menu.addAction(clear_action)

        edit_menu.addSeparator()

        # 批量处理菜单
        batch_menu = edit_menu.addMenu("批量处理(&B)")

        # 批量导入
        batch_import_action = QAction("批量导入文件夹(&I)", self)
        batch_import_action.setShortcut("Ctrl+Shift+I")
        batch_import_action.setStatusTip("批量导入文件夹中的所有图像")
        batch_import_action.triggered.connect(self._batch_import_folder)
        batch_menu.addAction(batch_import_action)

        # 批量生成SDF
        batch_generate_action = QAction("批量生成SDF(&G)", self)
        batch_generate_action.setShortcut("Ctrl+Shift+G")
        batch_generate_action.setStatusTip("为每张图像单独生成SDF")
        batch_generate_action.triggered.connect(self._batch_generate_sdf)
        batch_menu.addAction(batch_generate_action)

        # 批量导出
        batch_export_action = QAction("批量导出(&E)", self)
        batch_export_action.setShortcut("Ctrl+Shift+E")
        batch_export_action.setStatusTip("批量导出所有SDF结果")
        batch_export_action.triggered.connect(self._batch_export_sdf)
        batch_menu.addAction(batch_export_action)

        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")

        # 重置视图
        reset_view_action = QAction("重置视图(&R)", self)
        reset_view_action.setShortcut("Ctrl+R")
        reset_view_action.setStatusTip("重置预览视图")
        reset_view_action.triggered.connect(self._reset_view)
        view_menu.addAction(reset_view_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        # 关于
        about_action = QAction("关于(&A)", self)
        about_action.setStatusTip("关于SDF工具")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _init_status_bar(self):
        """初始化状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)

        # 计算时间标签
        self.time_label = QLabel("")
        self.status_bar.addPermanentWidget(self.time_label)

        # 图像数量标签
        self.image_count_label = QLabel("图像: 0")
        self.status_bar.addPermanentWidget(self.image_count_label)



    def _connect_signals(self):
        """连接信号和槽"""
        # 按钮信号
        self.import_btn.clicked.connect(self._import_images)
        self.generate_btn.clicked.connect(self._generate_sdf)
        self.export_btn.clicked.connect(self._export_sdf)

        # 预览快速操作按钮
        self.fit_btn.clicked.connect(self._fit_to_window)
        self.actual_btn.clicked.connect(self._actual_size)
        self.reset_btn.clicked.connect(self._reset_view)

        # 合并SDF预览缩放信号
        self.merged_sdf_preview.zoom_changed.connect(self._on_merged_sdf_zoom_changed)

        # 光照控制滑竿
        self.angle_slider.valueChanged.connect(self._on_angle_changed)

        # 混合模式信号连接已移除（现在由参数控制区域统一管理）

        # 图像卡片容器信号
        self.image_cards_container.images_changed.connect(self._on_images_changed)
        self.image_cards_container.angle_changed.connect(self._on_angle_changed_card)

        # 参数组件信号
        self.parameter_widget.parameters_changed.connect(self._on_parameters_changed)

    def _show_welcome_message(self):
        """显示欢迎信息"""
        self.status_label.setText("欢迎使用SDF工具！请导入图像开始使用。")

    def _on_angle_changed(self, value):
        """光照角度改变"""
        self.angle_value_label.setText(f"{value}°")
        self._update_lighting_preview()

    # 光照强度和环境光方法已移除，现在使用固定值

    def _update_lighting_preview(self):
        """更新光照效果预览"""
        # 检查是否有合并的SDF数据
        if not hasattr(self, 'current_merged_sdf') or self.current_merged_sdf is None:
            return

        try:
            # 获取光照参数
            angle = self.angle_slider.value()
            intensity = 1.0  # 固定光照强度
            ambient = 0.3   # 固定环境光

            # 生成光照效果
            lighting_result = self._apply_lighting_effect(
                self.current_merged_sdf,
                angle,
                intensity,
                ambient
            )

            if lighting_result is not None:
                # 转换为QPixmap并显示
                lighting_pixmap = self._numpy_to_pixmap(lighting_result)
                if not lighting_pixmap.isNull():
                    # 缩放到预览区域大小，保持宽高比并居中显示
                    scaled_pixmap = lighting_pixmap.scaled(
                        self.lighting_preview.width(),
                        self.lighting_preview.height(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.lighting_preview.setPixmap(scaled_pixmap)
                    self.lighting_preview.setText("")  # 清除文本
                    # 确保图像居中显示
                    self.lighting_preview.setAlignment(Qt.AlignCenter)
                else:
                    self.lighting_preview.setText("光照效果\n生成失败")

        except Exception as e:
            print(f"更新光照预览失败: {e}")
            self.lighting_preview.setText("光照效果\n预览错误")

    def _apply_lighting_effect(self, sdf_data, angle_deg, intensity, ambient):
        """
        应用光照效果到SDF数据

        角度范围：-180到180度
        - 0到-180度：SDF左右镜像反转后映射到0-1，与角度映射值比较
        - 0到180度：SDF正常映射到0-1，与角度映射值比较
        - 比较规则：SDF值 > 角度映射值 → 白色，否则 → 黑色
        """
        try:
            import numpy as np

            # 确保SDF数据是numpy数组
            if not isinstance(sdf_data, np.ndarray):
                return None

            # 归一化SDF数据到0-1范围
            sdf_normalized = sdf_data.astype(np.float32)
            if sdf_normalized.max() > 1.0:
                sdf_normalized = sdf_normalized / 255.0

            # 根据角度范围处理SDF数据
            if angle_deg <= 0:  # 0到-180度范围
                # SDF左右镜像反转
                sdf_processed = np.fliplr(sdf_normalized)
                # 角度映射：-180到0 映射到 0到1
                angle_mapped = 1 - ((angle_deg + 180) / 180.0)
            else:  # 0到180度范围
                # SDF正常使用
                sdf_processed = sdf_normalized
                # 角度映射：0到180 映射到 0到1
                angle_mapped = angle_deg / 180.0

            # 比较SDF值与角度映射值
            # SDF值 > 角度映射值 → 白色(1)，否则 → 黑色(0)
            result = (sdf_processed > angle_mapped).astype(np.float32)

            # 转换回0-255范围用于显示
            result = (result * 255).astype(np.uint8)

            return result

        except Exception as e:
            print(f"应用光照效果失败: {e}")
            return None



    def _on_angle_changed_card(self, image_path, angle):
        """图像卡片角度改变"""
        print(f"图像 {Path(image_path).name} 角度改变为 {angle}°，需要重新生成SDF")

    def _on_parameters_changed(self):
        """参数变化时的处理"""
        # 参数变化时只记录，不自动重新生成
        print("SDF参数已更改，需要重新生成SDF")

    def _on_images_changed(self):
        """图像列表变化时的处理"""
        count = self.image_cards_container.get_image_count()
        self.image_count_label.setText(f"图像: {count}")
        self.generate_btn.setEnabled(count > 0)

        # 同步更新SDF卡片
        images_data = self.image_cards_container.get_images_data()
        self.sdf_cards_container.update_cards_from_images(images_data)

        # 参数组件不需要图像数量信息（已简化）

        if count == 0:
            self.status_label.setText("请导入图像开始使用")
        else:
            self.status_label.setText(f"已导入 {count} 张图像")

    # 拖拽事件处理
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否包含图像文件
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile():
                    file_path = Path(url.toLocalFile())
                    if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tga']:
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        urls = event.mimeData().urls()
        image_files = []

        for url in urls:
            if url.isLocalFile():
                file_path = Path(url.toLocalFile())
                if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tga']:
                    image_files.append(str(file_path))

        if image_files:
            self._add_images(image_files)
            event.acceptProposedAction()
        else:
            event.ignore()

    # 槽函数实现
    def _import_images(self):
        """导入图像文件"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("图像文件 (*.png *.jpg *.jpeg *.bmp *.tga)")
        file_dialog.setViewMode(QFileDialog.Detail)

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            self._add_images(file_paths)

    def _add_images(self, file_paths: List[str]):
        """添加图像到列表"""
        try:
            added_count = 0
            max_images = 10

            # 检查是否超过最大数量
            current_count = self.image_cards_container.get_image_count()
            available_slots = max_images - current_count

            if available_slots <= 0:
                QMessageBox.warning(self, "导入限制", f"最多只能导入 {max_images} 张图像")
                return

            # 限制导入数量
            if len(file_paths) > available_slots:
                file_paths = file_paths[:available_slots]
                QMessageBox.information(self, "导入提示",
                                      f"由于数量限制，只导入前 {available_slots} 张图像")

            for file_path in file_paths:
                # 检查是否已存在
                existing_images = [data[0] for data in self.image_cards_container.get_images_data()]
                if file_path not in existing_images:
                    # 添加到图像卡片容器
                    if self.image_cards_container.add_image(file_path):
                        added_count += 1
                        print(f"✅ 添加图像: {Path(file_path).name}")
                    else:
                        print(f"❌ 无法添加图像: {file_path}")

            if added_count > 0:
                self.status_label.setText(f"已导入 {added_count} 张图像")
            else:
                self.status_label.setText("没有有效的图像文件")

        except Exception as e:
            QMessageBox.warning(self, "导入错误", f"导入图像时发生错误：\n{str(e)}")

    def _generate_sdf(self):
        """生成SDF - 新版本"""
        # 获取图像数据
        images_data = self.image_cards_container.get_images_data()
        if not images_data:
            QMessageBox.information(self, "提示", "请先导入图像")
            return

        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(images_data))
        self.progress_bar.setValue(0)
        self.generate_btn.setEnabled(False)
        self.status_label.setText("正在生成SDF...")

        # 设置所有SDF卡片为生成中状态
        self.sdf_cards_container.set_all_status("generating")

        # 开始生成每张图像的SDF
        self._generate_individual_sdfs(images_data)

    def _generate_individual_sdfs(self, images_data: list):
        """生成每张图像的SDF"""
        self.current_sdf_results = {}  # 存储每张图像的SDF结果

        for i, (image_path, angle) in enumerate(images_data):
            try:
                # 更新进度
                self.progress_bar.setValue(i)
                filename = Path(image_path).name
                self.status_label.setText(f"正在生成SDF: {filename} ({i+1}/{len(images_data)})")

                # 获取对应的SDF卡片
                sdf_card = self.sdf_cards_container.get_sdf_card(image_path)
                if sdf_card:
                    sdf_card.set_status("generating")

                # 生成SDF
                start_time = time.time()

                # 获取参数组件的参数
                params = self.parameter_widget.get_sdf_params()
                sdf_result, computation_time = self.sdf_generator.compute_single_sdf(
                    image_path,
                    threshold=params.get('threshold', 0.5),
                    normalize=params.get('normalize', True),
                    invert=params.get('invert', False),
                    sdf_direction=params.get('sdf_direction', 'both'),
                    max_distance=params.get('max_distance', 100),
                    num_threads=params.get('num_threads')
                )

                # 更新SDF卡片
                if sdf_card:
                    sdf_card.set_generation_time(computation_time)
                    sdf_card.set_status("completed")

                    # 设置SDF预览图
                    if sdf_result is not None:
                        # 将numpy数组转换为QPixmap
                        sdf_pixmap = self._numpy_to_pixmap(sdf_result)
                        sdf_card.set_sdf_preview(sdf_pixmap)

                # 存储结果
                self.current_sdf_results[image_path] = sdf_result

                print(f"✅ {filename}: 生成成功 ({computation_time:.3f}s)")

            except Exception as e:
                print(f"❌ {filename}: 生成失败 - {str(e)}")
                if sdf_card:
                    sdf_card.set_status("failed")

        # 完成所有单张SDF生成
        self.progress_bar.setValue(len(images_data))
        self.status_label.setText(f"SDF生成完成，共处理 {len(images_data)} 张图像")

        # 生成合并SDF
        self._generate_merged_sdf(images_data)

    def _generate_merged_sdf(self, images_data: list):
        """生成合并SDF"""
        if len(images_data) == 1:
            # 单张图像，直接显示
            image_path = images_data[0][0]
            sdf_result = self.current_sdf_results.get(image_path)
            if sdf_result is not None:
                merged_pixmap = self._numpy_to_pixmap(sdf_result)
                self._update_merged_sdf_preview(merged_pixmap)

                # 存储为当前合并SDF并更新光照预览
                self.current_merged_sdf = sdf_result
                self.sdf_result = sdf_result  # 同时更新导出用的变量
                self._update_lighting_preview()
        else:
            # 多张图像，需要合并
            try:
                self.status_label.setText("正在合并SDF...")

                # 准备数据
                image_paths = [data[0] for data in images_data]
                angles = [data[1] for data in images_data]

                # 获取混合模式
                blend_mode = self.parameter_widget.get_blend_mode()

                # 获取参数组件的参数
                params = self.parameter_widget.get_sdf_params()

                # 生成合并SDF
                merged_sdf, computation_time = self.sdf_generator.compute_multi_sdf(
                    image_paths,
                    angles=angles,
                    threshold=params.get('threshold', 0.5),
                    normalize=params.get('normalize', True),
                    invert=params.get('invert', False),
                    blend_mode=blend_mode,
                    sdf_direction=params.get('sdf_direction', 'both'),
                    max_distance=params.get('max_distance', 100),
                    num_threads=params.get('num_threads')
                )

                # 显示合并结果
                if merged_sdf is not None:
                    merged_pixmap = self._numpy_to_pixmap(merged_sdf)
                    self._update_merged_sdf_preview(merged_pixmap)

                    # 存储合并结果
                    self.current_merged_sdf = merged_sdf
                    self.sdf_result = merged_sdf  # 同时更新导出用的变量

                    # 更新光照预览
                    self._update_lighting_preview()

                    print(f"✅ 合并SDF生成成功 ({computation_time:.3f}s)")
                    self.status_label.setText(f"合并SDF生成完成 ({computation_time:.3f}s)")

            except Exception as e:
                print(f"❌ 合并SDF生成失败: {str(e)}")
                self.status_label.setText(f"合并SDF生成失败: {str(e)}")

        # 完成所有生成
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        self.export_btn.setEnabled(True)

    def _numpy_to_pixmap(self, numpy_array) -> QPixmap:
        """将numpy数组转换为QPixmap"""
        try:
            import numpy as np
            from PySide6.QtGui import QImage

            # 确保数组是uint8类型
            if numpy_array.dtype != np.uint8:
                # 归一化到0-255
                if numpy_array.max() <= 1.0:
                    numpy_array = (numpy_array * 255).astype(np.uint8)
                else:
                    numpy_array = numpy_array.astype(np.uint8)

            # 处理不同的数组形状
            if len(numpy_array.shape) == 2:
                # 灰度图像
                height, width = numpy_array.shape
                bytes_per_line = width
                q_image = QImage(numpy_array.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            elif len(numpy_array.shape) == 3 and numpy_array.shape[2] == 3:
                # RGB图像
                height, width, channels = numpy_array.shape
                bytes_per_line = width * channels
                q_image = QImage(numpy_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
            else:
                raise ValueError(f"不支持的数组形状: {numpy_array.shape}")

            return QPixmap.fromImage(q_image)

        except Exception as e:
            print(f"转换QPixmap失败: {e}")
            return QPixmap()

    def _update_merged_sdf_preview(self, pixmap: QPixmap):
        """更新合并SDF预览"""
        if not pixmap.isNull():
            # 直接设置到可缩放组件
            self.merged_sdf_preview.set_image(pixmap)
            # 自动适应窗口
            self.merged_sdf_preview.fit_to_window()
        else:
            # 设置空图像
            self.merged_sdf_preview.set_image(QPixmap())

    def _generate_single_sdf(self, image_path: str, params: dict):
        """生成单张图像SDF"""
        try:
            sdf_result, computation_time = self.sdf_generator.compute_single_sdf(
                image_path,
                threshold=params.get('threshold', 0.5),
                normalize=params.get('normalize', True),
                invert=params.get('invert', False),
                sdf_direction=params.get('sdf_direction', 'both'),
                max_distance=params.get('max_distance', 100),
                num_threads=params.get('num_threads')
            )
            self._on_sdf_generated(sdf_result, computation_time)
        except Exception as e:
            self._on_sdf_generation_failed(str(e))

    def _generate_multi_sdf(self, image_paths: List[str], params: dict):
        """生成多张图像混合SDF"""
        try:
            sdf_result, computation_time = self.sdf_generator.compute_multi_sdf(
                image_paths,
                angles=params.get('angles'),
                threshold=params.get('threshold', 0.5),
                normalize=params.get('normalize', True),
                blend_mode=params.get('blend_mode', 'weighted'),
                sdf_direction=params.get('sdf_direction', 'both'),
                max_distance=params.get('max_distance', 100),
                num_threads=params.get('num_threads')
            )
            self._on_sdf_generated(sdf_result, computation_time)
        except Exception as e:
            self._on_sdf_generation_failed(str(e))

    def _on_sdf_generated(self, sdf_result, computation_time):
        """SDF生成完成"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)

        # 调试信息
        print(f"✅ SDF生成完成!")
        print(f"📊 结果形状: {sdf_result.shape}")
        print(f"📈 值域: [{sdf_result.min():.3f}, {sdf_result.max():.3f}]")
        print(f"⏱️  计算时间: {computation_time:.3f}s")

        # 保存结果
        self.sdf_result = sdf_result
        self.computation_time = computation_time

        # 更新UI
        self._update_ui_state()
        self.status_label.setText("SDF生成完成")
        self.time_label.setText(f"计算时间: {self.computation_time:.2f}s")

        # 直接传递原始numpy数组给预览组件
        # 预览组件内部会处理显示转换和光照预览
        self.preview_widget.set_sdf_result(sdf_result)

    def _on_sdf_generation_failed(self, error_message: str):
        """SDF生成失败"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)

        # 显示错误信息
        self.status_label.setText("SDF生成失败")
        QMessageBox.warning(self, "生成错误", f"SDF生成失败：\n{error_message}")

    def _convert_sdf_for_display(self, sdf_data):
        """将SDF数据转换为可显示的图像"""
        try:
            # 将numpy数组转换为QPixmap
            pil_image = ImageUtils.numpy_to_pil(sdf_data)

            # 转换为QPixmap
            from PySide6.QtGui import QPixmap
            import io

            # 保存到内存中的字节流
            img_bytes = io.BytesIO()
            pil_image.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            # 从字节流创建QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(img_bytes.getvalue())

            return pixmap

        except Exception as e:
            print(f"转换SDF显示图像失败: {e}")
            return None

    def _export_sdf(self):
        """导出SDF结果"""
        if self.sdf_result is None:
            QMessageBox.information(self, "提示", "请先生成SDF")
            return

        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("PNG文件 (*.png);;JPEG文件 (*.jpg);;TIFF文件 (*.tiff)")
        file_dialog.setDefaultSuffix("png")

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            try:
                # 使用ImageUtils保存SDF结果
                if hasattr(self.sdf_result, 'shape'):
                    # 如果是numpy数组，使用SDF专用保存方法
                    success = ImageUtils.save_sdf_as_image(self.sdf_result, file_path, quality=95)
                else:
                    # 如果是其他格式，使用通用保存方法
                    success = ImageUtils.save_image(self.sdf_result, file_path, quality=95)

                if success:
                    self.status_label.setText(f"SDF已导出到: {file_path}")
                    QMessageBox.information(self, "导出成功", f"SDF已成功导出到:\n{file_path}")
                else:
                    QMessageBox.warning(self, "导出错误", "导出SDF时发生未知错误")

            except Exception as e:
                QMessageBox.warning(self, "导出错误", f"导出SDF时发生错误：\n{str(e)}")

    def _clear_images(self):
        """清空所有图像"""
        self.current_images.clear()
        # self.image_list.clear()  # 这个属性不存在，注释掉
        self.image_manager.clear_all()
        self.sdf_result = None
        self.current_merged_sdf = None  # 同时清空合并SDF
        # self.preview_widget.clear()  # 这个属性不存在，注释掉
        self._update_ui_state()
        self.status_label.setText("已清空所有图像")
        # self.time_label.setText("")  # 这个属性不存在，注释掉

    def _reset_view(self):
        """重置预览视图"""
        self.merged_sdf_preview.reset_view()
        self.status_label.setText("视图已重置")

    def _fit_to_window(self):
        """适应窗口大小"""
        self.merged_sdf_preview.fit_to_window()
        self.status_label.setText("已适应窗口大小")

    def _actual_size(self):
        """显示实际大小"""
        self.merged_sdf_preview.actual_size()
        self.status_label.setText("已显示实际大小")

    def _on_merged_sdf_zoom_changed(self, zoom_factor):
        """合并SDF缩放改变"""
        percentage = int(zoom_factor * 100)
        self.zoom_label.setText(f"{percentage}%")

    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于SDF工具",
                         "SDF工具 v0.1.0\n\n"
                         "二次元脸部SDF生成工具\n"
                         "支持多角度光照图像混合和实时预览\n\n"
                         "作者: Mya\n"
                         "技术栈: Python + PySide6 + C++")





    def _update_ui_state(self):
        """更新UI状态"""
        has_images = len(self.current_images) > 0
        has_sdf = self.sdf_result is not None

        # 更新按钮状态
        self.generate_btn.setEnabled(has_images)
        self.export_btn.setEnabled(has_sdf)
        self.export_action.setEnabled(has_sdf)

        # 更新状态栏
        self.image_count_label.setText(f"图像: {len(self.current_images)}")

    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(self, "确认退出",
                                   "确定要退出SDF工具吗？",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    # 批量处理方法
    def _batch_import_folder(self):
        """批量导入文件夹"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "选择图像文件夹", "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if not folder_path:
            return

        try:
            # 支持的图像格式
            supported_formats = {'.png', '.jpg', '.jpeg', '.bmp', '.tga', '.tiff'}

            # 扫描文件夹中的图像文件
            image_files = []
            folder = Path(folder_path)

            for file_path in folder.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                    image_files.append(str(file_path))

            if not image_files:
                QMessageBox.information(self, "提示", "文件夹中没有找到支持的图像文件")
                return

            # 询问是否替换当前图像
            if self.current_images:
                reply = QMessageBox.question(
                    self, "确认导入",
                    f"找到 {len(image_files)} 个图像文件。\n是否替换当前已导入的图像？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply != QMessageBox.Yes:
                    return

            # 导入图像
            self.current_images = sorted(image_files)  # 按文件名排序
            self.image_list.set_images(self.current_images)

            # 角度配置已简化，不需要更新

            self.status_label.setText(f"批量导入完成：{len(image_files)} 个图像文件")
            print(f"📁 批量导入完成: {len(image_files)} 个图像文件")

        except Exception as e:
            QMessageBox.warning(self, "导入错误", f"批量导入时发生错误：\n{str(e)}")

    def _batch_generate_sdf(self):
        """批量生成SDF"""
        if not self.current_images:
            QMessageBox.information(self, "提示", "请先导入图像")
            return

        # 询问生成模式
        reply = QMessageBox.question(
            self, "批量生成模式",
            "选择批量生成模式：\n\n"
            "是(Yes): 为每张图像单独生成SDF\n"
            "否(No): 将所有图像混合生成一个SDF\n"
            "取消: 取消操作",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Cancel:
            return

        self.batch_processing = True
        self.batch_sdf_results.clear()

        # 获取参数
        params = self.parameter_widget.get_sdf_params()

        try:
            if reply == QMessageBox.Yes:
                # 单独生成模式
                self._batch_generate_individual(params)
            else:
                # 混合生成模式
                self._batch_generate_mixed(params)

        except Exception as e:
            self._on_sdf_generation_failed(str(e))
        finally:
            self.batch_processing = False

    def _batch_generate_individual(self, params: dict):
        """批量单独生成SDF"""
        print(f"🔄 开始批量单独生成SDF: {len(self.current_images)} 张图像")

        # 显示进度
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(self.current_images))
        self.generate_btn.setEnabled(False)

        total_time = 0.0
        success_count = 0

        for i, image_path in enumerate(self.current_images):
            try:
                self.status_label.setText(f"正在处理: {Path(image_path).name} ({i+1}/{len(self.current_images)})")
                self.progress_bar.setValue(i)

                # 生成单张SDF
                sdf_result, computation_time = self.sdf_generator.compute_single_sdf(
                    image_path,
                    threshold=params.get('threshold', 0.5),
                    normalize=params.get('normalize', True),
                    invert=params.get('invert', False),
                    sdf_direction=params.get('sdf_direction', 'both'),
                    max_distance=params.get('max_distance', 100),
                    num_threads=params.get('num_threads')
                )

                # 保存结果
                self.batch_sdf_results[image_path] = sdf_result
                total_time += computation_time
                success_count += 1

                print(f"  ✅ {Path(image_path).name}: 成功 ({computation_time:.3f}s)")

            except Exception as e:
                print(f"  ❌ {Path(image_path).name}: 失败 - {str(e)}")

        # 完成
        self.progress_bar.setValue(len(self.current_images))
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)

        # 显示最后一个成功的结果
        if success_count > 0:
            last_result = list(self.batch_sdf_results.values())[-1]
            self.sdf_result = last_result
            self.preview_widget.set_sdf_result(last_result)

        self.status_label.setText(f"批量生成完成: {success_count}/{len(self.current_images)} 成功, 总时间 {total_time:.3f}s")
        print(f"🎉 批量单独生成完成: {success_count}/{len(self.current_images)} 成功")

    def _batch_generate_mixed(self, params: dict):
        """批量混合生成SDF"""
        print(f"🔄 开始批量混合生成SDF: {len(self.current_images)} 张图像")

        # 显示进度
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.generate_btn.setEnabled(False)
        self.status_label.setText("正在生成混合SDF...")

        try:
            # 生成混合SDF
            sdf_result, computation_time = self.sdf_generator.compute_multi_sdf(
                self.current_images,
                angles=params.get('angles'),
                threshold=params.get('threshold', 0.5),
                normalize=params.get('normalize', True),
                blend_mode=params.get('blend_mode', 'weighted'),
                sdf_direction=params.get('sdf_direction', 'both'),
                max_distance=params.get('max_distance', 100),
                num_threads=params.get('num_threads')
            )

            # 保存结果
            self.batch_sdf_results['mixed_result'] = sdf_result
            self._on_sdf_generated(sdf_result, computation_time)

            print(f"🎉 批量混合生成完成: {computation_time:.3f}s")

        except Exception as e:
            raise e
        finally:
            self.progress_bar.setVisible(False)
            self.generate_btn.setEnabled(True)

    def _batch_export_sdf(self):
        """批量导出SDF"""
        if not self.batch_sdf_results:
            QMessageBox.information(self, "提示", "没有可导出的SDF结果\n请先进行批量生成")
            return

        # 选择导出文件夹
        export_folder = QFileDialog.getExistingDirectory(
            self, "选择导出文件夹", "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if not export_folder:
            return

        try:
            export_path = Path(export_folder)
            export_path.mkdir(exist_ok=True)

            # 显示进度
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, len(self.batch_sdf_results))

            success_count = 0

            for i, (source_path, sdf_result) in enumerate(self.batch_sdf_results.items()):
                try:
                    # 生成输出文件名
                    if source_path == 'mixed_result':
                        output_name = "mixed_sdf_result.png"
                    else:
                        source_name = Path(source_path).stem
                        output_name = f"{source_name}_sdf.png"

                    output_path = export_path / output_name

                    self.status_label.setText(f"正在导出: {output_name} ({i+1}/{len(self.batch_sdf_results)})")
                    self.progress_bar.setValue(i)

                    # 导出SDF
                    from ..utils.image_utils import ImageUtils
                    if ImageUtils.save_sdf_as_image(sdf_result, str(output_path)):
                        success_count += 1
                        print(f"  ✅ 导出成功: {output_name}")
                    else:
                        print(f"  ❌ 导出失败: {output_name}")

                except Exception as e:
                    print(f"  ❌ 导出失败: {output_name} - {str(e)}")

            # 完成
            self.progress_bar.setValue(len(self.batch_sdf_results))
            self.progress_bar.setVisible(False)

            self.status_label.setText(f"批量导出完成: {success_count}/{len(self.batch_sdf_results)} 成功")

            if success_count > 0:
                QMessageBox.information(
                    self, "导出完成",
                    f"批量导出完成！\n\n"
                    f"成功: {success_count}/{len(self.batch_sdf_results)}\n"
                    f"导出位置: {export_folder}"
                )

            print(f"🎉 批量导出完成: {success_count}/{len(self.batch_sdf_results)} 成功")

        except Exception as e:
            QMessageBox.warning(self, "导出错误", f"批量导出时发生错误：\n{str(e)}")
            self.progress_bar.setVisible(False)
