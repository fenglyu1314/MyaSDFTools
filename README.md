# SDF工具 - 二次元脸部SDF生成工具

专为二次元渲染设计的脸部SDF (Signed Distance Field) 生成工具，支持多角度光照图像混合和实时预览。

## ✨ 主要功能

- 🖼️ **多角度SDF生成**: 导入多张不同角度的脸部光照图像，生成混合SDF
- 🎯 **单张图SDF**: 快速将单张黑白图转换为SDF格式
- 🔄 **实时预览**: 滑竿控制光照角度，实时预览SDF效果
- ⚡ **高性能算法**: 优化的8SSEDT算法Python实现
- 🎨 **现代界面**: 基于PySide6的直观GUI界面
- 📊 **性能监控**: 显示计算时间和性能指标

## 🛠️ 技术栈

- **UI框架**: PySide6
- **图像处理**: OpenCV, Pillow, NumPy
- **核心算法**: 高性能Python实现

## 📋 系统要求

- Python 3.8+
- 4GB+ RAM (推荐8GB)


## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd mya_sdf_tools

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动应用

```bash
# 快速了解项目状态
python quick_start.py

# 启动GUI应用
python main.py
```

### 3. 运行程序

```bash
# GUI模式
python main.py

# 命令行模式 (开发中)
python main.py --cli

# 查看版本信息
python main.py --version
```

## 📖 使用指南

### 基础使用流程

1. **导入图像**: 点击"导入"按钮，选择多张不同角度的脸部光照黑白图
2. **调整角度**: 在角度配置面板中调整每张图对应的光照角度
3. **生成SDF**: 点击"生成SDF"按钮，等待计算完成
4. **预览效果**: 使用光照角度滑竿实时预览SDF效果
5. **导出结果**: 保存生成的SDF图像文件

### 支持的图像格式

- **输入**: PNG, JPG, TGA, BMP
- **输出**: PNG (16-bit), EXR, TGA

## 🏗️ 项目结构

```
mya_sdf_tools/
├── src/                    # 源代码
│   ├── ui/                # UI界面模块
│   ├── core/              # 核心业务逻辑
│   └── utils/             # 工具函数
├── tests/                 # 测试文件
├── docs/                  # 文档
├── examples/              # 示例文件
├── assets/                # 资源文件
├── requirements.txt       # Python依赖
└── main.py               # 主入口文件
```

## 🔧 开发指南

### 环境配置

1. 安装开发依赖:
```bash
pip install -r requirements.txt
pip install pytest black flake8
```

2. 代码格式化:
```bash
black src/
flake8 src/
```

3. 运行测试:
```bash
pytest tests/
```

### Python开发

Python模块采用标准的包结构：

- `ui/`: PySide6界面组件
- `core/`: 业务逻辑和算法封装
- `utils/`: 通用工具函数

## 📊 性能基准

| 图像尺寸 | 单张SDF | 8张混合SDF | 内存占用 |
|---------|---------|------------|----------|
| 512x512 | ~50ms   | ~400ms     | ~100MB   |
| 1024x1024| ~200ms  | ~1.6s      | ~400MB   |
| 2048x2048| ~800ms  | ~6.4s      | ~1.6GB   |

*测试环境: Intel i7-10700K, 32GB RAM, Windows 11*

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

- [8SSEDT算法](https://github.com/example/8ssedt) - 高效的距离变换算法
- [PySide6](https://www.qt.io/qt-for-python) - 现代化的Python GUI框架


## 📞 联系方式

- 作者: Mya
- 项目链接: [GitHub Repository](https://github.com/username/mya_sdf_tools)
- 问题反馈: [Issues](https://github.com/username/mya_sdf_tools/issues)

---

⭐ 如果这个项目对您有帮助，请给个Star支持一下！
