#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SDF工具构建脚本

用于自动化编译C++扩展模块和项目打包
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
    
    # 检查CMake
    try:
        result = run_command("cmake --version", check=False)
        if result.returncode == 0:
            print("✓ CMake已安装")
        else:
            print("✗ CMake未找到，请安装CMake")
            return False
    except:
        print("✗ CMake未找到")
        return False
    
    # 检查编译器
    if sys.platform == "win32":
        # Windows: 检查MSVC
        try:
            result = run_command("cl", check=False)
            if "Microsoft" in result.stderr:
                print("✓ MSVC编译器已找到")
            else:
                print("✗ MSVC编译器未找到，请安装Visual Studio")
                return False
        except:
            print("✗ MSVC编译器未找到")
            return False
    else:
        # Linux/Mac: 检查GCC/Clang
        try:
            result = run_command("gcc --version", check=False)
            if result.returncode == 0:
                print("✓ GCC编译器已找到")
            else:
                result = run_command("clang --version", check=False)
                if result.returncode == 0:
                    print("✓ Clang编译器已找到")
                else:
                    print("✗ 编译器未找到，请安装GCC或Clang")
                    return False
        except:
            print("✗ 编译器未找到")
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

def build_cpp_extension(build_type="Release"):
    """编译C++扩展模块"""
    print(f"编译C++扩展模块 ({build_type})...")
    
    # 创建构建目录
    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()
    
    # 配置CMake
    cmake_args = [
        "cmake",
        "..",
        f"-DCMAKE_BUILD_TYPE={build_type}"
    ]
    
    if sys.platform == "win32":
        cmake_args.extend([
            "-A", "x64",  # 64位构建
            "-T", "host=x64"
        ])
    
    cmd = " ".join(cmake_args)
    result = run_command(cmd, cwd=build_dir, check=False)
    
    if result.returncode != 0:
        print("✗ CMake配置失败")
        return False
    
    # 编译
    cmd = f"cmake --build . --config {build_type} --parallel"
    result = run_command(cmd, cwd=build_dir, check=False)
    
    if result.returncode != 0:
        print("✗ C++编译失败")
        return False
    
    print("✓ C++扩展模块编译成功")
    
    # 复制编译结果到src目录
    if sys.platform == "win32":
        src_file = build_dir / build_type / "sdf_core.pyd"
        if not src_file.exists():
            src_file = build_dir / "sdf_core.pyd"
    else:
        src_file = build_dir / "sdf_core.so"
    
    if src_file.exists():
        dst_file = Path("src") / src_file.name
        shutil.copy2(src_file, dst_file)
        print(f"✓ 扩展模块已复制到 {dst_file}")
    else:
        print("✗ 找不到编译后的扩展模块")
        return False
    
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
    
    # 打包命令
    cmd = [
        "pyinstaller",
        "--name=SDF_Tool",
        "--windowed",
        "--onefile",
        "--add-data=assets;assets",
        "--add-binary=src/sdf_core.*;.",
        "--icon=assets/icon.ico" if Path("assets/icon.ico").exists() else "",
        "main.py"
    ]
    
    cmd = " ".join(filter(None, cmd))
    result = run_command(cmd, check=False)
    
    if result.returncode == 0:
        print("✓ 应用程序打包成功")
        print("可执行文件位于: dist/SDF_Tool.exe")
        return True
    else:
        print("✗ 应用程序打包失败")
        return False

def clean_build():
    """清理构建文件"""
    print("清理构建文件...")
    
    dirs_to_clean = ["build", "dist", "__pycache__", "*.egg-info"]
    files_to_clean = ["src/sdf_core.pyd", "src/sdf_core.so"]
    
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
    parser.add_argument("--cpp", action="store_true", help="编译C++扩展")
    parser.add_argument("--test", action="store_true", help="运行测试")
    parser.add_argument("--package", action="store_true", help="打包应用程序")
    parser.add_argument("--all", action="store_true", help="执行完整构建流程")
    parser.add_argument("--build-type", default="Release", choices=["Debug", "Release"], help="构建类型")
    
    args = parser.parse_args()
    
    if args.clean:
        clean_build()
        return
    
    if not any([args.deps, args.cpp, args.test, args.package, args.all]):
        parser.print_help()
        return
    
    # 检查依赖
    if not check_dependencies():
        print("依赖检查失败，请安装必要的工具")
        sys.exit(1)
    
    success = True
    
    if args.all or args.deps:
        success &= install_python_deps()
    
    if args.all or args.cpp:
        success &= build_cpp_extension(args.build_type)
    
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
