#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI组件创建器

负责创建各种UI组件和区域
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QProgressBar, QSlider, QStatusBar
)
from PySide6.QtCore import Qt

from .window_styles import ButtonStyles, WidgetStyles, LayoutConstants
from .image_card_widget import ImageCardsContainer
from .sdf_card_widget import SDFCardsContainer
from .parameter_widget import ParameterWidget
from .zoomable_image_widget import ZoomableImageWidget
from .responsive_layout import ResponsiveGroupBox
from .layout_config import layout_config_manager


class UIComponentFactory:
    """UI组件工厂类"""

    @staticmethod
    def create_image_import_area():
        """创建图像导入区域 - 响应式版本"""
        area = ResponsiveGroupBox("1. 图像导入", "image_import_area")

        # 图像卡片容器
        image_cards_container = ImageCardsContainer()
        area.main_layout.addWidget(image_cards_container)

        # 进度条
        progress_bar = QProgressBar()
        progress_bar.setTextVisible(False)
        progress_bar.setVisible(False)
        progress_bar.setFixedHeight(LayoutConstants.SPACING_MEDIUM // 2)
        progress_bar.setStyleSheet(WidgetStyles.progress_bar_style())
        area.main_layout.addWidget(progress_bar)

        return area, image_cards_container, progress_bar

    @staticmethod
    def create_sdf_results_area():
        """创建SDF生成结果区域 - 响应式版本"""
        area = ResponsiveGroupBox("2. SDF生成结果", "sdf_results_area")

        # SDF结果卡片容器
        sdf_cards_container = SDFCardsContainer()
        area.main_layout.addWidget(sdf_cards_container)

        return area, sdf_cards_container

    @staticmethod
    def create_parameter_area():
        """创建参数控制区域 - 响应式版本"""
        area = ResponsiveGroupBox("3. SDF参数控制", "parameter_area")

        # 参数控制组件
        parameter_widget = ParameterWidget()
        area.main_layout.addWidget(parameter_widget)

        return area, parameter_widget

    @staticmethod
    def create_button_area():
        """创建操作按钮区域 - 响应式版本"""
        area_config = layout_config_manager.get_area_config("button_area")
        area = QWidget()
        layout = QVBoxLayout(area)
        layout.setContentsMargins(*area_config.padding)
        layout.setSpacing(LayoutConstants.SPACING_SMALL)

        # 计算按钮尺寸
        button_width, button_height = LayoutConstants.BASE_UNIT * 35, LayoutConstants.BASE_UNIT * 4 + 4

        # 导入按钮
        import_btn = QPushButton("导入图像")
        import_btn.setStyleSheet(ButtonStyles.success_button("normal"))
        import_btn.setMinimumSize(button_width, button_height)
        layout.addWidget(import_btn)

        # 生成按钮
        generate_btn = QPushButton("生成SDF")
        generate_btn.setEnabled(False)
        generate_btn.setStyleSheet(ButtonStyles.primary_button("normal"))
        generate_btn.setMinimumSize(button_width, button_height)
        layout.addWidget(generate_btn)

        # 导出按钮
        export_btn = QPushButton("导出SDF")
        export_btn.setEnabled(False)
        export_btn.setStyleSheet(ButtonStyles.secondary_button("normal"))
        export_btn.setMinimumSize(button_width, button_height)
        layout.addWidget(export_btn)

        return area, import_btn, generate_btn, export_btn

    @staticmethod
    def create_merged_sdf_area():
        """创建合并SDF预览区域"""
        area = QGroupBox("4. 合并SDF预览")
        area.setStyleSheet(WidgetStyles.group_box_style())
        layout = QVBoxLayout(area)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(5)

        # 预览组件
        merged_sdf_preview = ZoomableImageWidget()
        merged_sdf_preview.setFixedSize(443, 280)
        layout.addWidget(merged_sdf_preview)

        # 控制按钮区域
        control_layout = QHBoxLayout()
        control_layout.setSpacing(5)

        # 快速操作按钮
        fit_btn = QPushButton("适应")
        fit_btn.setMaximumWidth(50)
        fit_btn.setStyleSheet(ButtonStyles.secondary_button("small"))
        control_layout.addWidget(fit_btn)

        actual_btn = QPushButton("1:1")
        actual_btn.setMaximumWidth(40)
        actual_btn.setStyleSheet(ButtonStyles.secondary_button("small"))
        control_layout.addWidget(actual_btn)

        reset_btn = QPushButton("重置")
        reset_btn.setMaximumWidth(50)
        reset_btn.setStyleSheet(ButtonStyles.secondary_button("small"))
        control_layout.addWidget(reset_btn)

        control_layout.addStretch()

        # 缩放显示
        zoom_label = QLabel("100%")
        zoom_label.setMinimumWidth(50)
        zoom_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        control_layout.addWidget(zoom_label)

        layout.addLayout(control_layout)

        area.setFixedSize(451, 350)
        return area, merged_sdf_preview, fit_btn, actual_btn, reset_btn, zoom_label

    @staticmethod
    def create_lighting_preview_area():
        """创建光照效果预览区域"""
        area = QGroupBox("5. 光照效果预览")
        area.setStyleSheet(WidgetStyles.group_box_style())
        layout = QVBoxLayout(area)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(5)

        # 光照预览组件 - 使用普通QLabel显示完整图像
        lighting_preview = QLabel("光照效果预览\n请先生成SDF")
        lighting_preview.setAlignment(Qt.AlignCenter)
        lighting_preview.setFixedSize(443, 280)
        lighting_preview.setScaledContents(False)  # 不自动缩放内容，保持图像质量
        lighting_preview.setStyleSheet("""
            QLabel {
                border: 1px solid #cccccc;
                background-color: #f8f9fa;
                color: #666666;
                font-size: 14px;
            }
        """)
        layout.addWidget(lighting_preview)

        # 光照控制区域
        control_layout = QHBoxLayout()
        control_layout.setSpacing(8)

        # 角度标签
        angle_label = QLabel("光照角度:")
        angle_label.setMinimumWidth(60)
        control_layout.addWidget(angle_label)

        # 角度滑竿
        angle_slider = QSlider(Qt.Horizontal)
        angle_slider.setRange(-180, 180)
        angle_slider.setValue(0)
        angle_slider.setStyleSheet(WidgetStyles.slider_style())
        control_layout.addWidget(angle_slider)

        # 角度值显示
        angle_value_label = QLabel("0°")
        angle_value_label.setMinimumWidth(40)
        angle_value_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(angle_value_label)

        layout.addLayout(control_layout)

        area.setFixedSize(451, 350)
        return area, lighting_preview, angle_slider, angle_value_label

    @staticmethod
    def create_menu_bar(main_window):
        """创建菜单栏"""
        menubar = main_window.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        import_action, export_action, exit_action = MenuFactory.create_file_menu_actions()
        file_menu.addAction(import_action)
        file_menu.addSeparator()
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        about_action = MenuFactory.create_help_menu_actions()
        help_menu.addAction(about_action)

        return {
            'import_action': import_action,
            'export_action': export_action,
            'exit_action': exit_action,
            'about_action': about_action
        }

    @staticmethod
    def create_status_bar(main_window):
        """创建状态栏"""
        status_bar = QStatusBar()
        main_window.setStatusBar(status_bar)

        # 创建状态栏组件
        status_label, image_count_label, time_label, zoom_label = StatusBarFactory.create_status_widgets()

        # 添加到状态栏
        status_bar.addWidget(status_label, 1)  # 拉伸
        status_bar.addPermanentWidget(image_count_label)
        status_bar.addPermanentWidget(time_label)
        status_bar.addPermanentWidget(zoom_label)

        return {
            'status_bar': status_bar,
            'status_label': status_label,
            'image_count_label': image_count_label,
            'time_label': time_label,
            'status_zoom_label': zoom_label
        }


class StatusBarFactory:
    """状态栏工厂类"""

    @staticmethod
    def create_status_widgets():
        """创建状态栏组件"""
        # 主状态标签
        status_label = QLabel("准备就绪")
        status_label.setMinimumWidth(200)

        # 图像计数标签
        image_count_label = QLabel("图像: 0")
        image_count_label.setMinimumWidth(80)

        # 计算时间标签
        time_label = QLabel("")
        time_label.setMinimumWidth(120)

        # 缩放标签
        zoom_label = QLabel("100%")
        zoom_label.setMinimumWidth(60)

        return status_label, image_count_label, time_label, zoom_label


class MenuFactory:
    """菜单工厂类"""

    @staticmethod
    def create_file_menu_actions():
        """创建文件菜单动作"""
        from PySide6.QtGui import QAction
        
        # 导入图像动作
        import_action = QAction("导入图像(&I)")
        import_action.setShortcut("Ctrl+I")
        import_action.setStatusTip("导入图像文件")

        # 导出SDF动作
        export_action = QAction("导出SDF(&E)")
        export_action.setShortcut("Ctrl+E")
        export_action.setStatusTip("导出SDF结果")
        export_action.setEnabled(False)

        # 退出动作
        exit_action = QAction("退出(&X)")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("退出应用程序")

        return import_action, export_action, exit_action

    @staticmethod
    def create_help_menu_actions():
        """创建帮助菜单动作"""
        from PySide6.QtGui import QAction
        
        # 关于动作
        about_action = QAction("关于(&A)")
        about_action.setStatusTip("关于SDF工具")

        return about_action
