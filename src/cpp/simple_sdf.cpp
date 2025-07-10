// Simple SDF implementation for testing
// Minimal C++ implementation without complex features

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <cmath>
#include <algorithm>
#include <iostream>

namespace py = pybind11;

// Simple SDF computation using basic distance transform
std::vector<float> compute_simple_sdf(const std::vector<float> &image_data,
                                      int width, int height,
                                      float threshold = 0.5f,
                                      bool normalize = true,
                                      int max_distance = 100)
{

    std::vector<float> result(width * height);

    // Binary threshold
    std::vector<bool> binary(width * height);
    for (int i = 0; i < width * height; ++i)
    {
        binary[i] = image_data[i] > threshold;
    }

    // Fast distance transform using simplified algorithm
    // Initialize distance arrays with max_distance limit
    std::vector<float> inside_dist(width * height, static_cast<float>(max_distance));
    std::vector<float> outside_dist(width * height, static_cast<float>(max_distance));

    // Initialize boundary points
    for (int y = 0; y < height; ++y)
    {
        for (int x = 0; x < width; ++x)
        {
            int idx = y * width + x;
            bool is_inside = binary[idx];

            // Check if this is a boundary point
            bool is_boundary = false;
            for (int dy = -1; dy <= 1 && !is_boundary; ++dy)
            {
                for (int dx = -1; dx <= 1 && !is_boundary; ++dx)
                {
                    if (dx == 0 && dy == 0)
                        continue;

                    int nx = x + dx;
                    int ny = y + dy;

                    if (nx >= 0 && nx < width && ny >= 0 && ny < height)
                    {
                        int nidx = ny * width + nx;
                        bool neighbor_inside = binary[nidx];

                        if (neighbor_inside != is_inside)
                        {
                            is_boundary = true;
                        }
                    }
                    else if (is_inside)
                    {
                        // Inside points touching image boundary are boundary points
                        is_boundary = true;
                    }
                }
            }

            if (is_boundary)
            {
                if (is_inside)
                {
                    inside_dist[idx] = 0.0f;
                }
                else
                {
                    outside_dist[idx] = 0.0f;
                }
            }
        }
    }

    // Ultra-fast distance propagation with very limited iterations
    bool changed = true;
    int iterations = 0;
    const int max_iterations = std::min(max_distance, 5); // 大幅限制迭代次数

    while (changed && iterations < max_iterations)
    {
        changed = false;
        iterations++;

        // Forward pass
        for (int y = 0; y < height; ++y)
        {
            for (int x = 0; x < width; ++x)
            {
                int idx = y * width + x;

                if (binary[idx])
                {
                    // Inside point - update inside distance
                    float &current_dist = inside_dist[idx];

                    // Check 4-connected neighbors (with max_distance limit)
                    if (x > 0 && inside_dist[idx - 1] + 1.0f < current_dist && inside_dist[idx - 1] + 1.0f <= max_distance)
                    {
                        current_dist = inside_dist[idx - 1] + 1.0f;
                        changed = true;
                    }
                    if (y > 0 && inside_dist[idx - width] + 1.0f < current_dist && inside_dist[idx - width] + 1.0f <= max_distance)
                    {
                        current_dist = inside_dist[idx - width] + 1.0f;
                        changed = true;
                    }
                }
                else
                {
                    // Outside point - update outside distance
                    float &current_dist = outside_dist[idx];

                    // Check 4-connected neighbors (with max_distance limit)
                    if (x > 0 && outside_dist[idx - 1] + 1.0f < current_dist && outside_dist[idx - 1] + 1.0f <= max_distance)
                    {
                        current_dist = outside_dist[idx - 1] + 1.0f;
                        changed = true;
                    }
                    if (y > 0 && outside_dist[idx - width] + 1.0f < current_dist && outside_dist[idx - width] + 1.0f <= max_distance)
                    {
                        current_dist = outside_dist[idx - width] + 1.0f;
                        changed = true;
                    }
                }
            }
        }

        // Backward pass
        for (int y = height - 1; y >= 0; --y)
        {
            for (int x = width - 1; x >= 0; --x)
            {
                int idx = y * width + x;

                if (binary[idx])
                {
                    // Inside point - update inside distance
                    float &current_dist = inside_dist[idx];

                    // Check 4-connected neighbors (with max_distance limit)
                    if (x < width - 1 && inside_dist[idx + 1] + 1.0f < current_dist && inside_dist[idx + 1] + 1.0f <= max_distance)
                    {
                        current_dist = inside_dist[idx + 1] + 1.0f;
                        changed = true;
                    }
                    if (y < height - 1 && inside_dist[idx + width] + 1.0f < current_dist && inside_dist[idx + width] + 1.0f <= max_distance)
                    {
                        current_dist = inside_dist[idx + width] + 1.0f;
                        changed = true;
                    }
                }
                else
                {
                    // Outside point - update outside distance
                    float &current_dist = outside_dist[idx];

                    // Check 4-connected neighbors (with max_distance limit)
                    if (x < width - 1 && outside_dist[idx + 1] + 1.0f < current_dist && outside_dist[idx + 1] + 1.0f <= max_distance)
                    {
                        current_dist = outside_dist[idx + 1] + 1.0f;
                        changed = true;
                    }
                    if (y < height - 1 && outside_dist[idx + width] + 1.0f < current_dist && outside_dist[idx + width] + 1.0f <= max_distance)
                    {
                        current_dist = outside_dist[idx + width] + 1.0f;
                        changed = true;
                    }
                }
            }
        }
    }

    // Build SDF using the corrected normalization (matching Python version)
    if (normalize)
    {
        // Calculate max distances for normalization
        float inside_max = 0.0f;
        float outside_max = 0.0f;

        for (int i = 0; i < width * height; ++i)
        {
            if (binary[i])
            {
                inside_max = std::max(inside_max, inside_dist[i]);
            }
            else
            {
                outside_max = std::max(outside_max, outside_dist[i]);
            }
        }

        // Avoid division by zero
        inside_max = std::max(inside_max, 1e-8f);
        outside_max = std::max(outside_max, 1e-8f);

        // Apply the corrected normalization (matching Python algorithm)
        // 按照文章算法：内部暗(0)，外部亮(1)，边界(0.5)
        for (int i = 0; i < width * height; ++i)
        {
            result[i] = 0.5f; // 边界基准值

            if (binary[i])
            {
                // 内部区域：0.5 到 0.0 (内部中心最暗)
                float normalized_inside = inside_dist[i] / inside_max * 0.5f;
                result[i] = 0.5f - normalized_inside;
            }
            else
            {
                // 外部区域：0.5 到 1.0 (外部最远最亮)
                float normalized_outside = outside_dist[i] / outside_max * 0.5f;
                result[i] = 0.5f + normalized_outside;
            }

            // 确保结果在 [0, 1] 范围内
            result[i] = std::max(0.0f, std::min(1.0f, result[i]));
        }
    }
    else
    {
        // 不归一化时使用原始距离值
        for (int j = 0; j < width * height; ++j)
        {
            if (binary[j])
            {
                result[j] = inside_dist[j];
            }
            else
            {
                result[j] = outside_dist[j];
            }
        }
    }

    return result;
}

