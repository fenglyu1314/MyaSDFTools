#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SDF工具构建脚本

用于项目打包，生成可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

def run_command(cmd, cwd=None, show_output=True, log_file=None):
    """运行命令"""
    print(f"执行: {cmd}")

    # 记录到日志文件
    if log_file:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"命令: {cmd}\n")
            f.write(f"工作目录: {cwd or os.getcwd()}\n")
            f.write(f"{'='*60}\n")

    try:
        if show_output:
            # 实时显示输出，同时捕获到日志
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                check=True,
                text=True,
                encoding='utf-8',
                capture_output=True
            )

            # 显示输出
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)

            # 记录到日志文件
            if log_file:
                with open(log_file, 'a', encoding='utf-8') as f:
                    if result.stdout:
                        f.write("STDOUT:\n")
                        f.write(result.stdout)
                        f.write("\n")
                    if result.stderr:
                        f.write("STDERR:\n")
                        f.write(result.stderr)
                        f.write("\n")
                    f.write("状态: 成功\n")
        else:
            # 只捕获输出
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                check=True,
                text=True,
                encoding='utf-8',
                capture_output=True
            )

            # 记录到日志文件
            if log_file:
                with open(log_file, 'a', encoding='utf-8') as f:
                    if result.stdout:
                        f.write("STDOUT:\n")
                        f.write(result.stdout)
                        f.write("\n")
                    if result.stderr:
                        f.write("STDERR:\n")
                        f.write(result.stderr)
                        f.write("\n")
                    f.write("状态: 成功\n")

        return True
    except subprocess.CalledProcessError as e:
        error_msg = f"❌ 命令执行失败: {e}"
        print(error_msg)

        if hasattr(e, 'stderr') and e.stderr:
            print(f"错误信息: {e.stderr}")
        if hasattr(e, 'stdout') and e.stdout:
            print(f"输出信息: {e.stdout}")

        # 记录错误到日志文件
        if log_file:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"状态: 失败\n")
                f.write(f"错误: {e}\n")
                if hasattr(e, 'stdout') and e.stdout:
                    f.write("STDOUT:\n")
                    f.write(e.stdout)
                    f.write("\n")
                if hasattr(e, 'stderr') and e.stderr:
                    f.write("STDERR:\n")
                    f.write(e.stderr)
                    f.write("\n")

        return False

def create_build_log():
    """创建构建日志文件"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"build_log_{timestamp}.txt"

    # 创建日志文件并写入头部信息
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("SDF工具构建日志\n")
        f.write("="*60 + "\n")
        f.write(f"构建开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Python版本: {sys.version}\n")
        f.write(f"工作目录: {os.getcwd()}\n")
        f.write("="*60 + "\n")

    print(f"📝 创建构建日志: {log_file}")
    return log_file

def check_pyinstaller():
    """检查并安装PyInstaller"""
    try:
        __import__('PyInstaller')
        print("✓ PyInstaller已安装")
        return True
    except ImportError:
        print("安装PyInstaller...")
        return run_command(f"{sys.executable} -m pip install pyinstaller")

def clean_previous_build():
    """清理之前的构建文件"""
    print("🧹 清理之前的构建文件...")

    dirs_to_clean = ["build", "dist"]
    files_to_clean = ["*.spec"]

    cleaned_items = 0
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"  ✓ 删除目录: {dir_name}")
            cleaned_items += 1

    for file_pattern in files_to_clean:
        for path in Path(".").glob(file_pattern):
            if path.is_file():
                path.unlink()
                print(f"  ✓ 删除文件: {path}")
                cleaned_items += 1

    if cleaned_items == 0:
        print("  ✓ 无需清理，目录已干净")

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
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
        'sphinx',
        'sphinx.ext.napoleon',
        'pygments.lexers.c_cpp',
        'docutils',
        'jinja2',
        'babel',
        'IPython',
        'jupyter',
        'notebook',
        'pandas',
        'sympy',
        'setuptools',
        'distutils',
        'pkg_resources',
        'email',
        'xml',
        'urllib3',
        'requests',
        'certifi',
        'charset_normalizer',
        'idna',
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

    print("📝 创建PyInstaller配置文件: SDF_Tool.spec")

def package(log_file=None):
    """执行打包"""
    print("🔨 开始打包...")
    print("📋 这可能需要几分钟时间，请耐心等待...")
    print("📊 PyInstaller正在分析依赖关系...")
    print("💡 注意: 如果看到strip相关的警告，这是正常的，不影响打包结果")
    if log_file:
        print(f"📄 详细日志将保存到: {log_file}")
    print()

    # 使用spec文件打包，保存详细日志
    cmd = "pyinstaller --clean --noconfirm --log-level=INFO SDF_Tool.spec"

    print("🚀 执行打包命令...")
    if run_command(cmd, show_output=True, log_file=log_file):
        print("\n✅ 打包成功!")
        print("📁 可执行文件位于: dist/SDF_Tool.exe")

        # 显示文件大小
        exe_path = Path("dist/SDF_Tool.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📏 文件大小: {size_mb:.1f} MB")

        return True
    else:
        print("\n❌ 打包失败")
        return False

def main():
    """主函数"""
    print("🔧 SDF工具构建脚本")
    print("=" * 40)
    print("📦 准备打包SDF工具为可执行文件...")
    print()

    # 创建构建日志
    log_file = create_build_log()

    try:
        # 检查当前目录
        if not Path("main.py").exists():
            print("❌ 错误: 请在项目根目录运行此脚本")
            return 1

        print("✅ 项目目录检查通过")

        # 检查并安装PyInstaller
        if not check_pyinstaller():
            print("❌ PyInstaller安装失败")
            return 1

        # 清理之前的构建
        clean_previous_build()

        # 创建spec文件
        create_spec_file()

        # 执行打包
        if package(log_file):
            print("\n🎉 打包完成!")
            print("📁 你可以在 dist/ 目录找到 SDF_Tool.exe")
            print(f"📄 详细构建日志已保存: {log_file}")

            # 询问是否打开文件夹
            try:
                response = input("\n💡 是否打开dist文件夹? (y/n): ").lower()
                if response in ['y', 'yes', '是']:
                    dist_path = Path("dist").absolute()
                    os.startfile(str(dist_path))
                    print("📂 已打开文件夹")
            except KeyboardInterrupt:
                print("\n👋 用户取消操作")
            except Exception as e:
                print(f"⚠️  打开文件夹失败: {e}")

            return 0
        else:
            print("\n❌ 打包失败!")
            print(f"📄 详细错误信息请查看日志: {log_file}")
            print("💡 请检查日志文件中的错误信息，或尝试重新运行脚本")
            return 1

    except Exception as e:
        print(f"\n❌ 构建过程中发生异常: {e}")
        print(f"📄 详细信息请查看日志: {log_file}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
