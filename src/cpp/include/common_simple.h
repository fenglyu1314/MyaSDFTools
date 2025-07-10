#pragma once

#include <vector>
#include <memory>
#include <cmath>
#include <algorithm>
#include <chrono>
#include <string>
#include <limits>
#include <cstring>

namespace sdf {

// Basic data types
using ImageData = std::vector<float>;
using ImagePtr = std::shared_ptr<ImageData>;

// Image information structure
struct ImageInfo {
    int width;
    int height;
    int channels;
    
    ImageInfo(int w = 0, int h = 0, int c = 1) 
        : width(w), height(h), channels(c) {}
    
    size_t size() const {
        return static_cast<size_t>(width) * height * channels;
    }
};

// 2D point structure
struct Point2D {
    int x, y;
    
    Point2D(int px = 0, int py = 0) : x(px), y(py) {}
    
    float distanceTo(const Point2D& other) const {
        float dx = static_cast<float>(x - other.x);
        float dy = static_cast<float>(y - other.y);
        return std::sqrt(dx * dx + dy * dy);
    }
    
    int distanceSquaredTo(const Point2D& other) const {
        int dx = x - other.x;
        int dy = y - other.y;
        return dx * dx + dy * dy;
    }
};

// SDF computation parameters
struct SDFParams {
    float threshold;         // Binarization threshold (0.0-1.0)
    bool normalize;          // Whether to normalize to [0,1]
    bool invert;            // Whether to invert inside/outside
    int max_distance;       // Maximum distance limit (pixels)
    std::string direction;  // Computation direction ("both", "inside", "outside")
    
    SDFParams(float thresh = 0.5f, bool norm = true, bool inv = false, 
              int max_dist = 100, const std::string& dir = "both")
        : threshold(thresh), normalize(norm), invert(inv), 
          max_distance(max_dist), direction(dir) {}
};

// Blend parameters
struct BlendParams {
    std::string mode;           // Blend mode ("sdf_blend", "weighted", "average", "max", "min")
    std::vector<float> weights; // Weight list (for weighted mode)
    
    BlendParams(const std::string& blend_mode = "sdf_blend")
        : mode(blend_mode) {}
};

// Distance grid structure (for 8SSEDT algorithm)
struct DistanceGrid {
    std::vector<Point2D> grid;  // Nearest point grid
    std::vector<int> distances; // Distance squared grid
    int width, height;
    
    DistanceGrid(int w, int h) : width(w), height(h) {
        grid.resize(w * h);
        distances.resize(w * h);
        reset();
    }
    
    void reset() {
        const int max_dist = std::numeric_limits<int>::max();
        for (int i = 0; i < width * height; ++i) {
            grid[i] = Point2D(-1, -1);  // Invalid point
            distances[i] = max_dist;
        }
    }
    
    Point2D& getPoint(int x, int y) {
        return grid[y * width + x];
    }
    
    const Point2D& getPoint(int x, int y) const {
        return grid[y * width + x];
    }
    
    int& getDistance(int x, int y) {
        return distances[y * width + x];
    }
    
    const int& getDistance(int x, int y) const {
        return distances[y * width + x];
    }
    
    bool isValid(int x, int y) const {
        return x >= 0 && x < width && y >= 0 && y < height;
    }
};

// Performance timer
class Timer {
private:
    std::chrono::high_resolution_clock::time_point start_time;
    
public:
    void start() {
        start_time = std::chrono::high_resolution_clock::now();
    }
    
    double elapsed() const {
        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
            end_time - start_time);
        return duration.count() / 1000.0; // Return milliseconds
    }
};

// Utility functions
namespace utils {
    // Safe array access
    inline float getPixel(const ImageData& data, int x, int y, int width, int height) {
        if (x < 0 || x >= width || y < 0 || y >= height) {
            return 0.0f;
        }
        return data[y * width + x];
    }
    
    // Set pixel value
    inline void setPixel(ImageData& data, int x, int y, int width, float value) {
        if (x >= 0 && x < width && y >= 0) {
            data[y * width + x] = value;
        }
    }
    
    // Value clamping
    template<typename T>
    inline T clamp(T value, T min_val, T max_val) {
        return std::max(min_val, std::min(value, max_val));
    }
    
    // Linear interpolation
    inline float lerp(float a, float b, float t) {
        return a + t * (b - a);
    }

    // Angle conversion
    inline float radians(float degrees) {
        return degrees * 3.14159265359f / 180.0f;
    }

    inline float degrees(float radians) {
        return radians * 180.0f / 3.14159265359f;
    }
}

// Common constants
constexpr float PI = 3.14159265359f;
constexpr float EPSILON = 1e-6f;

} // namespace sdf
