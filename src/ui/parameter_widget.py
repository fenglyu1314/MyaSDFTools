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

from typing import Dict, Any, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QSlider, QDoubleSpinBox, QSpinBox, QCheckBox,
    QComboBox, QGroupBox, QPushButton, QFrame, QScrollArea,
    QListWidget, QListWidgetItem, QLineEdit, QGridLayout, QToolButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

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
    """参数控制组件"""
    
    parameters_changed = Signal()  # 参数变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)

        # 角度配置数据
        self.image_angles = []  # 存储每张图像的角度配置
        self.angle_widgets = []  # 存储角度控件

        self._init_ui()
        self._connect_signals()
        self._load_default_parameters()
    
    def _init_ui(self):
        """初始化UI - 使用折叠式分组"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)  # 减少边距
        layout.setSpacing(5)  # 减少间距

        # 基础参数组 - 折叠式
        basic_group = CollapsibleGroupBox("基础参数")
        basic_content = self._create_basic_parameters_content()
        basic_group.add_widget(basic_content)
        layout.addWidget(basic_group)

        # 角度配置组 - 折叠式
        angle_group = CollapsibleGroupBox("角度配置")
        angle_content = self._create_angle_configuration_content()
        angle_group.add_widget(angle_content)
        layout.addWidget(angle_group)

        # 高级参数组 - 折叠式，默认折叠
        advanced_group = CollapsibleGroupBox("高级参数")
        advanced_group._toggle_expanded()  # 默认折叠
        advanced_content = self._create_advanced_parameters_content()
        advanced_group.add_widget(advanced_content)
        layout.addWidget(advanced_group)

        # 重置按钮 - 更紧凑
        reset_layout = QHBoxLayout()
        reset_layout.addStretch()

        self.reset_btn = QPushButton("重置")
        self.reset_btn.setMaximumWidth(60)  # 减少宽度
        self.reset_btn.setMaximumHeight(28)  # 减少高度
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 3px 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        reset_layout.addWidget(self.reset_btn)

        layout.addLayout(reset_layout)
        layout.addStretch()

    def _create_basic_parameters_content(self) -> QWidget:
        """创建基础参数内容"""
        widget = QWidget()
        form_layout = QFormLayout(widget)
        form_layout.setSpacing(5)  # 减少间距
        form_layout.setContentsMargins(0, 0, 0, 0)

        # 二值化阈值 - 更紧凑
        threshold_layout = QHBoxLayout()
        threshold_layout.setSpacing(5)

        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 100)
        self.threshold_slider.setValue(50)
        self.threshold_slider.setMaximumWidth(120)  # 限制宽度
        threshold_layout.addWidget(self.threshold_slider)

        self.threshold_spinbox = QDoubleSpinBox()
        self.threshold_spinbox.setRange(0.0, 1.0)
        self.threshold_spinbox.setSingleStep(0.01)
        self.threshold_spinbox.setDecimals(2)
        self.threshold_spinbox.setValue(0.50)
        self.threshold_spinbox.setMaximumWidth(60)  # 减少宽度
        threshold_layout.addWidget(self.threshold_spinbox)

        form_layout.addRow("阈值:", threshold_layout)

        # 归一化选项
        self.normalize_checkbox = QCheckBox("归一化输出")
        self.normalize_checkbox.setChecked(True)
        form_layout.addRow("", self.normalize_checkbox)

        # 反转内外
        self.invert_checkbox = QCheckBox("反转内外")
        self.invert_checkbox.setChecked(False)
        form_layout.addRow("", self.invert_checkbox)

        return widget

    def _create_angle_configuration_content(self) -> QWidget:
        """创建角度配置内容"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)  # 减少间距
        layout.setContentsMargins(0, 0, 0, 0)

        # 混合模式选择 - 更紧凑
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("混合:"))

        self.blend_mode_combo = QComboBox()
        self.blend_mode_combo.addItems([
            "智能权重",
            "简单平均",
            "最大值",
            "最小值"
        ])
        self.blend_mode_combo.setCurrentIndex(0)
        self.blend_mode_combo.setMaximumWidth(120)  # 限制宽度
        mode_layout.addWidget(self.blend_mode_combo)
        mode_layout.addStretch()

        layout.addLayout(mode_layout)

        # 角度分布模式 - 更紧凑
        distribution_layout = QHBoxLayout()
        distribution_layout.addWidget(QLabel("分布:"))

        self.angle_distribution_combo = QComboBox()
        self.angle_distribution_combo.addItems([
            "自动均匀",
            "手动设置"
        ])
        self.angle_distribution_combo.setCurrentIndex(0)
        self.angle_distribution_combo.setMaximumWidth(120)  # 限制宽度
        distribution_layout.addWidget(self.angle_distribution_combo)
        distribution_layout.addStretch()

        layout.addLayout(distribution_layout)

        # 角度列表区域 - 更小高度
        self.angle_list_widget = QListWidget()
        self.angle_list_widget.setMaximumHeight(80)  # 从120减少到80
        self.angle_list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                background-color: #FAFAFA;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 3px;
                border-bottom: 1px solid #EEEEEE;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
            }
        """)
        layout.addWidget(self.angle_list_widget)

        # 角度控制按钮 - 紧凑版
        button_layout = QHBoxLayout()
        button_layout.setSpacing(3)

        self.auto_distribute_btn = QPushButton("自动")
        self.auto_distribute_btn.setMaximumWidth(50)
        self.auto_distribute_btn.setMaximumHeight(24)
        self.auto_distribute_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 11px;
                padding: 2px 6px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        button_layout.addWidget(self.auto_distribute_btn)

        self.reset_angles_btn = QPushButton("重置")
        self.reset_angles_btn.setMaximumWidth(50)
        self.reset_angles_btn.setMaximumHeight(24)
        self.reset_angles_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 11px;
                padding: 2px 6px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        button_layout.addWidget(self.reset_angles_btn)

        self.analyze_angles_btn = QPushButton("分析")
        self.analyze_angles_btn.setMaximumWidth(50)
        self.analyze_angles_btn.setMaximumHeight(24)
        self.analyze_angles_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 11px;
                padding: 2px 6px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)
        button_layout.addWidget(self.analyze_angles_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # 角度验证状态 - 紧凑版
        self.angle_status_label = QLabel("✅ 正常")
        self.angle_status_label.setStyleSheet("color: #4CAF50; font-size: 10px;")
        layout.addWidget(self.angle_status_label)

        return widget

    def _create_advanced_parameters_content(self) -> QWidget:
        """创建高级参数内容"""
        widget = QWidget()
        form_layout = QFormLayout(widget)
        form_layout.setSpacing(5)  # 减少间距
        form_layout.setContentsMargins(0, 0, 0, 0)

        # 算法选择 - 更紧凑
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems([
            "8SSEDT",
            "Jump Flood",
            "Brute Force"
        ])
        self.algorithm_combo.setCurrentIndex(0)
        self.algorithm_combo.setMaximumWidth(120)  # 限制宽度
        form_layout.addRow("算法:", self.algorithm_combo)

        # 线程数 - 更紧凑
        thread_layout = QHBoxLayout()
        thread_layout.setSpacing(3)

        self.thread_spinbox = QSpinBox()
        self.thread_spinbox.setRange(0, 16)
        self.thread_spinbox.setValue(0)
        self.thread_spinbox.setSpecialValueText("自动")
        self.thread_spinbox.setMaximumWidth(60)  # 减少宽度
        thread_layout.addWidget(self.thread_spinbox)

        thread_info = QLabel("(自动)")
        thread_info.setStyleSheet("color: #666666; font-size: 10px;")
        thread_layout.addWidget(thread_info)
        thread_layout.addStretch()

        form_layout.addRow("线程:", thread_layout)

        # 内存限制 - 更紧凑
        memory_layout = QHBoxLayout()
        memory_layout.setSpacing(3)

        self.memory_spinbox = QSpinBox()
        self.memory_spinbox.setRange(512, 8192)
        self.memory_spinbox.setValue(2048)
        self.memory_spinbox.setSuffix("MB")
        self.memory_spinbox.setMaximumWidth(80)  # 减少宽度
        memory_layout.addWidget(self.memory_spinbox)
        memory_layout.addStretch()

        form_layout.addRow("内存:", memory_layout)

        # 质量设置 - 更紧凑
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            "高质量",
            "平衡",
            "高速度"
        ])
        self.quality_combo.setCurrentIndex(1)
        self.quality_combo.setMaximumWidth(120)  # 限制宽度
        form_layout.addRow("质量:", self.quality_combo)

        return widget

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

    def _create_angle_configuration(self) -> QGroupBox:
        """创建角度配置组"""
        group = QGroupBox("角度配置")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        # 混合模式选择
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("混合模式:"))

        self.blend_mode_combo = QComboBox()
        self.blend_mode_combo.addItems([
            "智能权重 (推荐)",
            "简单平均",
            "最大值混合",
            "最小值混合"
        ])
        self.blend_mode_combo.setCurrentIndex(0)
        mode_layout.addWidget(self.blend_mode_combo)
        mode_layout.addStretch()

        layout.addLayout(mode_layout)

        # 角度分布模式
        distribution_layout = QHBoxLayout()
        distribution_layout.addWidget(QLabel("角度分布:"))

        self.angle_distribution_combo = QComboBox()
        self.angle_distribution_combo.addItems([
            "自动均匀分布",
            "手动设置角度"
        ])
        self.angle_distribution_combo.setCurrentIndex(0)
        distribution_layout.addWidget(self.angle_distribution_combo)
        distribution_layout.addStretch()

        layout.addLayout(distribution_layout)

        # 角度列表区域
        self.angle_list_widget = QListWidget()
        self.angle_list_widget.setMaximumHeight(120)
        self.angle_list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                background-color: #FAFAFA;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #EEEEEE;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
            }
        """)
        layout.addWidget(self.angle_list_widget)

        # 角度控制按钮
        button_layout = QHBoxLayout()

        self.auto_distribute_btn = QPushButton("自动分布")
        self.auto_distribute_btn.setMaximumWidth(80)
        self.auto_distribute_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        button_layout.addWidget(self.auto_distribute_btn)

        self.reset_angles_btn = QPushButton("重置角度")
        self.reset_angles_btn.setMaximumWidth(80)
        self.reset_angles_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        button_layout.addWidget(self.reset_angles_btn)

        self.analyze_angles_btn = QPushButton("分析角度")
        self.analyze_angles_btn.setMaximumWidth(80)
        self.analyze_angles_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)
        button_layout.addWidget(self.analyze_angles_btn)

        button_layout.addStretch()

        # 角度验证状态
        self.angle_status_label = QLabel("✅ 角度配置正常")
        self.angle_status_label.setStyleSheet("color: #4CAF50; font-size: 11px;")
        button_layout.addWidget(self.angle_status_label)

        layout.addLayout(button_layout)

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

        # 角度配置信号
        self.blend_mode_combo.currentTextChanged.connect(self.parameters_changed)
        self.angle_distribution_combo.currentTextChanged.connect(self._on_angle_distribution_changed)
        self.auto_distribute_btn.clicked.connect(self._auto_distribute_angles)
        self.reset_angles_btn.clicked.connect(self._reset_angles)
        self.analyze_angles_btn.clicked.connect(self._show_angle_analysis)

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
        params = {
            'threshold': self.threshold_spinbox.value(),
            'normalize': self.normalize_checkbox.isChecked(),
            'invert': self.invert_checkbox.isChecked(),
            'num_threads': self.thread_spinbox.value() if self.thread_spinbox.value() > 0 else None
        }

        # 添加角度配置参数
        params.update(self.get_angle_params())
        return params

    def get_angle_params(self) -> Dict[str, Any]:
        """获取角度配置参数"""
        blend_mode_map = {
            "智能权重 (推荐)": "weighted",
            "简单平均": "average",
            "最大值混合": "max",
            "最小值混合": "min"
        }

        return {
            'blend_mode': blend_mode_map.get(self.blend_mode_combo.currentText(), "weighted"),
            'angles': self.get_current_angles(),
            'auto_distribute': self.angle_distribution_combo.currentIndex() == 0
        }

    def set_image_count(self, count: int):
        """设置图像数量，更新角度配置"""
        self.image_angles = [0.0] * count

        # 如果是自动分布模式，计算均匀角度
        if self.angle_distribution_combo.currentIndex() == 0:
            self._auto_distribute_angles()
        else:
            self._update_angle_list()

    def get_current_angles(self) -> List[float]:
        """获取当前角度列表"""
        return self.image_angles.copy()

    def _on_angle_distribution_changed(self):
        """角度分布模式改变"""
        if self.angle_distribution_combo.currentIndex() == 0:
            # 自动分布
            self._auto_distribute_angles()
        else:
            # 手动设置
            self._update_angle_list()

        self.parameters_changed.emit()

    def _auto_distribute_angles(self):
        """自动分布角度"""
        if not self.image_angles:
            return

        count = len(self.image_angles)
        if count == 1:
            self.image_angles[0] = 0.0
        else:
            angle_step = 360.0 / count
            for i in range(count):
                self.image_angles[i] = i * angle_step

        self._update_angle_list()
        self._validate_angles()
        self.parameters_changed.emit()

    def _reset_angles(self):
        """重置角度"""
        for i in range(len(self.image_angles)):
            self.image_angles[i] = 0.0

        self._update_angle_list()
        self._validate_angles()
        self.parameters_changed.emit()

    def _update_angle_list(self):
        """更新角度列表显示"""
        self.angle_list_widget.clear()

        for i, angle in enumerate(self.image_angles):
            item_widget = self._create_angle_item(i, angle)
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            self.angle_list_widget.addItem(item)
            self.angle_list_widget.setItemWidget(item, item_widget)

    def _create_angle_item(self, index: int, angle: float) -> QWidget:
        """创建角度项控件"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)

        # 图像标签
        label = QLabel(f"图像 {index + 1}:")
        label.setMinimumWidth(60)
        layout.addWidget(label)

        # 角度输入框
        angle_spinbox = QDoubleSpinBox()
        angle_spinbox.setRange(0.0, 359.9)
        angle_spinbox.setSingleStep(1.0)
        angle_spinbox.setDecimals(1)
        angle_spinbox.setValue(angle)
        angle_spinbox.setSuffix("°")
        angle_spinbox.setMaximumWidth(80)

        # 连接信号
        angle_spinbox.valueChanged.connect(
            lambda value, idx=index: self._on_angle_changed(idx, value)
        )

        layout.addWidget(angle_spinbox)
        layout.addStretch()

        return widget

    def _on_angle_changed(self, index: int, value: float):
        """角度值改变"""
        if 0 <= index < len(self.image_angles):
            self.image_angles[index] = value
            self._validate_angles()
            self.parameters_changed.emit()

    def _validate_angles(self):
        """验证角度配置"""
        if not self.image_angles:
            self.angle_status_label.setText("⚠️ 无图像")
            self.angle_status_label.setStyleSheet("color: #FF9800; font-size: 11px;")
            return

        if len(self.image_angles) == 1:
            self.angle_status_label.setText("✅ 单图像模式")
            self.angle_status_label.setStyleSheet("color: #4CAF50; font-size: 11px;")
            return

        # 进行详细的角度分析
        analysis = self._analyze_angle_coverage()

        # 根据分析结果设置状态
        if analysis['quality'] == 'excellent':
            self.angle_status_label.setText("✅ 角度配置优秀")
            self.angle_status_label.setStyleSheet("color: #4CAF50; font-size: 11px;")
        elif analysis['quality'] == 'good':
            self.angle_status_label.setText("✅ 角度配置良好")
            self.angle_status_label.setStyleSheet("color: #4CAF50; font-size: 11px;")
        elif analysis['quality'] == 'fair':
            self.angle_status_label.setText("⚠️ 角度配置一般")
            self.angle_status_label.setStyleSheet("color: #FF9800; font-size: 11px;")
        else:  # poor
            self.angle_status_label.setText("❌ 角度配置较差")
            self.angle_status_label.setStyleSheet("color: #F44336; font-size: 11px;")

        # 设置详细提示
        self.angle_status_label.setToolTip(analysis['tooltip'])

    def _analyze_angle_coverage(self) -> Dict[str, Any]:
        """分析角度覆盖情况"""
        if len(self.image_angles) < 2:
            return {
                'quality': 'good',
                'tooltip': '单图像模式，无需角度分析'
            }

        # 标准化角度到[0, 360)范围
        normalized_angles = [(angle % 360.0) for angle in self.image_angles]
        sorted_angles = sorted(set(normalized_angles))  # 去重并排序

        # 检查重复角度
        duplicates = len(normalized_angles) - len(sorted_angles)

        # 计算角度间隔
        gaps = []
        for i in range(len(sorted_angles)):
            next_angle = sorted_angles[(i + 1) % len(sorted_angles)]
            if i == len(sorted_angles) - 1:
                # 最后一个角度到第一个角度的间隔
                gap = (360.0 + sorted_angles[0] - sorted_angles[i]) % 360.0
            else:
                gap = next_angle - sorted_angles[i]
            gaps.append(gap)

        # 分析统计信息
        max_gap = max(gaps)
        min_gap = min(gaps)
        avg_gap = sum(gaps) / len(gaps)
        gap_variance = sum((gap - avg_gap) ** 2 for gap in gaps) / len(gaps)
        gap_std = gap_variance ** 0.5

        # 理想间隔
        ideal_gap = 360.0 / len(sorted_angles)

        # 质量评估
        quality_score = 0
        issues = []
        suggestions = []

        # 1. 检查重复角度
        if duplicates > 0:
            issues.append(f"发现 {duplicates} 个重复角度")
            suggestions.append("移除或调整重复的角度值")
            quality_score -= 20

        # 2. 检查最大间隔
        if max_gap > 180.0:
            issues.append(f"最大角度间隔过大: {max_gap:.1f}°")
            suggestions.append("在大间隔区域添加更多角度")
            quality_score -= 30
        elif max_gap > ideal_gap * 2:
            issues.append(f"存在较大角度间隔: {max_gap:.1f}°")
            suggestions.append("考虑调整角度分布使其更均匀")
            quality_score -= 15

        # 3. 检查最小间隔
        if min_gap < 10.0:
            issues.append(f"角度间隔过小: {min_gap:.1f}°")
            suggestions.append("增大过近角度之间的间距")
            quality_score -= 10

        # 4. 检查分布均匀性
        if gap_std > ideal_gap * 0.5:
            issues.append(f"角度分布不均匀 (标准差: {gap_std:.1f}°)")
            suggestions.append("使用自动分布功能获得更均匀的角度")
            quality_score -= 15

        # 5. 检查覆盖范围
        total_coverage = sum(gaps)
        if total_coverage < 300.0:
            issues.append(f"角度覆盖不足: {total_coverage:.1f}°")
            suggestions.append("增加更多角度以获得完整的360°覆盖")
            quality_score -= 25

        # 基础分数
        base_score = 100
        final_score = max(0, base_score + quality_score)

        # 确定质量等级
        if final_score >= 90:
            quality = 'excellent'
        elif final_score >= 70:
            quality = 'good'
        elif final_score >= 50:
            quality = 'fair'
        else:
            quality = 'poor'

        # 生成详细提示
        tooltip_lines = [
            f"角度分析报告 (评分: {final_score}/100)",
            f"图像数量: {len(self.image_angles)}",
            f"有效角度: {len(sorted_angles)}",
            f"角度范围: {min(sorted_angles):.1f}° - {max(sorted_angles):.1f}°",
            f"最大间隔: {max_gap:.1f}°",
            f"最小间隔: {min_gap:.1f}°",
            f"平均间隔: {avg_gap:.1f}° (理想: {ideal_gap:.1f}°)",
            ""
        ]

        if issues:
            tooltip_lines.append("⚠️ 发现的问题:")
            for issue in issues:
                tooltip_lines.append(f"  • {issue}")
            tooltip_lines.append("")

        if suggestions:
            tooltip_lines.append("💡 改进建议:")
            for suggestion in suggestions:
                tooltip_lines.append(f"  • {suggestion}")

        if not issues:
            tooltip_lines.append("✅ 角度配置优秀，无需调整")

        return {
            'quality': quality,
            'score': final_score,
            'gaps': gaps,
            'max_gap': max_gap,
            'min_gap': min_gap,
            'avg_gap': avg_gap,
            'issues': issues,
            'suggestions': suggestions,
            'tooltip': '\n'.join(tooltip_lines)
        }

    def _show_angle_analysis(self):
        """显示详细的角度分析对话框"""
        if not self.image_angles:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "角度分析", "没有图像需要分析")
            return

        analysis = self._analyze_angle_coverage()

        # 创建分析对话框
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("角度配置分析报告")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(dialog)

        # 分析报告文本
        report_text = QTextEdit()
        report_text.setReadOnly(True)
        report_text.setPlainText(analysis['tooltip'])
        report_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                background-color: #F5F5F5;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 10px;
            }
        """)
        layout.addWidget(report_text)

        # 按钮区域
        button_layout = QHBoxLayout()

        # 自动优化按钮
        if analysis['quality'] in ['fair', 'poor']:
            optimize_btn = QPushButton("自动优化角度")
            optimize_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            optimize_btn.clicked.connect(lambda: self._optimize_angles_and_close(dialog))
            button_layout.addWidget(optimize_btn)

        button_layout.addStretch()

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        # 显示对话框
        dialog.exec()

    def _optimize_angles_and_close(self, dialog):
        """优化角度并关闭对话框"""
        self._auto_distribute_angles()
        dialog.accept()

        # 显示优化结果
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "角度优化", "角度已自动优化为均匀分布")
