# SDF工具测试素材

用于SDF工具开发和测试的脸部光照图像素材。

## 目录结构

```
test_images/
├── face_lighting/     # 8张脸部光照图像 (a.png ~ h.png)
└── sdf_samples/       # SDF生成结果
    └── face_sdf.png   # 期望的合并SDF结果
```

## 素材说明

### face_lighting/
- **内容**: 8张脸部光照黑白图像 (a.png 到 h.png)
- **用途**: 作为SDF工具的输入素材，测试多角度光照合并功能
- **格式**: PNG格式，黑白图像

### sdf_samples/
- **face_sdf.png**: 基于8张光照图生成的标准SDF合并结果
- **用途**: 验证SDF算法输出的正确性

## 使用方法

1. 在SDF工具中导入 `face_lighting/` 目录下的8张图像
2. 生成合并SDF并与 `face_sdf.png` 对比验证结果
