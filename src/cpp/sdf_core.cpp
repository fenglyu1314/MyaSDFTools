/**
 * SDF核心处理类实现
 * 
 * 提供Python接口的主要入口点
 * 封装8SSEDT算法和SDF混合算法
 */

#include "sdf_core.h"
#include "sdf_algorithms.h"
#include <iostream>
#include <stdexcept>

namespace sdf {

SDFCore::SDFCore() {
    std::cout << "SDF核心模块初始化完成" << std::endl;
}

SDFCore::~SDFCore() {
    // 清理资源
}

std::vector<float> SDFCore::computeSingleSDF(const std::vector<float>& image_data,
                                            int width, int height,
                                            float threshold,
                                            bool normalize) {
    try {
        // 验证输入参数
        if (image_data.empty()) {
            throw std::runtime_error("输入图像数据不能为空");
        }
        
        if (width <= 0 || height <= 0) {
            throw std::runtime_error("图像尺寸必须大于0");
        }
        
        if (static_cast<int>(image_data.size()) != width * height) {
            throw std::runtime_error("图像数据大小与尺寸不匹配");
        }
        
        if (threshold < 0.0f || threshold > 1.0f) {
            throw std::runtime_error("阈值必须在[0,1]范围内");
        }
        
        // 创建图像信息和参数
        ImageInfo info(width, height, 1);
        SDFParams params(threshold, normalize, false, 100, "both");
        
        // 调用8SSEDT算法
        auto result = EightSSEDT::computeSDF(image_data, info, params);
        
        // 返回结果
        return *result;
        
    } catch (const std::exception& e) {
        std::cerr << "SDF计算错误: " << e.what() << std::endl;
        throw;
    }
}

std::vector<float> SDFCore::computeMultiSDF(const std::vector<std::vector<float>>& images,
                                           const std::vector<float>& angles,
                                           int width, int height,
                                           float threshold,
                                           bool normalize,
                                           const std::string& blend_mode) {
    try {
        // 验证输入参数
        if (images.empty()) {
            throw std::runtime_error("图像列表不能为空");
        }
        
        if (images.size() != angles.size()) {
            throw std::runtime_error("图像数量必须与角度数量相同");
        }
        
        if (width <= 0 || height <= 0) {
            throw std::runtime_error("图像尺寸必须大于0");
        }
        
        // 验证每张图像的尺寸
        int expected_size = width * height;
        for (size_t i = 0; i < images.size(); ++i) {
            if (static_cast<int>(images[i].size()) != expected_size) {
                throw std::runtime_error("第" + std::to_string(i+1) + "张图像尺寸不匹配");
            }
        }
        
        // 创建图像信息和参数
        ImageInfo info(width, height, 1);
        SDFParams params(threshold, normalize, false, 100, "both");
        
        // 转换图像数据格式
        std::vector<ImageData> image_list;
        image_list.reserve(images.size());
        for (const auto& img : images) {
            image_list.push_back(img);
        }
        
        // 调用多图像SDF算法
        auto result = EightSSEDT::computeMultiSDF(image_list, angles, info, params);
        
        // 返回结果
        return *result;
        
    } catch (const std::exception& e) {
        std::cerr << "多图像SDF计算错误: " << e.what() << std::endl;
        throw;
    }
}

std::vector<float> SDFCore::blendSDFs(const std::vector<std::vector<float>>& sdf_images,
                                     const std::vector<float>& angles,
                                     int width, int height,
                                     const std::string& blend_mode) {
    try {
        // 验证输入参数
        if (sdf_images.empty()) {
            throw std::runtime_error("SDF图像列表不能为空");
        }
        
        if (sdf_images.size() != angles.size()) {
            throw std::runtime_error("SDF图像数量必须与角度数量相同");
        }
        
        // 创建图像信息
        ImageInfo info(width, height, 1);
        
        // 转换为ImagePtr格式
        std::vector<ImagePtr> sdf_ptrs;
        sdf_ptrs.reserve(sdf_images.size());
        for (const auto& sdf : sdf_images) {
            auto ptr = std::make_shared<ImageData>(sdf);
            sdf_ptrs.push_back(ptr);
        }
        
        // 根据混合模式选择算法
        ImagePtr result;
        if (blend_mode == "sdf_blend") {
            // 使用SDF特性混合算法（推荐）
            result = EightSSEDT::blendSDFPairwise(sdf_ptrs, angles, info);
        } else {
            // 其他混合模式可以在这里添加
            throw std::runtime_error("不支持的混合模式: " + blend_mode);
        }
        
        return *result;
        
    } catch (const std::exception& e) {
        std::cerr << "SDF混合错误: " << e.what() << std::endl;
        throw;
    }
}

std::vector<float> SDFCore::generateLightingPreview(const std::vector<float>& sdf_data,
                                                   float light_angle,
                                                   int width, int height) {
    try {
        // 验证输入参数
        if (sdf_data.empty()) {
            throw std::runtime_error("SDF数据不能为空");
        }
        
        if (static_cast<int>(sdf_data.size()) != width * height) {
            throw std::runtime_error("SDF数据大小与尺寸不匹配");
        }
        
        // 创建结果图像
        std::vector<float> result(sdf_data.size());
        
        // 简单的光照效果实现
        // 这里可以根据需要实现更复杂的光照算法
        float angle_rad = utils::radians(light_angle);
        float cos_angle = std::cos(angle_rad);
        float sin_angle = std::sin(angle_rad);
        
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                int idx = y * width + x;
                float sdf_value = sdf_data[idx];
                
                // 基于SDF值和光照角度计算光照效果
                // 这是一个简化的实现，实际可能需要更复杂的算法
                float lighting = sdf_value;
                
                // 应用光照方向影响
                float direction_factor = cos_angle * 0.5f + 0.5f;
                lighting = lighting * direction_factor;
                
                result[idx] = utils::clamp(lighting, 0.0f, 1.0f);
            }
        }
        
        return result;
        
    } catch (const std::exception& e) {
        std::cerr << "光照预览生成错误: " << e.what() << std::endl;
        throw;
    }
}

std::string SDFCore::getVersionInfo() {
    return "SDF Core C++ v1.0.0 - 8SSEDT算法实现";
}

bool SDFCore::validateImageData(const std::vector<float>& data, int width, int height) {
    if (data.empty()) {
        return false;
    }
    
    if (width <= 0 || height <= 0) {
        return false;
    }
    
    if (static_cast<int>(data.size()) != width * height) {
        return false;
    }
    
    // 检查数据范围
    for (float value : data) {
        if (value < 0.0f || value > 1.0f) {
            return false;
        }
    }
    
    return true;
}

} // namespace sdf
