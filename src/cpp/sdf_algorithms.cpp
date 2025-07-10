/**
 * SDF算法实现
 *
 * 实现8SSEDT算法和SDF混合算法的C++版本
 * 基于《二游脸部SDF贴图制作全解》文章中的算法
 */

#include "sdf_algorithms.h"
#include <iostream>
#include <cmath>
#include <algorithm>

namespace sdf
{

    /**
     * 8SSEDT算法实现类
     */

    ImagePtr EightSSEDT::computeSDF(const ImageData &input_data,
                                    const ImageInfo &info,
                                    const SDFParams &params)
    {
        Timer timer;
        timer.start();

        // 创建结果图像
        auto result = std::make_shared<ImageData>(info.size());

        // 二值化输入图像
        ImageData binary_image(info.size());
        for (size_t i = 0; i < input_data.size(); ++i)
        {
            binary_image[i] = input_data[i] > params.threshold ? 1.0f : 0.0f;
        }

        // 根据计算方向选择算法
        if (params.direction == "inside")
        {
            computeInsideSDF(binary_image, *result, info, params);
        }
        else if (params.direction == "outside")
        {
            computeOutsideSDF(binary_image, *result, info, params);
        }
        else
        {
            // 默认双向计算
            computeBidirectionalSDF(binary_image, *result, info, params);
        }

        // 归一化处理
        if (params.normalize)
        {
            normalizeSDF(*result, info);
        }

        // 反转处理
        if (params.invert)
        {
            for (float &pixel : *result)
            {
                pixel = 1.0f - pixel;
            }
        }

        std::cout << "8SSEDT计算完成，耗时: " << timer.elapsed() << "ms" << std::endl;
        return result;
    }

    ImagePtr EightSSEDT::computeMultiSDF(const std::vector<ImageData> &images,
                                         const std::vector<float> &angles,
                                         const ImageInfo &info,
                                         const SDFParams &params)
    {
        if (images.empty())
        {
            throw std::runtime_error("图像列表不能为空");
        }

        if (images.size() != angles.size())
        {
            throw std::runtime_error("图像数量必须与角度数量相同");
        }

        Timer timer;
        timer.start();

        // 计算每张图像的SDF
        std::vector<ImagePtr> sdf_images;
        sdf_images.reserve(images.size());

        for (size_t i = 0; i < images.size(); ++i)
        {
            auto sdf = computeSDF(images[i], info, params);
            sdf_images.push_back(sdf);
        }

        // 使用SDF特性混合算法
        auto result = blendSDFPairwise(sdf_images, angles, info);

        std::cout << "多图像SDF计算完成，耗时: " << timer.elapsed() << "ms" << std::endl;
        return result;
    }

    void EightSSEDT::computeBidirectionalSDF(const ImageData &binary_image,
                                             ImageData &result,
                                             const ImageInfo &info,
                                             const SDFParams &params)
    {
        // 创建内部和外部距离网格
        DistanceGrid inside_grid(info.width, info.height);
        DistanceGrid outside_grid(info.width, info.height);

        // 初始化种子点
        initializeSeedPoints(binary_image, inside_grid, outside_grid, info);

        // 执行8SSEDT算法
        compute8SSEDT(inside_grid);
        compute8SSEDT(outside_grid);

        // 构建有向距离场
        buildSignedDistanceField(inside_grid, outside_grid, result, info, params);
    }

