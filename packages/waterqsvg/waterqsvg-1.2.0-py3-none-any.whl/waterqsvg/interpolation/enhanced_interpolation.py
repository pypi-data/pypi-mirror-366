#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强插值算法模块
集成边界检测和高分辨率插值，包含邻域分析功能
"""
import logging
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter, distance_transform_edt
from typing import Optional, Tuple, Union, Dict, Any

from .alpha_shape import compute_alpha_shape
from .convex_hull import compute_convex_hull, create_convex_hull_mask
from .density_boundary import compute_density_based_boundary
from .kriging_interpolation import kriging_interpolation, get_available_kriging_methods
from ..config.grid_config import (
    create_adaptive_grid, create_fixed_grid, apply_boundary_margin,
    get_grid_config, GRID_CONFIG
)

logger = logging.getLogger(__name__)

def enhanced_interpolation_with_boundary(
    data: Union[pd.DataFrame, np.ndarray],
    indicator_col: Optional[str] = None,
    grid_resolution: int = 200,
    method: str = 'linear',
    neighborhood_radius: int = 3,
    boundary_method: str = 'alpha_shape',
    fixed_bounds: Optional[list] = None,
    intelligent_grid: bool = True,
    spatial_resolution: Optional[float] = None,
    kriging_params: Optional[Dict[str, Any]] = None,
    kml_boundary_path: Optional[str] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Optional[np.ndarray]]:
    """
    基于智能边界的高分辨率插值，包含邻域分析
    🎯 扩展支持Universal Kriging和智能网格系统
    
    Args:
        data: 包含坐标和指标数据的DataFrame或numpy数组
        indicator_col: 指标列名，如果为None则使用第一个非坐标列
        grid_resolution: 网格分辨率（固定网格模式使用）
        method: 插值方法 ('universal_kriging'[默认], 'ordinary_kriging_spherical', 'ordinary_kriging_exponential')
        neighborhood_radius: 邻域分析半径(像素, 默认3与AutoReportV3一致)
        boundary_method: 边界检测方法 ('convex_hull', 'alpha_shape', 'density_based', 'kml')
        fixed_bounds: 固定的地理边界范围 [min_x, min_y, max_x, max_y]
        intelligent_grid: 是否使用智能自适应网格（推荐，与AutoReportV3一致）
        spatial_resolution: 自定义空间分辨率（度/像素），仅智能网格模式使用
        kriging_params: 克里金参数字典（用于高级配置）
        kml_boundary_path: KML边界文件路径（仅当boundary_method='kml'时使用）
        
    Returns:
        (插值结果, 网格X坐标, 网格Y坐标, 边界掩码, 边界点)
    """
    try:
        logger.info(f"开始增强插值计算，网格分辨率: {grid_resolution}, 边界方法: {boundary_method}")
        
        # 数据预处理
        points, values = _prepare_data(data, indicator_col)
        
        if len(points) < 3:
            logger.error("数据点数量不足（少于3个点）")
            return None, None, None, None, None
        
        # 计算边界
        boundary_points, boundary_mask_func = _compute_boundary(points, boundary_method, kml_boundary_path)
        
        # 确定插值范围
        bounds = _determine_interpolation_bounds(points, boundary_points, fixed_bounds, boundary_method)
        
        # 🎯 智能网格系统集成：根据配置选择网格生成方式
        if intelligent_grid:
            # 智能自适应网格模式（推荐，与AutoReportV3一致）
            grid_config = get_grid_config()['adaptive_grid'].copy()
            if spatial_resolution is not None:
                grid_config['desired_resolution'] = spatial_resolution
                logger.info(f"使用自定义空间分辨率: {spatial_resolution:.6f}度/像素")
            
            grid_x, grid_y = create_adaptive_grid(bounds, grid_config)
        else:
            # 固定分辨率网格模式（向后兼容）
            grid_x, grid_y = create_fixed_grid(bounds, grid_resolution)
        
        # 🎯 执行Universal Kriging插值（高精度方法）
        grid_values = _perform_kriging_interpolation(
            points, values, grid_x, grid_y, method, kriging_params,
            kml_boundary_path, boundary_method
        )
        
        # 应用边界掩码
        if boundary_mask_func is not None:
            boundary_mask = boundary_mask_func(grid_x, grid_y)
        else:
            boundary_mask = create_convex_hull_mask(grid_x, grid_y, boundary_points)
        
        # 应用边界掩码
        grid_values[~boundary_mask] = np.nan
        
        # 邻域分析和平滑
        grid_values = _apply_neighborhood_analysis(grid_values, boundary_mask, neighborhood_radius)
        
        logger.info(f"插值计算完成，有效网格点数: {np.sum(~np.isnan(grid_values))}")
        
        return grid_values, grid_x, grid_y, boundary_mask, boundary_points
        
    except Exception as e:
        logger.error(f"增强插值计算失败: {str(e)}")
        return None, None, None, None, None

def _prepare_data(data: Union[pd.DataFrame, np.ndarray], indicator_col: Optional[str]) -> Tuple[np.ndarray, np.ndarray]:
    """
    准备插值数据
    
    Args:
        data: 输入数据
        indicator_col: 指标列名
        
    Returns:
        (坐标点数组, 数值数组)
    """
    try:
        if isinstance(data, pd.DataFrame):
            # DataFrame处理
            if 'longitude' in data.columns and 'latitude' in data.columns:
                points = data[['longitude', 'latitude']].values
            elif 'lon' in data.columns and 'lat' in data.columns:
                points = data[['lon', 'lat']].values
            else:
                # 假设前两列是坐标
                points = data.iloc[:, :2].values
            
            # 获取指标数据
            if indicator_col is not None:
                if indicator_col not in data.columns:
                    raise ValueError(f"指定的指标列 {indicator_col} 不存在")
                values = data[indicator_col].values
            else:
                # 获取第一个非坐标列
                coord_cols = ['longitude', 'latitude', 'lon', 'lat', 'index']
                value_cols = [col for col in data.columns if col not in coord_cols]
                
                if len(value_cols) == 0:
                    raise ValueError("未找到有效的指标数据列")
                
                values = data[value_cols[0]].values
                logger.info(f"使用指标列: {value_cols[0]}")
        
        elif isinstance(data, np.ndarray):
            # numpy数组处理
            if data.shape[1] < 3:
                raise ValueError("数组至少需要3列（x, y, value）")
            
            points = data[:, :2]
            values = data[:, 2]
        
        else:
            raise ValueError("不支持的数据类型")
        
        # 数据验证和清洗
        valid_mask = ~(np.isnan(points).any(axis=1) | np.isnan(values))
        points = points[valid_mask]
        values = values[valid_mask]
        
        if len(points) == 0:
            raise ValueError("没有有效的数据点")
        
        logger.debug(f"数据准备完成，有效点数: {len(points)}")
        
        return points, values
        
    except Exception as e:
        logger.error(f"数据准备失败: {str(e)}")
        raise

def _compute_boundary(points: np.ndarray, boundary_method: str, kml_boundary_path: Optional[str] = None) -> Tuple[Optional[np.ndarray], Optional[callable]]:
    """
    计算边界
    
    Args:
        points: 点坐标数组
        boundary_method: 边界计算方法
        kml_boundary_path: KML边界文件路径
        
    Returns:
        (边界点, 边界掩码函数)
    """
    try:
        logger.debug(f"计算边界，方法: {boundary_method}")
        
        if boundary_method == 'kml':
            # KML边界方法
            if kml_boundary_path is None:
                logger.warning("KML边界方法需要提供kml_boundary_path参数，回退到alpha_shape")
                boundary_points = compute_alpha_shape(points)
                return boundary_points, None
            
            try:
                import os
                if not os.path.exists(kml_boundary_path):
                    logger.warning(f"KML文件不存在: {kml_boundary_path}，回退到alpha_shape")
                    boundary_points = compute_alpha_shape(points)
                    return boundary_points, None
                
                # 导入KML边界功能
                from .kml_boundary import get_kml_boundary_points, create_kml_boundary_mask
                
                # 获取KML边界点
                boundary_points = get_kml_boundary_points(kml_boundary_path)
                
                if boundary_points is not None:
                    logger.info(f"成功从KML文件获取边界点: {len(boundary_points)} 个")
                    
                    # 创建KML边界掩码函数
                    def kml_mask_func(grid_x, grid_y):
                        return create_kml_boundary_mask(grid_x, grid_y, kml_boundary_path)
                    
                    return boundary_points, kml_mask_func
                else:
                    logger.warning("无法从KML文件获取边界点，回退到alpha_shape")
                    boundary_points = compute_alpha_shape(points)
                    return boundary_points, None
                    
            except ImportError as e:
                logger.error(f"导入KML模块失败: {str(e)}，回退到alpha_shape")
                boundary_points = compute_alpha_shape(points)
                return boundary_points, None
            except Exception as e:
                logger.error(f"处理KML边界失败: {str(e)}，回退到alpha_shape")
                boundary_points = compute_alpha_shape(points)
                return boundary_points, None
                
        elif boundary_method == 'alpha_shape':
            boundary_points = compute_alpha_shape(points)
            return boundary_points, None
            
        elif boundary_method == 'density_based':
            boundary_mask_func = compute_density_based_boundary(points)
            return None, boundary_mask_func
            
        else:  # 默认使用凸包
            boundary_points = compute_convex_hull(points)
            return boundary_points, None
        
    except Exception as e:
        logger.warning(f"边界计算失败，使用凸包: {str(e)}")
        try:
            boundary_points = compute_convex_hull(points)
            return boundary_points, None
        except Exception as e2:
            logger.error(f"凸包计算也失败: {str(e2)}")
            return None, None

def _determine_interpolation_bounds(
    points: np.ndarray, 
    boundary_points: Optional[np.ndarray], 
    fixed_bounds: Optional[list],
    boundary_method: str = "alpha_shape"
) -> list:
    """
    确定插值范围
    
    Args:
        points: 数据点
        boundary_points: 边界点
        fixed_bounds: 固定边界
        boundary_method: 边界检测方法
        
    Returns:
        [min_x, min_y, max_x, max_y]
    """
    try:
        if fixed_bounds is not None:
            logger.debug("使用固定边界")
            return fixed_bounds
        
        # 使用边界点确定范围
        if boundary_points is not None and len(boundary_points) > 0:
            x_min, x_max = boundary_points[:, 0].min(), boundary_points[:, 0].max()
            y_min, y_max = boundary_points[:, 1].min(), boundary_points[:, 1].max()
        else:
            # 使用数据点范围
            x_min, x_max = points[:, 0].min(), points[:, 0].max()
            y_min, y_max = points[:, 1].min(), points[:, 1].max()
        
        # 🔧 修复KML边界外推差异：只在使用数据边界时才添加边界扩展（KML方法不需要扩展）
        # 参考AutoReportV3 maps.py:839的实现
        if boundary_method != "kml":
            # 添加边距（仅对非KML边界方法）
            x_range = x_max - x_min
            y_range = y_max - y_min
            margin_factor = 0.01  # 1%边距，减少边界扩展，避免边缘效应
            
            x_min -= x_range * margin_factor
            x_max += x_range * margin_factor
            y_min -= y_range * margin_factor
            y_max += y_range * margin_factor
            
            logger.debug(f"为{boundary_method}边界添加1%边距扩展")
        else:
            logger.debug("KML边界方法不添加边距扩展，严格按照KML定义的边界")
        
        bounds = [x_min, y_min, x_max, y_max]
        logger.debug(f"插值边界: {bounds}")
        
        return bounds
        
    except Exception as e:
        logger.error(f"确定插值范围失败: {str(e)}")
        # 使用数据点的最小边界
        x_min, x_max = points[:, 0].min(), points[:, 0].max()
        y_min, y_max = points[:, 1].min(), points[:, 1].max()
        return [x_min, y_min, x_max, y_max]

def _create_interpolation_grid(bounds: list, resolution: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    创建插值网格
    
    Args:
        bounds: 边界范围
        resolution: 网格分辨率
        
    Returns:
        (网格X坐标, 网格Y坐标)
    """
    try:
        x_min, y_min, x_max, y_max = bounds
        
        # 创建网格
        grid_y, grid_x = np.mgrid[y_min:y_max:resolution*1j, x_min:x_max:resolution*1j]
        
        logger.debug(f"创建网格，形状: {grid_x.shape}")
        
        return grid_x, grid_y
        
    except Exception as e:
        logger.error(f"创建插值网格失败: {str(e)}")
        raise

