#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主窗口模块

实现SDF工具的主界面，包含：
- 图像导入区域
- SDF预览区域  
- 参数控制面板
- 菜单栏和状态栏
"""

import sys
import os
from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QProgressBar, QStatusBar, QMenuBar,
    QFileDialog, QMessageBox, QSplitter, QGroupBox, QSlider,
    QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QTextEdit,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QSize
from PySide6.QtGui import QPixmap, QAction, QIcon, QFont, QDragEnterEvent, QDropEvent

# 导入自定义组件
from .image_list_widget import ImageListWidget
from .preview_widget import PreviewWidget
from .parameter_widget import ParameterWidget

# 导入核心模块
from ..core.sdf_generator import SDFGenerator
from ..core.image_manager import ImageManager
from ..utils.image_utils import ImageUtils

class MainWindow(QMainWindow):
    """SDF工具主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SDF工具 - 二次元脸部SDF生成")
        self.setMinimumSize(1200, 800)
        
        # 初始化变量
        self.current_images: List[str] = []
        self.sdf_result: Optional[object] = None
        self.computation_time: float = 0.0

        # 初始化核心组件
        self.sdf_generator = SDFGenerator()
        self.image_manager = ImageManager()
        
        # 设置窗口图标
        self._set_window_icon()
        
        # 初始化UI
        self._init_ui()
        self._init_menu_bar()
        self._init_status_bar()
        self._connect_signals()
        
        # 启用拖拽
        self.setAcceptDrops(True)
        
        # 显示欢迎信息
        self._show_welcome_message()
    
    def _set_window_icon(self):
        """设置窗口图标"""
        icon_path = Path("assets/icon.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧面板 - 图像管理和参数控制
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # 右侧面板 - 预览区域
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setSizes([400, 800])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
    
    def _create_left_panel(self) -> QWidget:
        """创建左侧控制面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 图像导入区域
        import_group = QGroupBox("图像导入")
        import_layout = QVBoxLayout(import_group)
        
        # 导入按钮
        self.import_btn = QPushButton("导入图像")
        self.import_btn.setMinimumHeight(40)
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        import_layout.addWidget(self.import_btn)
        
        # 图像列表
        self.image_list = ImageListWidget()
        import_layout.addWidget(self.image_list)
        
        layout.addWidget(import_group)
        
        # 参数控制区域
        self.parameter_widget = ParameterWidget()
        layout.addWidget(self.parameter_widget)
        
        # 生成按钮
        self.generate_btn = QPushButton("生成SDF")
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.setEnabled(False)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #1976D2;
            }
            QPushButton:pressed:enabled {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        layout.addWidget(self.generate_btn)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """创建右侧预览面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 预览区域标题
        title_layout = QHBoxLayout()
        
        preview_title = QLabel("SDF预览")
        preview_title.setFont(QFont("Arial", 14, QFont.Bold))
        title_layout.addWidget(preview_title)
        
        title_layout.addStretch()
        
        # 导出按钮
        self.export_btn = QPushButton("导出SDF")
        self.export_btn.setEnabled(False)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #F57C00;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        title_layout.addWidget(self.export_btn)
        
        layout.addLayout(title_layout)
        
        # 预览组件
        self.preview_widget = PreviewWidget()
        layout.addWidget(self.preview_widget)

        # 预览操作提示
        hint_label = QLabel("💡 提示: 鼠标滚轮缩放，左键拖拽移动，右侧按钮快速调整视图")
        hint_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 11px;
                padding: 5px;
                background-color: #F0F8FF;
                border: 1px solid #E0E0E0;
                border-radius: 3px;
            }
        """)
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)

        return panel

    def _init_menu_bar(self):
        """初始化菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        # 导入图像
        import_action = QAction("导入图像(&I)", self)
        import_action.setShortcut("Ctrl+I")
        import_action.setStatusTip("导入图像文件")
        import_action.triggered.connect(self._import_images)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        # 导出SDF
        export_action = QAction("导出SDF(&E)", self)
        export_action.setShortcut("Ctrl+E")
        export_action.setStatusTip("导出SDF结果")
        export_action.setEnabled(False)
        export_action.triggered.connect(self._export_sdf)
        file_menu.addAction(export_action)
        self.export_action = export_action

        file_menu.addSeparator()

        # 退出
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("退出程序")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")

        # 清空图像
        clear_action = QAction("清空图像(&C)", self)
        clear_action.setShortcut("Ctrl+Delete")
        clear_action.setStatusTip("清空所有导入的图像")
        clear_action.triggered.connect(self._clear_images)
        edit_menu.addAction(clear_action)

        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")

        # 重置视图
        reset_view_action = QAction("重置视图(&R)", self)
        reset_view_action.setShortcut("Ctrl+R")
        reset_view_action.setStatusTip("重置预览视图")
        reset_view_action.triggered.connect(self._reset_view)
        view_menu.addAction(reset_view_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        # 关于
        about_action = QAction("关于(&A)", self)
        about_action.setStatusTip("关于SDF工具")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _init_status_bar(self):
        """初始化状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)

        # 计算时间标签
        self.time_label = QLabel("")
        self.status_bar.addPermanentWidget(self.time_label)

        # 图像数量标签
        self.image_count_label = QLabel("图像: 0")
        self.status_bar.addPermanentWidget(self.image_count_label)

    def _connect_signals(self):
        """连接信号和槽"""
        # 按钮信号
        self.import_btn.clicked.connect(self._import_images)
        self.generate_btn.clicked.connect(self._generate_sdf)
        self.export_btn.clicked.connect(self._export_sdf)

        # 图像列表信号
        self.image_list.images_changed.connect(self._on_images_changed)

        # 参数变化信号
        self.parameter_widget.parameters_changed.connect(self._on_parameters_changed)

    def _show_welcome_message(self):
        """显示欢迎信息"""
        self.status_label.setText("欢迎使用SDF工具！请导入图像开始使用。")

    # 拖拽事件处理
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否包含图像文件
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile():
                    file_path = Path(url.toLocalFile())
                    if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tga']:
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        urls = event.mimeData().urls()
        image_files = []

        for url in urls:
            if url.isLocalFile():
                file_path = Path(url.toLocalFile())
                if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tga']:
                    image_files.append(str(file_path))

        if image_files:
            self._add_images(image_files)
            event.acceptProposedAction()
        else:
            event.ignore()

    # 槽函数实现
    def _import_images(self):
        """导入图像文件"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("图像文件 (*.png *.jpg *.jpeg *.bmp *.tga)")
        file_dialog.setViewMode(QFileDialog.Detail)

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            self._add_images(file_paths)

    def _add_images(self, file_paths: List[str]):
        """添加图像到列表"""
        try:
            added_count = 0
            for file_path in file_paths:
                if file_path not in self.current_images:
                    # 添加到图像管理器
                    if self.image_manager.add_image(file_path):
                        self.current_images.append(file_path)
                        self.image_list.add_image(file_path)
                        added_count += 1
                    else:
                        print(f"无法添加图像: {file_path}")

            self._update_ui_state()
            if added_count > 0:
                self.status_label.setText(f"已导入 {added_count} 张图像")
            else:
                self.status_label.setText("没有有效的图像文件")

        except Exception as e:
            QMessageBox.warning(self, "导入错误", f"导入图像时发生错误：\n{str(e)}")

    def _generate_sdf(self):
        """生成SDF"""
        if not self.current_images:
            QMessageBox.information(self, "提示", "请先导入图像")
            return

        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.generate_btn.setEnabled(False)
        self.status_label.setText("正在生成SDF...")

        # 获取参数
        params = self.parameter_widget.get_sdf_params()

        try:
            if len(self.current_images) == 1:
                # 单张图像SDF
                self._generate_single_sdf(self.current_images[0], params)
            else:
                # 多张图像混合SDF
                self._generate_multi_sdf(self.current_images, params)
        except Exception as e:
            self._on_sdf_generation_failed(str(e))

    def _generate_single_sdf(self, image_path: str, params: dict):
        """生成单张图像SDF"""
        try:
            sdf_result, computation_time = self.sdf_generator.compute_single_sdf(
                image_path,
                threshold=params.get('threshold', 0.5),
                normalize=params.get('normalize', True),
                invert=params.get('invert', False)
            )
            self._on_sdf_generated(sdf_result, computation_time)
        except Exception as e:
            self._on_sdf_generation_failed(str(e))

    def _generate_multi_sdf(self, image_paths: List[str], params: dict):
        """生成多张图像混合SDF"""
        try:
            sdf_result, computation_time = self.sdf_generator.compute_multi_sdf(
                image_paths,
                threshold=params.get('threshold', 0.5),
                normalize=params.get('normalize', True)
            )
            self._on_sdf_generated(sdf_result, computation_time)
        except Exception as e:
            self._on_sdf_generation_failed(str(e))

    def _on_sdf_generated(self, sdf_result, computation_time):
        """SDF生成完成"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)

        # 保存结果
        self.sdf_result = sdf_result
        self.computation_time = computation_time

        # 更新UI
        self._update_ui_state()
        self.status_label.setText("SDF生成完成")
        self.time_label.setText(f"计算时间: {self.computation_time:.2f}s")

        # 转换SDF结果为可显示的图像
        display_image = self._convert_sdf_for_display(sdf_result)

        # 更新预览
        self.preview_widget.set_sdf_result(display_image)

    def _on_sdf_generation_failed(self, error_message: str):
        """SDF生成失败"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)

        # 显示错误信息
        self.status_label.setText("SDF生成失败")
        QMessageBox.warning(self, "生成错误", f"SDF生成失败：\n{error_message}")

    def _convert_sdf_for_display(self, sdf_data):
        """将SDF数据转换为可显示的图像"""
        try:
            # 将numpy数组转换为QPixmap
            pil_image = ImageUtils.numpy_to_pil(sdf_data)

            # 转换为QPixmap
            from PySide6.QtGui import QPixmap
            import io

            # 保存到内存中的字节流
            img_bytes = io.BytesIO()
            pil_image.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            # 从字节流创建QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(img_bytes.getvalue())

            return pixmap

        except Exception as e:
            print(f"转换SDF显示图像失败: {e}")
            return None

    def _export_sdf(self):
        """导出SDF结果"""
        if self.sdf_result is None:
            QMessageBox.information(self, "提示", "请先生成SDF")
            return

        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("PNG文件 (*.png);;JPEG文件 (*.jpg);;TIFF文件 (*.tiff)")
        file_dialog.setDefaultSuffix("png")

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            try:
                # 使用ImageUtils保存SDF结果
                success = ImageUtils.save_image(self.sdf_result, file_path, quality=95)

                if success:
                    self.status_label.setText(f"SDF已导出到: {file_path}")
                    QMessageBox.information(self, "导出成功", f"SDF已成功导出到:\n{file_path}")
                else:
                    QMessageBox.warning(self, "导出错误", "导出SDF时发生未知错误")

            except Exception as e:
                QMessageBox.warning(self, "导出错误", f"导出SDF时发生错误：\n{str(e)}")

    def _clear_images(self):
        """清空所有图像"""
        self.current_images.clear()
        self.image_list.clear()
        self.image_manager.clear_all()
        self.sdf_result = None
        self.preview_widget.clear()
        self._update_ui_state()
        self.status_label.setText("已清空所有图像")
        self.time_label.setText("")

    def _reset_view(self):
        """重置预览视图"""
        self.preview_widget.reset_view()
        self.status_label.setText("视图已重置")

    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于SDF工具",
                         "SDF工具 v0.1.0\n\n"
                         "二次元脸部SDF生成工具\n"
                         "支持多角度光照图像混合和实时预览\n\n"
                         "作者: Mya\n"
                         "技术栈: Python + PySide6 + C++")

    def _on_images_changed(self):
        """图像列表变化时的处理"""
        self._update_ui_state()

    def _on_parameters_changed(self):
        """参数变化时的处理"""
        # 如果已有SDF结果，可以考虑实时更新预览
        pass

    def _update_ui_state(self):
        """更新UI状态"""
        has_images = len(self.current_images) > 0
        has_sdf = self.sdf_result is not None

        # 更新按钮状态
        self.generate_btn.setEnabled(has_images)
        self.export_btn.setEnabled(has_sdf)
        self.export_action.setEnabled(has_sdf)

        # 更新状态栏
        self.image_count_label.setText(f"图像: {len(self.current_images)}")

    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(self, "确认退出",
                                   "确定要退出SDF工具吗？",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
