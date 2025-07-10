#pragma once

#include <vector>
#include <memory>
#include <cmath>
#include <algorithm>
#include <chrono>
#include <string>
#include <limits>
#include <cstring>

namespace sdf
{

    // 基础数据类型定义
    using ImageData = std::vector<float>;
    using ImagePtr = std::shared_ptr<ImageData>;

    // 图像信息结构体
    struct ImageInfo
    {
        int width;
        int height;
        int channels;

        ImageInfo(int w = 0, int h = 0, int c = 1)
            : width(w), height(h), channels(c) {}

        size_t size() const
        {
            return static_cast<size_t>(width) * height * channels;
        }
    };

    // 2D点结构体
    struct Point2D
    {
        int x, y;

        Point2D(int x = 0, int y = 0) : x(x), y(y) {}

        float distanceTo(const Point2D &other) const
        {
            float dx = static_cast<float>(x - other.x);
            float dy = static_cast<float>(y - other.y);
            return std::sqrt(dx * dx + dy * dy);
        }

        int distanceSquaredTo(const Point2D &other) const
        {
            int dx = x - other.x;
            int dy = y - other.y;
            return dx * dx + dy * dy;
        }
    };

    // SDF计算参数
    struct SDFParams
    {
        float threshold;       // 二值化阈值 (0.0-1.0)
        bool normalize;        // 是否归一化到[0,1]
        bool invert;           // 是否反转内外区域
        int max_distance;      // 最大距离限制 (像素)
        std::string direction; // 计算方向 ("both", "inside", "outside")

        SDFParams(float thresh = 0.5f, bool norm = true, bool inv = false,
                  int max_dist = 100, const std::string &dir = "both")
            : threshold(thresh), normalize(norm), invert(inv),
              max_distance(max_dist), direction(dir) {}
    };

    // 混合参数
    struct BlendParams
    {
        std::string mode;           // 混合模式 ("sdf_blend", "weighted", "average", "max", "min")
        std::vector<float> weights; // 权重列表（用于weighted模式）

        BlendParams(const std::string &blend_mode = "sdf_blend")
            : mode(blend_mode) {}
    };

    // 距离网格结构（用于8SSEDT算法）
    struct DistanceGrid
    {
        std::vector<Point2D> grid;  // 最近点网格
        std::vector<int> distances; // 距离平方网格
        int width, height;

        DistanceGrid(int w, int h) : width(w), height(h)
        {
            grid.resize(w * h);
            distances.resize(w * h);
            reset();
        }

        void reset()
        {
            const int max_dist = std::numeric_limits<int>::max();
            for (int i = 0; i < width * height; ++i)
            {
                grid[i] = Point2D(-1, -1); // 无效点
                distances[i] = max_dist;
            }
        }

        Point2D &getPoint(int x, int y)
        {
            return grid[y * width + x];
        }

        const Point2D &getPoint(int x, int y) const
        {
            return grid[y * width + x];
        }

        int &getDistance(int x, int y)
        {
            return distances[y * width + x];
        }

        const int &getDistance(int x, int y) const
        {
            return distances[y * width + x];
        }

        bool isValid(int x, int y) const
        {
            return x >= 0 && x < width && y >= 0 && y < height;
        }
    };

    // 性能计时器
    class Timer
    {
    private:
        std::chrono::high_resolution_clock::time_point start_time;

    public:
        void start()
        {
            start_time = std::chrono::high_resolution_clock::now();
        }

        double elapsed() const
        {
            auto end_time = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
                end_time - start_time);
            return duration.count() / 1000.0; // 返回毫秒
        }
    };

    // 工具函数
    namespace utils
    {
        // 安全的数组访问
        inline float getPixel(const ImageData &data, int x, int y, int width, int height)
        {
            if (x < 0 || x >= width || y < 0 || y >= height)
            {
                return 0.0f;
            }
            return data[y * width + x];
        }

        // 设置像素值
        inline void setPixel(ImageData &data, int x, int y, int width, float value)
        {
            if (x >= 0 && x < width && y >= 0)
            {
                data[y * width + x] = value;
            }
        }

        // 值域限制
        template <typename T>
        inline T clamp(T value, T min_val, T max_val)
        {
            return std::max(min_val, std::min(value, max_val));
        }

        // 线性插值
        inline float lerp(float a, float b, float t)
        {
            return a + t * (b - a);
        }

        // 角度转换
        inline float radians(float degrees)
        {
            return degrees * 3.14159265359f / 180.0f;
        }

        inline float degrees(float radians)
        {
            return radians * 180.0f / 3.14159265359f;
        }
    }

    // 常用常量
    constexpr float PI = 3.14159265359f;
    constexpr float EPSILON = 1e-6f;

} // namespace sdf
