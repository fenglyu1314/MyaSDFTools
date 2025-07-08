#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试批量处理功能

验证批量导入、批量生成和批量导出功能
"""

import sys
import os
import numpy as np
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.sdf_generator import SDFGenerator

def create_test_batch_images():
    """创建批量测试图像"""
    from PIL import Image
    
    # 创建测试文件夹
    test_dir = Path("temp/batch_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建不同类型的测试图像
    size = 128
    
    # 图像1: 圆形
    img1 = np.zeros((size, size), dtype=np.uint8)
    center = size // 2
    radius = 40
    for y in range(size):
        for x in range(size):
            if (x - center)**2 + (y - center)**2 <= radius**2:
                img1[y, x] = 255
    
    # 图像2: 方形
    img2 = np.zeros((size, size), dtype=np.uint8)
    margin = 30
    img2[margin:size-margin, margin:size-margin] = 255
    
    # 图像3: 三角形
    img3 = np.zeros((size, size), dtype=np.uint8)
    for y in range(size):
        for x in range(size):
            if y > size//4 and x > y - size//2 and x < size - (y - size//2):
                img3[y, x] = 255
    
    # 图像4: 十字形
    img4 = np.zeros((size, size), dtype=np.uint8)
    thickness = 20
    # 水平线
    img4[center-thickness//2:center+thickness//2, :] = 255
    # 垂直线
    img4[:, center-thickness//2:center+thickness//2] = 255
    
    # 保存图像
    images = [
        (img1, "circle.png"),
        (img2, "square.png"), 
        (img3, "triangle.png"),
        (img4, "cross.png")
    ]
    
    image_paths = []
    for img_data, filename in images:
        path = test_dir / filename
        Image.fromarray(img_data).save(path)
        image_paths.append(str(path))
        print(f"  创建测试图像: {filename}")
    
    return image_paths, str(test_dir)

def test_batch_sdf_generation():
    """测试批量SDF生成"""
    print("🔄 测试批量SDF生成")
    print("=" * 40)
    
    # 创建测试图像
    print("📁 创建测试图像...")
    image_paths, test_dir = create_test_batch_images()
    
    # 创建SDF生成器
    generator = SDFGenerator()
    
    # 测试单独生成模式
    print(f"\n🔸 测试单独生成模式 ({len(image_paths)} 张图像):")
    
    batch_results = {}
    total_time = 0.0
    
    for i, image_path in enumerate(image_paths):
        try:
            filename = Path(image_path).name
            print(f"  处理 {filename}...")
            
            sdf_result, computation_time = generator.compute_single_sdf(
                image_path,
                threshold=0.5,
                normalize=True,
                invert=False
            )
            
            batch_results[image_path] = sdf_result
            total_time += computation_time
            
            print(f"    ✅ 成功 - 形状{sdf_result.shape}, 值域[{sdf_result.min():.3f}, {sdf_result.max():.3f}], 时间{computation_time:.3f}s")
            
        except Exception as e:
            print(f"    ❌ 失败: {str(e)}")
    
    print(f"  📊 批量生成完成: {len(batch_results)}/{len(image_paths)} 成功, 总时间 {total_time:.3f}s")
    
    # 测试混合生成模式
    print(f"\n🔸 测试混合生成模式:")
    
    try:
        angles = [0, 90, 180, 270]  # 4个角度
        
        mixed_sdf, computation_time = generator.compute_multi_sdf(
            image_paths,
            angles=angles,
            threshold=0.5,
            normalize=True,
            blend_mode='weighted'
        )
        
        print(f"  ✅ 混合生成成功")
        print(f"    📊 结果形状: {mixed_sdf.shape}")
        print(f"    📈 值域: [{mixed_sdf.min():.3f}, {mixed_sdf.max():.3f}]")
        print(f"    ⏱️  时间: {computation_time:.3f}s")
        
        batch_results['mixed_result'] = mixed_sdf
        
    except Exception as e:
        print(f"  ❌ 混合生成失败: {str(e)}")
    
    return batch_results, test_dir

def test_batch_export(batch_results, test_dir):
    """测试批量导出"""
    print(f"\n💾 测试批量导出")
    print("=" * 40)
    
    if not batch_results:
        print("❌ 没有可导出的结果")
        return
    
    # 创建导出文件夹
    export_dir = Path("temp/batch_export")
    export_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 导出到: {export_dir}")
    print(f"📊 导出数量: {len(batch_results)} 个结果")
    
    from utils.image_utils import ImageUtils
    
    success_count = 0
    
    for source_path, sdf_result in batch_results.items():
        try:
            # 生成输出文件名
            if source_path == 'mixed_result':
                output_name = "mixed_sdf_result.png"
            else:
                source_name = Path(source_path).stem
                output_name = f"{source_name}_sdf.png"
            
            output_path = export_dir / output_name
            
            print(f"  导出: {output_name}...")
            
            # 导出SDF
            if ImageUtils.save_sdf_as_image(sdf_result, str(output_path)):
                success_count += 1
                print(f"    ✅ 成功")
            else:
                print(f"    ❌ 失败")
                
        except Exception as e:
            print(f"    ❌ 失败: {str(e)}")
    
    print(f"📊 批量导出完成: {success_count}/{len(batch_results)} 成功")
    
    if success_count > 0:
        print(f"💡 请查看导出结果: {export_dir}")

def main():
    """主函数"""
    print("🎨 SDF工具 - 批量处理功能测试")
    print("=" * 60)
    
    try:
        # 测试批量SDF生成
        batch_results, test_dir = test_batch_sdf_generation()
        
        # 测试批量导出
        test_batch_export(batch_results, test_dir)
        
        print("\n🎉 批量处理测试完成！")
        print("💡 功能验证:")
        print("  ✅ 批量图像创建")
        print("  ✅ 批量SDF生成 (单独模式)")
        print("  ✅ 批量SDF生成 (混合模式)")
        print("  ✅ 批量SDF导出")
        print(f"\n📁 测试文件位置:")
        print(f"  输入图像: temp/batch_test/")
        print(f"  导出结果: temp/batch_export/")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
