#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI组件工厂模块

负责创建各种UI组件和区域，从ui_components模块中提取的工厂方法
"""

from PySide6.QtWidgets import QStatusBar, QMenuBar
from PySide6.QtGui import QAction

from .ui_components import UIComponentFactory as OriginalFactory, StatusBarFactory, MenuFactory


class UIComponentFactory:
    """UI组件工厂类 - 重构后的简化版本"""

    @staticmethod
    def create_image_import_area():
        """创建图像导入区域"""
        return OriginalFactory.create_image_import_area()

    @staticmethod
    def create_sdf_results_area():
        """创建SDF结果区域"""
        return OriginalFactory.create_sdf_results_area()

    @staticmethod
    def create_merged_sdf_area():
        """创建合并SDF预览区域"""
        return OriginalFactory.create_merged_sdf_area()

    @staticmethod
    def create_lighting_preview_area():
        """创建光照预览区域"""
        return OriginalFactory.create_lighting_preview_area()

    @staticmethod
    def create_parameter_area():
        """创建参数设置区域"""
        return OriginalFactory.create_parameter_area()

    @staticmethod
    def create_button_area():
        """创建操作按钮区域"""
        return OriginalFactory.create_button_area()

    @staticmethod
    def create_control_area():
        """创建控制区域"""
        return OriginalFactory.create_control_area()

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
        status_label, image_count_label, time_label, total_progress_label = StatusBarFactory.create_status_widgets()

        # 添加到状态栏
        status_bar.addWidget(status_label, 1)  # 拉伸
        status_bar.addPermanentWidget(image_count_label)
        status_bar.addPermanentWidget(time_label)
        status_bar.addPermanentWidget(total_progress_label)

        return {
            'status_bar': status_bar,
            'status_label': status_label,
            'image_count_label': image_count_label,
            'time_label': time_label,
            'total_progress_label': total_progress_label
        }