// 两两SDF混合函数（匹配Python版本）
std::vector<float> blend_two_sdfs(const std::vector<float> &sdf_a,
                                  const std::vector<float> &sdf_b,
                                  int width, int height)
{
    std::vector<float> result(width * height);

    for (int i = 0; i < width * height; ++i)
    {
        // 将SDF从[0,1]转换到[-1,1]范围
        // 按照文章的定义：0.5 -> 0 (边界), <0.5 -> 负值 (内部), >0.5 -> 正值 (外部)
        float SDFA = (sdf_a[i] - 0.5f) * 2.0f;
        float SDFB = (sdf_b[i] - 0.5f) * 2.0f;

        // 应用混合规则 (注意：现在<0.5是内部，>0.5是外部)
        if (SDFA < 0.0f)
        {
            // 在A内部 (SDFA < 0, 即 sdf_a < 0.5)
            result[i] = 1.0f;
        }
        else if (SDFB > 0.0f)
        {
            // 在B外部 (SDFB > 0, 即 sdf_b > 0.5)
            result[i] = 0.0f;
        }
        else
        {
            // 在A外部且B内部 (SDFA >= 0 and SDFB <= 0)
            float abs_SDFB = std::abs(SDFB);
            float abs_SDFA = std::abs(SDFA);
            float denominator = abs_SDFB + abs_SDFA;

            if (denominator > 1e-8f)
            {
                result[i] = abs_SDFB / denominator;
            }
            else
            {
                result[i] = 0.5f; // 默认值
            }
        }
    }

    return result;
}

