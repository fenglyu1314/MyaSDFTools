#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
直接测试SDF生成和预览功能

绕过主窗口，直接测试预览组件
"""

import sys
import os
import numpy as np
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

from core.sdf_generator import SDFGenerator

def create_simple_sdf():
    """创建简单的测试SDF"""
    size = 128
    center = size // 2
    radius = 40
    
    sdf = np.zeros((size, size), dtype=np.float32)
    
    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center
            distance = np.sqrt(dx*dx + dy*dy)
            
            if distance <= radius:
                # 内部：距离中心越近值越大
                sdf[y, x] = 1.0 - (distance / radius)
            else:
                # 外部：距离边界越远值越小
                sdf[y, x] = max(0.0, 1.0 - (distance - radius) / 20.0)
    
    return sdf

class TestWindow(QMainWindow):
    """测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SDF预览测试")
        self.setMinimumSize(800, 600)
        
        # 创建中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 创建预览组件
        sys.path.append(str(Path(__file__).parent / "src" / "ui"))
        from preview_widget import PreviewWidget
        self.preview_widget = PreviewWidget()
        layout.addWidget(self.preview_widget)
        
        # 测试SDF数据
        self._test_sdf_preview()
    
    def _test_sdf_preview(self):
        """测试SDF预览"""
        print("🧪 开始测试SDF预览功能")
        
        # 创建测试SDF
        sdf_data = create_simple_sdf()
        print(f"📊 创建测试SDF: 类型={type(sdf_data)}, 形状={sdf_data.shape}")
        print(f"📈 值域: [{sdf_data.min():.3f}, {sdf_data.max():.3f}]")
        
        # 直接设置SDF结果
        print("🔧 设置SDF结果到预览组件...")
        self.preview_widget.set_sdf_result(sdf_data)
        
        print("✅ SDF预览测试完成")
        print("💡 请检查预览窗口:")
        print("   - 左侧应显示原始SDF")
        print("   - 右侧应显示光照效果")
        print("   - 拖动光照角度滑竿应该有效果")

def main():
    """主函数"""
    print("🎨 SDF预览直接测试")
    print("=" * 40)
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = TestWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
