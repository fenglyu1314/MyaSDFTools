#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理器

负责应用程序配置的加载、保存和管理。
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class UIConfig:
    """UI配置"""
    window_width: int = 1600
    window_height: int = 900
    theme: str = "auto"  # auto, light, dark
    language: str = "zh_CN"
    remember_window_state: bool = True

@dataclass
class SDFConfig:
    """SDF计算配置"""
    default_threshold: float = 0.5
    normalize_output: bool = True
    num_threads: int = 0  # 0表示自动检测
    algorithm: str = "8ssedt"

@dataclass
class PreviewConfig:
    """预览配置"""
    preview_size: int = 512
    update_interval: int = 100  # 毫秒
    show_grid: bool = False
    zoom_factor: float = 1.0
    enable_smooth_zoom: bool = True

@dataclass
class ExportConfig:
    """导出配置"""
    default_format: str = "png"
    bit_depth: int = 16
    compression: int = 6
    output_directory: str = "output"
    auto_create_subdirs: bool = True

@dataclass
class PerformanceConfig:
    """性能配置"""
    max_image_size: int = 2048
    memory_limit_mb: int = 2048
    enable_gpu: bool = False
    cache_size: int = 100
    enable_multithreading: bool = True

@dataclass
class DebugConfig:
    """调试配置"""
    log_level: str = "INFO"
    log_file: str = "sdf_tool.log"
    show_computation_time: bool = True
    enable_profiling: bool = False
    save_intermediate_results: bool = False

class ConfigManager:
    """配置管理器
    
    负责加载、保存和管理应用程序的所有配置。
    """
    
    def __init__(self, config_file: str = "config.json"):
        """初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file)
        
        # 初始化默认配置
        self.ui = UIConfig()
        self.sdf = SDFConfig()
        self.preview = PreviewConfig()
        self.export = ExportConfig()
        self.performance = PerformanceConfig()
        self.debug = DebugConfig()
        
        # 加载配置
        self.load()
    
    def load(self) -> bool:
        """加载配置文件
        
        Returns:
            是否成功加载
        """
        try:
            if not self.config_file.exists():
                print(f"配置文件不存在，使用默认配置: {self.config_file}")
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 更新各个配置段
            if 'ui' in data:
                self._update_config(self.ui, data['ui'])
            if 'sdf' in data:
                self._update_config(self.sdf, data['sdf'])
            if 'preview' in data:
                self._update_config(self.preview, data['preview'])
            if 'export' in data:
                self._update_config(self.export, data['export'])
            if 'performance' in data:
                self._update_config(self.performance, data['performance'])
            if 'debug' in data:
                self._update_config(self.debug, data['debug'])
            
            print(f"✅ 配置加载成功: {self.config_file}")
            return True
            
        except Exception as e:
            print(f"❌ 配置加载失败: {e}")
            return False
    
    def save(self) -> bool:
        """保存配置文件
        
        Returns:
            是否成功保存
        """
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 构建配置数据
            config_data = {
                'ui': asdict(self.ui),
                'sdf': asdict(self.sdf),
                'preview': asdict(self.preview),
                'export': asdict(self.export),
                'performance': asdict(self.performance),
                'debug': asdict(self.debug)
            }
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 配置保存成功: {self.config_file}")
            return True
            
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
            return False
    
    def _update_config(self, config_obj: Any, data: Dict[str, Any]):
        """更新配置对象"""
        for key, value in data.items():
            if hasattr(config_obj, key):
                setattr(config_obj, key, value)
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self.ui = UIConfig()
        self.sdf = SDFConfig()
        self.preview = PreviewConfig()
        self.export = ExportConfig()
        self.performance = PerformanceConfig()
        self.debug = DebugConfig()
        print("配置已重置为默认值")
    
    def get_output_directory(self) -> Path:
        """获取输出目录路径"""
        output_dir = Path(self.export.output_directory)
        if self.export.auto_create_subdirs:
            output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

# 全局配置实例
config = ConfigManager()
