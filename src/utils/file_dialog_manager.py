#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件对话框管理模块

负责管理文件选择和保存对话框
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple


class FileDialogManager:
    """文件对话框管理器"""

    # 支持的图像格式
    IMAGE_FORMATS = {
        'png': 'PNG图像 (*.png)',
        'jpg': 'JPEG图像 (*.jpg *.jpeg)',
        'bmp': 'BMP图像 (*.bmp)',
        'tga': 'TGA图像 (*.tga)',
        'tiff': 'TIFF图像 (*.tiff *.tif)',
        'webp': 'WebP图像 (*.webp)'
    }

    # 支持的导出格式
    EXPORT_FORMATS = {
        'png': 'PNG图像 (*.png)',
        'tiff': 'TIFF图像 (*.tiff)',
        'npy': 'NumPy数组 (*.npy)',
        'json': 'JSON数据 (*.json)'
    }

    @classmethod
    def get_image_filter(cls) -> str:
        """获取图像文件过滤器"""
        all_formats = []
        individual_formats = []
        
        for format_name, filter_text in cls.IMAGE_FORMATS.items():
            individual_formats.append(filter_text)
            # 提取扩展名
            extensions = filter_text.split('(')[1].split(')')[0].split()
            all_formats.extend(extensions)
        
        # 创建"所有图像"过滤器
        all_images_filter = f"所有图像 ({' '.join(all_formats)})"
        
        # 组合所有过滤器
        filters = [all_images_filter] + individual_formats + ["所有文件 (*.*)"]
        return ";;".join(filters)

    @classmethod
    def get_export_filter(cls) -> str:
        """获取导出文件过滤器"""
        filters = []
        for format_name, filter_text in cls.EXPORT_FORMATS.items():
            filters.append(filter_text)
        filters.append("所有文件 (*.*)")
        return ";;".join(filters)

    @staticmethod
    def select_image_files(parent=None, title: str = "选择图像文件") -> List[str]:
        """选择图像文件"""
        try:
            from PySide6.QtWidgets import QFileDialog
            
            file_dialog = QFileDialog(parent)
            file_dialog.setWindowTitle(title)
            file_dialog.setFileMode(QFileDialog.ExistingFiles)
            file_dialog.setNameFilter(FileDialogManager.get_image_filter())
            file_dialog.setViewMode(QFileDialog.Detail)
            
            # 设置默认目录
            default_dir = FileDialogManager._get_default_directory('images')
            if default_dir:
                file_dialog.setDirectory(default_dir)
            
            if file_dialog.exec():
                selected_files = file_dialog.selectedFiles()
                # 保存最后使用的目录
                if selected_files:
                    FileDialogManager._save_last_directory('images', 
                                                         Path(selected_files[0]).parent)
                return selected_files
            
            return []
            
        except ImportError:
            print("❌ PySide6不可用，无法显示文件对话框")
            return []
        except Exception as e:
            print(f"❌ 文件选择失败: {e}")
            return []

    @staticmethod
    def select_single_image_file(parent=None, title: str = "选择图像文件") -> Optional[str]:
        """选择单个图像文件"""
        files = FileDialogManager.select_image_files(parent, title)
        return files[0] if files else None

    @staticmethod
    def save_file_dialog(parent=None, 
                        title: str = "保存文件", 
                        default_name: str = "output",
                        file_type: str = "png") -> Optional[str]:
        """保存文件对话框"""
        try:
            from PySide6.QtWidgets import QFileDialog
            
            file_dialog = QFileDialog(parent)
            file_dialog.setWindowTitle(title)
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.setNameFilter(FileDialogManager.get_export_filter())
            
            # 设置默认文件名和扩展名
            if not default_name.endswith(f'.{file_type}'):
                default_name = f"{default_name}.{file_type}"
            
            # 设置默认目录
            default_dir = FileDialogManager._get_default_directory('exports')
            if default_dir:
                file_dialog.setDirectory(default_dir)
                file_dialog.selectFile(default_name)
            else:
                file_dialog.selectFile(default_name)
            
            # 设置默认后缀
            file_dialog.setDefaultSuffix(file_type)
            
            if file_dialog.exec():
                selected_file = file_dialog.selectedFiles()[0]
                # 保存最后使用的目录
                FileDialogManager._save_last_directory('exports', 
                                                     Path(selected_file).parent)
                return selected_file
            
            return None
            
        except ImportError:
            print("❌ PySide6不可用，无法显示保存对话框")
            return None
        except Exception as e:
            print(f"❌ 保存对话框失败: {e}")
            return None

    @staticmethod
    def select_directory(parent=None, title: str = "选择目录") -> Optional[str]:
        """选择目录"""
        try:
            from PySide6.QtWidgets import QFileDialog
            
            file_dialog = QFileDialog(parent)
            file_dialog.setWindowTitle(title)
            file_dialog.setFileMode(QFileDialog.Directory)
            file_dialog.setOption(QFileDialog.ShowDirsOnly, True)
            
            # 设置默认目录
            default_dir = FileDialogManager._get_default_directory('general')
            if default_dir:
                file_dialog.setDirectory(default_dir)
            
            if file_dialog.exec():
                selected_dir = file_dialog.selectedFiles()[0]
                # 保存最后使用的目录
                FileDialogManager._save_last_directory('general', selected_dir)
                return selected_dir
            
            return None
            
        except ImportError:
            print("❌ PySide6不可用，无法显示目录选择对话框")
            return None
        except Exception as e:
            print(f"❌ 目录选择失败: {e}")
            return None

    @staticmethod
    def _get_default_directory(category: str) -> Optional[str]:
        """获取默认目录"""
        try:
            from .basic_file_operations import BasicFileOperations
            
            config_file = "config/dialog_settings.json"
            config = BasicFileOperations.load_json(config_file)
            
            if config and 'last_directories' in config:
                last_dir = config['last_directories'].get(category)
                if last_dir and Path(last_dir).exists():
                    return last_dir
            
            # 返回默认目录
            defaults = {
                'images': 'sdf_test',
                'exports': 'output',
                'general': '.'
            }
            
            default_dir = defaults.get(category, '.')
            if Path(default_dir).exists():
                return default_dir
            
            return None
            
        except Exception:
            return None

    @staticmethod
    def _save_last_directory(category: str, directory: str):
        """保存最后使用的目录"""
        try:
            from .basic_file_operations import BasicFileOperations
            
            config_file = "config/dialog_settings.json"
            config = BasicFileOperations.load_json(config_file) or {}
            
            if 'last_directories' not in config:
                config['last_directories'] = {}
            
            config['last_directories'][category] = str(directory)
            BasicFileOperations.save_json(config, config_file)
            
        except Exception as e:
            print(f"⚠️ 保存目录设置失败: {e}")

    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """获取文件信息"""
        try:
            from .basic_file_operations import BasicFileOperations
            
            path = Path(file_path)
            if not path.exists():
                return {'error': '文件不存在'}
            
            stat = path.stat()
            
            return {
                'name': path.name,
                'stem': path.stem,
                'suffix': path.suffix,
                'size': stat.st_size,
                'size_formatted': BasicFileOperations.format_file_size(stat.st_size),
                'modified': stat.st_mtime,
                'is_image': BasicFileOperations.is_image_file(file_path),
                'parent': str(path.parent),
                'absolute_path': str(path.absolute())
            }
            
        except Exception as e:
            return {'error': f'获取文件信息失败: {e}'}

    @staticmethod
    def validate_file_path(file_path: str, must_exist: bool = True) -> Tuple[bool, str]:
        """验证文件路径"""
        try:
            path = Path(file_path)
            
            if must_exist and not path.exists():
                return False, "文件不存在"
            
            if must_exist and not path.is_file():
                return False, "路径不是文件"
            
            # 检查父目录是否存在（对于新文件）
            if not must_exist and not path.parent.exists():
                return False, "父目录不存在"
            
            # 检查文件名是否有效
            if not path.name or path.name in ['.', '..']:
                return False, "文件名无效"
            
            return True, ""
            
        except Exception as e:
            return False, f"路径验证失败: {e}"
