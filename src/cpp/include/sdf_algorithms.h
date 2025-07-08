#pragma once

#include "common.h"

namespace sdf {

/**
 * 8SSEDT算法实现类
 * 8-point Sequential Signed Distance Transform
 */
class EightSSEDT {
public:
    /**
     * 计算单张图像的SDF
     * @param input_data 输入图像数据 (灰度值 0-1)
     * @param info 图像信息
     * @param params SDF计算参数
     * @return SDF结果数据
     */
    static ImagePtr computeSDF(const ImageData& input_data, 
                              const ImageInfo& info, 
                              const SDFParams& params = SDFParams());

    /**
     * 计算多张图像的混合SDF
     * @param images 输入图像列表
     * @param angles 对应的光照角度列表 (度数)
     * @param info 图像信息
     * @param params SDF计算参数
     * @return 混合SDF结果
     */
    static ImagePtr computeMultiSDF(const std::vector<ImageData>& images,
                                   const std::vector<float>& angles,
                                   const ImageInfo& info,
                                   const SDFParams& params = SDFParams());

private:
    // 内部实现结构体
    struct GridPoint {
        int x, y;
        int dist_sq;
        
        GridPoint(int x = 0, int y = 0, int d = INT_MAX) 
            : x(x), y(y), dist_sq(d) {}
        
        void update(int new_x, int new_y, int ref_x, int ref_y) {
            int dx = new_x - ref_x;
            int dy = new_y - ref_y;
            int new_dist = dx * dx + dy * dy;
            if (new_dist < dist_sq) {
                x = new_x;
                y = new_y;
                dist_sq = new_dist;
            }
        }
    };

    // 核心算法函数
    static void computeDistanceTransform(const ImageData& binary_data,
                                       std::vector<GridPoint>& grid,
                                       const ImageInfo& info,
                                       bool inside);
    
    static void forwardPass(std::vector<GridPoint>& grid, const ImageInfo& info);
    static void backwardPass(std::vector<GridPoint>& grid, const ImageInfo& info);
    
    static ImagePtr createSignedDistanceField(const std::vector<GridPoint>& inside_grid,
                                             const std::vector<GridPoint>& outside_grid,
                                             const ImageInfo& info,
                                             const SDFParams& params);
    
    // SDF混合算法
    static float blendSDFValues(float sdf_a, float sdf_b);
    static ImagePtr blendMultipleSDFs(const std::vector<ImagePtr>& sdf_images,
                                     const std::vector<float>& weights,
                                     const ImageInfo& info);
};

/**
 * SDF预览和插值类
 */
class SDFPreview {
public:
    /**
     * 根据光照角度插值SDF效果
     * @param sdf_data SDF数据
     * @param light_angle 光照角度 (0-360度)
     * @param info 图像信息
     * @return 插值后的光照效果图像
     */
    static ImagePtr interpolateLighting(const ImageData& sdf_data,
                                       float light_angle,
                                       const ImageInfo& info);

    /**
     * 生成SDF可视化图像
     * @param sdf_data SDF数据
     * @param info 图像信息
     * @param show_distance 是否显示距离场
     * @return 可视化图像
     */
    static ImagePtr visualizeSDF(const ImageData& sdf_data,
                                const ImageInfo& info,
                                bool show_distance = false);
};

/**
 * 性能测试和优化工具
 */
class SDFBenchmark {
public:
    struct BenchmarkResult {
        double computation_time_ms;
        double memory_usage_mb;
        int image_size;
        std::string algorithm_name;
    };

    /**
     * 测试SDF计算性能
     */
    static BenchmarkResult benchmarkSDF(const ImageData& input_data,
                                       const ImageInfo& info,
                                       const SDFParams& params);
};

} // namespace sdf
