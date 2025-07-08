#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SDF工具快速启动脚本

用于新会话中快速了解项目状态和启动开发
"""

import sys
import os
from pathlib import Path

def print_banner():
    """显示项目横幅"""
    print("=" * 60)
    print("🎨 SDF工具 - 二次元脸部SDF生成工具")
    print("📅 版本: v0.1.0 MVP")
    print("👨‍💻 状态: 功能完整，可正常使用")
    print("=" * 60)

def check_project_structure():
    """检查项目结构"""
    print("\n📁 检查项目结构...")
    
    required_files = [
        "main.py",
        "requirements.txt", 
        "src/ui/main_window.py",
        "src/core/sdf_generator.py",
        "docs/项目状态报告.md",
        "docs/MVP使用说明.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ 缺少文件: {missing_files}")
        return False
    
    print("✅ 项目结构完整")
    return True

def check_dependencies():
    """检查依赖项"""
    print("\n📦 检查依赖项...")
    
    dependencies = [
        ('PySide6', 'PySide6'),
        ('PIL', 'Pillow'),
        ('numpy', 'numpy'),
        ('cv2', 'opencv-python'),
        ('scipy', 'scipy')
    ]
    
    missing_deps = []
    
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ {package_name} (缺失)")
            missing_deps.append(package_name)
    
    if missing_deps:
        print(f"\n⚠️  需要安装: pip install {' '.join(missing_deps)}")
        return False
    
    print("✅ 所有依赖项已安装")
    return True

def show_current_status():
    """显示当前状态"""
    print("\n📊 当前项目状态:")
    print("  🎯 MVP版本: ✅ 已完成")
    print("  🖥️  UI界面: ✅ 功能完整")
    print("  🧮 SDF算法: ✅ 已验证")
    print("  🔍 预览功能: ✅ 智能缩放+拖拽")
    print("  📁 图像管理: ✅ 多格式支持")
    print("  📤 导出功能: ✅ 多格式导出")

def show_quick_commands():
    """显示快速命令"""
    print("\n🚀 快速命令:")
    print("  python test_mvp.py        # 运行MVP测试")
    print("  python main.py            # 启动应用程序")
    print("  python test_sdf_visual.py # 可视化测试")
    print("  python build.py --help    # 查看构建选项")

def show_important_docs():
    """显示重要文档"""
    print("\n📚 重要文档:")
    print("  docs/项目状态报告.md      # 完整项目状态")
    print("  docs/MVP使用说明.md       # 用户使用指南")
    print("  docs/预览功能改进说明.md   # 最新功能说明")
    print("  docs/开发指南.md          # 开发环境指南")
    print("  README.md                # 项目概述")

def show_next_steps():
    """显示下一步建议"""
    print("\n🎯 继续开发建议:")
    print("  1. 运行 'python test_mvp.py' 验证环境")
    print("  2. 运行 'python main.py' 体验当前功能")
    print("  3. 查看 'docs/项目状态报告.md' 了解详细状态")
    print("  4. 根据需求选择下一步开发方向:")
    print("     - C++后端集成 (性能提升)")
    print("     - 多角度功能优化")
    print("     - 批量处理功能")
    print("     - 高级预览功能")

def show_git_status():
    """显示Git状态"""
    print("\n📝 Git状态检查:")
    try:
        import subprocess
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print("  ⚠️  有未提交的更改")
                print("  建议运行: git add . && git commit -m 'save current state'")
            else:
                print("  ✅ 工作目录干净")
        else:
            print("  ❓ 不是Git仓库或Git不可用")
    except:
        print("  ❓ 无法检查Git状态")

def main():
    """主函数"""
    print_banner()
    
    # 检查项目状态
    structure_ok = check_project_structure()
    deps_ok = check_dependencies()
    
    if not (structure_ok and deps_ok):
        print("\n❌ 项目环境有问题，请先解决上述问题")
        return
    
    # 显示状态信息
    show_current_status()
    show_git_status()
    show_quick_commands()
    show_important_docs()
    show_next_steps()
    
    print("\n" + "=" * 60)
    print("🎉 项目准备就绪！可以开始继续开发了。")
    print("💡 建议先运行 'python test_mvp.py' 验证功能")
    print("=" * 60)

if __name__ == "__main__":
    main()
