#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础文件操作模块

提供基本的文件和目录操作功能
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
import json


class BasicFileOperations:
    """基础文件操作类"""
    
    @staticmethod
    def ensure_directory(directory: str) -> bool:
        """确保目录存在，如果不存在则创建"""
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建目录失败 {directory}: {e}")
            return False
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """获取文件扩展名"""
        return Path(file_path).suffix.lower()
    
    @staticmethod
    def get_file_name_without_extension(file_path: str) -> str:
        """获取不带扩展名的文件名"""
        return Path(file_path).stem
    
    @staticmethod
    def is_image_file(file_path: str) -> bool:
        """检查是否为图像文件"""
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tga', '.tiff', '.webp'}
        return BasicFileOperations.get_file_extension(file_path) in image_extensions
    
    @staticmethod
    def get_unique_filename(file_path: str) -> str:
        """获取唯一的文件名（如果文件已存在，添加数字后缀）"""
        path = Path(file_path)
        
        if not path.exists():
            return file_path
        
        base_name = path.stem
        extension = path.suffix
        directory = path.parent
        
        counter = 1
        while True:
            new_name = f"{base_name}_{counter}{extension}"
            new_path = directory / new_name
            
            if not new_path.exists():
                return str(new_path)
            
            counter += 1
            
            # 防止无限循环
            if counter > 9999:
                import time
                timestamp = int(time.time())
                new_name = f"{base_name}_{timestamp}{extension}"
                return str(directory / new_name)
    
    @staticmethod
    def copy_file(source: str, destination: str, overwrite: bool = False) -> bool:
        """复制文件"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                print(f"源文件不存在: {source}")
                return False
            
            if dest_path.exists() and not overwrite:
                print(f"目标文件已存在: {destination}")
                return False
            
            # 确保目标目录存在
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source, destination)
            return True
            
        except Exception as e:
            print(f"复制文件失败: {e}")
            return False
    
    @staticmethod
    def move_file(source: str, destination: str, overwrite: bool = False) -> bool:
        """移动文件"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                print(f"源文件不存在: {source}")
                return False
            
            if dest_path.exists() and not overwrite:
                print(f"目标文件已存在: {destination}")
                return False
            
            # 确保目标目录存在
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(source, destination)
            return True
            
        except Exception as e:
            print(f"移动文件失败: {e}")
            return False
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """删除文件"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            else:
                print(f"文件不存在: {file_path}")
                return False
        except Exception as e:
            print(f"删除文件失败: {e}")
            return False
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小（字节）"""
        try:
            return Path(file_path).stat().st_size
        except:
            return 0
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    @staticmethod
    def find_files(directory: str, pattern: str = "*", recursive: bool = True) -> List[str]:
        """查找文件"""
        try:
            path = Path(directory)
            if not path.exists():
                return []
            
            if recursive:
                files = list(path.rglob(pattern))
            else:
                files = list(path.glob(pattern))
            
            # 只返回文件，不包括目录
            return [str(f) for f in files if f.is_file()]
            
        except Exception as e:
            print(f"查找文件失败: {e}")
            return []
    
    @staticmethod
    def find_image_files(directory: str, recursive: bool = True) -> List[str]:
        """查找图像文件"""
        all_files = BasicFileOperations.find_files(directory, "*", recursive)
        return [f for f in all_files if BasicFileOperations.is_image_file(f)]
    
    @staticmethod
    def save_json(data: dict, file_path: str, indent: int = 2) -> bool:
        """保存JSON文件"""
        try:
            # 确保目录存在
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            return True
            
        except Exception as e:
            print(f"保存JSON文件失败: {e}")
            return False
    
    @staticmethod
    def load_json(file_path: str) -> Optional[dict]:
        """加载JSON文件"""
        try:
            if not Path(file_path).exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"加载JSON文件失败: {e}")
            return None
    
    @staticmethod
    def get_directory_size(directory: str) -> int:
        """获取目录总大小（字节）"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(file_path)
                    except:
                        continue
        except:
            pass
        return total_size
    
    @staticmethod
    def clean_directory(directory: str, keep_subdirs: bool = True) -> bool:
        """清理目录内容"""
        try:
            path = Path(directory)
            if not path.exists():
                return True
            
            for item in path.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir() and not keep_subdirs:
                    shutil.rmtree(item)
            
            return True
            
        except Exception as e:
            print(f"清理目录失败: {e}")
            return False
    
    @staticmethod
    def backup_file(file_path: str, backup_suffix: str = ".bak") -> Optional[str]:
        """备份文件"""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                return None
            
            backup_path = source_path.with_suffix(source_path.suffix + backup_suffix)
            backup_path = Path(BasicFileOperations.get_unique_filename(str(backup_path)))
            
            shutil.copy2(file_path, backup_path)
            return str(backup_path)
            
        except Exception as e:
            print(f"备份文件失败: {e}")
            return None
