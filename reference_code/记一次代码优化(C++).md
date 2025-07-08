---
title: "记一次代码优化(C++)"
source: "https://www.jianshu.com/p/58271568781d"
author:
  - "[[简书]]"
published: 2018-04-26
created: 2025-07-08
description: "零 引言 最近做一个图形学项目的时候用到了signed diatance field（没找着这个词的中文翻译…如果想了解其用途，可以参考知乎上这个回答），暴力算法很简单，然而..."
tags:
  - "clippings"
---


## 零 引言

最近做一个图形学项目的时候用到了signed diatance field（没找着这个词的中文翻译…如果想了解其用途，可以参考知乎上 [这个回答](https://link.jianshu.com/?t=https%3A%2F%2Fwww.zhihu.com%2Fquestion%2F41950114%2Fanswer%2F93445003) ），暴力算法很简单，然而复杂度O(N^2)。本着一颗不想动手 只愿坐享其成 快速解决战斗的心，网上找了一圈更优秀的算法和解释性的文章，无奈它们都太长长长了。最后有幸找到 [这篇博客](https://link.jianshu.com/?t=https%3A%2F%2Fblog.csdn.net%2Fpizi0475%2Farticle%2Fdetails%2F51673436) ，其代码转自 [这个网站](https://link.jianshu.com/?t=http%3A%2F%2Fwww.codersnotes.com%2Fnotes%2Fsigned-distance-fields%2F) ，是一个CPU上跑的串行代码，算法简称8SSEDT，看起来很简洁，而且复杂度O(N)，非常优秀。

为了不显得自己白白用了人家的代码 没啥贡献，我决定让它变得复杂且丑陋但跑得更快一些。本篇文章将会详细解释如何一步一步把它优化到 **速度提高80%以上** 。算法原理就不解释了，我也不清楚，只是纯粹从代码的角度尝试分析。以下所有代码可以在我的 [GitHub](https://link.jianshu.com/?t=https%3A%2F%2Fgithub.com%2Flun0522%2F8ssedt) 上找到（按理说应该各个平台都能运行）。如果路过的时候给我加个star就更棒了:)。因为初学C++，可能代码风格不是那么令人愉悦，请见谅，请指出难看之处。另外如发现其他可优化之处，欢迎讨论。

摘录算法源代码如下：

```cpp
#define WIDTH  256
#define HEIGHT 256

struct Point
{
    int dx, dy;

    int DistSq() const { return dx*dx + dy*dy; }
};

struct Grid
{
    Point grid[HEIGHT][WIDTH];
};

Point inside = { 0, 0 };
Point empty = { 9999, 9999 };
Grid grid1, grid2;

Point Get( Grid &g, int x, int y )
{
    // OPTIMIZATION: you can skip the edge check code if you make your grid 
    // have a 1-pixel gutter.
    if ( x >= 0 && y >= 0 && x < WIDTH && y < HEIGHT )
        return g.grid[y][x];
    else
        return empty;
}

void Put( Grid &g, int x, int y, const Point &p )
{
    g.grid[y][x] = p;
}

void Compare( Grid &g, Point &p, int x, int y, int offsetx, int offsety )
{
    Point other = Get( g, x+offsetx, y+offsety );
    other.dx += offsetx;
    other.dy += offsety;

    if (other.DistSq() < p.DistSq())
        p = other;
}

void GenerateSDF( Grid &g )
{
    // Pass 0
    for (int y=0;y<HEIGHT;y++)
    {
        for (int x=0;x<WIDTH;x++)
        {
            Point p = Get( g, x, y );
            Compare( g, p, x, y, -1,  0 );
            Compare( g, p, x, y,  0, -1 );
            Compare( g, p, x, y, -1, -1 );
            Compare( g, p, x, y,  1, -1 );
            Put( g, x, y, p );
        }

        for (int x=WIDTH-1;x>=0;x--)
        {
            Point p = Get( g, x, y );
            Compare( g, p, x, y, 1, 0 );
            Put( g, x, y, p );
        }
    }

    // Pass 1
    for (int y=HEIGHT-1;y>=0;y--)
    {
        for (int x=WIDTH-1;x>=0;x--)
        {
            Point p = Get( g, x, y );
            Compare( g, p, x, y,  1,  0 );
            Compare( g, p, x, y,  0,  1 );
            Compare( g, p, x, y, -1,  1 );
            Compare( g, p, x, y,  1,  1 );
            Put( g, x, y, p );
        }

        for (int x=0;x<WIDTH;x++)
        {
            Point p = Get( g, x, y );
            Compare( g, p, x, y, -1, 0 );
            Put( g, x, y, p );
        }
    }
}

int main( int argc, char* args[] )
{
    ......
    // Generate the SDF.
    GenerateSDF( grid1 );
    GenerateSDF( grid2 );
    ......
}
```

main函数只截取了中间一点点。其余部分主要是读取图像，初始化 `grid1` 和 `grid2` ，中间如截取部分所示调用两次 `GenerateSDF` ，最后把结果写回图片。所以最重要的部分都已经在这里了。值得注意的是 `grid1` 和 `grid2` 的初始化是相反的： `grid1` 把前景像素初始化为 `inside` ，背景初始化为 `empty` ； `grid2` 则刚好相反。前面提到这个代码是用来计算 **signed** diatance field的，实现的方式就是 `grid1` 算正的部分， `grid2` 算负的部分。

如果打开 [我的repo](https://link.jianshu.com/?t=https%3A%2F%2Fgithub.com%2Flun0522%2F8ssedt) ，将看到这些文件：  
[main.cpp](https://link.jianshu.com/?t=https%3A%2F%2Fgithub.com%2Flun0522%2F8ssedt%2Fblob%2Fmaster%2F8ssedt%2Fsrc%2Fmain.cpp)  
[plain\_original.hpp/cpp](https://link.jianshu.com/?t=https%3A%2F%2Fgithub.com%2Flun0522%2F8ssedt%2Fblob%2Fmaster%2F8ssedt%2Finclude%2Fplain_original.hpp)  
[all\_together.hpp/cpp](https://link.jianshu.com/?t=https%3A%2F%2Fgithub.com%2Flun0522%2F8ssedt%2Fblob%2Fmaster%2F8ssedt%2Finclude%2Fall_together.hpp)  
[sdf.hpp](https://link.jianshu.com/?t=https%3A%2F%2Fgithub.com%2Flun0522%2F8ssedt%2Fblob%2Fmaster%2F8ssedt%2Finclude%2Fsdf.hpp)  
[original.hpp/cpp](https://link.jianshu.com/?t=https%3A%2F%2Fgithub.com%2Flun0522%2F8ssedt%2Fblob%2Fmaster%2F8ssedt%2Finclude%2Foriginal.hpp)  
[avoid\_edge\_check.hpp/cpp](https://link.jianshu.com/?t=https%3A%2F%2Fgithub.com%2Flun0522%2F8ssedt%2Fblob%2Fmaster%2F8ssedt%2Finclude%2Favoid_edge_check.hpp)  
[simd\_compare.hpp/cpp](https://link.jianshu.com/?t=https%3A%2F%2Fgithub.com%2Flun0522%2F8ssedt%2Fblob%2Fmaster%2F8ssedt%2Finclude%2Fsimd_compare.hpp)  
[simple\_compare.hpp/cpp](https://link.jianshu.com/?t=https%3A%2F%2Fgithub.com%2Flun0522%2F8ssedt%2Fblob%2Fmaster%2F8ssedt%2Finclude%2Fsimple_compare.hpp)

- **main** 的开头几行有讲XCode里面需要设置的optimization level和允许AVX 2指令。这里只有一个叫 `run` 的函数，它的唯一一个参数就是输出图片的文件名，它的第3行 `sdf.run(1, name);`那个数字指定的是代码会被跑多少次然后取平均运行时间
- **plain\_original** 基本上和源代码是一样的，只是用 [stb](https://link.jianshu.com/?t=https%3A%2F%2Fgithub.com%2Fnothings%2Fstb) 来替换了图片文件的存取的代码。 **all\_together** 是把所有的优化都放在一起了。在 **main** 里面执行 `run<PlainOriginal>("plain_original");`和 `run<AllTogether>("all_together");`就可以对比它们的速度
- **sdf** (signed distance field缩写)是其他所有文件的base class，规定了统一的接口
- **original** 和之前的 **plain\_original** 包含的代码是一样的，不同的是它继承了 **sdf** 。值得注意的是，就因为这个继承，它的速度就比 **plain\_original** 慢了很多？等大神来解释为什么会这样
- 后面的 **avoid\_edge\_check** ， **simd\_compare** 和 **simple\_compare** ，从之前的 **original** 开始，一个继承另一个，每一个都包含了一种优化。最后一个 **simple\_compare** 实际包含了和 **all\_together** 一样的代码，但它也因为继承，比后者慢了很多

现在我们可以看有什么可优化的了。

## 一 减少函数调用，并避免边界检查

这里说的减少函数调用，倒不是说优化代码结构， 只是说加个 `inline` 而已。像源代码里的 `Get` 和 `Put` 这种短短的方法， `inline` 一下无伤大雅。另外一个避免边界检查，源代码的作者也提到了这一点，要避免 `Get` 里面那个 `if` ，就得在初始化 `points` 的时候周边加一圈 `Point` 。这俩优化都不难。 `Get` 和 `Put` 后来变成了这样：

```cpp
inline Point Get(Grid &g, int x, int y) override {
    return g.points[(y + 1) * gridWidth + (x + 1)];
}

inline void Put(Grid &g, int x, int y, const Point &p) override {
    g.points[(y + 1) * gridWidth + (x + 1)] = p;
}
```

`gridWidth` 也就是输入图片的宽度加2， 然后 `x` 和 `y` 各自加一个偏置1。比较dirty的部分在于 **avoid\_edge\_check.cpp** 里面初始化grid那一段，周围加一圈东西，在此不赘述。我用一张4000x4000像素的输入图片来测试，经过这个优化运行时间从 **original** 的大约2.73秒降到2.49秒，这就快了10%了。

## 二 运算并行化(SIMD)

我最开始拿到源代码的时候，一眼望去这么多 `for` 循环，满心欢喜，岂不是放几个 `#pragma omp paralle for` 就能快得不要不要的了？然而事实总是不如人意。仔细看看 `GenerateSDF` 里边，每算一个格都依赖于前一列和前一行的计算结果，这还 `parallel for` 个啥，只能老老实实串行算下去了。不过此时又观察到 `GenerateSDF` 里面有：

```cpp
// Pass 0
for (int y=0;y<HEIGHT;y++)
{
    for (int x=0;x<WIDTH;x++)
    {
        Point p = Get( g, x, y );
        Compare( g, p, x, y, -1,  0 );
        Compare( g, p, x, y,  0, -1 );
        Compare( g, p, x, y, -1, -1 );
        Compare( g, p, x, y,  1, -1 );
        Put( g, x, y, p );
    }
    ......
}
```

再一看 `Compare` ：

```cpp
void PlainOriginal::Compare( Grid &g, Point &p, int x, int y, int offsetx, int offsety )
{
    Point other = Get( g, x+offsetx, y+offsety );
    other.dx += offsetx;
    other.dy += offsety;
    
    if (other.DistSq() < p.DistSq())
        p = other;
}
```

这是啥，这是取了中心一个点和邻居四个点，加上偏置 `offsetx` 和 `offsety` ，然后算平方距离 `DistSq()` ，最后取距离最小那个点来更新中心点。这事用不着分四次来做啊。用上SIMD指令（这里用的是AVX 2），我们可以一条指令算出来四个数加四个数，或者四个数乘四个数的结果嘛。直接看修改后的代码：

```cpp
inline void GroupCompare(Grid &g, int x, int y, const __m256i& offsets) {
    Point p = Get(g, x, y);
    
    /* Point other = Get( g, x+offsetx, y+offsety ); */
    int *offsetsPtr = (int *)&offsets;
    Point pn[4] = {
        Get(g, x + offsetsPtr[0], y + offsetsPtr[4]),
        Get(g, x + offsetsPtr[1], y + offsetsPtr[5]),
        Get(g, x + offsetsPtr[2], y + offsetsPtr[6]),
        Get(g, x + offsetsPtr[3], y + offsetsPtr[7]),
    };
    
    /* other.dx += offsetx; other.dy += offsety; */
    __m256i *pnPtr = (__m256i *)pn;
    // x0, y0, x1, y1, x2, y2, x3, y3 -> x0, x1, x2, x3, y0, y1, y2, y3
    static const __m256i mask = _mm256_setr_epi32(0, 2, 4, 6, 1, 3, 5, 7);
    __m256i vecCoords = _mm256_permutevar8x32_epi32(*pnPtr, mask);
    vecCoords = _mm256_add_epi32(vecCoords, offsets);
    
    /* other.DistSq() */
    int *coordsPtr = (int *)&vecCoords;
    // note that _mm256_mul_epi32 only applies on the lower 128 bits
    __m256i vecPermuted = _mm256_permute2x128_si256(vecCoords , vecCoords, 1);
    __m256i vecSqrDists = _mm256_add_epi64(_mm256_mul_epi32(vecCoords, vecCoords),
                                           _mm256_mul_epi32(vecPermuted, vecPermuted));
    
    /* if (other.DistSq() < p.DistSq()) p = other; */
    int64_t prevDist = p.DistSq(), index = -1;
    for (int i = 0; i < 4; ++i) {
        int64_t dist = *((int64_t *)&vecSqrDists + i);
        if (dist < prevDist) {
            prevDist = dist;
            index = i;
        }
    }
    if (index != -1) Put(g, x, y, { coordsPtr[index], coordsPtr[index + 4] });
}
```

然后在 `GenerateSDF` 里简简单单地：

```cpp
static const __m256i offsets0 = _mm256_setr_epi32(-1, -1, 0, 1, 0, -1, -1, -1);
for (int y = 0; y < imageHeight; ++y) {
    for (int x = 0; x < imageWidth; ++x)
        GroupCompare(g, x, y, offsets0);
    ......
}
```

这代码一下就长了很多，但并不妨碍它更快。我们先把邻居四个点取出来放 `pn` 里，4个x和4个y刚好8个32bits的int，占满256个bits，放在一个vector里面，然后一句 `_mm256_add_epi32(vecCoords, offsets);`就能让它们都加上各自的 `offsetx` 和 `offsety` 。注意在 `pn` 里数字的排列是一个x坐标然后一个y坐标，然后再来一个x，这样x和y交错着。因为一会儿算距离需要把x和y分开，这里我们先用 `_mm256_permutevar8x32_epi32` 把x全放前边四个位置，y全放后边。

接下来要实现和 `DistSq()` 一样的操作(即 `dx*dx + dy*dy`)，也就是每个点x平方加上y平方。首先算平方。这里有一个 **坑** ：虽然 `_mm256_mul_epi32` 这个函数名看起来很像把两个256bits的vector对应位置相乘，但是！因为一个32bits的int乘上另一个32bits的结果可能需要64bits来存， `_mm256_mul_epi32` 实际上计算的是 **这个vector里面低128位** 和 **另一个vector低128位** 相乘，结果是256bits的vector，里面存的就不再是8个32bits的int，而是 **4个64bits的int** 。因此，这里我们用 `_mm256_permute2x128_si256` 交换了高低128位，然后才能计算高128位里面4个数各自的平方。

如果不想相乘的结果是64bits的int，而仍然是32bits，可以调用 `_mm256_mullo_epi32` 。这个 `lo` 的意思是它的计算结果其实是8个64bits的int，但是每个int只保留低32位，所以最后结果能塞进256bits的vector里。还有一个值得注意的问题是我在代码里把 `_mm256_add_epi64` 和 `_mm256_mul_epi32` 写在了一起，是希望编译器能把它优化成 `fmadd` ，也就是把乘和加结合在一个指令里，能快一点点（ `fmadd` 没有针对 `__m256i` 的版本，没法直接调用）。不知道编译器有没有这么做。

到最后还是写了一个很串行的 `for` 循环来找距离最大的点，不知道有没有更好更并行的方法。尽管如此，经过SIMD指令的改造，运行时间还是降到了2.18秒左右，也就是说这一项大约让速度提升了15%，虽丑犹荣。

## 三 数据复用

**simd\_compare** 其实还包含了另一个简单但效果相当好的改进。注意到在前面 `GroupCompare` 的末尾有一个 `Put` ，也就是说中心点的值有可能被更新了。想想 `GenerateSDF` 里面接下来会发生什么：

```cpp
for (int x = 0; x < imageWidth; ++x)
    GroupCompare(g, x, y, offsets0);
```

接下来我们会往右移一格（即(x+1, y)成为新的中心点），然后开始下一遍 `GroupCompare` ，然后刚才被 `Put` 的那一点（即当前的(x-1, y)）又被 `Get` 出来。这是何苦呢。于是我们稍微改改，让 `GroupCompare` 有返回值，也就是把前面说到的那位兄弟返回给 `GenerateSDF` ，然后下一回合作为参数再传给 `GroupCompare` ：

```cpp
inline Point GroupCompare(Grid &g, Point other, int x, int y, const __m256i& offsets) {
    Point self = Get(g, x, y);
    
    /* Point other = Get( g, x+offsetx, y+offsety ); */
    int *offsetsPtr = (int *)&offsets;
    Point pn[4] = {
        other,
        Get(g, x + offsetsPtr[1], y + offsetsPtr[5]),
        Get(g, x + offsetsPtr[2], y + offsetsPtr[6]),
        Get(g, x + offsetsPtr[3], y + offsetsPtr[7]),
    };

    ......

    if (index != -1) {
        other = { coordsPtr[index], coordsPtr[index + 4] };
        Put(g, x, y, other);
        return other;
    } else {
        return self;
    }
}
```

同时在 `GenerateSDF` 里：

```cpp
Point prev = Get(g, -1, y);
for (int x = 0; x < imageWidth; ++x)
    prev = GroupCompare(g, prev, x, y, offsets0);
```

Surprise咯！运行时间破了2秒，到了大约1.97。这点改动就贡献了差不多15%的速度提升。

## 四 故技重施

回想 `GenerateSDF` ，在我们前面改动的地方之后一点点，有这么一小段：

```cpp
for (int y=0;y<imageHeight;y++)
{
    ......
    
    for (int x=imageWidth-1;x>=0;x--)
    {
        Point p = Get( g, x, y );
        Compare( g, p, x, y, 1, 0 );
        Put( g, x, y, p );
    }
}
```

这么点事情何须调用 `Compare` 。我们手动把它展开也没几行。此外，我们在第三点中的改进同样可以用到这里。其实那一点在这里表现得更加丧心病狂：前一次刚刚 `Put` 进去，下一个循环 `Compare` 的时候马上又 `Get` 出来。干脆加一个这样的方法：

```cpp
inline Point SingleCompare(Grid &g, Point other,
                           int x, int y, int offsetx, int offsety) {
    Point self = Get(g, x, y);
    other.dx += offsetx;
    other.dy += offsety;
    
    if (other.DistSq() < self.DistSq()) {
        Put(g, x, y, other);
        return other;
    } else {
        return self;
    }
}
```

然后在 `GenerateSDF` 里面：

```xml
for (int y=0;y<imageHeight;y++)
{
    ......
    
    prev = Get(g, imageWidth, y);
    for (int x = imageWidth - 1; x >= 0; --x)
       prev = SingleCompare(g, prev, x, y, 1, 0);
}
```

这样就大大减少了 `Get` 的次数。更加surprise咯，现在只要1.53秒！从 **original** 到这里已经非常接近80% 的速度提升。还剩下最后一项——

## 五 全部放在一起

很早的时候我就说过继承关系竟然也会降低速度。前面我们让运行时间从2.73秒一路降到了1.53秒。现在我们可以把所有优化平铺在一个类里面（ **all\_together** ）， 同时也让源代码不继承地放在一个类里（ **plain\_original** ）。实验发现这个条件下源代码需要1.87秒，而优化过的代码只要1秒整，这不就大于80%了吗。

继续改进的空间当然还有不少，比如前面提到的找最大距离或许可以并行化，比如修改后的 `GroupCompare` 实际上有3个点可以传给下一个循环来复用。要更快的话，可能需要花点功夫理解GPU版的代码。之前提到的源代码的 [网站](https://link.jianshu.com/?t=http%3A%2F%2Fwww.codersnotes.com%2Fnotes%2Fsigned-distance-fields%2F) 上说，GPU版有复杂度O(NlogN)的算法，但毕竟是可以高度并行化，我猜测应该比这个串行版快很多。不过现在这个速度也足够令人愉悦了。

除了以上提及的几个优秀的链接以外，还需要致谢 [stb](https://link.jianshu.com/?t=https%3A%2F%2Fgithub.com%2Fnothings%2Fstb) ，本项目依赖于它读写图片。

©著作权归作者所有,转载或内容合作请联系作者  
平台声明：文章内容（如有图片或视频亦包括在内）由作者上传并发布，文章内容仅代表作者本人观点，简书系信息发布平台，仅提供信息存储服务。

3人点赞

[日记本](https://www.jianshu.com/nb/9763707)

更多精彩内容，就在简书APP

"小礼物走一走，来简书关注我"

共2人赞赏

[![  ](https://cdn2.jianshu.io/assets/default_avatar/8-a356878e44b45ab268a3b0bbaaadeeb7.jpg)](https://www.jianshu.com/u/2724ffbe3a06)

[伦啊伦](https://www.jianshu.com/u/2724ffbe3a06 "伦啊伦")

总资产55 共写了1.5W字 获得78个赞 共79个粉丝

### 全部评论0只看作者按时间倒序按时间正序

3赞 4赞

2赞赏

![](https://www.jianshu.com/p/4hTAVCJ16826v+N2iLC/nORCfTsxhHZsZt6yo3OOXp4U5/F0I45zV2q2gf7dgwFj2Iemu2SZFVwoWHPVJVHYBRDu92gst/ydBtW6hYpGMyG4vrrK0MJxgyGPXEkFS0uh96A7ML1ohlZE3SYuqIhq9vXQLBnb0CZVRctmkrWenTkdRFquqWMCNpA1ueesqgSKgoQehrc4oB+52XkriM2nsktBbVipy8wNAHWSIjTqOfk8Kv7DA441IdBhNOz8AsXtcXlRhbkBj2AAA=)

手机看全文