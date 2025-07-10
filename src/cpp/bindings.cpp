/**
 * Python绑定接口
 * 
 * 使用pybind11将C++算法暴露给Python
 * 提供与Python版本兼容的接口
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "sdf_core.h"
#include "sdf_algorithms.h"

namespace py = pybind11;

PYBIND11_MODULE(sdf_core, m) {
    m.doc() = "SDF工具C++扩展模块 - 高性能8SSEDT算法实现";
    
    // 版本信息
    m.attr("__version__") = "1.0.0";
    
    // 导出SDFCore类
    py::class_<sdf::SDFCore>(m, "SDFCore")
        .def(py::init<>())
        .def("compute_single_sdf", &sdf::SDFCore::computeSingleSDF,
             "计算单张图像的SDF",
             py::arg("image_data"), py::arg("width"), py::arg("height"),
             py::arg("threshold") = 0.5f, py::arg("normalize") = true)
        .def("compute_multi_sdf", &sdf::SDFCore::computeMultiSDF,
             "计算多张图像的混合SDF",
             py::arg("images"), py::arg("angles"), py::arg("width"), py::arg("height"),
             py::arg("threshold") = 0.5f, py::arg("normalize") = true,
             py::arg("blend_mode") = "sdf_blend")
        .def("blend_sdfs", &sdf::SDFCore::blendSDFs,
             "混合多个SDF图像",
             py::arg("sdf_images"), py::arg("angles"), py::arg("width"), py::arg("height"),
             py::arg("blend_mode") = "sdf_blend")
        .def("generate_lighting_preview", &sdf::SDFCore::generateLightingPreview,
             "生成光照效果预览",
             py::arg("sdf_data"), py::arg("light_angle"), py::arg("width"), py::arg("height"))
        .def("get_version_info", &sdf::SDFCore::getVersionInfo,
             "获取版本信息")
        .def("validate_image_data", &sdf::SDFCore::validateImageData,
             "验证图像数据有效性",
             py::arg("data"), py::arg("width"), py::arg("height"));
    
    // 导出数据结构
    py::class_<sdf::ImageInfo>(m, "ImageInfo")
        .def(py::init<int, int, int>(), py::arg("width"), py::arg("height"), py::arg("channels") = 1)
        .def_readwrite("width", &sdf::ImageInfo::width)
        .def_readwrite("height", &sdf::ImageInfo::height)
        .def_readwrite("channels", &sdf::ImageInfo::channels)
        .def("size", &sdf::ImageInfo::size);
    
    py::class_<sdf::SDFParams>(m, "SDFParams")
        .def(py::init<float, bool, bool, int, const std::string&>(),
             py::arg("threshold") = 0.5f, py::arg("normalize") = true, py::arg("invert") = false,
             py::arg("max_distance") = 100, py::arg("direction") = "both")
        .def_readwrite("threshold", &sdf::SDFParams::threshold)
        .def_readwrite("normalize", &sdf::SDFParams::normalize)
        .def_readwrite("invert", &sdf::SDFParams::invert)
        .def_readwrite("max_distance", &sdf::SDFParams::max_distance)
        .def_readwrite("direction", &sdf::SDFParams::direction);
    
    py::class_<sdf::BlendParams>(m, "BlendParams")
        .def(py::init<const std::string&>(), py::arg("mode") = "sdf_blend")
        .def_readwrite("mode", &sdf::BlendParams::mode)
        .def_readwrite("weights", &sdf::BlendParams::weights);
    
    // 导出EightSSEDT算法类的静态方法
    py::class_<sdf::EightSSEDT>(m, "EightSSEDT")
        .def_static("compute_sdf", &sdf::EightSSEDT::computeSDF,
                   "使用8SSEDT算法计算单张图像的SDF",
                   py::arg("input_data"), py::arg("info"), py::arg("params") = sdf::SDFParams())
        .def_static("compute_multi_sdf", &sdf::EightSSEDT::computeMultiSDF,
                   "使用8SSEDT算法计算多张图像的混合SDF",
                   py::arg("images"), py::arg("angles"), py::arg("info"), py::arg("params") = sdf::SDFParams());
    
    // 便捷函数 - 直接暴露给Python使用
    m.def("compute_single_sdf", [](const std::vector<float>& image_data,
                                  int width, int height,
                                  float threshold,
                                  bool normalize) {
        sdf::SDFCore core;
        return core.computeSingleSDF(image_data, width, height, threshold, normalize);
    }, "计算单张图像的SDF（便捷函数）",
       py::arg("image_data"), py::arg("width"), py::arg("height"),
       py::arg("threshold") = 0.5f, py::arg("normalize") = true);
    
    m.def("compute_multi_sdf", [](const std::vector<std::vector<float>>& images,
                                 const std::vector<float>& angles,
                                 int width, int height,
                                 float threshold,
                                 bool normalize,
                                 const std::string& blend_mode) {
        sdf::SDFCore core;
        return core.computeMultiSDF(images, angles, width, height, threshold, normalize, blend_mode);
    }, "计算多张图像的混合SDF（便捷函数）",
       py::arg("images"), py::arg("angles"), py::arg("width"), py::arg("height"),
       py::arg("threshold") = 0.5f, py::arg("normalize") = true,
       py::arg("blend_mode") = "sdf_blend");
    
    m.def("blend_sdfs", [](const std::vector<std::vector<float>>& sdf_images,
                          const std::vector<float>& angles,
                          int width, int height,
                          const std::string& blend_mode) {
        sdf::SDFCore core;
        return core.blendSDFs(sdf_images, angles, width, height, blend_mode);
    }, "混合多个SDF图像（便捷函数）",
       py::arg("sdf_images"), py::arg("angles"), py::arg("width"), py::arg("height"),
       py::arg("blend_mode") = "sdf_blend");
    
    m.def("generate_lighting_preview", [](const std::vector<float>& sdf_data,
                                         float light_angle,
                                         int width, int height) {
        sdf::SDFCore core;
        return core.generateLightingPreview(sdf_data, light_angle, width, height);
    }, "生成光照效果预览（便捷函数）",
       py::arg("sdf_data"), py::arg("light_angle"), py::arg("width"), py::arg("height"));
    
    // 工具函数
    m.def("get_version", []() {
        sdf::SDFCore core;
        return core.getVersionInfo();
    }, "获取C++扩展版本信息");
    
    m.def("validate_image", [](const std::vector<float>& data, int width, int height) {
        sdf::SDFCore core;
        return core.validateImageData(data, width, height);
    }, "验证图像数据有效性",
       py::arg("data"), py::arg("width"), py::arg("height"));
    
    // 常量定义
    m.attr("PI") = sdf::PI;
    m.attr("EPSILON") = sdf::EPSILON;
    
    // 支持的混合模式
    py::list blend_modes;
    blend_modes.append("sdf_blend");
    blend_modes.append("weighted");
    blend_modes.append("average");
    blend_modes.append("max");
    blend_modes.append("min");
    m.attr("SUPPORTED_BLEND_MODES") = blend_modes;
    
    // 支持的SDF计算方向
    py::list sdf_directions;
    sdf_directions.append("both");
    sdf_directions.append("inside");
    sdf_directions.append("outside");
    m.attr("SUPPORTED_SDF_DIRECTIONS") = sdf_directions;
    
    // 异常处理
    py::register_exception<std::runtime_error>(m, "SDFError");
    
    // 模块信息
    m.def("get_build_info", []() {
        py::dict info;
        info["version"] = "1.0.0";
        info["algorithm"] = "8SSEDT";
        info["blend_algorithm"] = "SDF Pairwise Blending";
        info["build_date"] = __DATE__;
        info["build_time"] = __TIME__;
        return info;
    }, "获取构建信息");
}
