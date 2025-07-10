# C++后端算法一致性指南

## 概述

为了确保C++后端与Python实现的算法一致性，需要更新C++代码以匹配最新的SDF算法修复。

## 当前状态

### Python版本（已修复）✅
- **SDF归一化**: 内部暗(0)，外部亮(1)，边界(0.5)
- **混合算法**: 相邻帧混合（7次）
- **混合逻辑**: 按照参考文章的三种情况实现

### C++版本（需要更新）⚠️
- **SDF归一化**: 可能使用旧的归一化方式
- **混合算法**: 可能不支持相邻帧混合
- **混合逻辑**: 可能与Python版本不一致

## 需要更新的C++代码

### 1. SDF归一化算法

**Python参考实现**:
```python
# 按照文章算法进行归一化
# 初始化为边界值 0.5
result = np.full_like(inside_dist, 0.5, dtype=np.float32)

# 处理内部区域：0.5 到 0.0 (内部中心最暗)
if np.any(inside_mask):
    normalized_inside = inside_dist[inside_mask] / inside_max * 0.5
    result[inside_mask] = 0.5 - normalized_inside

# 处理外部区域：0.5 到 1.0 (外部最远最亮)
if np.any(outside_mask):
    normalized_outside = outside_dist[outside_mask] / outside_max * 0.5
    result[outside_mask] = 0.5 + normalized_outside
```

**需要在C++中实现**:
```cpp
// 伪代码
float val = 0.5f;  // 边界基准值
if (dist < 0) {
    // 外部区域：0.5 到 1.0
    val += abs(dist) / sqrt(outsideMax) * 0.5f;
} else {
    // 内部区域：0.5 到 0.0
    val -= dist / sqrt(insideMax) * 0.5f;
}
```

### 2. 混合算法

**Python参考实现**:
```python
# 相邻帧混合
for i in range(num_images - 1):
    sdf_a = sdf_images[i]
    sdf_b = sdf_images[i + 1]
    blend_result = blend_two_sdfs(sdf_a, sdf_b)
    blend_results.append(blend_result)

# 平均所有混合结果
final_result = np.mean(blend_results, axis=0)
```

**需要在C++中实现**:
```cpp
// 伪代码
std::vector<cv::Mat> blend_results;
for (int i = 0; i < num_images - 1; i++) {
    cv::Mat blend_result = blendTwoSDFs(sdf_images[i], sdf_images[i + 1]);
    blend_results.push_back(blend_result);
}

// 计算平均值
cv::Mat final_result = computeMean(blend_results);
```

### 3. 两两混合逻辑

**Python参考实现**:
```python
# 将SDF从[0,1]转换到[-1,1]范围
SDFA = (sdf_a - 0.5) * 2.0
SDFB = (sdf_b - 0.5) * 2.0

# 应用混合规则
# 在A内部 (SDFA < 0, 即 sdf_a < 0.5)
mask_a_inside = SDFA < 0.0
result[mask_a_inside] = 1.0

# 在B外部 (SDFB > 0, 即 sdf_b > 0.5)
mask_b_outside = SDFB > 0.0
result[mask_b_outside] = 0.0

# 过渡区域
mask_transition = (~mask_a_inside) & (~mask_b_outside)
if np.any(mask_transition):
    abs_SDFB = np.abs(SDFB[mask_transition])
    abs_SDFA = np.abs(SDFA[mask_transition])
    denominator = abs_SDFB + abs_SDFA
    result[mask_transition] = abs_SDFB / denominator
```

## 更新步骤

### 第一步：备份现有C++代码
```bash
cp src/cpp/sdf_core.cpp src/cpp/sdf_core.cpp.backup
```

### 第二步：更新SDF归一化函数
- 修改`compute_single_sdf`函数
- 实现正确的0.5基准归一化

### 第三步：更新混合算法
- 添加相邻帧混合支持
- 修改`blend_multiple_sdfs`函数

### 第四步：更新两两混合逻辑
- 修改`blend_two_sdfs`函数
- 实现正确的内外判断逻辑

### 第五步：测试验证
- 对比C++和Python版本的输出
- 确保结果一致

## 验证方法

### 1. 单张SDF对比
```python
# 使用相同参数计算
python_result = compute_sdf_python(image, normalize=True)
cpp_result = compute_sdf_cpp(image, normalize=True)

# 计算差异
diff = np.abs(python_result - cpp_result)
max_diff = np.max(diff)
mean_diff = np.mean(diff)

print(f"最大差异: {max_diff}")
print(f"平均差异: {mean_diff}")
```

### 2. 混合结果对比
```python
# 对比最终混合结果
python_final = blend_multiple_sdfs_python(sdf_images, angles, "sdf_blend")
cpp_final = blend_multiple_sdfs_cpp(sdf_images, angles, "sdf_blend")

# 验证一致性
assert np.allclose(python_final, cpp_final, atol=1e-6)
```

## 注意事项

1. **浮点精度**: C++和Python的浮点运算可能有微小差异
2. **内存布局**: 确保C++中的数组布局与Python一致
3. **边界处理**: 特别注意图像边界的处理方式
4. **线程安全**: 如果使用多线程，确保线程安全

## 当前建议

在C++后端完全更新之前，建议：
1. **默认使用Python后端**以获得最佳效果
2. **提供UI选项**让用户选择后端
3. **显示警告信息**当使用可能不一致的C++后端时

## 更新完成后

C++后端更新完成后，应该：
1. 移除警告信息
2. 默认启用C++后端
3. 添加自动化测试确保持续一致性
