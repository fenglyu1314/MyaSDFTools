## 一、SDF基础理论

### 1.1SDF简单介绍

一般来说，无论2d或者3d资产都有**隐式（implicit）**和**显式（explicit）**两种存储方式，比如3d模型就可以用mesh直接存储模型数据，也可以用sdf、点云(point cloud)、神经网络(nerual rendering)来表示，2d资产（这里指贴图）也是如此。比如贴图一般直接使用rgb、hsv等参数来进行表示，但这样子再放大图片后会出现锯齿，所以想要获取高清的图像就需要较大的存储空间，这时候就需要矢量表示，在2d贴图中sdf就是为了这种需求产生的。

SDF(Signed Distance Field)在3d和2d中都有对应的应用。在3d中光线追踪对于性能的消耗过大，所以sdf常常被用来作为物体的隐式表达，配合[ray marching](https://zhida.zhihu.com/search?content_id=207362415&content_type=Article&match_order=1&q=ray+marching&zhida_source=entity)达到接近光线追踪的效果，也有比如[deepSDF](https://zhida.zhihu.com/search?content_id=207362415&content_type=Article&match_order=1&q=deepSDF&zhida_source=entity)这种对于模型的隐式表达方面的应用。在2d中，sdf常常被用来表示字体，原神的面部渲染中阴影部分贴图也是基于sdf生成的。

SDF的本质就是存储每个点到图形的最近距离，即将模型划出一个表面，在模型表面外侧的点数值大于0，在模型表面内侧的点数值小于0，如下所示：

![](https://pic2.zhimg.com/v2-cd3dd98e940270c7d7e9941eb5225189_1440w.jpg)

与SDF对应的是Unsigned Distance Field，对于物体内部的点距离都表示为0，物体外侧的点则为正数，存储到最近物体的距离。如下所示，就是一个Unsigned Distance Field。

![](https://pica.zhimg.com/v2-082f446c92f48a6c6d4044f7c85b8654_1440w.jpg)

Unsigned Distance Field表示一条直线

SDF就是在Unsigned Distance Field的基础上添加了正负关系来表示是在物体内部还是外部

![](https://pica.zhimg.com/v2-5a286cdfaa056a09f7f1fef11102d47e_1440w.jpg)

### 1.2SDF的性质

2d的sdf图映射到[0,1]上后的重要性质就是**0.5表示物体的边界**，而且显卡可以在硬件层面上进行bilinear interpolation，这样也就能保证，无论sdf图放大多少只要设置阈值只显示大于0.5的区域就可以保证图片的清晰度。

## 二、由灰度图生成二维SDF

### 2.1暴力法

1）一种简单的方法是:

到前景的distance field：各点到最近前景点的距离。**（不清楚包不包括到自身的距离）**

到背景的distance field：各点到最近背景景点的距离。

则： signed distance field = 到背景的distance field - 到前景的distance field。

当然这样子计算出来的数值有正负之分，想要存储在贴图中还需要对其进行映射。

(sdfDis-minDis)/(maxDis-minDis)这样子即可将其映射到[0,1]之间，也可以再乘以255映射到[0,255]之间。

很拉跨的O(n^4)复杂度的代码

```python
import math

import cv2 as cv
import numpy as np

width = 100

min_dis = np.ones((width,width),dtype=np.uint8)*(width+1)
min_dis2 = np.ones((width,width),dtype=np.uint8)*(width+1)

ori_img = cv.imread('a.png',0)
show_img = cv.resize(ori_img, (width,width),interpolation=cv.INTER_AREA)

def getDis(x, y, x1, y1):
    return math.sqrt((x-x1)*(x-x1) + (y-y1)*(y-y1))

#白色区域，在表面外部
def isWhite(x,y):
    return show_img[x][y]==255

#各点到最近的白色距离
for x in range(width):
    for y in range(width):
        tmp_min_dis = width+1
        for x1 in range(width):
            for y1 in range(width):
                if(isWhite(x1,y1)):
                    tmp_min_dis = min(tmp_min_dis,getDis(x,y,x1,y1))
        min_dis[x][y] = tmp_min_dis

#各点到最近的黑色距离
for x in range(width):
    for y in range(width):
        tmp_min_dis = width+1
        for x1 in range(width):
            for y1 in range(width):
                if(not(isWhite(x1,y1))):
                    tmp_min_dis = min(tmp_min_dis,getDis(x,y,x1,y1))
        min_dis2[x][y] = tmp_min_dis

final_dis = min_dis2 - min_dis
min_val = np.min(final_dis)
max_val = np.max(final_dis)
val_dis = max_val-min_val
final_dis = (final_dis+min_val)*255/val_dis

cv.imshow("img",final_dis)
cv.waitKey(0)
cv.destroyAllWindows()
```

结果如下

![](https://pica.zhimg.com/v2-f3c129c11cf8a810a68b04b722f9d1a4_1440w.png)

复杂度太高了，只能画那么大的图像，虽然不知道结果可能错了，但核心思想基本如此。

2）暴力法还有一种方法就是假设源纹理为2000*2000，将其压缩到500*500的目标纹理上，那么就扫描一遍原始纹理，找到对应的目标纹理上的点，并且将点分为inside和outside两种，对每个点求最近的和自己不是一种类型的点的距离（即inside点求离自己最近的outside点的距离，ouside点亦之）。

### 2.2**Saito的算法**

求解欧式距离可以进行分解，saito算法就是基于这种原理：

[欧几里得距离转换（EDT）算法_tianwaifeimao的博客-CSDN博客_meijster算法](https://link.zhihu.com/?target=https%3A//blog.csdn.net/tianwaifeimao/article/details/45078661)

![](https://pic1.zhimg.com/v2-6eed10a75ff07a6785ca16e592ae575e_1440w.jpg)

![](https://pic2.zhimg.com/v2-942488f9f15fb69dc0db102338360847_1440w.jpg)

### 2.3 8ssedt算法

[Signed Distance Fields](https://link.zhihu.com/?target=http%3A//www.codersnotes.com/notes/signed-distance-fields/)

[欧克欧克：Signed Distance Field](https://zhuanlan.zhihu.com/p/337944099)

上面的网址提到8ssedt算法并且给出了c++实现，可以在线性时间内生成sdf图。

![](https://picx.zhimg.com/v2-d8d95ff34d92fc143f998d1f25a4f54d_1440w.jpg)

以下是对以上网站提供的c++代码的注释版本

```cpp
#include "SDL/sdl.h"
#include <math.h>

#define WIDTH  256
#define HEIGHT 256

struct Point
{
	//dx,dy表示对于当前点的偏移值
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
	//获取当前点偏移后的点
	Point other = Get( g, x+offsetx, y+offsety );
	//给获取的点的dx和dy设置对应的偏移值
	other.dx += offsetx;
	other.dy += offsety;

	if (other.DistSq() < p.DistSq())
		p = other;
}

// Now all we have to do is run the propagation algorithm. See the paper for exactly what's happening here, 
// but basically the idea is to see what the neighboring pixel has for it's dx/dy,
//  then try adding it onto ours to see if it's better than what we already have.
void GenerateSDF( Grid &g )
{
	// Pass 0
	//遍历当前点以及左右、左下、右下、正下方的点，找到距离最短的点存储在网格对应位置处
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
    if ( SDL_Init( SDL_INIT_VIDEO ) == -1 )
        return 1;

    SDL_Surface *screen = SDL_SetVideoMode( WIDTH, HEIGHT, 32, SDL_SWSURFACE );
    if ( !screen )
        return 1;

	// Initialize the grid from the BMP file.
    SDL_Surface *temp = SDL_LoadBMP( "test.bmp" );
	temp = SDL_ConvertSurface( temp, screen->format, SDL_SWSURFACE ); 
	SDL_LockSurface( temp );
	for( int y=0;y<HEIGHT;y++ )
	{
		for ( int x=0;x<WIDTH;x++ )
		{
			Uint8 r,g,b;
			Uint32 *src = ( (Uint32 *)( (Uint8 *)temp->pixels + y*temp->pitch ) ) + x;
			SDL_GetRGB( *src, temp->format, &r, &g, &b );
			
			// Points inside get marked with a dx/dy of zero.
			// Points outside get marked with an infinitely large distance.
			// 两个网格，一个内部设置成0，外部设置成正无穷，另一个网格相反。
			if ( g < 128 )
			{
				Put( grid1, x, y, inside );
				Put( grid2, x, y, empty );
			} else {
				Put( grid2, x, y, inside );
				Put( grid1, x, y, empty );
			}
		}
	}
	SDL_UnlockSurface( temp );

	// Generate the SDF.
	GenerateSDF( grid1 );
	GenerateSDF( grid2 );
	
	// Render out the results.
	SDL_LockSurface( screen );
	for( int y=0;y<HEIGHT;y++ )
	{
		for ( int x=0;x<WIDTH;x++ )
		{
			// Calculate the actual distance from the dx/dy
			//计算偏移值的点距离当前点的距离
			int dist1 = (int)( sqrt( (double)Get( grid1, x, y ).DistSq() ) );
			int dist2 = (int)( sqrt( (double)Get( grid2, x, y ).DistSq() ) );
			int dist = dist1 - dist2;

			// Clamp and scale it, just for display purposes.
			int c = dist*3 + 128;
			if ( c < 0 ) c = 0;
			if ( c > 255 ) c = 255;

			Uint32 *dest = ( (Uint32 *)( (Uint8 *)screen->pixels + y*screen->pitch ) ) + x;
			*dest = SDL_MapRGB( screen->format, c, c, c );
		}
	}
	SDL_UnlockSurface( screen );
	SDL_Flip( screen );

	// Wait for a keypress
	SDL_Event event;
	while( true )
	{
		if ( SDL_PollEvent( &event ) ) 
		switch( event.type )
		{
		case SDL_QUIT:
		case SDL_KEYDOWN:
			return true;
		}
	}

	return 0;
}
```

以下是该代码的输入和运算结果

![](https://pic4.zhimg.com/v2-e0c87fb13be4ac99288e5ffa64ce3f91_1440w.jpg)

![](https://picx.zhimg.com/v2-3eb91ddb08cb0894f77c3e31e8099f3b_1440w.jpg)

下面的博客还对8ssedt方法进行了编译上的优化

[记一次代码优化(C++)](https://link.zhihu.com/?target=https%3A//www.jianshu.com/p/58271568781d)

## 三、参考

[https://en.wikipedia.org/wiki/Signed_distance_function](https://link.zhihu.com/?target=https%3A//en.wikipedia.org/wiki/Signed_distance_function)

[Signed Distance Fields Part 1: Unsigned Distance Fields](https://link.zhihu.com/?target=https%3A//shaderfun.com/2018/03/23/signed-distance-fields-part-1-unsigned-distance-fields/)

[Signed Distance Fields Part 2: Solid geometry](https://link.zhihu.com/?target=https%3A//shaderfun.com/2018/03/25/signed-distance-fields-part-2-solid-geometry/)

[小鱼干：SDF(signed distance field) 算法（转）](https://zhuanlan.zhihu.com/p/25102683)

[欧几里得距离转换（EDT）算法_tianwaifeimao的博客-CSDN博客_meijster算法](https://link.zhihu.com/?target=https%3A//blog.csdn.net/tianwaifeimao/article/details/45078661)

[Signed Distance Fields](https://link.zhihu.com/?target=http%3A//www.codersnotes.com/notes/signed-distance-fields/)

[欧克欧克：Signed Distance Field](https://zhuanlan.zhihu.com/p/337944099)