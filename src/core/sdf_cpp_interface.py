#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SDF C++接口模块 - 重构后的简化版

负责与C++后端的交互
"""

from typing import Optional, Dict, Any, List
import numpy as np

from .cpp_backend_validator import CppBackendValidator
from .cpp_performance_monitor import CppPerformanceMonitor


class SDFCppInterface:
    """SDF C++后端接口 - 重构后的简化版"""

    def __init__(self):
        """初始化C++接口"""
        self.cpp_backend = None
        self.use_cpp_backend = False
        self.cpp_available = False

        # 初始化验证器和性能监控器
        self.validator = None
        self.performance_monitor = None

        self._init_cpp_backend()

    def _init_cpp_backend(self):
        """初始化C++后端"""
        try:
            import sdf_core
            self.cpp_backend = sdf_core
            self.cpp_available = True
            self.use_cpp_backend = True

            # 初始化验证器和性能监控器
            self.validator = CppBackendValidator(self.cpp_backend)
            self.performance_monitor = CppPerformanceMonitor(self.cpp_backend)

            print("✅ C++后端可用")
        except ImportError:
            self.cpp_available = False
            self.use_cpp_backend = False
            print("⚠️ C++后端不可用，使用Python实现")

    def set_use_cpp_backend(self, use_cpp: bool):
        """设置是否使用C++后端"""
        if use_cpp and not self.cpp_available:
            print("⚠️ C++后端不可用，无法启用")
            return False

        self.use_cpp_backend = use_cpp
        backend_name = "C++后端" if use_cpp else "Python实现"
        print(f"🔧 切换到{backend_name}")
        return True

    def is_available(self) -> bool:
        """检查C++后端是否可用"""
        return self.use_cpp_backend

    def compute_sdf_cpp(self,
                       binary_image: np.ndarray,
                       normalize: bool = True,
                       invert: bool = False,
                       sdf_direction: str = "both",
                       max_distance: int = 100,
                       num_threads: Optional[int] = None) -> np.ndarray:
        """使用C++后端计算SDF"""
        if not self.use_cpp_backend:
            raise RuntimeError("C++后端不可用")

        height, width = binary_image.shape
        image_data = binary_image.flatten().tolist()

        def compute_operation():
            return self.cpp_backend.compute_single_sdf(
                image_data, width, height, 0.5, normalize, max_distance
            )

        # 使用性能监控器监控操作
        if self.performance_monitor:
            sdf_result, _ = self.performance_monitor.monitor_operation(
                'compute_single_sdf', compute_operation
            )
        else:
            sdf_result = compute_operation()

        # 转换回numpy数组
        result = np.array(sdf_result, dtype=np.float32).reshape(height, width)

        if invert:
            result = 1.0 - result

        return result

    def compute_multi_sdf_cpp(self,
                             image_data_list: list,
                             width: int,
                             height: int,
                             parameters: dict) -> np.ndarray:
        """使用C++后端计算多图像SDF"""
        if not self.use_cpp_backend:
            raise RuntimeError("C++后端不可用")

        if not hasattr(self.cpp_backend, 'compute_multi_sdf'):
            raise RuntimeError("C++后端不支持多图像SDF计算")

        def compute_operation():
            return self.cpp_backend.compute_multi_sdf(
                image_data_list, width, height,
                parameters.get('threshold', 0.5),
                parameters.get('normalize', True),
                parameters.get('max_distance', 100)
            )

        # 使用性能监控器监控操作
        if self.performance_monitor:
            sdf_result, _ = self.performance_monitor.monitor_operation(
                'compute_multi_sdf', compute_operation
            )
        else:
            sdf_result = compute_operation()

        # 转换回numpy数组
        result = np.array(sdf_result, dtype=np.float32).reshape(height, width)

        if parameters.get('invert', False):
            result = 1.0 - result

        return result

    def get_version_info(self) -> Dict[str, Any]:
        """获取C++后端版本信息"""
        if not self.validator:
            return {'available': False, 'error': 'C++后端不可用'}

        return self.validator.get_backend_info()

    def benchmark_performance(self) -> Dict[str, Any]:
        """性能基准测试"""
        if not self.performance_monitor:
            return {'available': False, 'error': 'C++后端不可用'}

        return self.performance_monitor.benchmark_performance()

    def validate_cpp_backend(self) -> Dict[str, Any]:
        """验证C++后端功能"""
        if not self.validator:
            return {'valid': False, 'error': 'C++后端不可用'}

        return self.validator.validate_cpp_backend()

    def blend_multiple_sdfs_cpp(self, sdf_images: List[np.ndarray]) -> np.ndarray:
        """使用C++后端进行多SDF混合"""
        if not self.use_cpp_backend:
            raise RuntimeError("C++后端不可用")

        if not sdf_images:
            return np.zeros((256, 256), dtype=np.float32)

        if len(sdf_images) == 1:
            return sdf_images[0].astype(np.float32)

        height, width = sdf_images[0].shape

        # 将numpy数组转换为列表
        sdf_data_list = [sdf.flatten().tolist() for sdf in sdf_images]

        def blend_operation():
            return self.cpp_backend.blend_multiple_sdfs(sdf_data_list, width, height)

        # 使用性能监控器监控操作
        if self.performance_monitor:
            blend_result, _ = self.performance_monitor.monitor_operation(
                'blend_multiple_sdfs', blend_operation
            )
        else:
            blend_result = blend_operation()

        # 转换回numpy数组
        result = np.array(blend_result, dtype=np.float32).reshape(height, width)
        return result

    def cleanup(self):
        """清理C++后端资源"""
        if self.use_cpp_backend and hasattr(self.cpp_backend, 'cleanup'):
            try:
                self.cpp_backend.cleanup()
                print("✅ C++后端资源已清理")
            except Exception as e:
                print(f"⚠️ C++后端清理失败: {e}")

    def __del__(self):
        """析构函数，自动清理资源"""
        self.cleanup()
