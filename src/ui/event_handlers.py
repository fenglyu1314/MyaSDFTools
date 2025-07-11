#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
事件处理器模块

负责处理各种UI事件和用户交互
"""

import os
import time
from pathlib import Path
from typing import List, Optional

from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import QObject, Signal, QThread
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from ..core.sdf_generator import SDFGenerator
from ..core.image_manager import ImageManager
from ..utils.image_utils import ImageUtils


class SDFGenerationWorker(QThread):
    """SDF生成工作线程"""

    finished = Signal(object, float)  # sdf_result, computation_time
    error = Signal(str)  # error_message
    progress = Signal(int)  # progress_value
    single_sdf_completed = Signal(str, object, float)  # image_path, sdf_result, computation_time
    merged_sdf_updated = Signal(object)  # merged_sdf_result

    def __init__(self, sdf_generator: SDFGenerator, image_paths: List[str], parameters: dict):
        super().__init__()
        self.sdf_generator = sdf_generator
        self.image_paths = image_paths
        self.parameters = parameters

    def run(self):
        """执行SDF生成 - 逐张计算并实时更新"""
        try:
            if len(self.image_paths) == 1:
                # 单张图像SDF生成 - 过滤单张SDF相关参数
                single_sdf_params = self._filter_single_sdf_params(self.parameters)
                sdf_result, computation_time = self.sdf_generator.compute_single_sdf(
                    self.image_paths[0],
                    **single_sdf_params
                )
                # 发出单张完成信号
                self.single_sdf_completed.emit(self.image_paths[0], sdf_result, computation_time)
                # 发出最终完成信号
                self.finished.emit(sdf_result, computation_time)
            else:
                # 多张图像逐张计算SDF
                sdf_images = []
                total_time = 0.0

                print(f"🔄 开始逐张计算SDF，共{len(self.image_paths)}张图像")

                # 第一阶段：逐张计算单张SDF
                for i, image_path in enumerate(self.image_paths):
                    print(f"📊 计算第{i+1}张SDF: {image_path}")

                    # 计算单张SDF - 过滤单张SDF相关参数
                    single_sdf_params = self._filter_single_sdf_params(self.parameters)
                    single_sdf, single_time = self.sdf_generator.compute_single_sdf(
                        image_path,
                        **single_sdf_params
                    )
                    sdf_images.append(single_sdf)
                    total_time += single_time

                    # 发出单张完成信号（立即显示）
                    self.single_sdf_completed.emit(image_path, single_sdf, single_time)

                    # 更新进度（单张计算占80%）
                    progress = int((i + 1) / len(self.image_paths) * 80)
                    self.progress.emit(progress)

                print(f"✅ 所有单张SDF计算完成，开始计算合并SDF")

                # 第二阶段：计算合并SDF（等所有单张完成后）
                merge_start_time = time.time()
                angles = self.sdf_generator.core_algorithm.calculate_even_angles(len(self.image_paths))
                final_sdf = self.sdf_generator.blend_algorithms.blend_multiple_sdfs(
                    sdf_images, angles, self.parameters.get('blend_mode', 'sdf_blend')
                )
                merge_time = time.time() - merge_start_time
                total_time += merge_time

                print(f"✅ 合并SDF计算完成，耗时{merge_time:.3f}s")

                # 发出合并SDF更新信号
                self.merged_sdf_updated.emit(final_sdf)

                # 更新最终进度
                self.progress.emit(100)

                # 发出最终完成信号
                self.finished.emit(final_sdf, total_time)

        except Exception as e:
            self.error.emit(str(e))

    def _filter_single_sdf_params(self, parameters: dict) -> dict:
        """过滤单张SDF计算相关的参数"""
        # compute_single_sdf 方法接受的参数
        valid_params = {
            'threshold', 'normalize', 'invert', 'sdf_direction',
            'max_distance', 'num_threads', 'use_cpp_backend'
        }

        return {k: v for k, v in parameters.items() if k in valid_params}


class MainWindowEventHandler(QObject):
    """主窗口事件处理器"""
    
    # 信号定义
    status_updated = Signal(str)
    ui_state_changed = Signal()
    sdf_generated = Signal(object, float)
    single_sdf_completed = Signal(str, object, float)  # image_path, sdf_result, computation_time
    merged_sdf_updated = Signal(object)  # merged_sdf_result
    progress_updated = Signal(int)  # progress_value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sdf_generator = SDFGenerator()
        self.image_manager = ImageManager()
        self.current_images: List[str] = []
        self.sdf_result: Optional[object] = None
        self.computation_time: float = 0.0
        self.sdf_worker: Optional[SDFGenerationWorker] = None

    def handle_import_images(self):
        """处理导入图像事件"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("图像文件 (*.png *.jpg *.jpeg *.bmp *.tga)")
        file_dialog.setViewMode(QFileDialog.Detail)
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            self._add_images(file_paths)

    def handle_generate_sdf(self, parameters: dict):
        """处理生成SDF事件"""
        if not self.current_images:
            QMessageBox.warning(None, "警告", "请先导入图像文件")
            return

        # 创建工作线程
        self.sdf_worker = SDFGenerationWorker(
            self.sdf_generator, 
            self.current_images, 
            parameters
        )
        
        # 连接信号
        self.sdf_worker.finished.connect(self._on_sdf_generated)
        self.sdf_worker.error.connect(self._on_sdf_error)
        self.sdf_worker.single_sdf_completed.connect(self._on_single_sdf_completed)
        self.sdf_worker.merged_sdf_updated.connect(self._on_merged_sdf_updated)
        self.sdf_worker.progress.connect(self._on_progress_updated)
        
        # 启动线程
        self.sdf_worker.start()
        self.status_updated.emit("正在生成SDF...")

    def handle_export_sdf(self):
        """处理导出SDF事件"""
        if self.sdf_result is None:
            QMessageBox.warning(None, "警告", "没有可导出的SDF结果")
            return

        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("PNG文件 (*.png);;TIFF文件 (*.tiff);;NumPy文件 (*.npy)")
        file_dialog.setDefaultSuffix("png")
        
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self._export_sdf_to_file(file_path)

    def handle_drag_enter(self, event: QDragEnterEvent):
        """处理拖拽进入事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile():
                    file_path = Path(url.toLocalFile())
                    if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tga']:
                        event.acceptProposedAction()
                        return
        event.ignore()

    def handle_drop(self, event: QDropEvent):
        """处理拖拽放下事件"""
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

    def handle_remove_image(self, image_path: str):
        """处理删除单张图像事件"""
        if image_path in self.current_images:
            # 从当前图像列表中移除
            self.current_images.remove(image_path)

            # 从后端图像管理器中移除
            self.image_manager.remove_image(image_path)

            # 如果没有图像了，清空SDF结果
            if not self.current_images:
                self.sdf_result = None

            # 更新UI状态
            self.ui_state_changed.emit()
            self.status_updated.emit(f"已删除图像: {Path(image_path).name}")
            print(f"🗑️ 后端删除图像: {Path(image_path).name}")

    def handle_image_order_changed(self, new_order: list):
        """处理图像顺序变化事件"""
        # 更新后端的图像顺序
        self.current_images = new_order.copy()
        print(f"🔄 后端图像顺序已更新: {[Path(p).name for p in self.current_images]}")

        # 发出UI状态变化信号，让SDF卡片容器也更新顺序
        self.ui_state_changed.emit()

    def handle_clear_images(self):
        """处理清空图像事件"""
        self.current_images.clear()
        self.image_manager.clear_all()
        self.sdf_result = None
        self.ui_state_changed.emit()
        self.status_updated.emit("已清空所有图像")

    def handle_angle_changed(self, angle: int):
        """处理角度改变事件"""
        # 这个方法将由主窗口实现具体的光照预览更新逻辑
        pass

    def handle_parameters_changed(self):
        """处理参数改变事件"""
        # 参数改变时的处理逻辑
        pass

    def _add_images(self, file_paths: List[str]):
        """添加图像文件"""
        added_count = 0
        max_images = 8  # 最大8张图像

        for file_path in file_paths:
            if len(self.current_images) >= max_images:
                QMessageBox.information(None, "提示", f"最多只能导入{max_images}张图像")
                break

            if file_path not in self.current_images:
                try:
                    # 验证图像文件
                    if self.image_manager.add_image(file_path):
                        self.current_images.append(file_path)
                        added_count += 1
                        print(f"✅ 后端成功添加图像: {Path(file_path).name}")
                    else:
                        print(f"❌ 后端添加图像失败: {Path(file_path).name}")
                        QMessageBox.warning(None, "警告", f"无效的图像文件: {Path(file_path).name}")
                except Exception as e:
                    print(f"❌ 图像加载异常: {str(e)}")
                    QMessageBox.warning(None, "错误", f"加载图像失败: {str(e)}")
            else:
                print(f"⚠️ 图像已存在，跳过: {Path(file_path).name}")

        if added_count > 0:
            print(f"📊 总共添加了 {added_count} 张图像，当前总数: {len(self.current_images)}")
            self.ui_state_changed.emit()
            self.status_updated.emit(f"已导入 {added_count} 张图像")

    def _on_sdf_generated(self, sdf_result, computation_time):
        """SDF生成完成回调"""
        self.sdf_result = sdf_result
        self.computation_time = computation_time
        self.sdf_generated.emit(sdf_result, computation_time)
        self.ui_state_changed.emit()
        self.status_updated.emit("SDF生成完成")

    def _on_sdf_error(self, error_message: str):
        """SDF生成错误回调"""
        QMessageBox.critical(None, "错误", f"SDF生成失败: {error_message}")
        self.status_updated.emit("SDF生成失败")

    def _on_single_sdf_completed(self, image_path: str, sdf_result: object, computation_time: float):
        """单张SDF计算完成回调"""
        print(f"✅ 单张SDF计算完成: {image_path}")
        # 转发信号给UI
        self.single_sdf_completed.emit(image_path, sdf_result, computation_time)

    def _on_merged_sdf_updated(self, merged_sdf: object):
        """合并SDF更新回调"""
        print(f"🔄 合并SDF更新")
        # 转发信号给UI
        self.merged_sdf_updated.emit(merged_sdf)

    def _on_progress_updated(self, progress: int):
        """进度更新回调"""
        # 转发信号给UI
        self.progress_updated.emit(progress)

    def _export_sdf_to_file(self, file_path: str):
        """导出SDF到文件"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.npy':
                # 导出为NumPy格式
                import numpy as np
                np.save(file_path, self.sdf_result)
            else:
                # 导出为图像格式 - 使用专门的SDF导出方法，确保输出为灰度图像
                from ..utils.export_manager import ExportManager
                success = ExportManager.export_sdf_image(self.sdf_result, file_path, file_ext[1:])
                if not success:
                    raise RuntimeError("SDF图像导出失败")
            
            self.status_updated.emit(f"SDF已导出到: {file_path}")
            
            # 询问是否打开文件夹
            reply = QMessageBox.question(
                None, "导出完成", 
                f"SDF已成功导出到:\n{file_path}\n\n是否打开文件夹？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self._open_file_folder(file_path)
                
        except Exception as e:
            QMessageBox.critical(None, "错误", f"导出失败: {str(e)}")

    def _open_file_folder(self, file_path: str):
        """打开文件所在文件夹"""
        try:
            folder_path = str(Path(file_path).parent)
            os.startfile(folder_path)
        except Exception as e:
            print(f"打开文件夹失败: {e}")

    # 属性访问器
    @property
    def has_images(self) -> bool:
        """是否有图像"""
        return len(self.current_images) > 0

    @property
    def has_sdf(self) -> bool:
        """是否有SDF结果"""
        return self.sdf_result is not None

    @property
    def image_count(self) -> int:
        """图像数量"""
        return len(self.current_images)
