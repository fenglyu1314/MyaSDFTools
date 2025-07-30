# SDF混合算法详解

## 📍 代码位置

### 主要文件
- **核心混合算法**: `src/core/sdf_blend_algorithms.py`
- **SDF生成器**: `src/core/sdf_generator.py` (调用混合算法)
- **UI事件处理**: `src/ui/event_handlers.py` (触发混合计算)

### 关键函数
1. `SDFBlendAlgorithms.blend_multiple_sdfs()` - 主混合入口
2. `SDFBlendAlgorithms.blend_sdf_pairwise()` - 相邻帧混合策略
3. `SDFBlendAlgorithms.blend_two_sdfs()` - 两个SDF的核心混合算法

## 🔄 当前混合算法流程

### 1. 整体流程 (`blend_multiple_sdfs`)
```python
# 输入: sdf_images (List[np.ndarray]), angles (List[float])
# 输出: 混合后的SDF (np.ndarray)

1. 验证输入参数 (图像数量、尺寸一致性)
2. 如果只有一张图像，直接返回
3. 调用 blend_sdf_pairwise() 进行相邻帧混合
```

### 2. 相邻帧混合策略 (`blend_sdf_pairwise`)
```python
# 当前策略: 相邻帧两两混合
for i in range(num_images - 1):
    sdf_a = sdf_images[i]      # 第i帧
    sdf_b = sdf_images[i + 1]  # 第i+1帧
    blend_result = blend_two_sdfs(sdf_a, sdf_b)
    blend_results.append(blend_result)

# 最终结果: 所有混合结果的平均值
final_result = np.mean(blend_results, axis=0)
```

**示例**: 4张图像 → 3个混合结果
- 混合1: 图像1 + 图像2
- 混合2: 图像2 + 图像3  
- 混合3: 图像3 + 图像4
- 最终: (混合1 + 混合2 + 混合3) / 3

### 3. 核心两两混合算法 (`blend_two_sdfs`)

#### SDF格式定义
```
- 0.0-0.5: 内部区域 (距离边界越远值越小，中心最暗)
- 0.5: 边界
- 0.5-1.0: 外部区域 (距离边界越远值越大，外部最亮)
```

#### 混合规则
```python
# 1. 转换到[-1,1]范围
SDFA = (sdf_a - 0.5) * 2.0  # A的符号距离
SDFB = (sdf_b - 0.5) * 2.0  # B的符号距离

# 2. 应用混合规则
if SDFA < 0.0:  # 在A内部
    result = 1.0
elif SDFB > 0.0:  # 在B外部  
    result = 0.0
else:  # 在A外部且B内部
    result = abs(SDFB) / (abs(SDFB) + SDFA)
```

## 🤔 当前算法的潜在问题

### 1. 相邻帧混合策略问题
- **问题**: 只考虑相邻帧，可能丢失全局信息
- **影响**: 某些角度的信息可能被稀释或丢失
- **表现**: 最终结果可能不够平滑或缺少某些细节

### 2. 平均值合并问题
- **问题**: 简单平均可能导致对比度降低
- **影响**: 最终SDF可能过于"平坦"
- **表现**: 光照效果不够明显

### 3. 混合规则的数学问题
- **问题**: 当前规则可能在某些边界情况下不稳定
- **影响**: 可能产生不连续的结果
- **表现**: 混合边界可能有明显的跳跃

## 🔧 可能的改进方向

### 1. 全局混合策略
```python
# 替代方案1: 所有帧两两组合
for i in range(num_images):
    for j in range(i+1, num_images):
        blend_result = blend_two_sdfs(sdf_images[i], sdf_images[j])
        blend_results.append(blend_result)

# 替代方案2: 基于角度权重的混合
# 根据角度差异计算权重，距离越近权重越大
```

### 2. 改进的合并方式
```python
# 替代方案1: 加权平均而非简单平均
weights = calculate_blend_weights(angles)
final_result = np.average(blend_results, axis=0, weights=weights)

# 替代方案2: 最大值/最小值混合
final_result = np.maximum.reduce(blend_results)  # 或 np.minimum.reduce
```

### 3. 改进的两两混合规则
```python
# 替代方案1: 平滑过渡
# 在边界区域使用平滑插值而非硬切换

# 替代方案2: 基于距离的权重混合
# 根据到边界的距离计算混合权重
```

## 📊 调试信息

当前算法会输出以下调试信息:
```
🔄 开始SDF特性混合，共X张图像
  ✅ 混合第1帧和第2帧
  ✅ 混合第2帧和第3帧
  ...
🎯 SDF相邻帧混合完成，共生成X个混合结果
🔄 SDF混合完成 - A内部像素: X, B外部像素: X, 过渡像素: X
📊 最终混合结果值范围: [min, max]
```

## 🛠️ 修改建议

1. **先分析问题**: 运行当前算法，观察输出的调试信息
2. **对比结果**: 与期望效果对比，确定具体问题
3. **逐步改进**: 先修改一个方面，测试效果
4. **参数调优**: 如果算法正确，可能需要调整参数

## 📝 测试方法

建议创建简单的测试用例:
```python
# 创建简单的测试SDF
test_sdf_1 = create_circle_sdf(center=(100, 100), radius=50)
test_sdf_2 = create_circle_sdf(center=(150, 100), radius=50)

# 测试混合效果
result = blend_two_sdfs(test_sdf_1, test_sdf_2)

# 可视化结果
visualize_sdf_comparison(test_sdf_1, test_sdf_2, result)
```