# 旧的scipy插值方法已被Universal Kriging替代
# 保留此注释用于版本追踪

def _apply_neighborhood_analysis(
    grid_values: np.ndarray, 
    boundary_mask: np.ndarray, 
    neighborhood_radius: int
) -> np.ndarray:
    """
    应用邻域分析和平滑
    
    Args:
        grid_values: 插值结果
        boundary_mask: 边界掩码
        neighborhood_radius: 邻域半径
        
    Returns:
        平滑后的插值结果
    """
    try:
        if neighborhood_radius <= 0:
            return grid_values
        
        logger.debug(f"应用邻域分析，半径: {neighborhood_radius}")
        
        # 找到有效数据
        valid_mask = ~np.isnan(grid_values) & boundary_mask
        
        if not np.any(valid_mask):
            logger.warning("没有有效数据进行邻域分析")
            return grid_values
        
        # 创建临时数组进行平滑
        temp_values = np.copy(grid_values)
        nan_mask = np.isnan(temp_values)
        
        # 使用最近邻有效值填充NaN区域
        if np.any(nan_mask):
            try:
                indices = distance_transform_edt(nan_mask, return_distances=False, return_indices=True)
                temp_values[nan_mask] = temp_values[tuple(indices[:, nan_mask])]
            except Exception as e:
                logger.debug(f"填充NaN值失败: {str(e)}")
        
        # 应用高斯滤波
        try:
            smoothed_values = gaussian_filter(temp_values, sigma=neighborhood_radius)
            # 只在有效区域应用平滑结果
            grid_values[valid_mask] = smoothed_values[valid_mask]
        except Exception as e:
            logger.warning(f"高斯平滑失败: {str(e)}")
        
        return grid_values
        
    except Exception as e:
        logger.warning(f"邻域分析失败: {str(e)}")
        return grid_values

