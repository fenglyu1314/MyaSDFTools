#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件操作工具

提供文件和目录操作的工具函数
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
import json

class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def ensure_directory(directory: str) -> bool:
        """
        确保目录存在，如果不存在则创建
        
        Args:
            directory: 目录路径
            
        Returns:
            是否成功
        """
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
        return FileUtils.get_file_extension(file_path) in image_extensions
    
    @staticmethod
    def get_unique_filename(file_path: str) -> str:
        """
        获取唯一的文件名（如果文件已存在，添加数字后缀）
        
        Args:
            file_path: 原始文件路径
            
        Returns:
            唯一的文件路径
        """
        if not os.path.exists(file_path):
            return file_path
        
        path = Path(file_path)
        directory = path.parent
        name = path.stem
        extension = path.suffix
        
        counter = 1
        while True:
            new_name = f"{name}_{counter}{extension}"
            new_path = directory / new_name
            if not new_path.exists():
                return str(new_path)
            counter += 1
    
    @staticmethod
    def copy_file(source: str, destination: str, overwrite: bool = False) -> bool:
        """
        复制文件
        
        Args:
            source: 源文件路径
            destination: 目标文件路径
            overwrite: 是否覆盖已存在的文件
            
        Returns:
            是否成功
        """
        try:
            if not overwrite and os.path.exists(destination):
                destination = FileUtils.get_unique_filename(destination)
            
            # 确保目标目录存在
            FileUtils.ensure_directory(str(Path(destination).parent))
            
            shutil.copy2(source, destination)
            return True
            
        except Exception as e:
            print(f"复制文件失败 {source} -> {destination}: {e}")
            return False
    
    @staticmethod
    def move_file(source: str, destination: str, overwrite: bool = False) -> bool:
        """
        移动文件
        
        Args:
            source: 源文件路径
            destination: 目标文件路径
            overwrite: 是否覆盖已存在的文件
            
        Returns:
            是否成功
        """
        try:
            if not overwrite and os.path.exists(destination):
                destination = FileUtils.get_unique_filename(destination)
            
            # 确保目标目录存在
            FileUtils.ensure_directory(str(Path(destination).parent))
            
            shutil.move(source, destination)
            return True
            
        except Exception as e:
            print(f"移动文件失败 {source} -> {destination}: {e}")
            return False
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否成功
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"删除文件失败 {file_path}: {e}")
            return False
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小（字节）"""
        try:
            return os.path.getsize(file_path)
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
        """
        查找文件
        
        Args:
            directory: 搜索目录
            pattern: 文件模式
            recursive: 是否递归搜索
            
        Returns:
            文件路径列表
        """
        try:
            path = Path(directory)
            if recursive:
                files = list(path.rglob(pattern))
            else:
                files = list(path.glob(pattern))
            
            return [str(f) for f in files if f.is_file()]
        except Exception as e:
            print(f"查找文件失败 {directory}: {e}")
            return []
    
    @staticmethod
    def find_image_files(directory: str, recursive: bool = True) -> List[str]:
        """查找图像文件"""
        all_files = FileUtils.find_files(directory, "*", recursive)
        return [f for f in all_files if FileUtils.is_image_file(f)]
    
    @staticmethod
    def save_json(data: dict, file_path: str, indent: int = 2) -> bool:
        """
        保存JSON文件
        
        Args:
            data: 要保存的数据
            file_path: 文件路径
            indent: 缩进空格数
            
        Returns:
            是否成功
        """
        try:
            # 确保目录存在
            FileUtils.ensure_directory(str(Path(file_path).parent))
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存JSON文件失败 {file_path}: {e}")
            return False
    
    @staticmethod
    def load_json(file_path: str) -> Optional[dict]:
        """
        加载JSON文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            加载的数据或None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载JSON文件失败 {file_path}: {e}")
            return None
    
    @staticmethod
    def get_directory_size(directory: str) -> int:
        """获取目录总大小（字节）"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except Exception as e:
            print(f"计算目录大小失败 {directory}: {e}")
        
        return total_size
    
    @staticmethod
    def clean_directory(directory: str, keep_subdirs: bool = True) -> bool:
        """
        清理目录内容
        
        Args:
            directory: 目录路径
            keep_subdirs: 是否保留子目录
            
        Returns:
            是否成功
        """
        try:
            if not os.path.exists(directory):
                return True
            
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path) and not keep_subdirs:
                    shutil.rmtree(item_path)
            
            return True
        except Exception as e:
            print(f"清理目录失败 {directory}: {e}")
            return False
    
    @staticmethod
    def backup_file(file_path: str, backup_suffix: str = ".bak") -> Optional[str]:
        """
        备份文件
        
        Args:
            file_path: 原文件路径
            backup_suffix: 备份文件后缀
            
        Returns:
            备份文件路径或None
        """
        if not os.path.exists(file_path):
            return None
        
        backup_path = file_path + backup_suffix
        backup_path = FileUtils.get_unique_filename(backup_path)
        
        if FileUtils.copy_file(file_path, backup_path):
            return backup_path
        
        return None
