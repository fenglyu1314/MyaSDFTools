#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SDF工具主入口文件

使用方法:
    python main.py              # 启动GUI界面
    python main.py --cli        # 命令行模式
    python main.py --help       # 显示帮助信息
"""

import sys
import os
import argparse
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def setup_environment():
    """设置运行环境"""
    # 确保必要的目录存在
    os.makedirs("output", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    # 检查依赖项
    try:
        import src
        if not src.check_dependencies():
            print("依赖项检查失败，请安装必要的依赖包")
            return False
    except ImportError:
        print("无法导入src模块，请检查项目结构")
        return False
    
    return True

def run_gui():
    """启动GUI界面"""
    try:
        from PySide6.QtWidgets import QApplication
        from src.ui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        app.setApplicationName("SDF工具")
        app.setApplicationVersion("0.1.0")
        
        # 设置应用图标 (如果存在)
        icon_path = Path("assets/icon.png")
        if icon_path.exists():
            from PySide6.QtGui import QIcon
            app.setWindowIcon(QIcon(str(icon_path)))
        
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        return app.exec()
        
    except ImportError as e:
        print(f"GUI启动失败: {e}")
        print("请确保已安装PySide6: pip install PySide6")
        return 1
    except Exception as e:
        print(f"应用程序错误: {e}")
        return 1

def run_cli(args):
    """命令行模式"""
    try:
        from src.core.sdf_generator import SDFGenerator
        from src.utils.file_utils import FileUtils
        
        print("SDF工具 - 命令行模式")
        print("功能开发中...")
        
        # TODO: 实现命令行功能
        # - 批量处理图像
        # - 参数配置
        # - 输出控制
        
        return 0
        
    except ImportError as e:
        print(f"命令行模式启动失败: {e}")
        return 1

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="SDF工具 - 二次元脸部SDF生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python main.py                    # 启动GUI界面
    python main.py --cli              # 命令行模式
    python main.py --version          # 显示版本信息
        """
    )
    
    parser.add_argument(
        '--cli', 
        action='store_true',
        help='使用命令行模式'
    )
    
    parser.add_argument(
        '--version',
        action='store_true', 
        help='显示版本信息'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    args = parser.parse_args()
    
    # 显示版本信息
    if args.version:
        try:
            import src
            version_info = src.get_version_info()
            print(f"SDF工具 v{version_info['version']}")
            print(f"C++扩展: {'已启用' if version_info['cpp_extension'] else '未启用'}")
            if 'cpp_version' in version_info:
                print(f"C++版本: {version_info['cpp_version']}")
        except:
            print("SDF工具 v0.1.0")
        return 0
    
    # 设置调试模式
    if args.debug:
        os.environ['SDF_DEBUG'] = '1'
        print("调试模式已启用")
    
    # 环境检查
    if not setup_environment():
        return 1
    
    # 选择运行模式
    if args.cli:
        return run_cli(args)
    else:
        return run_gui()

if __name__ == "__main__":
    sys.exit(main())