// 多SDF相邻帧混合函数（匹配Python版本）
std::vector<float> blend_multiple_sdfs(const std::vector<std::vector<float>> &sdf_images,
                                       int width, int height)
{
    if (sdf_images.empty())
    {
        return std::vector<float>(width * height, 0.0f);
    }

    if (sdf_images.size() == 1)
    {
        return sdf_images[0];
    }

    // 存储所有相邻帧混合的结果
    std::vector<std::vector<float>> blend_results;

    // 相邻帧混合：第1帧和第2帧，第2帧和第3帧，...，第(n-1)帧和第n帧
    for (size_t i = 0; i < sdf_images.size() - 1; ++i)
    {
        std::vector<float> blend_result = blend_two_sdfs(sdf_images[i], sdf_images[i + 1], width, height);
        blend_results.push_back(blend_result);
    }

    // 将所有混合结果相加并归一化
    std::vector<float> final_result(width * height, 0.0f);

    for (const auto &blend_result : blend_results)
    {
        for (int i = 0; i < width * height; ++i)
        {
            final_result[i] += blend_result[i];
        }
    }

    // 归一化：除以混合结果的数量
    float num_blends = static_cast<float>(blend_results.size());
    for (float &val : final_result)
    {
        val /= num_blends;
    }

    return final_result;
}

// Test function
std::string get_version()
{
    return "Simple SDF C++ v0.2.0 - Updated Algorithm";
}

// Validate image data
bool validate_image(const std::vector<float> &data, int width, int height)
{
    if (data.empty())
        return false;
    if (width <= 0 || height <= 0)
        return false;
    if (static_cast<int>(data.size()) != width * height)
        return false;

    for (float val : data)
    {
        if (val < 0.0f || val > 1.0f)
            return false;
    }

    return true;
}

PYBIND11_MODULE(sdf_core, m)
{
    m.doc() = "Simple SDF C++ extension with updated algorithm";

    m.def("compute_single_sdf", &compute_simple_sdf,
          "Compute SDF for a single image",
          py::arg("image_data"), py::arg("width"), py::arg("height"),
          py::arg("threshold") = 0.5f, py::arg("normalize") = true, py::arg("max_distance") = 100);

    m.def("blend_two_sdfs", &blend_two_sdfs,
          "Blend two SDF images using the corrected algorithm",
          py::arg("sdf_a"), py::arg("sdf_b"), py::arg("width"), py::arg("height"));

    m.def("blend_multiple_sdfs", &blend_multiple_sdfs,
          "Blend multiple SDF images using adjacent frame blending",
          py::arg("sdf_images"), py::arg("width"), py::arg("height"));

    m.def("get_version", &get_version,
          "Get version information");

    m.def("validate_image", &validate_image,
          "Validate image data",
          py::arg("data"), py::arg("width"), py::arg("height"));
}
