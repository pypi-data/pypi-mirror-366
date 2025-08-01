#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Kriging插值算法模块
从AutoReportV3完整迁移Universal Kriging和Ordinary Kriging算法
支持多种变差函数模型和负数处理策略
"""

import logging
from typing import Dict

import numpy as np
from pykrige.ok import OrdinaryKriging
from pykrige.uk import UniversalKriging
from scipy.interpolate import griddata

logger = logging.getLogger(__name__)

# ================== 克里金插值配置 ==================
# 完全复制AutoReportV3的配置系统

# 全局插值方法设置 - 修改此处可切换不同克里金方法进行对比测试
# 可选值: 'auto', 'universal_kriging', 'ordinary_kriging_spherical', 'ordinary_kriging_exponential'
GLOBAL_KRIGING_METHOD = "ordinary_kriging_spherical"  # 🎯 当前使用：泛克里金高斯模型

KRIGING_CONFIG = {
    "universal_kriging": {
        "variogram_model": "gaussian",  # 高斯模型：平滑过渡，无明确影响范围
        "drift_terms": ["regional_linear"],  # 区域线性趋势建模
        "description": "泛克里金-高斯模型（适合连续环境数据，支持趋势建模）",
        "enforce_positive": True,  # 强制插值结果为正数
        "transform_method": "log",  # 负数处理方法: 'log', 'clip', 'none'
    },
    "ordinary_kriging_spherical": {
        "variogram_model": "spherical",  # 球形模型：有明确影响范围和渐变特性
        "n_closest_points": 12,  # 搜索最近12个点（ArcGIS默认）
        "search_radius_factor": 0.3,  # 搜索半径为数据范围的30%
        "description": "普通克里金-球形模型（类似ArcGIS，有明确空间影响范围）",
        "enforce_positive": True,  # 强制插值结果为正数
        "transform_method": "clip",  # 负数处理方法: 直接截断
    },
    "ordinary_kriging_exponential": {
        "variogram_model": "exponential",  # 指数模型：快速衰减，适合局部变化
        "n_closest_points": 8,  # 搜索最近8个点
        "search_radius_factor": 0.25,  # 搜索半径为数据范围的25%
        "description": "普通克里金-指数模型（适合快速变化数据，局部影响强）",
        "enforce_positive": True,  # 强制插值结果为正数
        "transform_method": "clip",  # 负数处理方法: 直接截断
    },
}


def transform_data_for_kriging(values, method="log"):
    """
    为克里金插值预处理数据，处理负数或零值

    Args:
        values: 原始数据值
        method: 变换方法 ('log', 'clip', 'none')

    Returns:
        transformed_values: 变换后的数据
        transform_params: 变换参数（用于逆变换）
    """
    values = np.array(values)

    if method == "log":
        # 对数变换，适合环境数据（如水质指标）
        min_val = np.min(values)
        if min_val <= 0:
            # 如果有负数或零值，添加偏移量使所有值为正
            offset = abs(min_val) + 1e-6
            logger.info(f"检测到负数或零值，添加偏移量: {offset:.6f}")
        else:
            offset = 0

        transformed_values = np.log(values + offset)
        transform_params = {"method": "log", "offset": offset}

    elif method == "clip":
        # 简单截断，不进行数据变换
        transformed_values = values.copy()
        transform_params = {"method": "clip"}

    else:  # method == 'none'
        # 不处理
        transformed_values = values.copy()
        transform_params = {"method": "none"}

    return transformed_values, transform_params


def inverse_transform_data(values, transform_params):
    """
    对插值结果进行逆变换

    Args:
        values: 插值结果
        transform_params: 变换参数

    Returns:
        original_scale_values: 逆变换后的数据
    """
    method = transform_params["method"]

    if method == "log":
        # 指数逆变换
        offset = transform_params["offset"]
        result = np.exp(values) - offset
        # 确保结果为正数
        result = np.maximum(result, 1e-10)
        return result

    elif method == "clip":
        # 截断负值
        return np.maximum(values, 0)

    else:  # method == 'none'
        return values


def kriging_interpolation(points, values, grid_lon, grid_lat, method="auto"):
    """
    使用克里金插值方法，支持多种配置
    完全复制AutoReportV3的kriging_interpolation函数

    Args:
        points: 数据点坐标 (N, 2) [lon, lat]
        values: 数据值 (N,)
        grid_lon, grid_lat: 插值网格
        method: 插值方法 ('auto', 'universal_kriging', 'ordinary_kriging_spherical', 'ordinary_kriging_exponential')

    Returns:
        grid_values: 插值结果
    """
    x = points[:, 0]  # 经度
    y = points[:, 1]  # 纬度
    z = values

    # 数据点数量检查
    if len(x) < 3:
        logger.warning("数据点少于3个，使用线性插值")
        return griddata(points, values, (grid_lon, grid_lat), method="linear")

    # 计算数据范围（用于搜索半径）
    x_range = np.max(x) - np.min(x)
    y_range = np.max(y) - np.min(y)
    data_range = np.sqrt(x_range**2 + y_range**2)

    # 根据method参数决定尝试顺序
    if method == "auto":
        # 自动模式：按优先级尝试
        methods_to_try = [
            "universal_kriging",
            "ordinary_kriging_spherical",
            "ordinary_kriging_exponential",
        ]
    elif method in KRIGING_CONFIG:
        # 指定方法
        methods_to_try = [method]
    else:
        logger.warning(f"未知的插值方法: {method}，使用自动模式")
        methods_to_try = [
            "universal_kriging",
            "ordinary_kriging_spherical",
            "ordinary_kriging_exponential",
        ]

    # 依次尝试不同的克里金方法
    for method_name in methods_to_try:
        config = KRIGING_CONFIG[method_name]

        try:
            logger.info(f"尝试{config['description']}...")

            # 数据预处理：防止负数
            if config.get("enforce_positive", False):
                transform_method = config.get("transform_method", "clip")
                z_transformed, transform_params = transform_data_for_kriging(
                    z, transform_method
                )
                logger.info(f"使用{transform_method}方法处理数据，确保正数插值结果")
            else:
                z_transformed = z
                transform_params = {"method": "none"}

            if method_name == "universal_kriging":
                # 泛克里金
                kriging_obj = UniversalKriging(
                    x,
                    y,
                    z_transformed,
                    variogram_model=config["variogram_model"],
                    drift_terms=config["drift_terms"],
                    verbose=False,
                    enable_plotting=False,
                    exact_values=True,
                    pseudo_inv=False,
                )
                z_pred, ss = kriging_obj.execute("grid", grid_lon[0, :], grid_lat[:, 0])

            else:
                # 普通克里金（球形或指数模型）
                kriging_obj = OrdinaryKriging(
                    x,
                    y,
                    z_transformed,
                    variogram_model=config["variogram_model"],
                    verbose=False,
                    enable_plotting=False,
                    exact_values=True,
                    pseudo_inv=False,
                )

                # 计算搜索半径
                search_radius = data_range * config["search_radius_factor"]

                # 执行插值（使用搜索策略）
                z_pred, ss = kriging_obj.execute(
                    "grid",
                    grid_lon[0, :],
                    grid_lat[:, 0],
                    backend="loop",
                    n_closest_points=config["n_closest_points"],
                )

                logger.info(
                    f"搜索半径: {search_radius:.6f}, 最近点数: {config['n_closest_points']}"
                )

            # 逆变换回原始尺度
            z_pred = inverse_transform_data(z_pred, transform_params)

            # 统计插值结果范围
            valid_mask = ~np.isnan(z_pred)
            if np.any(valid_mask):
                min_val, max_val = (
                    np.min(z_pred[valid_mask]),
                    np.max(z_pred[valid_mask]),
                )
                negative_count = np.sum(z_pred[valid_mask] < 0)
                logger.info(
                    f"{config['description']}成功，网格大小: {z_pred.shape}, 值范围: [{min_val:.3f}, {max_val:.3f}], 负值数量: {negative_count}"
                )
            else:
                logger.info(f"{config['description']}成功，网格大小: {z_pred.shape}")

            return z_pred

        except Exception as e:
            logger.warning(f"{config['description']}失败: {str(e)}")
            continue

    # 所有克里金方法都失败，回退到线性插值
    logger.warning("所有克里金方法失败，回退到线性插值")
    return griddata(points, values, (grid_lon, grid_lat), method="linear")


def get_kriging_config() -> Dict:
    """
    获取当前的克里金配置

    Returns:
        当前的克里金配置字典
    """
    return KRIGING_CONFIG


def get_available_kriging_methods() -> list:
    """
    获取可用的克里金方法列表

    Returns:
        可用方法名称列表
    """
    return list(KRIGING_CONFIG.keys())


def set_global_kriging_method(method: str) -> None:
    """
    设置全局默认克里金方法

    Args:
        method: 克里金方法名称
    """
    global GLOBAL_KRIGING_METHOD
    if method in KRIGING_CONFIG:
        GLOBAL_KRIGING_METHOD = method
        logger.info(f"全局克里金方法已设置为: {method}")
    else:
        raise ValueError(f"不支持的克里金方法: {method}")
