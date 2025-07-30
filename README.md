# SDF工具 - 二次元脸部SDF生成工具

专为二次元渲染设计的脸部SDF (Signed Distance Field) 生成工具，支持多角度光照图像混合和实时预览。

## ✨ 主要功能

- 🖼️ **多角度SDF生成**: 导入多张不同角度的脸部光照图像，生成混合SDF
- 🎯 **单张图SDF**: 快速将单张黑白图转换为SDF格式
- 🔄 **实时预览**: 滑竿控制光照角度，实时预览SDF效果
- ⚡ **高性能算法**: 基于OpenCV距离变换的改进SDF算法
- 🎨 **现代界面**: 基于PySide6的直观GUI界面，支持深色/浅色主题
- 📊 **性能监控**: 显示计算时间和性能指标
- 📦 **独立可执行文件**: 支持打包为单文件可执行程序

## 🛠️ 技术栈

- **UI框架**: PySide6 6.9.1+
- **图像处理**: OpenCV 4.12.0+, Pillow 11.3.0+, NumPy 2.2.0+
- **科学计算**: SciPy 1.11.0+
- **核心算法**: 基于OpenCV距离变换的改进SDF算法

## 📋 系统要求

- Python 3.13+ (推荐)
- 4GB+ RAM (推荐8GB)
- Windows 10/11 (已测试)


## 🚀 快速开始

### 方式一：使用可执行文件（推荐）

1. 下载 `SDF_Tool.exe` 可执行文件
2. 双击运行即可，无需安装Python环境

### 方式二：从源码运行

#### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd mya_sdf_Tools

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

#### 2. 启动应用

```bash
# 启动GUI应用
python main.py
```

#### 3. 打包可执行文件

```bash
# 使用构建脚本
python build.py
```

## 📖 使用指南

### 基础使用流程

1. **导入图像**: 点击图像卡片或"导入图像"按钮，选择多张不同角度的脸部光照黑白图（最多8张）
2. **调整参数**: 在右侧参数面板中调整阈值和最大距离参数
3. **生成SDF**: 点击"生成SDF"按钮，等待计算完成
4. **预览效果**: 在合并SDF预览区域查看生成结果
5. **光照预览**: 使用光照角度滑竿实时预览不同角度的光照效果
6. **导出结果**: 点击"导出SDF"保存生成的SDF图像文件

### 界面功能

- **主题切换**: 右上角支持深色/浅色/跟随系统主题
- **图像拖拽**: 支持拖拽调整图像顺序
- **实时预览**: SDF生成后自动更新预览
- **进度显示**: 生成过程中显示进度条

### 支持的图像格式

- **输入**: PNG, JPG, JPEG, BMP, TGA
- **输出**: PNG, TGA

## 🏗️ 项目结构

```
mya_sdf_Tools/
├── src/                    # 源代码
│   ├── ui/                # UI界面模块
│   │   ├── main_window.py        # 主窗口
│   │   ├── theme_manager.py      # 主题管理
│   │   ├── image_card_widget.py  # 图像卡片组件
│   │   ├── preview_widget.py     # 预览组件
│   │   └── ...                   # 其他UI组件
│   ├── core/              # 核心业务逻辑
│   │   ├── sdf_generator.py      # SDF生成器
│   │   ├── sdf_core_algorithm.py # 核心算法
│   │   ├── image_manager.py      # 图像管理
│   │   └── ...                   # 其他核心模块
│   └── utils/             # 工具函数
│       ├── image_utils.py        # 图像处理工具
│       ├── file_utils.py         # 文件操作工具
│       └── ...                   # 其他工具模块
├── assets/                # 资源文件
│   └── test_images/       # 测试图像
├── dist/                  # 打包输出目录
│   └── SDF_Tool.exe      # 可执行文件
├── build/                 # 构建临时文件
├── docs/                  # 文档目录
├── requirements.txt       # Python依赖
├── build.py              # 构建脚本
├── SDF_Tool.spec         # PyInstaller配置
└── main.py               # 主入口文件
```

## 🔧 开发指南

### 环境配置

1. 创建虚拟环境:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 开发工具配置:
```bash
# 安装开发工具（可选）
pip install black flake8 pytest
```

### 代码结构

项目采用模块化设计：

- `src/ui/`: PySide6界面组件，包含主窗口、主题管理、各种UI组件
- `src/core/`: 核心业务逻辑，包含SDF算法、图像管理等
- `src/utils/`: 通用工具函数，包含图像处理、文件操作等

### 构建和打包

```bash
# 构建可执行文件
python build.py

# 生成的文件位于 dist/SDF_Tool.exe
```

## 📊 性能基准

| 图像尺寸 | 单张SDF | 8张混合SDF | 内存占用 |
|---------|---------|------------|----------|
| 512x512 | ~100ms  | ~800ms     | ~200MB   |
| 1024x1024| ~400ms  | ~3.2s      | ~800MB   |
| 2048x2048| ~1.6s   | ~12.8s     | ~3.2GB   |

*测试环境: Python 3.13, Windows 11*
*注：Python实现在某些情况下比C++实现更快*

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 提交规范

使用 [Conventional Commits](https://conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `style:` 代码格式
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具相关

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [OpenCV](https://opencv.org/) - 提供高效的距离变换算法
- [SDF渲染技术](https://prideout.net/blog/distance_fields/) - SDF渲染理论参考
- [PySide6](https://www.qt.io/qt-for-python) - 现代化的Python GUI框架
- [PyInstaller](https://pyinstaller.org/) - Python应用打包工具

## 📞 联系方式

- 作者: Mya
- 项目链接: [GitHub Repository](https://github.com/username/mya_sdf_Tools)
- 问题反馈: [Issues](https://github.com/username/mya_sdf_Tools/issues)

---

⭐ 如果这个项目对您有帮助，请给个Star支持一下！
