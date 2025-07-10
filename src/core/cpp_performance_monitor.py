#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
C++性能监控模块

负责监控C++后端的性能指标和基准测试
"""

import time
from typing import Dict, Any, List, Optional
import numpy as np


class CppPerformanceMonitor:
    """C++性能监控器"""

    def __init__(self, cpp_backend=None):
        self.cpp_backend = cpp_backend
        self.performance_history = []
        self.benchmark_results = {}

    def benchmark_performance(self) -> Dict[str, Any]:
        """性能基准测试"""
        if not self.cpp_backend:
            return {'error': 'C++后端不可用'}

        benchmark_results = {
            'single_sdf': {},
            'multi_sdf': {},
            'memory_usage': {},
            'comparison': {}
        }

        try:
            # 单张SDF基准测试
            benchmark_results['single_sdf'] = self._benchmark_single_sdf()
            
            # 多张SDF基准测试
            benchmark_results['multi_sdf'] = self._benchmark_multi_sdf()
            
            # 内存使用测试
            benchmark_results['memory_usage'] = self._benchmark_memory_usage()
            
            # 与Python实现对比
            benchmark_results['comparison'] = self._benchmark_comparison()

        except Exception as e:
            benchmark_results['error'] = f'基准测试失败: {str(e)}'

        self.benchmark_results = benchmark_results
        return benchmark_results

    def _benchmark_single_sdf(self) -> Dict[str, Any]:
        """单张SDF基准测试"""
        results = {
            'small_image': {},
            'medium_image': {},
            'large_image': {}
        }

        test_sizes = [
            (64, 64, 'small_image'),
            (256, 256, 'medium_image'),
            (512, 512, 'large_image')
        ]

        for width, height, size_key in test_sizes:
            try:
                # 创建测试图像
                test_image = np.random.randint(0, 2, (height, width), dtype=np.float32)
                test_data = test_image.flatten().tolist()

                # 多次测试取平均值
                times = []
                for _ in range(5):
                    start_time = time.time()
                    
                    if hasattr(self.cpp_backend, 'compute_single_sdf'):
                        result = self.cpp_backend.compute_single_sdf(
                            test_data, width, height, 0.5, True, 100
                        )
                        times.append(time.time() - start_time)

                if times:
                    results[size_key] = {
                        'avg_time': sum(times) / len(times),
                        'min_time': min(times),
                        'max_time': max(times),
                        'image_size': f'{width}x{height}',
                        'pixels': width * height
                    }

            except Exception as e:
                results[size_key] = {'error': str(e)}

        return results

    def _benchmark_multi_sdf(self) -> Dict[str, Any]:
        """多张SDF基准测试"""
        results = {
            '2_images': {},
            '4_images': {},
            '8_images': {}
        }

        test_configs = [
            (2, '2_images'),
            (4, '4_images'),
            (8, '8_images')
        ]

        width, height = 128, 128

        for num_images, config_key in test_configs:
            try:
                # 创建测试图像
                test_images = []
                for _ in range(num_images):
                    test_image = np.random.randint(0, 2, (height, width), dtype=np.float32)
                    test_images.append(test_image.flatten().tolist())

                # 多次测试取平均值
                times = []
                for _ in range(3):
                    start_time = time.time()
                    
                    if hasattr(self.cpp_backend, 'compute_multi_sdf'):
                        result = self.cpp_backend.compute_multi_sdf(
                            test_images, width, height, 0.5, True, 100
                        )
                        times.append(time.time() - start_time)

                if times:
                    results[config_key] = {
                        'avg_time': sum(times) / len(times),
                        'min_time': min(times),
                        'max_time': max(times),
                        'num_images': num_images,
                        'image_size': f'{width}x{height}'
                    }

            except Exception as e:
                results[config_key] = {'error': str(e)}

        return results

    def _benchmark_memory_usage(self) -> Dict[str, Any]:
        """内存使用基准测试"""
        results = {
            'baseline': 0,
            'single_sdf': 0,
            'multi_sdf': 0
        }

        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            
            # 基线内存使用
            results['baseline'] = process.memory_info().rss / 1024 / 1024  # MB

            # 单张SDF内存使用
            test_image = np.random.randint(0, 2, (256, 256), dtype=np.float32)
            test_data = test_image.flatten().tolist()
            
            if hasattr(self.cpp_backend, 'compute_single_sdf'):
                result = self.cpp_backend.compute_single_sdf(
                    test_data, 256, 256, 0.5, True, 100
                )
                results['single_sdf'] = process.memory_info().rss / 1024 / 1024

            # 多张SDF内存使用
            test_images = [test_data] * 4
            
            if hasattr(self.cpp_backend, 'compute_multi_sdf'):
                result = self.cpp_backend.compute_multi_sdf(
                    test_images, 256, 256, 0.5, True, 100
                )
                results['multi_sdf'] = process.memory_info().rss / 1024 / 1024

        except ImportError:
            results['error'] = 'psutil不可用，无法监控内存使用'
        except Exception as e:
            results['error'] = f'内存监控失败: {str(e)}'

        return results

    def _benchmark_comparison(self) -> Dict[str, Any]:
        """与Python实现对比"""
        results = {
            'cpp_time': 0,
            'python_time': 0,
            'speedup': 0,
            'accuracy_diff': 0
        }

        try:
            # 创建测试数据
            test_image = np.random.randint(0, 2, (128, 128), dtype=np.float32)
            test_data = test_image.flatten().tolist()

            # C++实现测试
            if hasattr(self.cpp_backend, 'compute_single_sdf'):
                start_time = time.time()
                cpp_result = self.cpp_backend.compute_single_sdf(
                    test_data, 128, 128, 0.5, True, 100
                )
                results['cpp_time'] = time.time() - start_time

            # Python实现测试（简单的距离变换）
            start_time = time.time()
            from scipy.ndimage import distance_transform_edt
            python_result = distance_transform_edt(test_image)
            results['python_time'] = time.time() - start_time

            # 计算加速比
            if results['python_time'] > 0:
                results['speedup'] = results['python_time'] / results['cpp_time']

            # 计算精度差异（如果两个结果都存在）
            if 'cpp_result' in locals() and 'python_result' in locals():
                cpp_array = np.array(cpp_result).reshape(128, 128)
                # 归一化到相同范围
                cpp_norm = (cpp_array - cpp_array.min()) / (cpp_array.max() - cpp_array.min())
                python_norm = (python_result - python_result.min()) / (python_result.max() - python_result.min())
                results['accuracy_diff'] = np.mean(np.abs(cpp_norm - python_norm))

        except Exception as e:
            results['error'] = f'对比测试失败: {str(e)}'

        return results

    def monitor_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """监控特定操作的性能"""
        start_time = time.time()
        start_memory = self._get_memory_usage()

        try:
            result = operation_func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)

        end_time = time.time()
        end_memory = self._get_memory_usage()

        performance_record = {
            'operation': operation_name,
            'timestamp': start_time,
            'duration': end_time - start_time,
            'memory_start': start_memory,
            'memory_end': end_memory,
            'memory_delta': end_memory - start_memory if start_memory and end_memory else None,
            'success': success,
            'error': error
        }

        self.performance_history.append(performance_record)
        return result, performance_record

    def _get_memory_usage(self) -> Optional[float]:
        """获取当前内存使用量（MB）"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except:
            return None

    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.performance_history:
            return {'message': '暂无性能数据'}

        summary = {
            'total_operations': len(self.performance_history),
            'avg_duration': 0,
            'total_duration': 0,
            'success_rate': 0,
            'operations_by_type': {}
        }

        durations = [record['duration'] for record in self.performance_history]
        successes = [record['success'] for record in self.performance_history]

        summary['avg_duration'] = sum(durations) / len(durations)
        summary['total_duration'] = sum(durations)
        summary['success_rate'] = sum(successes) / len(successes)

        # 按操作类型统计
        for record in self.performance_history:
            op_name = record['operation']
            if op_name not in summary['operations_by_type']:
                summary['operations_by_type'][op_name] = {
                    'count': 0,
                    'avg_duration': 0,
                    'success_rate': 0
                }
            
            summary['operations_by_type'][op_name]['count'] += 1

        # 计算每种操作的平均时间和成功率
        for op_name in summary['operations_by_type']:
            op_records = [r for r in self.performance_history if r['operation'] == op_name]
            op_durations = [r['duration'] for r in op_records]
            op_successes = [r['success'] for r in op_records]
            
            summary['operations_by_type'][op_name]['avg_duration'] = sum(op_durations) / len(op_durations)
            summary['operations_by_type'][op_name]['success_rate'] = sum(op_successes) / len(op_successes)

        return summary

    def clear_history(self):
        """清空性能历史记录"""
        self.performance_history.clear()

    def export_performance_data(self) -> Dict[str, Any]:
        """导出性能数据"""
        return {
            'benchmark_results': self.benchmark_results,
            'performance_history': self.performance_history,
            'summary': self.get_performance_summary()
        }
