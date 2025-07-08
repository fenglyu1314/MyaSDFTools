# 示例文件

本目录包含SDF工具的使用示例和测试数据。

## 📁 目录结构

```
examples/
├── sample_images/          # 示例图像
│   ├── face_0deg.png      # 0度光照
│   ├── face_45deg.png     # 45度光照
│   ├── face_90deg.png     # 90度光照
│   └── ...
├── expected_outputs/       # 预期输出结果
│   ├── single_sdf.png     # 单张SDF结果
│   └── multi_sdf.png      # 多张混合SDF结果
├── scripts/               # 示例脚本
│   ├── basic_usage.py     # 基础使用示例
│   ├── batch_process.py   # 批量处理示例
│   └── performance_test.py # 性能测试示例
└── README.md             # 本文件
```

## 🚀 快速开始

### 1. 基础使用示例

```python
# 运行基础示例
python examples/scripts/basic_usage.py
```

### 2. 批量处理示例

```python
# 批量处理多个图像
python examples/scripts/batch_process.py --input examples/sample_images/
```

### 3. 性能测试

```python
# 运行性能基准测试
python examples/scripts/performance_test.py
```

## 📊 示例数据说明

### 输入图像要求

- **格式**: PNG, JPG (推荐PNG)
- **尺寸**: 建议512x512或1024x1024
- **类型**: 灰度图或黑白图
- **内容**: 脸部光照阴影图

### 角度分布建议

对于8张图像的标准配置:
- 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°

## 🎯 预期效果

生成的SDF图像应该:
- 平滑的灰度过渡
- 清晰的边界定义
- 正确的内外区域标识
- 适合shader中的光照计算

## 📝 注意事项

1. 输入图像应该有清晰的明暗对比
2. 建议使用相同尺寸的图像
3. 角度分布应该尽量均匀覆盖360°
4. 避免过度复杂的阴影细节
