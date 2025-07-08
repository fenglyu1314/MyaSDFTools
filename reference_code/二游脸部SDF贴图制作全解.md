## 前言

在二游脸部渲染中，如果按照正常的光源方向着色，结果不具美感，有些极端的光源角度会显得脸部很脏很乱。

![](https://pic4.zhimg.com/v2-cc8072126d41d873eed07b831583a8a5_1440w.jpg)

![](https://pic2.zhimg.com/v2-f7d0061dde6076ca9f340cd2e8d95125_1440w.jpg)

如果光源方向不考虑上下Z的角度，只考虑平面XY的角度渲染时，相对能得到一个规整，美观的阴影，不会有很奇怪很脏的现象。

![](https://pica.zhimg.com/v2-d1e4c5e1c5f50302b34a5d496d4789b2_1440w.jpg)

以这个思路为基础，为了能够得到美观的阴影，并且对一些不满意的地方手调和自定义一些阴影的形状，艺术家们开始通过绘制以光照角度变化为时间基础的脸部阴影形状[关键帧](https://zhida.zhihu.com/search?content_id=253858368&content_type=Article&match_order=1&q=%E5%85%B3%E9%94%AE%E5%B8%A7&zhida_source=entity)，来描述光绕脸部旋转中的阴影形状的变化

但是只通过关键帧，无法得到光源绕脸部（0-180度）旋转的脸部阴影变化全过程(因为不可能以1度的变化为基准画关键帧，那样将会是很绝望的工作)，所以我们需要一张图能够将关键帧整合，然后计算出帧与帧之间的过度值，以达到完整描述光源绕脸部旋转的脸部阴影变化过程。

## 核心

根据前言我们就知道了需求，所谓脸部SDF图，其实就只是利用SDF(有向距离场)的特性(方向和距离)性质，计算出关键帧和关键帧之间阴影如何过度，最后将过度的结果整合归一，其实本质上更像是脸部阴影过度图。

那么总的制作思路就是：**制作出关键帧->将关键帧转换成SDF格式->利用SDF特性进行帧与帧之间的混合->将各个混合结果叠加并且[归一化](https://zhida.zhihu.com/search?content_id=253858368&content_type=Article&match_order=1&q=%E5%BD%92%E4%B8%80%E5%8C%96&zhida_source=entity)->得到完整的过度** 下面来逐步讲解

### 制作关键帧

这一步通常艺术家会自己绘画出他们想要的大致脸部阴影形状的走向

在这里我通过我制作的blender插件简单地计算出8帧

![](https://pica.zhimg.com/v2-819b2375866b1bc0ef44bfa4e14d48de_1440w.jpg)

根据光照方向简单的step得到的8帧

### 将关键帧转换成SDF格式

关于转换的算法，可以参考下面这位大佬写的文章

[![](https://pic1.zhimg.com/v2-0f7665e71be82e7f8ac6c8b9adc9f43e.png?source=7e7ef6e2&needBackground=1)AllAllAll：SDF(signed distance field)基础理论和计算262 赞同 · 4 评论文章](https://zhuanlan.zhihu.com/p/536530019)

也有支持支持GPU并行计算的算法

[Jump Flood Algorithm](https://link.zhihu.com/?target=https%3A//www.youtube.com/watch%3Fv%3DnKJgUsAU2d0)

在这里我采用[8ssedt算法](https://zhida.zhihu.com/search?content_id=253858368&content_type=Article&match_order=1&q=8ssedt%E7%AE%97%E6%B3%95&zhida_source=entity)，不过稍作了一点修改

首先在8ssedt中，我存储了两个grid计算后的最大距离值

```text
int maxValue = INT_MAX;
for(int y = height-1; y >=0; y--)
{
    for(int x = width - 1; x >= 0; x--)
    {
        //在这里做右，右上，上，左上四个方向的Compare
    }
    for(int x = 0; x < width; x++)
    {
        //在这里做左侧的Compare
        if(maxValue < point.DistSq()) maxValue = point.DistSq();
    }
} 
return maxValue;
```

然后在计算最终的结果时，对它做了一个归一化(个人认为这里归一化后更符合SDF的定义)

```text
	for (int y = 0; y < height; y++)
	{
		for (int x = 0; x < width; x++)
		{
			int dist1 = (int)(sqrtf(GetPoint(grid1, x, y).DistSq()));
			int dist2 = (int)(sqrtf(GetPoint(grid2, x, y).DistSq()));

			int dist = dist1 - dist2;
			float val = 0.5f;
            //在这里运用归一化
            //这样最远的地方就是1，物体内最中心的地方就是0
            //后续混合的时候转换一下就可以得到-1到1的区间
			if (dist < 0)
			{
				val += dist / sqrtf(outsideMax) * 0.5f;
			}
			else
			{
				val += dist / sqrtf(insideMax) * 0.5f;
			}
			result[y * texSize + x] = val;
		}
	}
```

最终我们可以把前一步的关键帧转换成SDF格式，如下图

![](https://pic4.zhimg.com/v2-40c0d78288bebecd55c8b04f19f40605_1440w.jpg)

8帧的SDF格式

### 利用SDF特性进行帧与帧之间的混合

现在我们已经得到了每张关键帧的SDF格式，接下来就是如何混合

以第一帧和第二帧混合为例，假设第一帧称为A，第二帧称为B

那么就有如下情况：

1. 当前位置在A里面
2. 当前位置在B外面
3. 当前位置在B里面，A的外面

我们希望在A内部，它的值恒等于1

B的外部值恒等于0

在A外部&&B内部的时候，值从1-0过度，离B边界越近，值越小，并且在B边界的时候值刚好为0

*这时候都运用到了SDF，由于SDF的特性，**我们能通过方向(正负号)判断内外，通过距离计算出过度值***

情况1情况2不用过多赘述

对于情况3来说，我们就是为了分辨当前的位置更靠近A还是更靠近B

->这就是一个权重问题，可以理解为在当前位置对应的AB边界之间的距离值中，SDFA贡献更大还是SDFB贡献更大

->我们这里以B为分析对象，当B的贡献越大，离B边界越远(相对的离A边界越近)，值为1，B的贡献越小，离B边界越近，值为0，那么这正好跟我们需要的过度一样

|SDFB| 就可以得到当前点离B边界的距离

|SDFB|+SDFA 则是对于当前点来说，边界A和边界B的总距离

那么 |SDFB||SDFB|+SDFA 就是当前点SDFB于当前点相对应的AB边界距离中的贡献值

所以最终可得

```text
float SDFA = Sample(A) * 2.0 - 1.0;
float SDFB = Sample(B) * 2.0 - 1.0;

float result = 0;
//情况1
if(SDFA < 0.0) result = 1.0;
//情况2
else if(SDFB > 0.0) result = 0.0;
//情况3
else
{
  result = abs(SDFB) / (abs(SDFB) + SDFA);
}
return result;
```

这样我们就可以得到两两帧之间的混合图

### 将各个混合结果叠加并且归一化

最终我们只需要将混合图相加，然后除以他们的数量做一个归一化，即可得到我们最终需要的SDF贴图

![](https://pic1.zhimg.com/v2-3753e32b777e350929313e9376448a74_1440w.jpg)

由8帧生成的最终SDF贴图

![动图](https://pic2.zhimg.com/v2-a9928458188324bde44746ab27fb0317_b.webp)

在PS中修改阈值模拟过度

发布于 2025-02-17 18:32・上海