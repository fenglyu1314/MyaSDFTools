#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI布局管理器 - 重构后的简化版本

负责管理主窗口的主要布局结构
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from .ui_component_factory import UIComponentFactory
from .ui_signal_manager import SignalConnectionManager
from .window_configuration import WindowConfiguration


class UILayoutManager:
    """UI布局管理器 - 重构后的简化版本"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.components = {}

    def setup_main_layout(self):
        """设置主布局"""
        # 创建中央部件
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(8)

        # 创建左侧布局
        left_layout = self._create_left_layout()

        # 创建右侧布局
        right_layout = self._create_right_layout()

        # 添加到主布局
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        return self.components

    def _create_left_layout(self):
        """创建左侧布局"""
        left_layout = QVBoxLayout()

        # 区域1: 图像导入区域
        image_import_area, image_cards_container, progress_bar = UIComponentFactory.create_image_import_area()
        left_layout.addWidget(image_import_area)
        self.components['image_cards_container'] = image_cards_container
        self.components['progress_bar'] = progress_bar

        # 区域2: SDF结果区域
        sdf_results_area, sdf_cards_container = UIComponentFactory.create_sdf_results_area()
        left_layout.addWidget(sdf_results_area)
        self.components['sdf_cards_container'] = sdf_cards_container

        # 区域4和5: 预览区域横向布局
        preview_layout = self._create_preview_layout()
        left_layout.addLayout(preview_layout)

        return left_layout

    def _create_preview_layout(self):
        """创建预览区域布局"""
        preview_layout = QHBoxLayout()
        preview_layout.setSpacing(8)

        # 区域4: 合并SDF预览区域
        merged_sdf_area, merged_sdf_preview, fit_btn, actual_btn, reset_btn, zoom_label = \
            UIComponentFactory.create_merged_sdf_area()
        preview_layout.addWidget(merged_sdf_area)

        self.components['merged_sdf_preview'] = merged_sdf_preview
        self.components['fit_btn'] = fit_btn
        self.components['actual_btn'] = actual_btn
        self.components['reset_btn'] = reset_btn
        self.components['zoom_label'] = zoom_label

        # 区域5: 光照效果预览区域
        lighting_area, lighting_preview, angle_slider, angle_value_label = \
            UIComponentFactory.create_lighting_preview_area()
        preview_layout.addWidget(lighting_area)

        self.components['lighting_preview'] = lighting_preview
        self.components['angle_slider'] = angle_slider
        self.components['angle_value_label'] = angle_value_label

        return preview_layout

    def _create_right_layout(self):
        """创建右侧布局"""
        right_layout = QVBoxLayout()

        # 区域3: 参数控制区域
        parameter_area, parameter_widget = UIComponentFactory.create_parameter_area()
        right_layout.addWidget(parameter_area)
        self.components['parameter_widget'] = parameter_widget

        # 操作按钮区域
        button_area, import_btn, generate_btn, export_btn = UIComponentFactory.create_button_area()
        right_layout.addWidget(button_area)

        self.components['import_btn'] = import_btn
        self.components['generate_btn'] = generate_btn
        self.components['export_btn'] = export_btn

        return right_layout

    def setup_menu_bar(self):
        """设置菜单栏"""
        menu_actions = UIComponentFactory.create_menu_bar(self.main_window)
        self.components.update(menu_actions)
        return menu_actions

    def setup_status_bar(self):
        """设置状态栏"""
        status_components = UIComponentFactory.create_status_bar(self.main_window)
        self.components.update(status_components)
        return status_components

    def get_component(self, name: str):
        """获取组件"""
        return self.components.get(name)

    def get_all_components(self):
        """获取所有组件"""
        return self.components.copy()


