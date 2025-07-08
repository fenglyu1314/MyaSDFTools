#pragma once

#include "common.h"
#include "sdf_algorithms.h"

namespace sdf {

/**
 * SDF核心处理类 - Python接口的主要入口
 */
class SDFCore {
public:
    SDFCore();
    ~SDFCore();

    /**
     * 从灰度图像数据计算SDF
     * @param image_data 图像数据 (numpy array转换而来)
     * @param width 图像宽度
     * @param height 图像高度
     * @param threshold 二值化阈值 (0.0-1.0)
     * @param normalize 是否归一化输出
     * @return SDF结果数据
     */
    std::vector<float> computeSingleSDF(const std::vector<float>& image_data,
                                       int width, int height,
                                       float threshold = 0.5f,
                                       bool normalize = true);

    /**
     * 从多张图像计算混合SDF
     * @param images_data 多张图像数据列表
     * @param angles 对应的光照角度列表
     * @param width 图像宽度
     * @param height 图像高度
     * @param threshold 二值化阈值
     * @param normalize 是否归一化输出
     * @return 混合SDF结果数据
     */
    std::vector<float> computeMultiSDF(const std::vector<std::vector<float>>& images_data,
                                      const std::vector<float>& angles,
                                      int width, int height,
                                      float threshold = 0.5f,
                                      bool normalize = true);

    /**
     * SDF光照效果预览
     * @param sdf_data SDF数据
     * @param light_angle 光照角度 (0-360度)
     * @param width 图像宽度
     * @param height 图像高度
     * @return 预览效果图像数据
     */
    std::vector<float> previewLighting(const std::vector<float>& sdf_data,
                                      float light_angle,
                                      int width, int height);

    /**
     * 获取最后一次计算的性能信息
     * @return 计算时间(毫秒)
     */
    double getLastComputationTime() const;

    /**
     * 设置多线程数量
     * @param num_threads 线程数量 (0为自动检测)
     */
    void setNumThreads(int num_threads);

    /**
     * 获取算法版本信息
     */
    std::string getVersionInfo() const;

private:
    double last_computation_time_;
    int num_threads_;
    
    // 内部辅助函数
    ImageData convertToImageData(const std::vector<float>& input_data);
    std::vector<float> convertFromImageData(const ImageData& image_data);
    
    // 验证输入参数
    bool validateInput(int width, int height, size_t data_size) const;
    bool validateAngles(const std::vector<float>& angles) const;
};

/**
 * 工具函数 - 供Python直接调用
 */
namespace utils {
    /**
     * 图像预处理 - 转换为灰度并归一化
     */
    std::vector<float> preprocessImage(const std::vector<uint8_t>& rgb_data,
                                      int width, int height, int channels);

    /**
     * 图像后处理 - 转换为可显示格式
     */
    std::vector<uint8_t> postprocessImage(const std::vector<float>& float_data,
                                         int width, int height);

    /**
     * 自动计算等角度分布
     */
    std::vector<float> calculateEvenAngles(int num_images);

    /**
     * 验证角度范围和分布
     */
    bool validateAngleDistribution(const std::vector<float>& angles);
}

} // namespace sdf
