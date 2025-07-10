#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
参数控制组件 - 重构后的简化版

提供SDF生成参数的控制界面，使用模块化设计
"""

from typing import Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QSlider, QDoubleSpinBox, QSpinBox, QCheckBox,
    QComboBox, QGroupBox, QPushButton
)
from PySide6.QtCore import Qt, Signal

from .parameter_defaults import ParameterDefaults
from .parameter_validators import ParameterValidator


class ParameterWidget(QWidget):
    """参数控制组件 - 重构后的简化版"""
    
    parameters_changed = Signal()  # 参数变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.validator = ParameterValidator()
        self._init_ui()
        self._connect_signals()
        self._load_default_parameters()
    
    def _init_ui(self):
        """初始化UI - 扁平化布局"""
        layout = QFormLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # 创建所有参数控件
        self._create_basic_parameters(layout)
        self._create_advanced_parameters(layout)

    def _create_basic_parameters(self, layout: QFormLayout):
        """创建基础参数控件"""
        # 阈值设置
        threshold_layout = QHBoxLayout()
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 100)
        self.threshold_slider.setValue(50)
        threshold_layout.addWidget(self.threshold_slider)

        self.threshold_spinbox = QDoubleSpinBox()
        self.threshold_spinbox.setRange(0.0, 1.0)
        self.threshold_spinbox.setSingleStep(0.01)
        self.threshold_spinbox.setDecimals(2)
        self.threshold_spinbox.setValue(0.5)
        self.threshold_spinbox.setFixedWidth(80)
        threshold_layout.addWidget(self.threshold_spinbox)
        layout.addRow("阈值:", threshold_layout)

        # 选项设置
        options_layout = QHBoxLayout()
        self.normalize_checkbox = QCheckBox("归一化")
        self.normalize_checkbox.setChecked(True)
        options_layout.addWidget(self.normalize_checkbox)

        self.invert_checkbox = QCheckBox("反转")
        self.invert_checkbox.setChecked(False)
        options_layout.addWidget(self.invert_checkbox)
        layout.addRow("选项:", options_layout)

        # SDF计算方向
        self.sdf_direction_combo = QComboBox()
        direction_options = ParameterDefaults.get_sdf_direction_options()
        for value, display in direction_options:
            self.sdf_direction_combo.addItem(display, value)
        layout.addRow("计算方向:", self.sdf_direction_combo)

        # 混合模式 - 隐藏控件，因为只有一个选项
        self.blend_mode_combo = QComboBox()
        blend_options = ParameterDefaults.get_blend_mode_options()
        for value, display in blend_options:
            self.blend_mode_combo.addItem(display, value)
        # 不添加到布局中，因为只有一个选项，用户无需选择
        # layout.addRow("混合模式:", self.blend_mode_combo)

    def _create_advanced_parameters(self, layout: QFormLayout):
        """创建高级参数控件"""
        # 最大距离
        max_distance_layout = QHBoxLayout()
        self.max_distance_slider = QSlider(Qt.Horizontal)
        self.max_distance_slider.setRange(1, 1000)
        self.max_distance_slider.setValue(100)
        max_distance_layout.addWidget(self.max_distance_slider)

        self.max_distance_spinbox = QSpinBox()
        self.max_distance_spinbox.setRange(1, 1000)
        self.max_distance_spinbox.setValue(100)
        self.max_distance_spinbox.setFixedWidth(80)
        max_distance_layout.addWidget(self.max_distance_spinbox)
        layout.addRow("最大距离:", max_distance_layout)

        # 后端选择
        self.use_cpp_checkbox = QCheckBox("使用C++后端")
        self.use_cpp_checkbox.setChecked(True)
        layout.addRow("后端:", self.use_cpp_checkbox)

    def _connect_signals(self):
        """连接信号"""
        # 阈值同步
        self.threshold_slider.valueChanged.connect(self._on_threshold_slider_changed)
        self.threshold_spinbox.valueChanged.connect(self._on_threshold_spinbox_changed)
        
        # 最大距离同步
        self.max_distance_slider.valueChanged.connect(self._on_max_distance_slider_changed)
        self.max_distance_spinbox.valueChanged.connect(self._on_max_distance_spinbox_changed)
        
        # 参数变化信号
        self.threshold_spinbox.valueChanged.connect(self.parameters_changed.emit)
        self.normalize_checkbox.toggled.connect(self.parameters_changed.emit)
        self.invert_checkbox.toggled.connect(self.parameters_changed.emit)
        self.sdf_direction_combo.currentTextChanged.connect(self.parameters_changed.emit)
        self.blend_mode_combo.currentTextChanged.connect(self.parameters_changed.emit)
        self.max_distance_spinbox.valueChanged.connect(self.parameters_changed.emit)
        self.use_cpp_checkbox.toggled.connect(self.parameters_changed.emit)

    def _on_threshold_slider_changed(self, value):
        """阈值滑竿变化"""
        threshold_value = value / 100.0
        self.threshold_spinbox.blockSignals(True)
        self.threshold_spinbox.setValue(threshold_value)
        self.threshold_spinbox.blockSignals(False)

    def _on_threshold_spinbox_changed(self, value):
        """阈值数值框变化"""
        slider_value = int(value * 100)
        self.threshold_slider.blockSignals(True)
        self.threshold_slider.setValue(slider_value)
        self.threshold_slider.blockSignals(False)

    def _on_max_distance_slider_changed(self, value):
        """最大距离滑竿变化"""
        self.max_distance_spinbox.blockSignals(True)
        self.max_distance_spinbox.setValue(value)
        self.max_distance_spinbox.blockSignals(False)

    def _on_max_distance_spinbox_changed(self, value):
        """最大距离数值框变化"""
        self.max_distance_slider.blockSignals(True)
        self.max_distance_slider.setValue(value)
        self.max_distance_slider.blockSignals(False)

    def _load_default_parameters(self):
        """加载默认参数"""
        defaults = ParameterDefaults.get_all_defaults()
        
        # 设置默认值
        self.threshold_spinbox.setValue(defaults.get('threshold', 0.5))
        self.normalize_checkbox.setChecked(defaults.get('normalize', True))
        self.invert_checkbox.setChecked(defaults.get('invert', False))
        self.max_distance_spinbox.setValue(defaults.get('max_distance', 100))
        self.use_cpp_checkbox.setChecked(defaults.get('use_cpp_backend', True))
        
        # 设置组合框默认值
        self._set_combo_default(self.sdf_direction_combo, defaults.get('sdf_direction', 'both'))
        self._set_combo_default(self.blend_mode_combo, defaults.get('blend_mode', 'sdf_blend'))

    def _set_combo_default(self, combo: QComboBox, value: str):
        """设置组合框默认值"""
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                break

    def get_sdf_params(self) -> Dict[str, Any]:
        """获取SDF参数"""
        params = {
            'threshold': self.threshold_spinbox.value(),
            'normalize': self.normalize_checkbox.isChecked(),
            'invert': self.invert_checkbox.isChecked(),
            'sdf_direction': self.sdf_direction_combo.currentData(),
            'blend_mode': self.blend_mode_combo.currentData(),
            'max_distance': self.max_distance_spinbox.value(),
            'use_cpp_backend': self.use_cpp_checkbox.isChecked()
        }
        
        # 验证参数
        is_valid, errors = self.validator.validate_all_parameters(params)
        if not is_valid:
            print(f"⚠️ 参数验证失败: {errors}")
            params = self.validator.sanitize_parameters(params)
        
        return params

    def set_parameters(self, params: Dict[str, Any]):
        """设置参数值"""
        # 验证和清理参数
        params = self.validator.sanitize_parameters(params)
        
        # 阻止信号发射
        self.blockSignals(True)
        
        try:
            if 'threshold' in params:
                self.threshold_spinbox.setValue(params['threshold'])
            if 'normalize' in params:
                self.normalize_checkbox.setChecked(params['normalize'])
            if 'invert' in params:
                self.invert_checkbox.setChecked(params['invert'])
            if 'max_distance' in params:
                self.max_distance_spinbox.setValue(params['max_distance'])
            if 'use_cpp_backend' in params:
                self.use_cpp_checkbox.setChecked(params['use_cpp_backend'])
            if 'sdf_direction' in params:
                self._set_combo_default(self.sdf_direction_combo, params['sdf_direction'])
            if 'blend_mode' in params:
                self._set_combo_default(self.blend_mode_combo, params['blend_mode'])
        finally:
            self.blockSignals(False)
            self.parameters_changed.emit()

    def reset_to_defaults(self):
        """重置为默认值"""
        self._load_default_parameters()
        self.parameters_changed.emit()

    def validate_current_parameters(self) -> bool:
        """验证当前参数"""
        params = self.get_sdf_params()
        is_valid, errors = self.validator.validate_all_parameters(params)
        
        if not is_valid:
            print(f"❌ 参数验证失败: {errors}")
        
        return is_valid
