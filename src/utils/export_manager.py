#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
导出管理模块

负责管理SDF结果的导出功能
"""

import os
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List
from PIL import Image

from .basic_file_operations import BasicFileOperations
from .file_dialog_manager import FileDialogManager


class ExportManager:
    """导出管理器"""

    @staticmethod
    def export_sdf_image(sdf_array: np.ndarray, 
                        file_path: str, 
                        format_type: str = "png",
                        normalize: bool = True) -> bool:
        """导出SDF为图像文件"""
        try:
            # 确保目录存在
            BasicFileOperations.ensure_directory(str(Path(file_path).parent))
            
            # 处理SDF数据
            if normalize:
                # 归一化到0-255范围
                sdf_normalized = ((sdf_array - sdf_array.min()) / 
                                (sdf_array.max() - sdf_array.min()) * 255)
            else:
                sdf_normalized = np.clip(sdf_array * 255, 0, 255)
            
            # 转换为uint8
            sdf_uint8 = sdf_normalized.astype(np.uint8)
            
            # 创建PIL图像
            if len(sdf_uint8.shape) == 2:
                # 灰度图像
                image = Image.fromarray(sdf_uint8, mode='L')
            else:
                # RGB图像
                image = Image.fromarray(sdf_uint8, mode='RGB')
            
            # 保存图像
            image.save(file_path, format=format_type.upper())
            
            print(f"✅ SDF图像已导出: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 导出SDF图像失败: {e}")
            return False

    @staticmethod
    def export_sdf_data(sdf_array: np.ndarray, 
                       file_path: str, 
                       format_type: str = "npy",
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """导出SDF数据文件"""
        try:
            # 确保目录存在
            BasicFileOperations.ensure_directory(str(Path(file_path).parent))
            
            if format_type.lower() == "npy":
                # 保存为NumPy数组
                np.save(file_path, sdf_array)
                
            elif format_type.lower() == "npz":
                # 保存为压缩NumPy数组，包含元数据
                if metadata:
                    np.savez_compressed(file_path, sdf=sdf_array, **metadata)
                else:
                    np.savez_compressed(file_path, sdf=sdf_array)
                    
            elif format_type.lower() == "json":
                # 保存为JSON（小数组）
                if sdf_array.size > 10000:
                    print("⚠️ 数组过大，不建议保存为JSON格式")
                    return False
                
                data = {
                    'sdf_data': sdf_array.tolist(),
                    'shape': sdf_array.shape,
                    'dtype': str(sdf_array.dtype)
                }
                
                if metadata:
                    data['metadata'] = metadata
                
                return BasicFileOperations.save_json(data, file_path)
                
            else:
                print(f"❌ 不支持的数据格式: {format_type}")
                return False
            
            print(f"✅ SDF数据已导出: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 导出SDF数据失败: {e}")
            return False

    @staticmethod
    def export_batch_images(sdf_list: List[np.ndarray], 
                           output_directory: str,
                           base_name: str = "sdf",
                           format_type: str = "png") -> List[str]:
        """批量导出SDF图像"""
        exported_files = []
        
        try:
            # 确保输出目录存在
            BasicFileOperations.ensure_directory(output_directory)
            
            for i, sdf_array in enumerate(sdf_list):
                # 生成文件名
                file_name = f"{base_name}_{i+1:03d}.{format_type}"
                file_path = os.path.join(output_directory, file_name)
                
                # 导出单个图像
                if ExportManager.export_sdf_image(sdf_array, file_path, format_type):
                    exported_files.append(file_path)
                else:
                    print(f"❌ 导出第{i+1}张图像失败")
            
            print(f"✅ 批量导出完成，共{len(exported_files)}张图像")
            return exported_files
            
        except Exception as e:
            print(f"❌ 批量导出失败: {e}")
            return exported_files

    @staticmethod
    def export_with_dialog(sdf_array: np.ndarray, 
                          parent=None,
                          default_name: str = "sdf_output") -> Optional[str]:
        """使用对话框导出SDF"""
        try:
            # 显示保存对话框
            file_path = FileDialogManager.save_file_dialog(
                parent=parent,
                title="导出SDF",
                default_name=default_name,
                file_type="png"
            )
            
            if not file_path:
                return None
            
            # 根据文件扩展名确定格式
            extension = BasicFileOperations.get_file_extension(file_path)
            
            if extension in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
                # 导出为图像
                success = ExportManager.export_sdf_image(sdf_array, file_path, extension[1:])
            elif extension in ['.npy', '.npz']:
                # 导出为数据文件
                success = ExportManager.export_sdf_data(sdf_array, file_path, extension[1:])
            elif extension == '.json':
                # 导出为JSON
                success = ExportManager.export_sdf_data(sdf_array, file_path, 'json')
            else:
                print(f"❌ 不支持的文件格式: {extension}")
                return None
            
            if success:
                return file_path
            else:
                return None
                
        except Exception as e:
            print(f"❌ 导出对话框失败: {e}")
            return None

    @staticmethod
    def create_export_summary(exported_files: List[str], 
                             output_directory: str,
                             metadata: Optional[Dict[str, Any]] = None) -> bool:
        """创建导出摘要文件"""
        try:
            summary_data = {
                'export_info': {
                    'timestamp': str(np.datetime64('now')),
                    'total_files': len(exported_files),
                    'output_directory': output_directory
                },
                'exported_files': []
            }
            
            # 添加元数据
            if metadata:
                summary_data['metadata'] = metadata
            
            # 收集文件信息
            for file_path in exported_files:
                file_info = FileDialogManager.get_file_info(file_path)
                if 'error' not in file_info:
                    summary_data['exported_files'].append({
                        'file_name': file_info['name'],
                        'file_size': file_info['size_formatted'],
                        'relative_path': os.path.relpath(file_path, output_directory)
                    })
            
            # 保存摘要文件
            summary_path = os.path.join(output_directory, "export_summary.json")
            return BasicFileOperations.save_json(summary_data, summary_path)
            
        except Exception as e:
            print(f"❌ 创建导出摘要失败: {e}")
            return False

    @staticmethod
    def open_export_folder(file_path: str) -> bool:
        """打开导出文件所在的文件夹"""
        try:
            folder_path = str(Path(file_path).parent)
            
            # 根据操作系统选择合适的方法
            import platform
            system = platform.system()
            
            if system == "Windows":
                os.startfile(folder_path)
            elif system == "Darwin":  # macOS
                os.system(f'open "{folder_path}"')
            else:  # Linux
                os.system(f'xdg-open "{folder_path}"')
            
            return True
            
        except Exception as e:
            print(f"❌ 打开文件夹失败: {e}")
            return False

    @staticmethod
    def validate_export_path(file_path: str) -> tuple[bool, str]:
        """验证导出路径"""
        try:
            path = Path(file_path)
            
            # 检查父目录是否存在或可创建
            parent_dir = path.parent
            if not parent_dir.exists():
                try:
                    parent_dir.mkdir(parents=True, exist_ok=True)
                except:
                    return False, "无法创建输出目录"
            
            # 检查文件名是否有效
            if not path.name or path.name in ['.', '..']:
                return False, "文件名无效"
            
            # 检查扩展名是否支持
            extension = path.suffix.lower()
            supported_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', 
                                  '.npy', '.npz', '.json'}
            
            if extension not in supported_extensions:
                return False, f"不支持的文件格式: {extension}"
            
            # 检查是否有写入权限
            try:
                test_file = parent_dir / "test_write_permission.tmp"
                test_file.touch()
                test_file.unlink()
            except:
                return False, "没有写入权限"
            
            return True, ""
            
        except Exception as e:
            return False, f"路径验证失败: {e}"

    @staticmethod
    def get_export_formats() -> Dict[str, str]:
        """获取支持的导出格式"""
        return {
            'png': 'PNG图像 - 无损压缩，支持透明度',
            'jpg': 'JPEG图像 - 有损压缩，文件较小',
            'tiff': 'TIFF图像 - 无损压缩，支持高精度',
            'npy': 'NumPy数组 - 保留原始数值精度',
            'npz': '压缩NumPy数组 - 包含元数据',
            'json': 'JSON数据 - 文本格式，便于查看'
        }
