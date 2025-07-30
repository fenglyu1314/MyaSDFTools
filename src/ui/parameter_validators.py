#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
参数验证模块

负责验证SDF生成参数的有效性和一致性
"""

from typing import Dict, Any, List, Tuple, Optional
from .parameter_defaults import ParameterDefaults


class ParameterValidator:
    """参数验证器类"""

    @staticmethod
    def validate_threshold(value: float) -> Tuple[bool, str]:
        """验证阈值参数"""
        if not isinstance(value, (int, float)):
            return False, "阈值必须是数值类型"
        
        if not (0.0 <= value <= 1.0):
            return False, "阈值必须在0.0到1.0之间"
        
        return True, ""

    @staticmethod
    def validate_max_distance(value: int) -> Tuple[bool, str]:
        """验证最大距离参数"""
        if not isinstance(value, int):
            return False, "最大距离必须是整数类型"
        
        if not (1 <= value <= 1000):
            return False, "最大距离必须在1到1000之间"
        
        return True, ""

    @staticmethod
    def validate_blend_mode(value: str) -> Tuple[bool, str]:
        """验证混合模式参数"""
        valid_modes = [mode[0] for mode in ParameterDefaults.get_blend_mode_options()]

        if value not in valid_modes:
            return False, f"混合模式必须是以下之一: {', '.join(valid_modes)}"

        return True, ""



    @staticmethod
    def validate_sdf_direction(value: str) -> Tuple[bool, str]:
        """验证SDF方向参数"""
        valid_directions = [direction[0] for direction in ParameterDefaults.get_sdf_direction_options()]
        
        if value not in valid_directions:
            return False, f"SDF方向必须是以下之一: {', '.join(valid_directions)}"
        
        return True, ""

    @staticmethod
    def validate_boolean_parameter(value: Any, param_name: str) -> Tuple[bool, str]:
        """验证布尔参数"""
        if not isinstance(value, bool):
            return False, f"{param_name}必须是布尔类型"
        
        return True, ""

    @classmethod
    def validate_all_parameters(cls, parameters: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证所有参数"""
        errors = []
        
        # 验证阈值
        if 'threshold' in parameters:
            valid, error = cls.validate_threshold(parameters['threshold'])
            if not valid:
                errors.append(f"阈值错误: {error}")
        
        # 验证最大距离
        if 'max_distance' in parameters:
            valid, error = cls.validate_max_distance(parameters['max_distance'])
            if not valid:
                errors.append(f"最大距离错误: {error}")
        
        # 验证混合模式
        if 'blend_mode' in parameters:
            valid, error = cls.validate_blend_mode(parameters['blend_mode'])
            if not valid:
                errors.append(f"混合模式错误: {error}")


        # 验证SDF方向
        if 'sdf_direction' in parameters:
            valid, error = cls.validate_sdf_direction(parameters['sdf_direction'])
            if not valid:
                errors.append(f"SDF方向错误: {error}")
        
        # 验证布尔参数
        boolean_params = ['normalize', 'invert', 'use_cpp_backend']
        for param in boolean_params:
            if param in parameters:
                valid, error = cls.validate_boolean_parameter(parameters[param], param)
                if not valid:
                    errors.append(f"{param}错误: {error}")
        
        return len(errors) == 0, errors

    @classmethod
    def sanitize_parameters(cls, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """清理和修正参数值"""
        sanitized = parameters.copy()
        
        # 修正阈值
        if 'threshold' in sanitized:
            sanitized['threshold'] = ParameterDefaults.clamp_parameter_value(
                'threshold', sanitized['threshold']
            )
        
        # 修正最大距离
        if 'max_distance' in sanitized:
            sanitized['max_distance'] = ParameterDefaults.clamp_parameter_value(
                'max_distance', sanitized['max_distance']
            )



        # 确保布尔参数是布尔类型
        boolean_params = ['normalize', 'invert', 'use_cpp_backend']
        for param in boolean_params:
            if param in sanitized and not isinstance(sanitized[param], bool):
                sanitized[param] = bool(sanitized[param])
        
        return sanitized

    @classmethod
    def get_parameter_constraints(cls, parameter_name: str) -> Dict[str, Any]:
        """获取参数约束信息"""
        constraints = {}
        
        if parameter_name == 'threshold':
            constraints = {
                'type': 'float',
                'min': 0.0,
                'max': 1.0,
                'step': 0.01,
                'description': '二值化阈值，用于将灰度图转换为黑白图'
            }
        elif parameter_name == 'max_distance':
            constraints = {
                'type': 'int',
                'min': 1,
                'max': 1000,
                'step': 1,
                'description': 'SDF计算的最大距离限制（像素）'
            }
        elif parameter_name == 'blend_mode':
            constraints = {
                'type': 'enum',
                'options': ParameterDefaults.get_blend_mode_options(),
                'description': '多张SDF图像的混合模式'
            }
        elif parameter_name == 'sdf_direction':
            constraints = {
                'type': 'enum',
                'options': ParameterDefaults.get_sdf_direction_options(),
                'description': 'SDF计算方向：双向、只向内或只向外'
            }
        elif parameter_name in ['normalize', 'invert', 'use_cpp_backend']:
            constraints = {
                'type': 'bool',
                'description': f'{parameter_name}选项'
            }
        
        return constraints
