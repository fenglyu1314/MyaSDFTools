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
        for (int i = 0; i < width * height; ++i)
        {
            result[i] = 0.5f; // boundary baseline
            
            if (binary[i])
            {
                // Inside region: 0.5 to 0.0 (center darkest)
                float normalized_inside = inside_dist[i] / inside_max * 0.5f;
                result[i] = 0.5f - normalized_inside;
            }
            else
            {
                // Outside region: 0.5 to 1.0 (farthest brightest)
                float normalized_outside = outside_dist[i] / outside_max * 0.5f;
                result[i] = 0.5f + normalized_outside;
            }
            
            // Ensure result is in [0, 1] range
            result[i] = std::max(0.0f, std::min(1.0f, result[i]));
        }
    }
    else
    {
        // Use raw distance values when not normalizing
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

    m.def("get_version", &get_version,
          "Get version information");

    m.def("validate_image", &validate_image,
          "Validate image data",
          py::arg("data"), py::arg("width"), py::arg("height"));
}