def validate_interpolation_result(
    grid_values: np.ndarray, 
    original_values: np.ndarray, 
    tolerance: float = 0.1
) -> bool:
    """
    验证插值结果的合理性
    
    Args:
        grid_values: 插值结果
        original_values: 原始数据值
        tolerance: 容差比例
        
    Returns:
        是否合理
    """
    try:
        if grid_values is None or len(original_values) == 0:
            return False
        
        valid_grid = grid_values[~np.isnan(grid_values)]
        
        if len(valid_grid) == 0:
            return False
        
        # 检查数值范围是否合理
        orig_min, orig_max = original_values.min(), original_values.max()
        grid_min, grid_max = valid_grid.min(), valid_grid.max()
        
        # 插值结果应该在原始数据范围的合理扩展内
        range_tolerance = (orig_max - orig_min) * tolerance
        
        range_valid = (
            grid_min >= orig_min - range_tolerance and
            grid_max <= orig_max + range_tolerance
        )
        
        # 检查有效数据比例
        valid_ratio = len(valid_grid) / grid_values.size
        ratio_valid = valid_ratio >= 0.1  # 至少10%的网格点有效
        
        return range_valid and ratio_valid
        
    except Exception as e:
        logger.debug(f"验证插值结果失败: {str(e)}")
        return False

