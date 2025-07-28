#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
核心模块 - 业务逻辑和算法

包含:
- SDF生成器 (SDFGenerator)
- 图像管理器 (ImageManager)
"""

from .sdf_generator import SDFGenerator
from .image_manager import ImageManager

__all__ = ['SDFGenerator', 'ImageManager']
