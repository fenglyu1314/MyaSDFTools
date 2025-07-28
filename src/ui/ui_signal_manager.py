#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI信号管理器模块

负责管理UI组件之间的信号连接和事件处理
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QMessageBox


class SignalConnectionManager:
    """信号连接管理器"""

    def __init__(self, components, event_handler):
        self.components = components
        self.event_handler = event_handler

    def connect_all_signals(self):
        """连接所有信号"""
        self._connect_button_signals()
        self._connect_menu_signals()
        self._connect_widget_signals()
        self._connect_event_handler_signals()

    def _connect_button_signals(self):
        """连接按钮信号"""
        self.components['import_btn'].clicked.connect(self.event_handler.handle_import_images)
        self.components['generate_btn'].clicked.connect(self._handle_generate_sdf)
        self.components['export_btn'].clicked.connect(self.event_handler.handle_export_sdf)
        
        # 预览控制按钮
        if 'fit_btn' in self.components:
            self.components['fit_btn'].clicked.connect(self._handle_fit_to_window)
        if 'actual_btn' in self.components:
            self.components['actual_btn'].clicked.connect(self._handle_actual_size)
        if 'reset_btn' in self.components:
            self.components['reset_btn'].clicked.connect(self._handle_reset_view)

    def _connect_menu_signals(self):
        """连接菜单信号"""
        self.components['import_action'].triggered.connect(self.event_handler.handle_import_images)
        self.components['export_action'].triggered.connect(self.event_handler.handle_export_sdf)
        self.components['exit_action'].triggered.connect(self._handle_exit)
        self.components['about_action'].triggered.connect(self._handle_about)

    def _connect_widget_signals(self):
        """连接组件信号"""
        # 角度滑竿
        if 'angle_slider' in self.components:
            self.components['angle_slider'].valueChanged.connect(self._handle_angle_changed)
        
        # 缩放信号
        merged_sdf_preview = self.components.get('merged_sdf_preview')
        if merged_sdf_preview and hasattr(merged_sdf_preview, 'zoom_changed'):
            merged_sdf_preview.zoom_changed.connect(self._handle_zoom_changed)
        
        # 图像卡片容器信号
        image_cards_container = self.components.get('image_cards_container')
        if image_cards_container:
            if hasattr(image_cards_container, 'images_changed'):
                image_cards_container.images_changed.connect(self._handle_images_changed)
            if hasattr(image_cards_container, 'image_remove_requested'):
                image_cards_container.image_remove_requested.connect(self.event_handler.handle_remove_image)
            if hasattr(image_cards_container, 'image_order_changed'):
                image_cards_container.image_order_changed.connect(self.event_handler.handle_image_order_changed)
        
        # 参数组件信号
        parameter_widget = self.components.get('parameter_widget')
        if parameter_widget and hasattr(parameter_widget, 'parameters_changed'):
            parameter_widget.parameters_changed.connect(self.event_handler.handle_parameters_changed)

    def _connect_event_handler_signals(self):
        """连接事件处理器信号"""
        self.event_handler.status_updated.connect(self._update_status)
        self.event_handler.ui_state_changed.connect(self._update_ui_state)
        self.event_handler.sdf_generated.connect(self._handle_sdf_generated)
        self.event_handler.overall_progress_updated.connect(self._handle_overall_progress_updated)
        self.event_handler.single_batch_progress_updated.connect(self._handle_single_batch_progress_updated)

    def _handle_generate_sdf(self):
        """处理生成SDF"""
        # 显示进度条并重置
        progress_bar = self.components.get('progress_bar')
        if progress_bar:
            progress_bar.setVisible(True)
            progress_bar.setValue(0)

        # 重置整体进度显示
        total_progress_label = self.components.get('total_progress_label')
        if total_progress_label:
            total_progress_label.setText("0%")

        parameters = self.components['parameter_widget'].get_sdf_params()
        self.event_handler.handle_generate_sdf(parameters)

    def _handle_angle_changed(self, value):
        """处理角度改变 - 只更新显示，不直接修改其他组件"""
        if 'angle_value_label' in self.components:
            self.components['angle_value_label'].setText(f"{value}°")

    def _handle_zoom_changed(self, zoom_factor):
        """处理缩放改变 - 只更新显示"""
        if 'zoom_label' in self.components:
            percentage = int(zoom_factor * 100)
            self.components['zoom_label'].setText(f"{percentage}%")

    def _handle_fit_to_window(self):
        """适应窗口 - 通过组件自身方法"""
        preview_widget = self.components.get('merged_sdf_preview')
        if preview_widget and hasattr(preview_widget, 'fit_to_window'):
            preview_widget.fit_to_window()

    def _handle_actual_size(self):
        """实际大小 - 通过组件自身方法"""
        preview_widget = self.components.get('merged_sdf_preview')
        if preview_widget and hasattr(preview_widget, 'actual_size'):
            preview_widget.actual_size()

    def _handle_reset_view(self):
        """重置视图 - 通过组件自身方法"""
        preview_widget = self.components.get('merged_sdf_preview')
        if preview_widget and hasattr(preview_widget, 'reset_view'):
            preview_widget.reset_view()

    def _handle_images_changed(self):
        """处理图像改变 - 避免循环触发，只更新UI状态"""
        # 不再发出ui_state_changed信号，避免循环触发
        # UI状态更新由事件处理器的_add_images方法统一管理
        print("📝 图像卡片容器状态改变")

    def _handle_exit(self):
        """处理退出"""
        sys.exit()

    def _handle_about(self):
        """处理关于"""
        QMessageBox.about(None, "关于SDF工具",
                         "SDF工具 v0.1.0\n\n"
                         "二次元脸部SDF生成工具\n"
                         "支持多角度光照图像混合和实时预览\n\n"
                         "作者: Mya\n"
                         "技术栈: Python + PySide6 + C++")

    def _update_status(self, message: str):
        """更新状态 - 安全地更新状态标签"""
        status_label = self.components.get('status_label')
        if status_label:
            status_label.setText(message)

    def _update_ui_state(self):
        """更新UI状态 - 安全地更新各组件状态"""
        if not self.event_handler:
            return

        # 防止重复更新
        if hasattr(self, '_updating_ui_state') and self._updating_ui_state:
            print("⚠️ 跳过重复的UI状态更新")
            return

        self._updating_ui_state = True
        try:
            has_images = self.event_handler.has_images
            has_sdf = self.event_handler.has_sdf

            # 更新图像卡片容器
            self._update_image_cards()

            # 更新SDF卡片容器
            self._update_sdf_cards()

            # 安全地更新按钮状态
            generate_btn = self.components.get('generate_btn')
            if generate_btn:
                generate_btn.setEnabled(has_images)

            export_btn = self.components.get('export_btn')
            if export_btn:
                export_btn.setEnabled(has_sdf)

            export_action = self.components.get('export_action')
            if export_action:
                export_action.setEnabled(has_sdf)

            # 安全地更新状态栏
            image_count_label = self.components.get('image_count_label')
            if image_count_label:
                image_count_label.setText(f"图像: {self.event_handler.image_count}")
        finally:
            self._updating_ui_state = False

    def _update_image_cards(self):
        """更新图像卡片显示"""
        image_cards_container = self.components.get('image_cards_container')
        if not image_cards_container or not self.event_handler:
            return

        # 获取当前图像列表
        current_images = self.event_handler.current_images

        # 获取容器中已有的图像路径
        existing_paths = [card.get_image_path() for card in image_cards_container.image_cards]

        # 添加新图像（只添加不存在的）
        for image_path in current_images:
            if image_path not in existing_paths:
                success = image_cards_container.add_image(image_path)
                if not success:
                    print(f"❌ UI添加图像卡片失败: {image_path}")

        # 移除不存在的图像
        for existing_path in existing_paths:
            if existing_path not in current_images:
                image_cards_container._remove_image(existing_path)
                print(f"🗑️ 移除图像卡片: {existing_path}")

        # 同步UI中的图像顺序到后端（如果UI中的顺序与后端不同）
        ui_order = image_cards_container.get_current_image_order()
        if ui_order != current_images and len(ui_order) == len(current_images):
            # UI中的顺序与后端不同，以UI为准更新后端
            self.event_handler.current_images = ui_order.copy()
            print(f"🔄 同步UI顺序到后端: {[Path(p).name for p in ui_order]}")

        # 调试信息
        print(f"🔄 UI状态同步: 后端{len(current_images)}张图像 → UI{len(image_cards_container.image_cards)}张卡片")

    def _update_sdf_cards(self):
        """更新SDF卡片显示"""
        sdf_cards_container = self.components.get('sdf_cards_container')
        if not sdf_cards_container or not self.event_handler:
            return

        # 根据当前图像更新SDF卡片
        current_images = self.event_handler.current_images
        images_data = [(path, 0) for path in current_images]  # 角度暂时设为0
        print(f"🔄 更新SDF卡片顺序: {[Path(p).name for p in current_images]}")
        sdf_cards_container.update_cards_from_images(images_data)

    def _handle_sdf_generated(self, sdf_result, computation_time):
        """处理SDF生成完成 - 安全地更新时间显示"""
        # 隐藏进度条
        progress_bar = self.components.get('progress_bar')
        if progress_bar:
            progress_bar.setVisible(False)

        time_label = self.components.get('time_label')
        if time_label:
            time_label.setText(f"计算时间: {computation_time:.2f}s")

    def _handle_overall_progress_updated(self, progress: int):
        """处理整体进度更新 - 更新右下角百分比显示（包括单张生成+合并）"""
        total_progress_label = self.components.get('total_progress_label')
        if total_progress_label:
            total_progress_label.setText(f"{progress}%")

    def _handle_single_batch_progress_updated(self, progress: int):
        """处理单张SDF批次进度更新 - 更新区域1的进度条（只显示单张生成进度）"""
        progress_bar = self.components.get('progress_bar')
        if progress_bar:
            progress_bar.setValue(progress)