def _add_kml_virtual_boundary_points(
    points: np.ndarray,
    values: np.ndarray,
    kml_boundary_path: str
) -> tuple[np.ndarray, np.ndarray]:
    """
    在KML边界上添加虚拟数据点，确保插值覆盖整个边界
    (移植自AutoReportV3的maps.py实现)
    
    Args:
        points: 原始数据点 (N, 2)
        values: 原始数据值 (N,)
        kml_boundary_path: KML边界文件路径
        
    Returns:
        扩展后的数据点和数据值
    """
    try:
        from .kml_boundary import get_kml_boundary_points
        from matplotlib.path import Path
        from scipy.spatial.distance import cdist
        
        logger.info(f"为KML边界添加虚拟数据点: {kml_boundary_path}")
        
        # 获取KML边界点
        kml_boundary_points = get_kml_boundary_points(kml_boundary_path)
        
        if kml_boundary_points is None:
            logger.warning("无法获取KML边界点，使用原始数据")
            return points, values
            
        # 在KML边界上均匀采样点（最多50个）
        n_boundary_points = min(50, len(kml_boundary_points))
        if len(kml_boundary_points) > n_boundary_points:
            # 均匀采样边界点
            indices = np.linspace(
                0, len(kml_boundary_points) - 1, n_boundary_points, dtype=int
            )
            sampled_boundary_points = kml_boundary_points[indices]
        else:
            sampled_boundary_points = kml_boundary_points
            
        # 首先筛选出在KML范围内的真实数据点
        kml_polygon_path = Path(kml_boundary_points)
        points_inside_mask = kml_polygon_path.contains_points(points)
        
        if np.any(points_inside_mask):
            # 获取在KML范围内的数据点
            points_inside_kml = points[points_inside_mask]
            values_inside_kml = values[points_inside_mask]
            
            # 计算边界点到KML范围内真实数据点的距离
            distances = cdist(sampled_boundary_points, points_inside_kml)
            
            # 找到每个边界点在KML范围内的最近真实数据点
            nearest_indices = np.argmin(distances, axis=1)
            
            # 使用KML范围内最近真实数据点的值作为边界虚拟点的值
            boundary_values = values_inside_kml[nearest_indices]
            
            logger.info(
                f"从 {len(points_inside_kml)} 个KML范围内的真实数据点中选择最近点作为边界值"
            )
        else:
            # 如果没有真实数据点在KML范围内，使用全局最近点（回退策略）
            logger.warning("没有真实数据点在KML范围内，使用全局最近点作为边界值")
            distances = cdist(sampled_boundary_points, points)
            nearest_indices = np.argmin(distances, axis=1)
            boundary_values = values[nearest_indices]
            
        # 合并原始数据和虚拟边界点
        extended_points = np.vstack([points, sampled_boundary_points])
        extended_values = np.concatenate([values, boundary_values])
        
        logger.info(f"添加 {len(sampled_boundary_points)} 个KML边界虚拟点进行插值")
        
        return extended_points, extended_values
        
    except Exception as e:
        logger.error(f"添加KML虚拟边界点失败: {str(e)}")
        return points, values