    void EightSSEDT::computeInsideSDF(const ImageData &binary_image,
                                      ImageData &result,
                                      const ImageInfo &info,
                                      const SDFParams &params)
    {
        DistanceGrid grid(info.width, info.height);

        // 只初始化内部种子点
        for (int y = 0; y < info.height; ++y)
        {
            for (int x = 0; x < info.width; ++x)
            {
                if (binary_image[y * info.width + x] > 0.5f)
                {
                    // 内部点，检查是否为边界
                    if (isBoundaryPoint(binary_image, x, y, info, true))
                    {
                        grid.getPoint(x, y) = Point2D(x, y);
                        grid.getDistance(x, y) = 0;
                    }
                }
            }
        }

        compute8SSEDT(grid);

        // 转换为SDF值
        for (int y = 0; y < info.height; ++y)
        {
            for (int x = 0; x < info.width; ++x)
            {
                int idx = y * info.width + x;
                if (binary_image[idx] > 0.5f)
                {
                    result[idx] = std::sqrt(static_cast<float>(grid.getDistance(x, y)));
                }
                else
                {
                    result[idx] = 0.0f;
                }
            }
        }
    }

    void EightSSEDT::computeOutsideSDF(const ImageData &binary_image,
                                       ImageData &result,
                                       const ImageInfo &info,
                                       const SDFParams &params)
    {
        DistanceGrid grid(info.width, info.height);

        // 只初始化外部种子点
        for (int y = 0; y < info.height; ++y)
        {
            for (int x = 0; x < info.width; ++x)
            {
                if (binary_image[y * info.width + x] <= 0.5f)
                {
                    // 外部点，检查是否为边界
                    if (isBoundaryPoint(binary_image, x, y, info, false))
                    {
                        grid.getPoint(x, y) = Point2D(x, y);
                        grid.getDistance(x, y) = 0;
                    }
                }
            }
        }

        compute8SSEDT(grid);

        // 转换为SDF值
        for (int y = 0; y < info.height; ++y)
        {
            for (int x = 0; x < info.width; ++x)
            {
                int idx = y * info.width + x;
                if (binary_image[idx] <= 0.5f)
                {
                    result[idx] = std::sqrt(static_cast<float>(grid.getDistance(x, y)));
                }
                else
                {
                    result[idx] = 0.0f;
                }
            }
        }
    }

    void EightSSEDT::initializeSeedPoints(const ImageData &binary_image,
                                          DistanceGrid &inside_grid,
                                          DistanceGrid &outside_grid,
                                          const ImageInfo &info)
    {
        // 扫描所有像素，找到边界点作为种子点
        for (int y = 0; y < info.height; ++y)
        {
            for (int x = 0; x < info.width; ++x)
            {
                bool is_inside = binary_image[y * info.width + x] > 0.5f;

                if (is_inside)
                {
                    // 内部点，检查是否为边界
                    if (isBoundaryPoint(binary_image, x, y, info, true))
                    {
                        inside_grid.getPoint(x, y) = Point2D(x, y);
                        inside_grid.getDistance(x, y) = 0;
                    }
                }
                else
                {
                    // 外部点，检查是否为边界
                    if (isBoundaryPoint(binary_image, x, y, info, false))
                    {
                        outside_grid.getPoint(x, y) = Point2D(x, y);
                        outside_grid.getDistance(x, y) = 0;
                    }
                }
            }
        }
    }

    bool EightSSEDT::isBoundaryPoint(const ImageData &binary_image,
                                     int x, int y,
                                     const ImageInfo &info,
                                     bool check_inside)
    {
        float current_value = binary_image[y * info.width + x];
        bool is_current_inside = current_value > 0.5f;

        // 如果当前点的内外状态与检查状态不符，返回false
        if (is_current_inside != check_inside)
        {
            return false;
        }

        // 检查8邻域
        for (int dy = -1; dy <= 1; ++dy)
        {
            for (int dx = -1; dx <= 1; ++dx)
            {
                if (dx == 0 && dy == 0)
                    continue;

                int nx = x + dx;
                int ny = y + dy;

                // 边界处理
                if (nx < 0 || nx >= info.width || ny < 0 || ny >= info.height)
                {
                    if (check_inside)
                    {
                        return true; // 内部点接触边界
                    }
                    continue;
                }

                float neighbor_value = binary_image[ny * info.width + nx];
                bool is_neighbor_inside = neighbor_value > 0.5f;

                // 如果邻居的内外状态与当前点不同，则为边界点
                if (is_neighbor_inside != is_current_inside)
                {
                    return true;
                }
            }
        }

        return false;
    }

