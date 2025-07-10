#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
参数默认值配置模块

定义SDF生成参数的默认值和范围
"""

from typing import Dict, Any, Tuple


class ParameterDefaults:
    """参数默认值配置类"""

    # 基础参数默认值
    BASIC_DEFAULTS = {
        'threshold': 0.5,
        'normalize': True,
        'invert': False,
        'blend_mode': 'sdf_blend',
        'sdf_direction': 'both',
        'max_distance': 100,
        'use_cpp_backend': True
    }

    # 参数范围定义
    PARAMETER_RANGES = {
        'threshold': (0.0, 1.0, 0.01),  # (min, max, step)
        'max_distance': (1, 1000, 1),
        'lighting_intensity': (0.0, 2.0, 0.1),
        'ambient_light': (0.0, 1.0, 0.1)
    }

    # 混合模式选项 - 只保留确认正确的混合模式
    BLEND_MODES = [
        ('sdf_blend', 'SDF混合')
    ]

    # SDF计算方向选项
    SDF_DIRECTIONS = [
        ('both', '双向计算'),
        ('inside', '只向内'),
        ('outside', '只向外')
    ]

    @classmethod
    def get_default_value(cls, parameter_name: str) -> Any:
        """获取参数默认值"""
        return cls.BASIC_DEFAULTS.get(parameter_name)

    @classmethod
    def get_parameter_range(cls, parameter_name: str) -> Tuple[float, float, float]:
        """获取参数范围"""
        return cls.PARAMETER_RANGES.get(parameter_name, (0.0, 1.0, 0.01))

    @classmethod
    def get_blend_mode_options(cls) -> list:
        """获取混合模式选项"""
        return cls.BLEND_MODES.copy()

    @classmethod
    def get_sdf_direction_options(cls) -> list:
        """获取SDF方向选项"""
        return cls.SDF_DIRECTIONS.copy()

    @classmethod
    def get_all_defaults(cls) -> Dict[str, Any]:
        """获取所有默认参数"""
        return cls.BASIC_DEFAULTS.copy()

    @classmethod
    def validate_parameter_value(cls, parameter_name: str, value: Any) -> bool:
        """验证参数值是否在有效范围内"""
        if parameter_name in cls.PARAMETER_RANGES:
            min_val, max_val, _ = cls.PARAMETER_RANGES[parameter_name]
            return min_val <= value <= max_val
        return True

    @classmethod
    def clamp_parameter_value(cls, parameter_name: str, value: Any) -> Any:
        """将参数值限制在有效范围内"""
        if parameter_name in cls.PARAMETER_RANGES:
            min_val, max_val, _ = cls.PARAMETER_RANGES[parameter_name]
            return max(min_val, min(max_val, value))
        return value
