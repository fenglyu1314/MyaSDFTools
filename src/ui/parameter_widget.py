#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
参数控制组件 - 简化版

提供SDF生成参数的控制界面，包括：
- 阈值设置
- 归一化选项
- 混合模式
- 高级参数
"""

from typing import Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QSlider, QDoubleSpinBox, QSpinBox, QCheckBox,
    QComboBox, QGroupBox, QPushButton, QScrollArea, QToolButton
)
from PySide6.QtCore import Qt, Signal

class CollapsibleGroupBox(QWidget):
    """可折叠的组框"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.is_expanded = True
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题按钮
        self.title_button = QToolButton()
        self.title_button.setText(self.title)
        self.title_button.setCheckable(True)
        self.title_button.setChecked(True)
        self.title_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.title_button.setArrowType(Qt.DownArrow)
        self.title_button.setStyleSheet("""
            QToolButton {
                background-color: #F0F0F0;
                border: 1px solid #CCCCCC;
                padding: 5px;
                font-weight: bold;
                text-align: left;
            }
            QToolButton:hover {
                background-color: #E0E0E0;
            }
        """)
        self.title_button.clicked.connect(self._toggle_expanded)
        layout.addWidget(self.title_button)

        # 内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.content_widget)

    def _toggle_expanded(self):
        """切换展开/折叠状态"""
        self.is_expanded = not self.is_expanded
        self.content_widget.setVisible(self.is_expanded)
        self.title_button.setArrowType(Qt.DownArrow if self.is_expanded else Qt.RightArrow)

    def add_widget(self, widget):
        """添加控件到内容区域"""
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        """添加布局到内容区域"""
        self.content_layout.addLayout(layout)