    void EightSSEDT::compute8SSEDT(DistanceGrid &grid)
    {
        // 8SSEDT算法的两次扫描

        // 第一次扫描：从左上到右下
        forwardScan(grid);

        // 第二次扫描：从右下到左上
        backwardScan(grid);
    }

    void EightSSEDT::forwardScan(DistanceGrid &grid)
    {
        // 前向扫描：从左上到右下
        for (int y = 0; y < grid.height; ++y)
        {
            for (int x = 0; x < grid.width; ++x)
            {
                // 检查左上、上、右上、左四个方向的邻居
                updateDistance(grid, x, y, -1, -1); // 左上
                updateDistance(grid, x, y, 0, -1);  // 上
                updateDistance(grid, x, y, 1, -1);  // 右上
                updateDistance(grid, x, y, -1, 0);  // 左
            }
        }
    }

    void EightSSEDT::backwardScan(DistanceGrid &grid)
    {
        // 后向扫描：从右下到左上
        for (int y = grid.height - 1; y >= 0; --y)
        {
            for (int x = grid.width - 1; x >= 0; --x)
            {
                // 检查右、左下、下、右下四个方向的邻居
                updateDistance(grid, x, y, 1, 0);  // 右
                updateDistance(grid, x, y, -1, 1); // 左下
                updateDistance(grid, x, y, 0, 1);  // 下
                updateDistance(grid, x, y, 1, 1);  // 右下
            }
        }
    }

    void EightSSEDT::updateDistance(DistanceGrid &grid, int x, int y, int dx, int dy)
    {
        int nx = x + dx;
        int ny = y + dy;

        // 边界检查
        if (!grid.isValid(nx, ny))
        {
            return;
        }

        // 获取邻居的最近点
        const Point2D &neighbor_point = grid.getPoint(nx, ny);

        // 如果邻居没有有效的最近点，跳过
        if (neighbor_point.x == -1 && neighbor_point.y == -1)
        {
            return;
        }

        // 计算从当前位置到邻居最近点的距离
        Point2D current_pos(x, y);
        int new_distance = current_pos.distanceSquaredTo(neighbor_point);

        // 如果新距离更小，更新当前点的信息
        if (new_distance < grid.getDistance(x, y))
        {
            grid.getDistance(x, y) = new_distance;
            grid.getPoint(x, y) = neighbor_point;
        }
    }

    void EightSSEDT::buildSignedDistanceField(const DistanceGrid &inside_grid,
                                              const DistanceGrid &outside_grid,
                                              ImageData &result,
                                              const ImageInfo &info,
                                              const SDFParams &params)
    {
        float max_distance = static_cast<float>(params.max_distance);

        for (int y = 0; y < info.height; ++y)
        {
            for (int x = 0; x < info.width; ++x)
            {
                int idx = y * info.width + x;

                // 获取内部和外部距离
                float inside_dist = std::sqrt(static_cast<float>(inside_grid.getDistance(x, y)));
                float outside_dist = std::sqrt(static_cast<float>(outside_grid.getDistance(x, y)));

                // 构建有向距离场
                // 内部为正值，外部为负值
                if (inside_dist < outside_dist)
                {
                    // 更接近内部边界，为内部点
                    result[idx] = std::min(inside_dist, max_distance);
                }
                else
                {
                    // 更接近外部边界，为外部点
                    result[idx] = -std::min(outside_dist, max_distance);
                }
            }
        }
    }

    void EightSSEDT::normalizeSDF(ImageData &sdf_data, const ImageInfo &info)
    {
        // 找到最大和最小值
        float min_val = std::numeric_limits<float>::max();
        float max_val = std::numeric_limits<float>::lowest();

        for (const float &value : sdf_data)
        {
            min_val = std::min(min_val, value);
            max_val = std::max(max_val, value);
        }

        // 避免除零
        float range = max_val - min_val;
        if (range < EPSILON)
        {
            std::fill(sdf_data.begin(), sdf_data.end(), 0.5f);
            return;
        }

        // 归一化到[0, 1]范围
        for (float &value : sdf_data)
        {
            value = (value - min_val) / range;
        }
    }

