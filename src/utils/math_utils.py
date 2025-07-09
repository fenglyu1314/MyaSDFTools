#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数学工具

提供数学计算相关的工具函数
"""

import math
import numpy as np
from typing import List, Tuple, Union

class MathUtils:
    """数学工具类"""
    
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """
        将值限制在指定范围内
        
        Args:
            value: 输入值
            min_val: 最小值
            max_val: 最大值
            
        Returns:
            限制后的值
        """
        return max(min_val, min(value, max_val))
    
    @staticmethod
    def lerp(a: float, b: float, t: float) -> float:
        """
        线性插值
        
        Args:
            a: 起始值
            b: 结束值
            t: 插值参数 (0.0-1.0)
            
        Returns:
            插值结果
        """
        return a + t * (b - a)
    
    @staticmethod
    def smoothstep(edge0: float, edge1: float, x: float) -> float:
        """
        平滑步进函数
        
        Args:
            edge0: 下边界
            edge1: 上边界
            x: 输入值
            
        Returns:
            平滑插值结果
        """
        t = MathUtils.clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)
    
    @staticmethod
    def normalize_angle(angle: float) -> float:
        """
        将角度归一化到[0, 360)范围
        
        Args:
            angle: 输入角度（度）
            
        Returns:
            归一化后的角度
        """
        while angle < 0:
            angle += 360
        while angle >= 360:
            angle -= 360
        return angle
    
    @staticmethod
    def angle_difference(angle1: float, angle2: float) -> float:
        """
        计算两个角度之间的最小差值
        
        Args:
            angle1: 角度1（度）
            angle2: 角度2（度）
            
        Returns:
            角度差值 (-180, 180]
        """
        diff = MathUtils.normalize_angle(angle2 - angle1)
        if diff > 180:
            diff -= 360
        return diff
    
    @staticmethod
    def degrees_to_radians(degrees: float) -> float:
        """角度转弧度"""
        return degrees * math.pi / 180.0
    
    @staticmethod
    def radians_to_degrees(radians: float) -> float:
        """弧度转角度"""
        return radians * 180.0 / math.pi
    
    @staticmethod
    def distance_2d(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """
        计算两点间的欧几里得距离
        
        Args:
            p1: 点1 (x, y)
            p2: 点2 (x, y)
            
        Returns:
            距离
        """
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return math.sqrt(dx * dx + dy * dy)
    
    @staticmethod
    def manhattan_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """
        计算曼哈顿距离
        
        Args:
            p1: 点1 (x, y)
            p2: 点2 (x, y)
            
        Returns:
            曼哈顿距离
        """
        return abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])
    
    @staticmethod
    def calculate_even_distribution(count: int, total_range: float = 180.0) -> List[float]:
        """
        计算均匀分布的值 - 默认180度分布

        Args:
            count: 数量
            total_range: 总范围（默认180度）

        Returns:
            均匀分布的值列表
        """
        if count <= 0:
            return []

        if count == 1:
            return [0.0]

        step = total_range / count
        return [i * step for i in range(count)]
    
    @staticmethod
    def gaussian_kernel_1d(size: int, sigma: float) -> np.ndarray:
        """
        生成1D高斯核
        
        Args:
            size: 核大小
            sigma: 标准差
            
        Returns:
            高斯核
        """
        kernel = np.zeros(size)
        center = size // 2
        
        for i in range(size):
            x = i - center
            kernel[i] = math.exp(-(x * x) / (2 * sigma * sigma))
        
        # 归一化
        kernel = kernel / np.sum(kernel)
        return kernel
    
    @staticmethod
    def gaussian_kernel_2d(size: int, sigma: float) -> np.ndarray:
        """
        生成2D高斯核
        
        Args:
            size: 核大小
            sigma: 标准差
            
        Returns:
            2D高斯核
        """
        kernel = np.zeros((size, size))
        center = size // 2
        
        for i in range(size):
            for j in range(size):
                x = i - center
                y = j - center
                kernel[i, j] = math.exp(-(x * x + y * y) / (2 * sigma * sigma))
        
        # 归一化
        kernel = kernel / np.sum(kernel)
        return kernel
    
    @staticmethod
    def bilinear_interpolation(image: np.ndarray, x: float, y: float) -> float:
        """
        双线性插值
        
        Args:
            image: 输入图像
            x: x坐标
            y: y坐标
            
        Returns:
            插值结果
        """
        height, width = image.shape[:2]
        
        # 边界检查
        x = MathUtils.clamp(x, 0, width - 1)
        y = MathUtils.clamp(y, 0, height - 1)
        
        # 获取整数坐标
        x0 = int(x)
        y0 = int(y)
        x1 = min(x0 + 1, width - 1)
        y1 = min(y0 + 1, height - 1)
        
        # 获取小数部分
        fx = x - x0
        fy = y - y0
        
        # 双线性插值
        top = MathUtils.lerp(image[y0, x0], image[y0, x1], fx)
        bottom = MathUtils.lerp(image[y1, x0], image[y1, x1], fx)
        
        return MathUtils.lerp(top, bottom, fy)
    
    @staticmethod
    def compute_gradient(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        计算图像梯度
        
        Args:
            image: 输入图像
            
        Returns:
            (grad_x, grad_y) 梯度
        """
        grad_y, grad_x = np.gradient(image)
        return grad_x, grad_y
    
    @staticmethod
    def compute_gradient_magnitude(grad_x: np.ndarray, grad_y: np.ndarray) -> np.ndarray:
        """
        计算梯度幅值
        
        Args:
            grad_x: x方向梯度
            grad_y: y方向梯度
            
        Returns:
            梯度幅值
        """
        return np.sqrt(grad_x**2 + grad_y**2)
    
    @staticmethod
    def compute_gradient_direction(grad_x: np.ndarray, grad_y: np.ndarray) -> np.ndarray:
        """
        计算梯度方向
        
        Args:
            grad_x: x方向梯度
            grad_y: y方向梯度
            
        Returns:
            梯度方向（弧度）
        """
        return np.arctan2(grad_y, grad_x)
    
    @staticmethod
    def safe_divide(a: Union[float, np.ndarray], 
                   b: Union[float, np.ndarray], 
                   default: float = 0.0) -> Union[float, np.ndarray]:
        """
        安全除法，避免除零错误
        
        Args:
            a: 被除数
            b: 除数
            default: 除零时的默认值
            
        Returns:
            除法结果
        """
        if isinstance(b, np.ndarray):
            result = np.where(np.abs(b) > 1e-8, a / b, default)
        else:
            result = a / b if abs(b) > 1e-8 else default
        
        return result
    
    @staticmethod
    def moving_average(data: List[float], window_size: int) -> List[float]:
        """
        计算移动平均
        
        Args:
            data: 输入数据
            window_size: 窗口大小
            
        Returns:
            移动平均结果
        """
        if window_size <= 0 or window_size > len(data):
            return data.copy()
        
        result = []
        for i in range(len(data)):
            start = max(0, i - window_size // 2)
            end = min(len(data), i + window_size // 2 + 1)
            avg = sum(data[start:end]) / (end - start)
            result.append(avg)
        
        return result
    
    @staticmethod
    def find_peaks(data: List[float], min_height: float = 0.0, min_distance: int = 1) -> List[int]:
        """
        查找峰值
        
        Args:
            data: 输入数据
            min_height: 最小高度
            min_distance: 最小距离
            
        Returns:
            峰值索引列表
        """
        peaks = []
        
        for i in range(1, len(data) - 1):
            if (data[i] > data[i-1] and data[i] > data[i+1] and 
                data[i] >= min_height):
                
                # 检查与已有峰值的距离
                valid = True
                for peak_idx in peaks:
                    if abs(i - peak_idx) < min_distance:
                        valid = False
                        break
                
                if valid:
                    peaks.append(i)
        
        return peaks
