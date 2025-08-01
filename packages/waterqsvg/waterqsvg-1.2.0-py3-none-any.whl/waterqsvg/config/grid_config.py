#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能网格配置模块
从AutoReportV3完整迁移智能网格生成算法
支持基于地理距离的自适应网格计算
"""
import logging
import numpy as np
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

# ================== 智能网格配置 ==================
# 🎯 与AutoReportV3完全一致的网格配置

GRID_CONFIG = {
    'adaptive_grid': {
        'enabled': True,
        'desired_resolution': 0.00002,  # 度/像素 (约2米)，固定空间分辨率
        'min_pixels': 50,               # 最小像素数，防止极小区域
        'max_pixels': 2000,             # 最大像素数，防止内存溢出
        'margin_factor': 0.01,          # 1%边界扩展因子
        'preserve_aspect_ratio': True,  # 保持真实地理比例
        'description': '基于地理距离的智能自适应网格（与AutoReportV3一致）'
    },
    'fixed_grid': {
        'enabled': False,               # 兼容模式，向后兼容
        'default_resolution': 300,      # 固定分辨率（与AutoReportV3一致）
        'description': '固定分辨率网格（向后兼容模式，与AutoReportV3一致）'
    }
}

def calculate_adaptive_grid_size(bounds: list, config: Dict[str, Any] = None) -> Tuple[int, int]:
    """
    根据地理范围计算智能网格尺寸
    完全复制AutoReportV3的adaptive grid算法 (maps.py:765-784)
    
    Args:
        bounds: 边界范围 [x_min, y_min, x_max, y_max] (经度、纬度)
        config: 网格配置，如果为None则使用默认配置
        
    Returns:
        (lon_pixels, lat_pixels): 经度和纬度方向的像素数
    """
    if config is None:
        config = GRID_CONFIG['adaptive_grid']
    
    x_min, y_min, x_max, y_max = bounds
    
    # 计算地理范围 - 保持实际地理比例
    lon_range = x_max - x_min
    lat_range = y_max - y_min
    aspect_ratio = lon_range / lat_range
    
    # 🎯 AutoReportV3的核心算法：
    # 根据地理范围和期望空间分辨率（单位：度/像素）动态计算网格分辨率
    # 这样可以保证无论地理范围大小，插值图像的空间分辨率都能满足需求
    # 避免大范围时画面变糊、小范围时像素过多浪费资源
    desired_resolution = config['desired_resolution']  # 0.00002度/像素（约2米/像素）
    
    lat_pixels = int(np.ceil(lat_range / desired_resolution))
    lon_pixels = int(np.ceil(lon_range / desired_resolution))
    
    # 限制最大和最小像素数，防止极端情况
    min_pixels = config['min_pixels']
    max_pixels = config['max_pixels']
    
    lat_pixels = min(max(lat_pixels, min_pixels), max_pixels)
    lon_pixels = min(max(lon_pixels, min_pixels), max_pixels)
    
    logger.info(f"智能网格计算: {lat_pixels} x {lon_pixels} (长宽比: {aspect_ratio:.3f})")
    logger.debug(f"地理范围: 经度 {lon_range:.6f}°, 纬度 {lat_range:.6f}°")
    logger.debug(f"空间分辨率: {desired_resolution:.6f}度/像素")
    
    return lon_pixels, lat_pixels

def create_adaptive_grid(bounds: list, config: Dict[str, Any] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    创建智能自适应插值网格
    完全复制AutoReportV3的网格生成算法 (maps.py:783-784)
    
    Args:
        bounds: 边界范围 [x_min, y_min, x_max, y_max]
        config: 网格配置
        
    Returns:
        (grid_x, grid_y): 网格坐标数组
    """
    if config is None:
        config = GRID_CONFIG['adaptive_grid']
    
    x_min, y_min, x_max, y_max = bounds
    
    # 计算智能网格尺寸
    lon_pixels, lat_pixels = calculate_adaptive_grid_size(bounds, config)
    
    logger.info(f"创建智能网格: {lat_pixels} x {lon_pixels}")
    
    # 🎯 AutoReportV3的网格生成方法：
    # 使用numpy的mgrid生成等间隔网格
    # 这里的`*1j`是numpy的复数语法，表示生成等间隔的复数个点（即像素数）
    # 例如lat_pixels*1j表示在纬度方向生成lat_pixels个点，lon_pixels*1j表示在经度方向生成lon_pixels个点
    # 这种写法常用于np.mgrid，等价于np.linspace(start, stop, num)，但能直接生成网格
    # 这里的j没有实际的虚数意义，只是numpy规定用来指定采样点数的语法糖
    grid_lat, grid_lon = np.mgrid[y_min:y_max:lat_pixels*1j, 
                                 x_min:x_max:lon_pixels*1j]
    
    logger.debug(f"网格形状: {grid_lon.shape}")
    
    return grid_lon, grid_lat

def apply_boundary_margin(bounds: list, config: Dict[str, Any] = None) -> list:
    """
    应用边界扩展
    复制AutoReportV3的边界扩展逻辑 (maps.py:750-758)
    
    Args:
        bounds: 原始边界范围 [x_min, y_min, x_max, y_max]
        config: 网格配置
        
    Returns:
        扩展后的边界范围
    """
    if config is None:
        config = GRID_CONFIG['adaptive_grid']
    
    x_min, y_min, x_max, y_max = bounds
    
    # 计算范围
    x_range = x_max - x_min
    y_range = y_max - y_min
    margin_factor = config['margin_factor']  # 1%边距
    
    # 添加边距
    x_min -= x_range * margin_factor
    x_max += x_range * margin_factor
    y_min -= y_range * margin_factor
    y_max += y_range * margin_factor
    
    expanded_bounds = [x_min, y_min, x_max, y_max]
    logger.debug(f"边界扩展: 原始 {bounds} -> 扩展后 {expanded_bounds}")
    
    return expanded_bounds

def create_fixed_grid(bounds: list, resolution: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    创建固定分辨率网格（向后兼容）
    保持waterqsvg原有的网格生成方式
    
    Args:
        bounds: 边界范围 [x_min, y_min, x_max, y_max]
        resolution: 固定分辨率
        
    Returns:
        (grid_x, grid_y): 网格坐标数组
    """
    x_min, y_min, x_max, y_max = bounds
    
    # 原有的固定分辨率方法
    grid_y, grid_x = np.mgrid[y_min:y_max:resolution*1j, x_min:x_max:resolution*1j]
    
    logger.debug(f"固定网格: {resolution}x{resolution}, 形状: {grid_x.shape}")
    
    return grid_x, grid_y

def get_grid_config() -> Dict[str, Any]:
    """
    获取当前的网格配置
    
    Returns:
        当前的网格配置字典
    """
    return GRID_CONFIG

def set_adaptive_grid_enabled(enabled: bool) -> None:
    """
    启用或禁用智能网格
    
    Args:
        enabled: 是否启用智能网格
    """
    GRID_CONFIG['adaptive_grid']['enabled'] = enabled
    GRID_CONFIG['fixed_grid']['enabled'] = not enabled
    
    mode = "智能自适应网格" if enabled else "固定分辨率网格"
    logger.info(f"网格模式已切换为: {mode}")

def update_spatial_resolution(resolution: float) -> None:
    """
    更新空间分辨率设置
    
    Args:
        resolution: 新的空间分辨率（度/像素）
    """
    GRID_CONFIG['adaptive_grid']['desired_resolution'] = resolution
    logger.info(f"空间分辨率已更新为: {resolution:.6f}度/像素")