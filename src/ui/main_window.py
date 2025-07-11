#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主窗口模块

重构后的简化主窗口，职责明确：
- 窗口初始化和配置
- 协调各个管理器
- 处理特定的业务逻辑（如光照预览）
"""

from pathlib import Path

from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QDragEnterEvent, QDropEvent

# 导入管理器和处理器
from .ui_layout_manager import UILayoutManager
from .window_configuration import WindowConfiguration
from .ui_signal_manager import SignalConnectionManager
from .event_handlers import MainWindowEventHandler
from .lighting_preview_handler import LightingPreviewHandler
from .sdf_preview_handler import SDFPreviewHandler
from .theme_manager import get_theme_manager
from .theme_switcher_widget import CompactThemeSwitcher


class MainWindow(QMainWindow):
    """主窗口类 - 重构后的简化版本"""

    def __init__(self):
        super().__init__()
        
        # 初始化管理器和处理器
        self.layout_manager = UILayoutManager(self)
        self.event_handler = MainWindowEventHandler(self)
        self.lighting_handler = LightingPreviewHandler(self)
        self.sdf_preview_handler = SDFPreviewHandler(self)

        # 暂时禁用主题管理器，避免初始化错误
        # self.theme_manager = get_theme_manager()
        # self.theme_switcher = None  # 将在UI初始化后创建
        
        # 初始化窗口
        self._init_window()
        self._init_ui()
        self._connect_signals()
        
        # 显示欢迎信息
        self._show_welcome_message()

    def _init_window(self):
        """初始化窗口属性"""
        WindowConfiguration.setup_window_properties(self)

    def _init_ui(self):
        """初始化用户界面"""
        # 设置主布局
        self.components = self.layout_manager.setup_main_layout()
        
        # 设置菜单栏
        self.menu_actions = self.layout_manager.setup_menu_bar()
        
        # 设置状态栏
        self.status_components = self.layout_manager.setup_status_bar()

        # 暂时禁用主题切换器
        # self.theme_switcher = CompactThemeSwitcher()
        # if hasattr(self, 'statusBar') and self.statusBar():
        #     self.statusBar().addPermanentWidget(self.theme_switcher)

    def _connect_signals(self):
        """连接信号和槽"""
        # 创建信号连接管理器
        self.signal_manager = SignalConnectionManager(self.components, self.event_handler)
        self.signal_manager.connect_all_signals()
        
        # 连接特定的主窗口信号
        self.event_handler.sdf_generated.connect(self._on_sdf_generated)

        # 暂时禁用主题相关功能
        # self.theme_manager.theme_changed.connect(self._on_theme_changed)
        # self.theme_manager.start_monitoring()
        self.event_handler.single_sdf_completed.connect(self._on_single_sdf_completed)
        self.event_handler.merged_sdf_updated.connect(self._on_merged_sdf_updated)
        self.components['angle_slider'].valueChanged.connect(self._on_angle_changed)

    def _show_welcome_message(self):
        """显示欢迎信息 - 安全地更新状态"""
        status_label = self.components.get('status_label')
        if status_label:
            status_label.setText("欢迎使用SDF工具！请导入图像开始使用。")

    def _on_sdf_generated(self, sdf_result, computation_time):
        """SDF生成完成处理 - 只处理最终完成的事务"""
        # 保存合并的SDF结果到光照处理器
        self.lighting_handler.set_merged_sdf(sdf_result)

        # 设置所有SDF卡片状态为完成（单张预览已在逐张计算时更新）
        self.sdf_preview_handler.set_all_sdf_cards_completed(self.components)

        # 显示调试信息
        print(f"✅ SDF生成完成!")
        print(f"📊 结果形状: {sdf_result.shape}")
        print(f"📈 值域: [{sdf_result.min():.3f}, {sdf_result.max():.3f}]")
        print(f"⏱️  计算时间: {computation_time:.3f}s")

    def _on_single_sdf_completed(self, image_path: str, sdf_result, computation_time: float):
        """单张SDF计算完成处理"""
        print(f"✅ 单张SDF完成: {Path(image_path).name}")

        # 使用SDF预览处理器更新卡片预览
        self.sdf_preview_handler.update_single_sdf_card_preview(
            self.components, image_path, sdf_result, computation_time
        )

    def _on_merged_sdf_updated(self, merged_sdf):
        """合并SDF更新处理"""
        print(f"🔄 合并SDF实时更新")

        # 使用SDF预览处理器更新合并预览
        self.sdf_preview_handler.update_merged_sdf_preview(self.components, merged_sdf)

        # 使用光照处理器更新光照预览
        self.lighting_handler.set_merged_sdf(merged_sdf)
        self._update_lighting_preview()



    def _on_angle_changed(self, angle: int):
        """角度改变处理 - 安全地更新角度显示和光照预览"""
        angle_label = self.components.get('angle_value_label')
        if angle_label:
            angle_label.setText(f"{angle}°")
        self._update_lighting_preview()



    def _update_lighting_preview(self):
        """更新光照效果预览 - 使用光照处理器"""
        try:
            lighting_preview = self.components.get('lighting_preview')
            angle_slider = self.components.get('angle_slider')

            if not lighting_preview or not angle_slider:
                return

            # 获取当前角度
            angle = angle_slider.value()

            # 使用光照处理器更新预览
            self.lighting_handler.update_lighting_preview(
                lighting_preview, angle, intensity=1.0, ambient=0.1
            )

        except Exception as e:
            print(f"❌ 更新光照预览失败: {e}")







    # 拖拽事件处理
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        self.event_handler.handle_drag_enter(event)

    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        self.event_handler.handle_drop(event)

    def _on_theme_changed(self, theme_name: str):
        """主题变化处理"""
        print(f"🎨 主题已切换到: {theme_name}")

        # 刷新所有组件的样式
        self._refresh_all_styles()

        # 刷新主题切换器样式
        if self.theme_switcher:
            self.theme_switcher.refresh_style()

    def _refresh_all_styles(self):
        """刷新所有组件的样式"""
        try:
            # 刷新所有ResponsiveGroupBox的样式
            from .responsive_layout import ResponsiveGroupBox
            for widget in self.findChildren(ResponsiveGroupBox):
                widget._apply_styles()

            # 刷新其他需要主题适配的组件
            # 这里可以添加更多组件的样式刷新逻辑

        except Exception as e:
            print(f"❌ 刷新样式失败: {e}")
