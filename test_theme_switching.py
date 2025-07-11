#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主题切换功能测试脚本

用于测试动态主题切换功能
"""

import sys
import time
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QTimer

from src.ui.theme_manager import get_theme_manager, ThemeMode
from src.ui.theme_switcher_widget import ThemeSwitcherWidget


class ThemeTestWindow(QWidget):
    """主题测试窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.theme_manager = get_theme_manager()
        self.init_ui()
        self.connect_signals()
        
        # 启动主题监听
        self.theme_manager.start_monitoring()
        
        # 应用初始主题
        self.apply_theme()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("主题切换测试")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 标题
        self.title_label = QLabel("主题切换功能测试")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)
        
        # 当前主题显示
        self.theme_info_label = QLabel()
        layout.addWidget(self.theme_info_label)
        
        # 主题切换控件
        self.theme_switcher = ThemeSwitcherWidget()
        layout.addWidget(self.theme_switcher)
        
        # 测试按钮
        self.test_btn = QPushButton("测试按钮")
        layout.addWidget(self.test_btn)
        
        # 状态标签
        self.status_label = QLabel("状态: 准备就绪")
        layout.addWidget(self.status_label)
        
        # 更新主题信息
        self.update_theme_info()
    
    def connect_signals(self):
        """连接信号"""
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        self.theme_switcher.theme_mode_changed.connect(self.on_theme_mode_changed)
    
    def on_theme_changed(self, theme_name):
        """主题变化处理"""
        print(f"🎨 主题已切换到: {theme_name}")
        self.apply_theme()
        self.update_theme_info()
        self.status_label.setText(f"状态: 主题已切换到 {theme_name}")
    
    def on_theme_mode_changed(self, theme_mode):
        """主题模式变化处理"""
        print(f"🎨 主题模式已切换到: {theme_mode.value}")
        self.status_label.setText(f"状态: 主题模式已切换到 {theme_mode.value}")
    
    def apply_theme(self):
        """应用主题"""
        colors = self.theme_manager.get_theme_colors()
        
        # 应用全局样式
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['bg_primary']};
                color: {colors['text_primary']};
            }}
            QLabel {{
                color: {colors['text_primary']};
                padding: 5px;
            }}
            QPushButton {{
                background-color: {colors['accent']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors['accent']};
                opacity: 0.8;
            }}
        """)
        
        # 刷新主题切换控件样式
        self.theme_switcher.refresh_style()
    
    def update_theme_info(self):
        """更新主题信息显示"""
        current_mode = self.theme_manager.get_current_mode()
        current_theme = self.theme_manager.get_current_theme()
        
        info_text = f"""
当前主题模式: {current_mode.value}
当前主题: {current_theme}
        """.strip()
        
        self.theme_info_label.setText(info_text)
    
    def closeEvent(self, event):
        """关闭事件"""
        self.theme_manager.stop_monitoring()
        super().closeEvent(event)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = ThemeTestWindow()
    window.show()
    
    print("🎨 主题切换测试窗口已启动")
    print("💡 请尝试:")
    print("   1. 使用下拉框切换主题模式")
    print("   2. 在系统设置中切换深色/浅色模式（如果选择了'跟随系统'）")
    print("   3. 观察窗口样式的实时变化")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