class ParameterWidget(QWidget):
    """参数控制组件 - 简化版"""
    
    parameters_changed = Signal()  # 参数变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._connect_signals()
        self._load_default_parameters()
    
    def _init_ui(self):
        """初始化UI - 扁平化布局，所有参数直接排列"""
        layout = QFormLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        # layout.setSpacing(6)  # 紧凑间距

        # 直接添加所有参数，不使用分组容器
        self._create_all_parameters(layout)



    def _create_all_parameters(self, layout: QFormLayout):
        """创建所有参数控件 - 扁平化布局"""

        # === 基础SDF参数 ===
        # 阈值设置 - 范围0-1
        threshold_layout = QHBoxLayout()
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 100)  # 0-100对应0.0-1.0
        self.threshold_slider.setValue(50)  # 默认0.5
        threshold_layout.addWidget(self.threshold_slider)

        self.threshold_spinbox = QDoubleSpinBox()
        self.threshold_spinbox.setRange(0.0, 1.0)
        self.threshold_spinbox.setSingleStep(0.01)
        self.threshold_spinbox.setDecimals(2)
        self.threshold_spinbox.setValue(0.5)
        self.threshold_spinbox.setFixedWidth(80)
        threshold_layout.addWidget(self.threshold_spinbox)
        threshold_layout.addStretch()
        layout.addRow("阈值:", threshold_layout)

        # 选项设置
        options_layout = QHBoxLayout()
        self.normalize_checkbox = QCheckBox("归一化")
        self.normalize_checkbox.setChecked(True)
        options_layout.addWidget(self.normalize_checkbox)

        self.invert_checkbox = QCheckBox("反转")
        self.invert_checkbox.setChecked(False)
        options_layout.addWidget(self.invert_checkbox)
        options_layout.addStretch()
        layout.addRow("选项:", options_layout)

        # SDF计算方向
        self.sdf_direction_combo = QComboBox()
        self.sdf_direction_combo.addItems(["双向计算", "只向内", "只向外"])
        self.sdf_direction_combo.setCurrentText("双向计算")
        layout.addRow("计算方向:", self.sdf_direction_combo)

        # === 混合模式 ===
        self.blend_mode_combo = QComboBox()
        self.blend_mode_combo.addItems(["智能权重", "简单平均", "最大值", "最小值"])
        self.blend_mode_combo.setCurrentText("智能权重")
        #self.blend_mode_combo.setFixedWidth(120)
        layout.addRow("混合模式:", self.blend_mode_combo)

        # === 高级参数 ===
        # 最大距离 - 改为滑竿设置，范围1-1000
        max_distance_layout = QHBoxLayout()
        self.max_distance_slider = QSlider(Qt.Horizontal)
        self.max_distance_slider.setRange(1, 1000)
        self.max_distance_slider.setValue(100)
        max_distance_layout.addWidget(self.max_distance_slider)

        self.max_distance_spinbox = QSpinBox()
        self.max_distance_spinbox.setRange(1, 1000)
        self.max_distance_spinbox.setValue(100)
        self.max_distance_spinbox.setSuffix(" px")
        self.max_distance_spinbox.setFixedWidth(80)
        max_distance_layout.addWidget(self.max_distance_spinbox)
        max_distance_layout.addStretch()
        layout.addRow("最大距离:", max_distance_layout)

        # 算法选择
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["8SSEDT", "欧几里得", "曼哈顿", "切比雪夫"])
        self.algorithm_combo.setCurrentText("8SSEDT")
        #self.algorithm_combo.setFixedWidth(120)
        layout.addRow("算法:", self.algorithm_combo)

        # 线程数
        self.thread_spinbox = QSpinBox()
        self.thread_spinbox.setRange(1, 16)
        self.thread_spinbox.setValue(1)
        #self.thread_spinbox.setFixedWidth(60)
        layout.addRow("线程数:", self.thread_spinbox)

        # 内存限制
        self.memory_spinbox = QSpinBox()
        self.memory_spinbox.setRange(512, 8192)
        self.memory_spinbox.setValue(2048)
        self.memory_spinbox.setSuffix(" MB")
        #self.memory_spinbox.setFixedWidth(100)
        layout.addRow("内存限制:", self.memory_spinbox)

        # 质量设置
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["快速", "标准", "高质量"])
        self.quality_combo.setCurrentText("标准")
        #self.quality_combo.setFixedWidth(120)
        layout.addRow("质量:", self.quality_combo)

        # 重置按钮 - 直接添加到FormLayout
        self.reset_btn = QPushButton("重置参数")
        self.reset_btn.setFixedSize(80, 28)  # 缩小按钮
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        layout.addRow("", self.reset_btn)





    def _connect_signals(self):
        """连接信号"""
        # 控件同步信号
        self.threshold_slider.valueChanged.connect(self._on_threshold_slider_changed)
        self.threshold_spinbox.valueChanged.connect(self._on_threshold_spinbox_changed)
        self.max_distance_slider.valueChanged.connect(self._on_max_distance_slider_changed)
        self.max_distance_spinbox.valueChanged.connect(self._on_max_distance_spinbox_changed)
        self.normalize_checkbox.toggled.connect(self.parameters_changed)
        self.invert_checkbox.toggled.connect(self.parameters_changed)
        self.sdf_direction_combo.currentTextChanged.connect(self.parameters_changed)
        self.blend_mode_combo.currentTextChanged.connect(self.parameters_changed)
        self.max_distance_slider.valueChanged.connect(self.parameters_changed)
        self.max_distance_spinbox.valueChanged.connect(self.parameters_changed)
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
        self.parameters_changed.emit()

    def _on_threshold_spinbox_changed(self, value):
        """阈值数值框变化"""
        slider_value = int(value * 100)
        self.threshold_slider.blockSignals(True)
        self.threshold_slider.setValue(slider_value)
        self.threshold_slider.blockSignals(False)
        self.parameters_changed.emit()

    def _on_max_distance_slider_changed(self, value):
        """最大距离滑竿变化"""
        self.max_distance_spinbox.blockSignals(True)
        self.max_distance_spinbox.setValue(value)
        self.max_distance_spinbox.blockSignals(False)
        self.parameters_changed.emit()

    def _on_max_distance_spinbox_changed(self, value):
        """最大距离数值框变化"""
        self.max_distance_slider.blockSignals(True)
        self.max_distance_slider.setValue(value)
        self.max_distance_slider.blockSignals(False)
        self.parameters_changed.emit()
    
    def _reset_parameters(self):
        """重置所有参数到默认值"""
        # 阻止信号发射
        self._block_all_signals(True)
        
        # 重置基础参数
        self.threshold_slider.setValue(50)
        self.threshold_spinbox.setValue(0.5)
        self.normalize_checkbox.setChecked(True)
        self.invert_checkbox.setChecked(False)

        # 重置SDF计算方向
        self.sdf_direction_combo.setCurrentIndex(0)

        # 重置混合模式
        self.blend_mode_combo.setCurrentIndex(0)

        # 重置高级参数
        self.max_distance_slider.setValue(100)
        self.max_distance_spinbox.setValue(100)
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
            self.sdf_direction_combo, self.blend_mode_combo,
            self.max_distance_slider, self.max_distance_spinbox,
            self.algorithm_combo, self.thread_spinbox,
            self.memory_spinbox, self.quality_combo
        ]

        for control in controls:
            control.blockSignals(block)
    
    def get_sdf_params(self) -> Dict[str, Any]:
        """获取SDF算法专用参数"""
        return {
            'threshold': self.threshold_spinbox.value(),
            'normalize': self.normalize_checkbox.isChecked(),
            'invert': self.invert_checkbox.isChecked(),
            'sdf_direction': self.get_sdf_direction(),
            'max_distance': self.max_distance_spinbox.value(),
            'num_threads': self.thread_spinbox.value() if self.thread_spinbox.value() > 0 else None
        }
    
    def get_sdf_direction(self) -> str:
        """获取SDF计算方向"""
        direction_map = {
            "双向计算": "both",
            "只向内": "inside",
            "只向外": "outside"
        }
        return direction_map.get(self.sdf_direction_combo.currentText(), "both")

    def get_blend_mode(self) -> str:
        """获取混合模式"""
        blend_mode_map = {
            "智能权重": "weighted",
            "简单平均": "average",
            "最大值": "max",
            "最小值": "min"
        }
        return blend_mode_map.get(self.blend_mode_combo.currentText(), "weighted")
