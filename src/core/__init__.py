#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
核心模块 - 业务逻辑和算法

包含:
- SDF生成器 (SDFGenerator)
- 图像管理器 (ImageManager)
- 配置管理器 (ConfigManager)
"""

from .sdf_generator import SDFGenerator
from .image_manager import ImageManager
from .config_manager import ConfigManager, config

__all__ = ['SDFGenerator', 'ImageManager', 'ConfigManager', 'config']
