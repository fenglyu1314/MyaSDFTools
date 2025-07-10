#pragma once

#include "common_simple.h"

namespace sdf
{

    /**
     * 8SSEDT算法实现类
     * 8-point Sequential Signed Distance Transform
     */
    class EightSSEDT
    {
    public:
        /**
         * 计算单张图像的SDF
         * @param input_data 输入图像数据 (灰度值 0-1)
         * @param info 图像信息
         * @param params SDF计算参数
         * @return SDF结果数据
         */
        static ImagePtr computeSDF(const ImageData &input_data,
                                   const ImageInfo &info,
                                   const SDFParams &params = SDFParams());

        /**
         * 计算多张图像的混合SDF
         * @param images 输入图像列表
         * @param angles 对应的光照角度列表 (度数)
         * @param info 图像信息
         * @param params SDF计算参数
         * @return 混合SDF结果
         */
        static ImagePtr computeMultiSDF(const std::vector<ImageData> &images,
                                        const std::vector<float> &angles,
                                        const ImageInfo &info,
                                        const SDFParams &params = SDFParams());

    private:
        // 核心8SSEDT算法函数
        static void computeBidirectionalSDF(const ImageData &binary_image,
                                            ImageData &result,
                                            const ImageInfo &info,
                                            const SDFParams &params);

        static void computeInsideSDF(const ImageData &binary_image,
                                     ImageData &result,
                                     const ImageInfo &info,
                                     const SDFParams &params);

        static void computeOutsideSDF(const ImageData &binary_image,
                                      ImageData &result,
                                      const ImageInfo &info,
                                      const SDFParams &params);

        // 8SSEDT核心算法
        static void compute8SSEDT(DistanceGrid &grid);
        static void forwardScan(DistanceGrid &grid);
        static void backwardScan(DistanceGrid &grid);
        static void updateDistance(DistanceGrid &grid, int x, int y, int dx, int dy);

        // 种子点初始化
        static void initializeSeedPoints(const ImageData &binary_image,
                                         DistanceGrid &inside_grid,
                                         DistanceGrid &outside_grid,
                                         const ImageInfo &info);

        static bool isBoundaryPoint(const ImageData &binary_image,
                                    int x, int y,
                                    const ImageInfo &info,
                                    bool check_inside);

        // 距离场构建
        static void buildSignedDistanceField(const DistanceGrid &inside_grid,
                                             const DistanceGrid &outside_grid,
                                             ImageData &result,
                                             const ImageInfo &info,
                                             const SDFParams &params);

        static void normalizeSDF(ImageData &sdf_data, const ImageInfo &info);

        // SDF混合算法（基于文章算法）
        static ImagePtr blendSDFPairwise(const std::vector<ImagePtr> &sdf_images,
                                         const std::vector<float> &angles,
                                         const ImageInfo &info);

        static ImagePtr blendTwoSDFs(const ImageData &sdf_a,
                                     const ImageData &sdf_b,
                                     const ImageInfo &info);
    };

    /**
     * SDF预览和插值类
     */
    class SDFPreview
    {
    public:
        /**
         * 根据光照角度插值SDF效果
         * @param sdf_data SDF数据
         * @param light_angle 光照角度 (0-360度)
         * @param info 图像信息
         * @return 插值后的光照效果图像
         */
        static ImagePtr interpolateLighting(const ImageData &sdf_data,
                                            float light_angle,
                                            const ImageInfo &info);

        /**
         * 生成SDF可视化图像
         * @param sdf_data SDF数据
         * @param info 图像信息
         * @param show_distance 是否显示距离场
         * @return 可视化图像
         */
        static ImagePtr visualizeSDF(const ImageData &sdf_data,
                                     const ImageInfo &info,
                                     bool show_distance = false);
    };

    /**
     * 性能测试和优化工具
     */
    class SDFBenchmark
    {
    public:
        struct BenchmarkResult
        {
            double computation_time_ms;
            double memory_usage_mb;
            int image_size;
            std::string algorithm_name;
        };

        /**
         * 测试SDF计算性能
         */
        static BenchmarkResult benchmarkSDF(const ImageData &input_data,
                                            const ImageInfo &info,
                                            const SDFParams &params);
    };

} // namespace sdf
