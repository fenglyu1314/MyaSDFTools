#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试角度配置界面

验证新的角度配置功能是否正常工作
"""

import sys
import os
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

# 直接导入参数控件，避免相对导入问题
import sys
sys.path.append(str(Path(__file__).parent / "src" / "ui"))
from parameter_widget import ParameterWidget

class TestWindow(QMainWindow):
    """测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("角度配置界面测试")
        self.setMinimumSize(400, 600)
        
        # 创建中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 创建参数控件
        self.parameter_widget = ParameterWidget()
        layout.addWidget(self.parameter_widget)
        
        # 连接信号
        self.parameter_widget.parameters_changed.connect(self._on_parameters_changed)
        
        # 模拟设置不同数量的图像
        self._test_different_image_counts()
    
    def _test_different_image_counts(self):
        """测试不同图像数量"""
        # 模拟4张图像
        self.parameter_widget.set_image_count(4)
        print("设置4张图像，角度:", self.parameter_widget.get_current_angles())
    
    def _on_parameters_changed(self):
        """参数变化处理"""
        params = self.parameter_widget.get_angle_params()
        print("角度参数变化:", params)

def main():
    """主函数"""
    print("🎨 角度配置界面测试")
    print("=" * 40)
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = TestWindow()
    window.show()
    
    print("✅ 界面已启动")
    print("💡 请在界面中测试角度配置功能")
    print("   - 切换混合模式")
    print("   - 切换角度分布模式")
    print("   - 手动调整角度值")
    print("   - 点击自动分布按钮")
    print("   - 观察角度验证状态")
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
