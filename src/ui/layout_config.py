#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
布局配置管理器

定义UI区域的布局规则、间距、比例等参数，实现自动化布局
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from .window_styles import LayoutConstants


@dataclass
class AreaConfig:
    """区域配置"""
    name: str
    min_width: int = 0
    min_height: int = 0
    max_width: int = 0  # 0表示无限制
    max_height: int = 0  # 0表示无限制
    flex_grow: float = 0.0  # 弹性增长系数
    flex_shrink: float = 1.0  # 弹性收缩系数
    aspect_ratio: Optional[float] = None  # 宽高比
    padding: Tuple[int, int, int, int] = (0, 0, 0, 0)  # 上右下左
    margin: Tuple[int, int, int, int] = (0, 0, 0, 0)  # 上右下左


@dataclass
class LayoutConfig:
    """布局配置"""
    direction: str = "horizontal"  # horizontal, vertical
    spacing: int = LayoutConstants.SPACING_MEDIUM
    alignment: str = "start"  # start, center, end, stretch
    wrap: bool = False  # 是否换行


class LayoutConfigManager:
    """布局配置管理器"""
    
    def __init__(self):
        self._configs = self._init_default_configs()
    
    def _init_default_configs(self) -> Dict[str, Dict]:
        """初始化默认配置"""
        return {
            # 主窗口配置
            "main_window": {
                "min_size": (1200, 700),
                "default_size": (1400, 900),
                "layout": LayoutConfig(direction="horizontal", spacing=LayoutConstants.SPACING_SMALL)
            },
            
            # 左侧区域配置
            "left_area": {
                "config": AreaConfig(
                    name="left_area",
                    min_width=900,
                    flex_grow=2.0,
                    padding=(LayoutConstants.MARGIN_SMALL,) * 4
                ),
                "layout": LayoutConfig(direction="vertical", spacing=LayoutConstants.SPACING_TINY)  # 减少间距
            },
            
            # 右侧区域配置
            "right_area": {
                "config": AreaConfig(
                    name="right_area",
                    min_width=300,
                    max_width=400,
                    flex_grow=1.0,
                    padding=(LayoutConstants.MARGIN_SMALL,) * 4
                ),
                "layout": LayoutConfig(direction="vertical", spacing=LayoutConstants.SPACING_SMALL)
            },
            
            # 图像导入区域配置
            "image_import_area": {
                "config": AreaConfig(
                    name="image_import_area",
                    min_height=190,  # 增加高度：卡片130 + 进度条8 + GroupBox标题16 + 内边距16 + 间距4 + 缓冲16 = 190
                    max_height=190,  # 固定高度，刚好容纳卡片和进度条
                    padding=(LayoutConstants.MARGIN_SMALL,) * 4
                ),
                "layout": LayoutConfig(direction="vertical", spacing=LayoutConstants.SPACING_TINY),
                "card_config": {
                    "max_cards": 8,
                    "card_spacing": LayoutConstants.SPACING_TINY
                }
            },
            
            # SDF结果区域配置
            "sdf_results_area": {
                "config": AreaConfig(
                    name="sdf_results_area",
                    min_height=165,  # 增加高度：卡片120 + GroupBox标题16 + 内边距16 + 间距4 + 缓冲9 = 165
                    max_height=165,  # 固定高度，刚好容纳SDF卡片
                    padding=(LayoutConstants.MARGIN_SMALL,) * 4
                ),
                "layout": LayoutConfig(direction="vertical", spacing=LayoutConstants.SPACING_TINY),
                "card_config": {
                    "max_cards": 8,
                    "card_spacing": LayoutConstants.SPACING_TINY
                }
            },
            
            # 预览区域配置
            "preview_area": {
                "config": AreaConfig(
                    name="preview_area",
                    min_height=300,  # 减少最小高度
                    flex_grow=2.0,  # 增加弹性增长，填充剩余空间
                    padding=(LayoutConstants.MARGIN_SMALL,) * 4
                ),
                "layout": LayoutConfig(direction="horizontal", spacing=LayoutConstants.SPACING_SMALL)
            },
            
            # 合并SDF预览配置
            "merged_sdf_preview": {
                "config": AreaConfig(
                    name="merged_sdf_preview",
                    min_width=300,
                    min_height=300,  # 减少最小高度
                    aspect_ratio=1.0,
                    flex_grow=1.0,  # 保持弹性增长
                    padding=(LayoutConstants.MARGIN_SMALL,) * 4
                ),
                "layout": LayoutConfig(direction="vertical", spacing=LayoutConstants.SPACING_TINY)
            },
            
            # 光照预览配置
            "lighting_preview": {
                "config": AreaConfig(
                    name="lighting_preview",
                    min_width=300,
                    min_height=300,  # 减少最小高度
                    aspect_ratio=1.0,
                    flex_grow=1.0,  # 增加弹性增长，与合并SDF预览保持一致
                    padding=(LayoutConstants.MARGIN_SMALL,) * 4
                ),
                "layout": LayoutConfig(direction="vertical", spacing=LayoutConstants.SPACING_TINY)
            },
            
            # 参数控制区域配置
            "parameter_area": {
                "config": AreaConfig(
                    name="parameter_area",
                    min_width=280,
                    max_width=350,
                    min_height=400,
                    padding=(LayoutConstants.MARGIN_SMALL,) * 4
                ),
                "layout": LayoutConfig(direction="vertical", spacing=LayoutConstants.SPACING_SMALL)
            },
            
            # 按钮区域配置
            "button_area": {
                "config": AreaConfig(
                    name="button_area",
                    min_width=280,
                    max_width=350,
                    min_height=120,
                    padding=(LayoutConstants.MARGIN_MEDIUM,) * 4
                ),
                "layout": LayoutConfig(direction="vertical", spacing=LayoutConstants.SPACING_SMALL)
            }
        }
    
    def get_config(self, area_name: str) -> Dict:
        """获取区域配置"""
        return self._configs.get(area_name, {})
    
    def get_area_config(self, area_name: str) -> AreaConfig:
        """获取区域配置对象"""
        config_dict = self.get_config(area_name)
        return config_dict.get("config", AreaConfig(name=area_name))
    
    def get_layout_config(self, area_name: str) -> LayoutConfig:
        """获取布局配置对象"""
        config_dict = self.get_config(area_name)
        return config_dict.get("layout", LayoutConfig())
    
    def calculate_area_size(self, area_name: str, available_width: int, available_height: int) -> Tuple[int, int]:
        """计算区域尺寸"""
        area_config = self.get_area_config(area_name)
        
        # 计算宽度
        width = available_width
        if area_config.min_width > 0:
            width = max(width, area_config.min_width)
        if area_config.max_width > 0:
            width = min(width, area_config.max_width)
        
        # 计算高度
        height = available_height
        if area_config.min_height > 0:
            height = max(height, area_config.min_height)
        if area_config.max_height > 0:
            height = min(height, area_config.max_height)
        
        # 应用宽高比
        if area_config.aspect_ratio:
            # 保持宽高比，取较小的约束
            if width / height > area_config.aspect_ratio:
                width = int(height * area_config.aspect_ratio)
            else:
                height = int(width / area_config.aspect_ratio)
        
        return width, height
    
    def update_config(self, area_name: str, config_updates: Dict):
        """更新配置"""
        if area_name in self._configs:
            self._configs[area_name].update(config_updates)
        else:
            self._configs[area_name] = config_updates


# 全局配置管理器实例
layout_config_manager = LayoutConfigManager()
