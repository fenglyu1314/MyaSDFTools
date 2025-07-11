#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件工具模块 - 重构后的统一接口

提供文件和目录操作的统一接口，整合各个子模块的功能
"""

from typing import List, Optional, Dict, Any, Tuple
import numpy as np

from .basic_file_operations import BasicFileOperations
from .file_dialog_manager import FileDialogManager
from .export_manager import ExportManager


class FileUtils:
    """文件工具类 - 重构后的统一接口"""

    # === 基础文件操作代理方法 ===
    
    @staticmethod
    def ensure_directory(directory: str) -> bool:
        """确保目录存在，如果不存在则创建"""
        return BasicFileOperations.ensure_directory(directory)
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """获取文件扩展名"""
        return BasicFileOperations.get_file_extension(file_path)
    
    @staticmethod
    def get_file_name_without_extension(file_path: str) -> str:
        """获取不带扩展名的文件名"""
        return BasicFileOperations.get_file_name_without_extension(file_path)
    
    @staticmethod
    def is_image_file(file_path: str) -> bool:
        """检查是否为图像文件"""
        return BasicFileOperations.is_image_file(file_path)
    
    @staticmethod
    def get_unique_filename(file_path: str) -> str:
        """获取唯一的文件名（如果文件已存在，添加数字后缀）"""
        return BasicFileOperations.get_unique_filename(file_path)
    
    @staticmethod
    def copy_file(source: str, destination: str, overwrite: bool = False) -> bool:
        """复制文件"""
        return BasicFileOperations.copy_file(source, destination, overwrite)
    
    @staticmethod
    def move_file(source: str, destination: str, overwrite: bool = False) -> bool:
        """移动文件"""
        return BasicFileOperations.move_file(source, destination, overwrite)
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """删除文件"""
        return BasicFileOperations.delete_file(file_path)
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小（字节）"""
        return BasicFileOperations.get_file_size(file_path)
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """格式化文件大小"""
        return BasicFileOperations.format_file_size(size_bytes)
    
    @staticmethod
    def find_files(directory: str, pattern: str = "*", recursive: bool = True) -> List[str]:
        """查找文件"""
        return BasicFileOperations.find_files(directory, pattern, recursive)
    
    @staticmethod
    def find_image_files(directory: str, recursive: bool = True) -> List[str]:
        """查找图像文件"""
        return BasicFileOperations.find_image_files(directory, recursive)
    
    @staticmethod
    def save_json(data: dict, file_path: str, indent: int = 2) -> bool:
        """保存JSON文件"""
        return BasicFileOperations.save_json(data, file_path, indent)
    
    @staticmethod
    def load_json(file_path: str) -> Optional[dict]:
        """加载JSON文件"""
        return BasicFileOperations.load_json(file_path)
    
    @staticmethod
    def get_directory_size(directory: str) -> int:
        """获取目录总大小（字节）"""
        return BasicFileOperations.get_directory_size(directory)
    
    @staticmethod
    def clean_directory(directory: str, keep_subdirs: bool = True) -> bool:
        """清理目录内容"""
        return BasicFileOperations.clean_directory(directory, keep_subdirs)
    
    @staticmethod
    def backup_file(file_path: str, backup_suffix: str = ".bak") -> Optional[str]:
        """备份文件"""
        return BasicFileOperations.backup_file(file_path, backup_suffix)

    # === 文件对话框代理方法 ===
    
    @staticmethod
    def select_image_files(parent=None, title: str = "选择图像文件") -> List[str]:
        """选择图像文件"""
        return FileDialogManager.select_image_files(parent, title)
    
    @staticmethod
    def select_single_image_file(parent=None, title: str = "选择图像文件") -> Optional[str]:
        """选择单个图像文件"""
        return FileDialogManager.select_single_image_file(parent, title)
    
    @staticmethod
    def save_file_dialog(parent=None, 
                        title: str = "保存文件", 
                        default_name: str = "output",
                        file_type: str = "png") -> Optional[str]:
        """保存文件对话框"""
        return FileDialogManager.save_file_dialog(parent, title, default_name, file_type)
    
    @staticmethod
    def select_directory(parent=None, title: str = "选择目录") -> Optional[str]:
        """选择目录"""
        return FileDialogManager.select_directory(parent, title)
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """获取文件信息"""
        return FileDialogManager.get_file_info(file_path)
    
    @staticmethod
    def validate_file_path(file_path: str, must_exist: bool = True) -> Tuple[bool, str]:
        """验证文件路径"""
        return FileDialogManager.validate_file_path(file_path, must_exist)

    # === 导出功能代理方法 ===
    
    @staticmethod
    def export_sdf_image(sdf_array: np.ndarray, 
                        file_path: str, 
                        format_type: str = "png",
                        normalize: bool = True) -> bool:
        """导出SDF为图像文件"""
        return ExportManager.export_sdf_image(sdf_array, file_path, format_type, normalize)
    
    @staticmethod
    def export_sdf_data(sdf_array: np.ndarray, 
                       file_path: str, 
                       format_type: str = "npy",
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """导出SDF数据文件"""
        return ExportManager.export_sdf_data(sdf_array, file_path, format_type, metadata)
    
    @staticmethod
    def export_batch_images(sdf_list: List[np.ndarray], 
                           output_directory: str,
                           base_name: str = "sdf",
                           format_type: str = "png") -> List[str]:
        """批量导出SDF图像"""
        return ExportManager.export_batch_images(sdf_list, output_directory, base_name, format_type)
    
    @staticmethod
    def export_with_dialog(sdf_array: np.ndarray, 
                          parent=None,
                          default_name: str = "sdf_output") -> Optional[str]:
        """使用对话框导出SDF"""
        return ExportManager.export_with_dialog(sdf_array, parent, default_name)
    
    @staticmethod
    def open_export_folder(file_path: str) -> bool:
        """打开导出文件所在的文件夹"""
        return ExportManager.open_export_folder(file_path)
    
    @staticmethod
    def validate_export_path(file_path: str) -> Tuple[bool, str]:
        """验证导出路径"""
        return ExportManager.validate_export_path(file_path)
    
    @staticmethod
    def get_export_formats() -> Dict[str, str]:
        """获取支持的导出格式"""
        return ExportManager.get_export_formats()

    # === 便捷方法 ===
    
    @staticmethod
    def quick_export_sdf(sdf_array: np.ndarray, 
                        output_dir: str = "output",
                        base_name: str = "sdf") -> Optional[str]:
        """快速导出SDF（自动生成文件名）"""
        try:
            FileUtils.ensure_directory(output_dir)
            
            # 生成唯一文件名
            file_path = f"{output_dir}/{base_name}.png"
            file_path = FileUtils.get_unique_filename(file_path)
            
            # 导出图像
            if FileUtils.export_sdf_image(sdf_array, file_path):
                return file_path
            else:
                return None
                
        except Exception as e:
            print(f"❌ 快速导出失败: {e}")
            return None
    
    @staticmethod
    def get_supported_image_extensions() -> List[str]:
        """获取支持的图像扩展名"""
        return ['.png', '.jpg', '.jpeg', '.bmp', '.tga', '.tiff', '.webp']
    
    @staticmethod
    def is_supported_export_format(file_path: str) -> bool:
        """检查是否为支持的导出格式"""
        extension = FileUtils.get_file_extension(file_path)
        supported = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.npy', '.npz', '.json'}
        return extension in supported