    ImagePtr EightSSEDT::blendSDFPairwise(const std::vector<ImagePtr> &sdf_images,
                                          const std::vector<float> &angles,
                                          const ImageInfo &info)
    {
        if (sdf_images.empty())
        {
            throw std::runtime_error("SDF图像列表不能为空");
        }

        if (sdf_images.size() == 1)
        {
            // 只有一张图像，直接返回副本
            return std::make_shared<ImageData>(*sdf_images[0]);
        }

        Timer timer;
        timer.start();

        std::cout << "🔄 开始SDF特性混合，共" << sdf_images.size() << "张图像" << std::endl;

        // 存储所有两两混合的结果
        std::vector<ImagePtr> blend_results;
        int blend_count = 0;

        // 对每两张图像进行混合（文章中的正确算法）
        for (size_t i = 0; i < sdf_images.size(); ++i)
        {
            for (size_t j = i + 1; j < sdf_images.size(); ++j)
            {
                auto blend_result = blendTwoSDFs(*sdf_images[i], *sdf_images[j], info);
                blend_results.push_back(blend_result);
                blend_count++;
                std::cout << "  ✅ 混合第" << (i + 1) << "帧和第" << (j + 1) << "帧" << std::endl;
            }
        }

        std::cout << "🎯 SDF特性混合完成，共生成" << blend_count << "个混合结果" << std::endl;

        // 将所有混合结果相加并归一化
        auto final_result = std::make_shared<ImageData>(info.size());
        std::fill(final_result->begin(), final_result->end(), 0.0f);

        // 累加所有混合结果
        for (const auto &blend_result : blend_results)
        {
            for (size_t i = 0; i < final_result->size(); ++i)
            {
                (*final_result)[i] += (*blend_result)[i];
            }
        }

        // 归一化（除以混合结果数量）
        float scale = 1.0f / static_cast<float>(blend_results.size());
        for (float &pixel : *final_result)
        {
            pixel *= scale;
        }

        std::cout << "SDF混合算法完成，耗时: " << timer.elapsed() << "ms" << std::endl;
        return final_result;
    }

    ImagePtr EightSSEDT::blendTwoSDFs(const ImageData &sdf_a,
                                      const ImageData &sdf_b,
                                      const ImageInfo &info)
    {
        auto result = std::make_shared<ImageData>(info.size());

        for (size_t i = 0; i < sdf_a.size(); ++i)
        {
            // 转换到[-1, 1]范围
            float sdf_a_signed = sdf_a[i] * 2.0f - 1.0f;
            float sdf_b_signed = sdf_b[i] * 2.0f - 1.0f;

            float blend_value = 0.0f;

            // 情况1: 当前位置在A里面 (优先级最高)
            if (sdf_a_signed < 0.0f)
            {
                blend_value = 1.0f;
            }
            // 情况2: 当前位置在B外面且A外面
            else if (sdf_b_signed > 0.0f)
            {
                blend_value = 0.0f;
            }
            // 情况3: 当前位置在A外面且B内部 - 过渡区域
            else
            {
                // result = abs(SDFB) / (abs(SDFB) + SDFA)
                float abs_sdf_b = std::abs(sdf_b_signed);
                float abs_sdf_a = std::abs(sdf_a_signed);

                // 避免除零
                if (abs_sdf_b + abs_sdf_a < EPSILON)
                {
                    blend_value = 0.5f;
                }
                else
                {
                    blend_value = abs_sdf_b / (abs_sdf_b + abs_sdf_a);
                }
            }

            (*result)[i] = utils::clamp(blend_value, 0.0f, 1.0f);
        }

        return result;
    }

} // namespace sdf
