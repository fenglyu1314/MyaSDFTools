#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
C++后端验证模块

负责验证C++后端的可用性和功能完整性
"""

from typing import Dict, Any, Tuple, Optional
import numpy as np


class CppBackendValidator:
    """C++后端验证器"""

    def __init__(self, cpp_backend=None):
        self.cpp_backend = cpp_backend

    def validate_cpp_backend(self) -> Dict[str, Any]:
        """验证C++后端功能"""
        validation_result = {
            'available': False,
            'functions': {},
            'performance': {},
            'errors': []
        }

        if not self.cpp_backend:
            validation_result['errors'].append('C++后端未初始化')
            return validation_result

        try:
            # 检查基础函数
            validation_result['functions'] = self._check_functions()
            
            # 检查性能
            validation_result['performance'] = self._check_performance()
            
            # 如果所有检查都通过
            if not validation_result['errors']:
                validation_result['available'] = True
                
        except Exception as e:
            validation_result['errors'].append(f'验证过程出错: {str(e)}')

        return validation_result

    def _check_functions(self) -> Dict[str, bool]:
        """检查C++后端函数可用性"""
        functions = {
            'compute_single_sdf': False,
            'compute_multi_sdf': False,
            'get_version': False,
            'cleanup': False
        }

        try:
            # 检查单张SDF计算函数
            if hasattr(self.cpp_backend, 'compute_single_sdf'):
                functions['compute_single_sdf'] = True
            
            # 检查多张SDF计算函数
            if hasattr(self.cpp_backend, 'compute_multi_sdf'):
                functions['compute_multi_sdf'] = True
            
            # 检查版本信息函数
            if hasattr(self.cpp_backend, 'get_version'):
                functions['get_version'] = True
            
            # 检查清理函数
            if hasattr(self.cpp_backend, 'cleanup'):
                functions['cleanup'] = True

        except Exception as e:
            print(f"❌ 函数检查失败: {e}")

        return functions

    def _check_performance(self) -> Dict[str, Any]:
        """检查C++后端性能"""
        performance = {
            'single_sdf_time': None,
            'multi_sdf_time': None,
            'memory_usage': None
        }

        try:
            # 创建测试数据
            test_image = np.random.randint(0, 2, (100, 100), dtype=np.float32)
            test_data = test_image.flatten().tolist()

            # 测试单张SDF性能
            if hasattr(self.cpp_backend, 'compute_single_sdf'):
                import time
                start_time = time.time()
                
                try:
                    result = self.cpp_backend.compute_single_sdf(
                        test_data, 100, 100, 0.5, True, 50
                    )
                    performance['single_sdf_time'] = time.time() - start_time
                except Exception as e:
                    print(f"⚠️ 单张SDF性能测试失败: {e}")

            # 测试多张SDF性能
            if hasattr(self.cpp_backend, 'compute_multi_sdf'):
                start_time = time.time()
                
                try:
                    result = self.cpp_backend.compute_multi_sdf(
                        [test_data, test_data], 100, 100, 0.5, True, 50
                    )
                    performance['multi_sdf_time'] = time.time() - start_time
                except Exception as e:
                    print(f"⚠️ 多张SDF性能测试失败: {e}")

        except Exception as e:
            print(f"❌ 性能测试失败: {e}")

        return performance

    def validate_function_call(self, function_name: str, *args, **kwargs) -> Tuple[bool, Any, str]:
        """验证特定函数调用"""
        if not self.cpp_backend:
            return False, None, "C++后端未初始化"

        if not hasattr(self.cpp_backend, function_name):
            return False, None, f"函数 {function_name} 不存在"

        try:
            func = getattr(self.cpp_backend, function_name)
            result = func(*args, **kwargs)
            return True, result, ""
        except Exception as e:
            return False, None, f"函数调用失败: {str(e)}"

    def get_backend_info(self) -> Dict[str, Any]:
        """获取后端信息"""
        info = {
            'available': False,
            'version': 'unknown',
            'build_info': {},
            'capabilities': []
        }

        if not self.cpp_backend:
            return info

        try:
            info['available'] = True
            
            # 获取版本信息
            if hasattr(self.cpp_backend, 'get_version'):
                try:
                    info['version'] = self.cpp_backend.get_version()
                except:
                    pass

            # 获取构建信息
            if hasattr(self.cpp_backend, 'get_build_info'):
                try:
                    info['build_info'] = self.cpp_backend.get_build_info()
                except:
                    pass

            # 检查功能
            capabilities = []
            if hasattr(self.cpp_backend, 'compute_single_sdf'):
                capabilities.append('single_sdf')
            if hasattr(self.cpp_backend, 'compute_multi_sdf'):
                capabilities.append('multi_sdf')
            if hasattr(self.cpp_backend, 'compute_blend_sdf'):
                capabilities.append('blend_sdf')
            
            info['capabilities'] = capabilities

        except Exception as e:
            print(f"❌ 获取后端信息失败: {e}")

        return info

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """运行综合测试"""
        test_result = {
            'overall_status': 'failed',
            'backend_info': {},
            'function_tests': {},
            'performance_tests': {},
            'errors': []
        }

        try:
            # 获取后端信息
            test_result['backend_info'] = self.get_backend_info()
            
            # 验证后端
            validation = self.validate_cpp_backend()
            test_result['function_tests'] = validation['functions']
            test_result['performance_tests'] = validation['performance']
            test_result['errors'].extend(validation['errors'])
            
            # 判断整体状态
            if validation['available'] and not validation['errors']:
                test_result['overall_status'] = 'passed'
            elif validation['available']:
                test_result['overall_status'] = 'partial'
            else:
                test_result['overall_status'] = 'failed'

        except Exception as e:
            test_result['errors'].append(f'综合测试失败: {str(e)}')

        return test_result
