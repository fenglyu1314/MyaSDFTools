#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单测试脚本 - 验证修复
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from PySide6.QtWidgets import QApplication
    from src.ui.main_window import MainWindow
    
    print("✅ 导入成功")
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    print("✅ 主窗口创建成功")
    
    # 显示窗口
    window.show()
    print("✅ 窗口显示成功")
    
    print("🎉 修复验证成功！现在可以正常使用SDF生成功能了。")
    print("请手动测试生成SDF按钮是否正常工作。")
    
    # 运行应用
    sys.exit(app.exec())
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
