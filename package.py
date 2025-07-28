#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SDF工具快速打包脚本

简化的打包流程，专门用于生成EXE文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令"""
    print(f"执行: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            check=True,
            text=True,
            encoding='utf-8'
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        return False

def check_pyinstaller():
    """检查并安装PyInstaller"""
    try:
        import PyInstaller
        print("✓ PyInstaller已安装")
        return True
    except ImportError:
        print("安装PyInstaller...")
        return run_command(f"{sys.executable} -m pip install pyinstaller")

def clean_previous_build():
    """清理之前的构建文件"""
    print("清理之前的构建文件...")
    
    dirs_to_clean = ["build", "dist"]
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"删除目录: {dir_name}")
    
    for file_pattern in files_to_clean:
        for path in Path(".").glob(file_pattern):
            if path.is_file():
                path.unlink()
                print(f"删除文件: {path}")

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'PIL',
        'PIL.Image',
        'cv2',
        'numpy',
        'scipy',
        'scipy.ndimage',
        'src.ui.main_window',
        'src.core.sdf_generator',
        'src.utils.image_utils',
        'src.utils.file_utils',
        'src.utils.math_utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'PyQt5',
        'PyQt6',
        'test_*',
        'tests',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SDF_Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open("SDF_Tool.spec", 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✓ 创建spec文件")

def package():
    """执行打包"""
    print("开始打包...")
    
    # 使用spec文件打包
    cmd = "pyinstaller --clean SDF_Tool.spec"
    if run_command(cmd):
        print("✓ 打包成功!")
        print("可执行文件位于: dist/SDF_Tool.exe")
        
        # 显示文件大小
        exe_path = Path("dist/SDF_Tool.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"文件大小: {size_mb:.1f} MB")
        
        return True
    else:
        print("✗ 打包失败")
        return False

def main():
    """主函数"""
    print("SDF工具快速打包脚本")
    print("=" * 40)
    
    # 检查当前目录
    if not Path("main.py").exists():
        print("错误: 请在项目根目录运行此脚本")
        return 1
    
    # 检查并安装PyInstaller
    if not check_pyinstaller():
        print("PyInstaller安装失败")
        return 1
    
    # 清理之前的构建
    clean_previous_build()
    
    # 创建spec文件
    create_spec_file()
    
    # 执行打包
    if package():
        print("\n🎉 打包完成!")
        print("你可以在 dist/ 目录找到 SDF_Tool.exe")
        
        # 询问是否打开文件夹
        try:
            response = input("\n是否打开dist文件夹? (y/n): ").lower()
            if response in ['y', 'yes', '是']:
                dist_path = Path("dist").absolute()
                os.startfile(str(dist_path))
        except:
            pass
        
        return 0
    else:
        print("\n❌ 打包失败!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
