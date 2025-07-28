#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SDF工具构建脚本

用于项目打包和依赖管理
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """运行命令并处理错误"""
    print(f"执行命令: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_dependencies():
    """检查构建依赖"""
    print("检查构建依赖...")

    # 检查Python
    try:
        import sys
        print(f"✓ Python {sys.version}")
    except:
        print("✗ Python未找到")
        return False

    return True

def install_python_deps():
    """安装Python依赖"""
    print("安装Python依赖...")

    # 检查requirements.txt
    if not Path("requirements.txt").exists():
        print("✗ requirements.txt未找到")
        return False

    # 安装依赖
    cmd = f"{sys.executable} -m pip install -r requirements.txt"
    result = run_command(cmd, check=False)

    if result.returncode == 0:
        print("✓ Python依赖安装成功")
        return True
    else:
        print("✗ Python依赖安装失败")
        return False

def install_build_deps():
    """安装构建依赖"""
    print("安装构建依赖...")

    build_deps = ["pyinstaller", "setuptools", "wheel"]

    for dep in build_deps:
        print(f"安装 {dep}...")
        cmd = f"{sys.executable} -m pip install {dep}"
        result = run_command(cmd, check=False)

        if result.returncode != 0:
            print(f"✗ {dep} 安装失败")
            return False

    print("✓ 构建依赖安装成功")
    return True



def run_tests():
    """运行测试"""
    print("运行测试...")
    
    # 检查pytest
    try:
        import pytest
    except ImportError:
        print("安装pytest...")
        run_command(f"{sys.executable} -m pip install pytest")
    
    # 运行测试
    cmd = f"{sys.executable} -m pytest tests/ -v"
    result = run_command(cmd, check=False)
    
    if result.returncode == 0:
        print("✓ 所有测试通过")
        return True
    else:
        print("✗ 测试失败")
        return False

def package_app():
    """打包应用程序"""
    print("打包应用程序...")

    # 检查PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("安装PyInstaller...")
        run_command(f"{sys.executable} -m pip install pyinstaller")

    # 创建临时spec文件以更好地控制打包过程
    spec_content = create_pyinstaller_spec()
    spec_file = "SDF_Tool.spec"

    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print(f"创建spec文件: {spec_file}")

    # 使用spec文件打包
    cmd = f"pyinstaller --clean {spec_file}"
    result = run_command(cmd, check=False)

    if result.returncode == 0:
        print("✓ 应用程序打包成功")
        print("可执行文件位于: dist/SDF_Tool.exe")

        # 清理临时文件
        if Path(spec_file).exists():
            Path(spec_file).unlink()

        return True
    else:
        print("✗ 应用程序打包失败")
        return False

def create_pyinstaller_spec():
    """创建PyInstaller spec文件内容"""
    return '''# -*- mode: python ; coding: utf-8 -*-

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

def clean_build():
    """清理构建文件"""
    print("清理构建文件...")
    
    dirs_to_clean = ["build", "dist", "__pycache__", "*.egg-info"]
    files_to_clean = []
    
    for dir_pattern in dirs_to_clean:
        for path in Path(".").glob(f"**/{dir_pattern}"):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"删除目录: {path}")
    
    for file_pattern in files_to_clean:
        for path in Path(".").glob(file_pattern):
            if path.is_file():
                path.unlink()
                print(f"删除文件: {path}")
    
    print("✓ 清理完成")

def main():
    parser = argparse.ArgumentParser(description="SDF工具构建脚本")
    parser.add_argument("--clean", action="store_true", help="清理构建文件")
    parser.add_argument("--deps", action="store_true", help="安装Python依赖")

    parser.add_argument("--test", action="store_true", help="运行测试")
    parser.add_argument("--package", action="store_true", help="打包应用程序")
    parser.add_argument("--all", action="store_true", help="执行完整构建流程")
    parser.add_argument("--build-type", default="Release", choices=["Debug", "Release"], help="构建类型")
    
    args = parser.parse_args()
    
    if args.clean:
        clean_build()
        return
    
    if not any([args.deps, args.test, args.package, args.all]):
        parser.print_help()
        return
    
    # 检查依赖
    if not check_dependencies():
        print("依赖检查失败，请安装必要的工具")
        sys.exit(1)
    
    success = True
    
    if args.all or args.deps:
        success &= install_python_deps()
        success &= install_build_deps()

    if args.all or args.test:
        success &= run_tests()

    if args.all or args.package:
        success &= package_app()
    
    if success:
        print("\n🎉 构建完成!")
    else:
        print("\n❌ 构建失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
