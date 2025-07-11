#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI组件创建器

负责创建各种UI组件和区域
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QPushButton, QProgressBar, QSlider, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .window_styles import ButtonStyles, WidgetStyles
from .image_cards_container import ImageCardsContainer
from .sdf_card_widget import SDFCardsContainer
from .parameter_widget import ParameterWidget
from .zoomable_image_widget import ZoomableImageWidget


class UIComponentFactory:
    """UI组件工厂类"""

    @staticmethod
    def create_image_import_area() -> QWidget:
        """创建图像导入区域"""
        area = QGroupBox("1. 图像导入")
        area.setStyleSheet(WidgetStyles.group_box_style())
        layout = QVBoxLayout(area)
        layout.setContentsMargins(4, 4, 4, 4)

        # 图像卡片容器
        image_cards_container = ImageCardsContainer()
        image_cards_container.setFixedHeight(200)
        layout.addWidget(image_cards_container)

        # 进度条
        progress_bar = QProgressBar()
        progress_bar.setTextVisible(False)
        progress_bar.setVisible(False)
        progress_bar.setFixedHeight(10)
        progress_bar.setStyleSheet(WidgetStyles.progress_bar_style())
        layout.addWidget(progress_bar)

        area.setFixedSize(1000, 210)
        return area, image_cards_container, progress_bar

    @staticmethod
    def create_sdf_results_area() -> QWidget:
        """创建SDF生成结果区域"""
        area = QGroupBox("2. SDF生成结果")
        area.setStyleSheet(WidgetStyles.group_box_style())
        layout = QVBoxLayout(area)
        layout.setContentsMargins(4, 4, 4, 4)

        # SDF结果卡片容器
        sdf_cards_container = SDFCardsContainer()
        sdf_cards_container.setFixedHeight(160)
        layout.addWidget(sdf_cards_container)

        area.setFixedSize(1000, 160)
        return area, sdf_cards_container

    @staticmethod
    def create_parameter_area() -> QWidget:
        """创建参数控制区域"""
        area = QGroupBox("3. SDF参数控制")
        area.setStyleSheet(WidgetStyles.group_box_style())
        layout = QVBoxLayout(area)
        layout.setContentsMargins(4, 4, 4, 4)

        # 参数控制组件
        parameter_widget = ParameterWidget()
        layout.addWidget(parameter_widget)

        area.setFixedSize(300, 580)
        return area, parameter_widget

    @staticmethod
    def create_button_area() -> QWidget:
        """创建操作按钮区域"""
        area = QWidget()
        layout = QVBoxLayout(area)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        button_width = 280
        button_height = 35

        # 导入按钮
        import_btn = QPushButton("导入图像")
        import_btn.setStyleSheet(ButtonStyles.success_button("normal"))
        import_btn.setFixedSize(button_width, button_height)
        layout.addWidget(import_btn)

        # 生成按钮
        generate_btn = QPushButton("生成SDF")
        generate_btn.setEnabled(False)
        generate_btn.setStyleSheet(ButtonStyles.primary_button("normal"))
        generate_btn.setFixedSize(button_width, button_height)
        layout.addWidget(generate_btn)

        # 导出按钮
        export_btn = QPushButton("导出SDF")
        export_btn.setEnabled(False)
        export_btn.setStyleSheet(ButtonStyles.secondary_button("normal"))
        export_btn.setFixedSize(button_width, button_height)
        layout.addWidget(export_btn)

        area.setFixedSize(300, 140)
        return area, import_btn, generate_btn, export_btn

    @staticmethod
    def create_merged_sdf_area() -> QWidget:
        """创建合并SDF预览区域"""
        area = QGroupBox("4. 合并SDF预览")
        area.setStyleSheet(WidgetStyles.group_box_style())
        layout = QVBoxLayout(area)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(5)

        # 预览组件
        merged_sdf_preview = ZoomableImageWidget()
        merged_sdf_preview.setFixedSize(480, 280)
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

        area.setFixedSize(490, 350)
        return area, merged_sdf_preview, fit_btn, actual_btn, reset_btn, zoom_label

    @staticmethod
    def create_lighting_preview_area() -> QWidget:
        """创建光照效果预览区域"""
        area = QGroupBox("5. 光照效果预览")
        area.setStyleSheet(WidgetStyles.group_box_style())
        layout = QVBoxLayout(area)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(5)

        # 光照预览组件 - 使用普通QLabel显示完整图像
        lighting_preview = QLabel("光照效果预览\n请先生成SDF")
        lighting_preview.setAlignment(Qt.AlignCenter)
        lighting_preview.setFixedSize(480, 280)
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

        area.setFixedSize(490, 350)
        return area, lighting_preview, angle_slider, angle_value_label


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
