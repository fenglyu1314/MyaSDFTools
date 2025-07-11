#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试修复后的SDF生成功能
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_parameter_filtering():
    """测试参数过滤功能"""
    from src.ui.event_handlers import SDFGenerationWorker
    from src.core.sdf_generator import SDFGenerator
    
    # 创建测试参数（包含blend_mode）
    test_parameters = {
        'threshold': 0.5,
        'normalize': True,
        'invert': False,
        'sdf_direction': 'both',
        'blend_mode': 'sdf_blend',  # 这个参数应该被过滤掉
        'max_distance': 100,
        'use_cpp_backend': True
    }
    
    # 创建工作线程实例
    sdf_generator = SDFGenerator()
    worker = SDFGenerationWorker(sdf_generator, ['test.png'], test_parameters)
    
    # 测试参数过滤
    filtered_params = worker._filter_single_sdf_params(test_parameters)
    
    print("原始参数:", test_parameters)
    print("过滤后参数:", filtered_params)
    
    # 验证blend_mode被过滤掉
    assert 'blend_mode' not in filtered_params, "blend_mode应该被过滤掉"
    assert 'threshold' in filtered_params, "threshold应该保留"
    assert 'sdf_direction' in filtered_params, "sdf_direction应该保留"
    
    print("✅ 参数过滤测试通过")

def test_compute_single_sdf_params():
    """测试compute_single_sdf方法的参数"""
    from src.core.sdf_generator import SDFGenerator
    import inspect
    
    # 获取方法签名
    sdf_generator = SDFGenerator()
    sig = inspect.signature(sdf_generator.compute_single_sdf)
    
    print("compute_single_sdf方法参数:")
    for param_name, param in sig.parameters.items():
        print(f"  {param_name}: {param.annotation if param.annotation != inspect.Parameter.empty else 'Any'}")
    
    # 验证不包含blend_mode
    assert 'blend_mode' not in sig.parameters, "compute_single_sdf不应该包含blend_mode参数"
    print("✅ compute_single_sdf参数检查通过")

if __name__ == "__main__":
    print("🧪 开始测试SDF参数修复...")
    
    try:
        test_parameter_filtering()
        test_compute_single_sdf_params()
        print("🎉 所有测试通过！修复成功。")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
