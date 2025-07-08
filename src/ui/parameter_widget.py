#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
参数控制组件

提供SDF生成参数的控制界面，包括：
- 阈值设置
- 归一化选项
- 算法选择
- 高级参数
"""

from typing import Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QSlider, QDoubleSpinBox, QSpinBox, QCheckBox,
    QComboBox, QGroupBox, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal

class ParameterWidget(QWidget):
    """参数控制组件"""
    
    parameters_changed = Signal()  # 参数变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._connect_signals()
        self._load_default_parameters()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 基础参数组
        basic_group = self._create_basic_parameters()
        layout.addWidget(basic_group)
        
        # 高级参数组
        advanced_group = self._create_advanced_parameters()
        layout.addWidget(advanced_group)
        
        # 重置按钮
        reset_layout = QHBoxLayout()
        reset_layout.addStretch()
        
        self.reset_btn = QPushButton("重置参数")
        self.reset_btn.setMaximumWidth(100)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        reset_layout.addWidget(self.reset_btn)
        
        layout.addLayout(reset_layout)
        layout.addStretch()
    
    def _create_basic_parameters(self) -> QGroupBox:
        """创建基础参数组"""
        group = QGroupBox("基础参数")
        form_layout = QFormLayout(group)
        form_layout.setSpacing(10)
        
        # 二值化阈值
        threshold_layout = QHBoxLayout()
        
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 100)
        self.threshold_slider.setValue(50)
        self.threshold_slider.setTickPosition(QSlider.TicksBelow)
        self.threshold_slider.setTickInterval(25)
        threshold_layout.addWidget(self.threshold_slider)
        
        self.threshold_spinbox = QDoubleSpinBox()
        self.threshold_spinbox.setRange(0.0, 1.0)
        self.threshold_spinbox.setSingleStep(0.01)
        self.threshold_spinbox.setDecimals(2)
        self.threshold_spinbox.setValue(0.50)
        self.threshold_spinbox.setMaximumWidth(80)
        threshold_layout.addWidget(self.threshold_spinbox)
        
        form_layout.addRow("二值化阈值:", threshold_layout)
        
        # 归一化选项
        self.normalize_checkbox = QCheckBox("归一化输出到 [0,1]")
        self.normalize_checkbox.setChecked(True)
        form_layout.addRow("", self.normalize_checkbox)
        
        # 反转内外
        self.invert_checkbox = QCheckBox("反转内外区域")
        self.invert_checkbox.setChecked(False)
        form_layout.addRow("", self.invert_checkbox)
        
        return group
    
    def _create_advanced_parameters(self) -> QGroupBox:
        """创建高级参数组"""
        group = QGroupBox("高级参数")
        form_layout = QFormLayout(group)
        form_layout.setSpacing(10)
        
        # 算法选择
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems([
            "8SSEDT (推荐)",
            "Jump Flood Algorithm",
            "Brute Force (慢)"
        ])
        self.algorithm_combo.setCurrentIndex(0)
        form_layout.addRow("算法:", self.algorithm_combo)
        
        # 线程数
        thread_layout = QHBoxLayout()
        
        self.thread_spinbox = QSpinBox()
        self.thread_spinbox.setRange(0, 16)
        self.thread_spinbox.setValue(0)
        self.thread_spinbox.setSpecialValueText("自动")
        self.thread_spinbox.setMaximumWidth(80)
        thread_layout.addWidget(self.thread_spinbox)
        
        thread_info = QLabel("(0=自动检测)")
        thread_info.setStyleSheet("color: #666666; font-size: 11px;")
        thread_layout.addWidget(thread_info)
        thread_layout.addStretch()
        
        form_layout.addRow("线程数:", thread_layout)
        
        # 内存限制
        memory_layout = QHBoxLayout()
        
        self.memory_spinbox = QSpinBox()
        self.memory_spinbox.setRange(512, 8192)
        self.memory_spinbox.setValue(2048)
        self.memory_spinbox.setSuffix(" MB")
        self.memory_spinbox.setMaximumWidth(100)
        memory_layout.addWidget(self.memory_spinbox)
        
        memory_layout.addStretch()
        
        form_layout.addRow("内存限制:", memory_layout)
        
        # 质量设置
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            "快速 (低质量)",
            "平衡 (推荐)",
            "高质量 (慢)"
        ])
        self.quality_combo.setCurrentIndex(1)
        form_layout.addRow("质量:", self.quality_combo)
        
        return group
    
    def _connect_signals(self):
        """连接信号"""
        # 阈值控件同步
        self.threshold_slider.valueChanged.connect(self._on_threshold_slider_changed)
        self.threshold_spinbox.valueChanged.connect(self._on_threshold_spinbox_changed)
        
        # 参数变化信号
        self.threshold_slider.valueChanged.connect(self.parameters_changed)
        self.threshold_spinbox.valueChanged.connect(self.parameters_changed)
        self.normalize_checkbox.toggled.connect(self.parameters_changed)
        self.invert_checkbox.toggled.connect(self.parameters_changed)
        self.algorithm_combo.currentTextChanged.connect(self.parameters_changed)
        self.thread_spinbox.valueChanged.connect(self.parameters_changed)
        self.memory_spinbox.valueChanged.connect(self.parameters_changed)
        self.quality_combo.currentTextChanged.connect(self.parameters_changed)
        
        # 重置按钮
        self.reset_btn.clicked.connect(self._reset_parameters)
    
    def _load_default_parameters(self):
        """加载默认参数"""
        # 默认参数已在UI初始化时设置
        pass
    
    def _on_threshold_slider_changed(self, value):
        """阈值滑竿变化"""
        threshold_value = value / 100.0
        self.threshold_spinbox.blockSignals(True)
        self.threshold_spinbox.setValue(threshold_value)
        self.threshold_spinbox.blockSignals(False)
    
    def _on_threshold_spinbox_changed(self, value):
        """阈值输入框变化"""
        slider_value = int(value * 100)
        self.threshold_slider.blockSignals(True)
        self.threshold_slider.setValue(slider_value)
        self.threshold_slider.blockSignals(False)
    
    def _reset_parameters(self):
        """重置所有参数到默认值"""
        # 阻止信号发射
        self._block_all_signals(True)
        
        # 重置参数
        self.threshold_slider.setValue(50)
        self.threshold_spinbox.setValue(0.50)
        self.normalize_checkbox.setChecked(True)
        self.invert_checkbox.setChecked(False)
        self.algorithm_combo.setCurrentIndex(0)
        self.thread_spinbox.setValue(0)
        self.memory_spinbox.setValue(2048)
        self.quality_combo.setCurrentIndex(1)
        
        # 恢复信号
        self._block_all_signals(False)
        
        # 发射参数变化信号
        self.parameters_changed.emit()
    
    def _block_all_signals(self, block: bool):
        """阻止/恢复所有控件的信号"""
        controls = [
            self.threshold_slider, self.threshold_spinbox,
            self.normalize_checkbox, self.invert_checkbox,
            self.algorithm_combo, self.thread_spinbox,
            self.memory_spinbox, self.quality_combo
        ]
        
        for control in controls:
            control.blockSignals(block)
    
    def get_parameters(self) -> Dict[str, Any]:
        """获取当前参数"""
        return {
            'threshold': self.threshold_spinbox.value(),
            'normalize': self.normalize_checkbox.isChecked(),
            'invert': self.invert_checkbox.isChecked(),
            'algorithm': self.algorithm_combo.currentText(),
            'num_threads': self.thread_spinbox.value(),
            'memory_limit_mb': self.memory_spinbox.value(),
            'quality': self.quality_combo.currentText()
        }
    
    def set_parameters(self, params: Dict[str, Any]):
        """设置参数"""
        self._block_all_signals(True)
        
        if 'threshold' in params:
            threshold = params['threshold']
            self.threshold_spinbox.setValue(threshold)
            self.threshold_slider.setValue(int(threshold * 100))
        
        if 'normalize' in params:
            self.normalize_checkbox.setChecked(params['normalize'])
        
        if 'invert' in params:
            self.invert_checkbox.setChecked(params['invert'])
        
        if 'algorithm' in params:
            algorithm = params['algorithm']
            index = self.algorithm_combo.findText(algorithm)
            if index >= 0:
                self.algorithm_combo.setCurrentIndex(index)
        
        if 'num_threads' in params:
            self.thread_spinbox.setValue(params['num_threads'])
        
        if 'memory_limit_mb' in params:
            self.memory_spinbox.setValue(params['memory_limit_mb'])
        
        if 'quality' in params:
            quality = params['quality']
            index = self.quality_combo.findText(quality)
            if index >= 0:
                self.quality_combo.setCurrentIndex(index)
        
        self._block_all_signals(False)
        self.parameters_changed.emit()
    
    def get_sdf_params(self) -> Dict[str, Any]:
        """获取SDF算法专用参数"""
        return {
            'threshold': self.threshold_spinbox.value(),
            'normalize': self.normalize_checkbox.isChecked(),
            'invert': self.invert_checkbox.isChecked(),
            'num_threads': self.thread_spinbox.value() if self.thread_spinbox.value() > 0 else None
        }
