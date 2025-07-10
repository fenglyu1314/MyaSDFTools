#!/usr/bin/env python3
"""
最终测试文件夹打开功能
"""

import os
import time
from pathlib import Path

def test_final_open():
    """最终测试"""
    print("🧪 最终测试文件夹打开功能")
    print("=" * 40)
    
    test_folder = Path.cwd()
    print(f"📁 将要打开: {test_folder}")
    
    print("⏳ 3秒后执行...")
    time.sleep(3)
    
    try:
        os.startfile(str(test_folder))
        print("✅ 成功执行os.startfile()")
        print("📂 应该已经打开了文件管理器")
    except Exception as e:
        print(f"❌ 失败: {e}")

if __name__ == "__main__":
    test_final_open()
