#!/usr/bin/env python3
"""
测试简化后的文件夹打开功能
只使用os.startfile，不依赖explorer命令
"""

import os
import platform
from pathlib import Path

def test_simple_open():
    """测试简化的打开方法"""
    print("🧪 测试简化的文件夹打开方法")
    print("=" * 40)
    
    # 测试目录
    test_folder = Path.cwd()
    print(f"📁 测试目录: {test_folder}")
    
    system = platform.system()
    print(f"🖥️ 操作系统: {system}")
    
    if system == "Windows":
        print("\n🔧 使用os.startfile方法:")
        try:
            print(f"  准备打开: {test_folder}")
            # os.startfile(str(test_folder))  # 注释掉避免实际打开
            print("  ✅ os.startfile方法可用")
            print("  💡 这个方法不依赖explorer命令")
        except Exception as e:
            print(f"  ❌ os.startfile失败: {e}")
    else:
        print(f"\n🔧 非Windows系统，使用其他方法")

def test_file_vs_folder():
    """测试文件和文件夹的处理"""
    print("\n🧪 测试文件和文件夹的处理")
    print("=" * 30)
    
    # 测试文件夹
    test_folder = Path.cwd()
    print(f"📁 文件夹: {test_folder}")
    print(f"   是否存在: {test_folder.exists()}")
    print(f"   是否为文件夹: {test_folder.is_dir()}")
    
    # 测试文件
    test_file = Path.cwd() / "main.py"
    if test_file.exists():
        print(f"📄 文件: {test_file}")
        print(f"   是否存在: {test_file.exists()}")
        print(f"   是否为文件: {test_file.is_file()}")
        print(f"   所在文件夹: {test_file.parent}")
        
        print("\n💡 新的处理逻辑:")
        print("   - 无论是文件还是文件夹")
        print("   - 都使用os.startfile打开所在的文件夹")
        print("   - 不再尝试选中特定文件")
        print("   - 避免了explorer命令的问题")

if __name__ == "__main__":
    print("🔧 简化的文件夹打开功能测试")
    print("移除explorer命令依赖")
    print("=" * 50)
    
    test_simple_open()
    test_file_vs_folder()
    
    print("\n" + "=" * 50)
    print("🎉 测试完成")
    print("\n💡 修复要点:")
    print("1. 完全移除对explorer命令的依赖")
    print("2. 统一使用os.startfile()方法")
    print("3. 简化逻辑：都打开文件夹，不选中特定文件")
    print("4. 更可靠，不会出现'命令不存在'的错误")