def _perform_kriging_interpolation(
    points: np.ndarray,
    values: np.ndarray,
    grid_x: np.ndarray,
    grid_y: np.ndarray,
    method: str,
    kriging_params: Optional[Dict[str, Any]] = None,
    kml_boundary_path: Optional[str] = None,
    boundary_method: str = "alpha_shape"
) -> np.ndarray:
    """
    执行Kriging插值计算
    
    Args:
        points: 数据点坐标
        values: 数据值
        grid_x: 网格X坐标
        grid_y: 网格Y坐标
        method: Kriging方法名称
        kriging_params: 额外的kriging参数
        
    Returns:
        插值结果数组
    """
    try:
        logger.info(f"执行Kriging插值，方法: {method}")
        
        # 🔧 KML虚拟边界点逻辑：当使用KML边界方法时，添加虚拟边界点改善插值效果
        if boundary_method == "kml" and kml_boundary_path:
            logger.info("检测到KML边界方法，添加虚拟边界点改善插值效果")
            points, values = _add_kml_virtual_boundary_points(points, values, kml_boundary_path)
        
        # 调用kriging_interpolation模块的函数
        grid_values = kriging_interpolation(
            points=points,
            values=values,
            grid_lon=grid_x,
            grid_lat=grid_y,
            method=method
        )
        
        # 检查插值结果
        valid_count = np.sum(~np.isnan(grid_values))
        total_count = grid_values.size
        
        logger.info(f"Kriging插值完成，有效点: {valid_count}/{total_count}")
        
        if valid_count == 0:
            logger.warning("Kriging插值结果全为NaN，尝试线性插值回退")
            from scipy.interpolate import griddata
            grid_values = griddata(
                points, 
                values, 
                (grid_x, grid_y), 
                method='linear',
                fill_value=np.nan
            )
        
        return grid_values
        
    except Exception as e:
        logger.error(f"Kriging插值计算失败: {str(e)}")
        logger.warning("回退到线性插值")
        # 回退到线性插值
        from scipy.interpolate import griddata
        return griddata(
            points, 
            values, 
            (grid_x, grid_y), 
            method='linear',
            fill_value=np.nan
        )

def get_supported_interpolation_methods() -> Dict[str, str]:
    """
    获取支持的插值方法列表（仅Kriging高精度方法）
    
    Returns:
        方法名称到描述的字典
    """
    from .kriging_interpolation import get_kriging_config
    
    kriging_config = get_kriging_config()
    return {
        method: config['description']
        for method, config in kriging_config.items()
    }