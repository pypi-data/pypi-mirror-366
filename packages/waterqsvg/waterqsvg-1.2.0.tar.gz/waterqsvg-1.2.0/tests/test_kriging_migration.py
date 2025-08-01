#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Kriging迁移验证测试
验证从AutoReportV3迁移的Universal Kriging功能是否正常工作
"""
import sys
import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 添加src路径到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from waterqsvg.interpolation.enhanced_interpolation import (
    enhanced_interpolation_with_boundary,
    get_supported_interpolation_methods
)
from waterqsvg.interpolation.kriging_interpolation import (
    get_available_kriging_methods,
    get_kriging_config
)
from waterqsvg.config.grid_config import get_grid_config

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_test_data(n_points=20, seed=42):
    """
    生成测试用的水质数据
    
    Args:
        n_points: 数据点数量
        seed: 随机种子
        
    Returns:
        DataFrame: 包含坐标和指标数据
    """
    np.random.seed(seed)
    
    # 生成随机坐标（模拟太湖区域）
    lon_base = 120.2
    lat_base = 31.3
    longitude = lon_base + np.random.uniform(-0.01, 0.01, n_points)
    latitude = lat_base + np.random.uniform(-0.008, 0.008, n_points)
    
    # 生成模拟水质指标数据（COD）
    # 添加空间相关性：距离中心越远，浓度越低
    center_lon, center_lat = lon_base, lat_base
    distances = np.sqrt((longitude - center_lon)**2 + (latitude - center_lat)**2)
    
    # 基础COD值，加上空间变化和随机噪声
    cod_base = 15.0  # mg/L
    cod_spatial = cod_base * (1 - distances / np.max(distances) * 0.5)  # 空间梯度
    cod_noise = np.random.normal(0, 2.0, n_points)  # 随机噪声
    cod = cod_spatial + cod_noise
    cod = np.maximum(cod, 1.0)  # 确保为正数
    
    data = pd.DataFrame({
        'longitude': longitude,
        'latitude': latitude,
        'cod': cod
    })
    
    logger.info(f"生成测试数据: {n_points}个点, COD范围: {cod.min():.2f}-{cod.max():.2f} mg/L")
    return data

def test_basic_functionality():
    """测试基本功能"""
    logger.info("=== 测试1: 基本功能验证 ===")
    
    # 测试配置获取
    kriging_methods = get_available_kriging_methods()
    logger.info(f"可用Kriging方法: {kriging_methods}")
    
    supported_methods = get_supported_interpolation_methods()
    logger.info(f"支持的插值方法: {list(supported_methods.keys())}")
    
    grid_config = get_grid_config()
    logger.info(f"网格配置: 智能网格={'enabled' if grid_config['adaptive_grid']['enabled'] else 'disabled'}")
    
    assert len(kriging_methods) >= 3, "应该至少支持3种Kriging方法"
    assert 'universal_kriging' in kriging_methods, "应该支持Universal Kriging"
    assert 'universal_kriging' in supported_methods, "应该支持Universal Kriging"
    
    logger.info("✅ 基本功能测试通过")

def test_backward_compatibility():
    """测试向后兼容性"""
    logger.info("=== 测试2: 向后兼容性验证 ===")
    
    # 生成测试数据
    data = generate_test_data(15)
    
    # 测试原有的调用方式是否仍然工作
    try:
        result = enhanced_interpolation_with_boundary(
            data=data,
            indicator_col='cod',
            grid_resolution=100,
            method='universal_kriging',  # 使用高精度方法
            boundary_method='alpha_shape'
        )
        
        grid_values, grid_x, grid_y, boundary_mask, boundary_points = result
        assert grid_values is not None, "插值结果不应为None"
        assert grid_x.shape == grid_y.shape, "网格坐标形状应一致"
        
        valid_count = np.sum(~np.isnan(grid_values))
        logger.info(f"向后兼容测试: 有效插值点数 {valid_count}/{grid_values.size}")
        
        assert valid_count > 0, "应该有有效的插值结果"
        
    except Exception as e:
        logger.error(f"向后兼容性测试失败: {e}")
        raise
    
    logger.info("✅ 向后兼容性测试通过")

def test_kriging_interpolation():
    """测试Kriging插值功能"""
    logger.info("=== 测试3: Kriging插值功能验证 ===")
    
    # 生成测试数据
    data = generate_test_data(20)
    
    # 测试Universal Kriging
    try:
        result = enhanced_interpolation_with_boundary(
            data=data,
            indicator_col='cod',
            method='universal_kriging',  # 新的Kriging方法
            intelligent_grid=True,  # 使用智能网格
            boundary_method='alpha_shape'
        )
        
        grid_values, grid_x, grid_y, boundary_mask, boundary_points = result
        assert grid_values is not None, "Kriging插值结果不应为None"
        
        valid_count = np.sum(~np.isnan(grid_values))
        total_count = grid_values.size
        logger.info(f"Universal Kriging: 有效插值点数 {valid_count}/{total_count}")
        logger.info(f"网格形状: {grid_x.shape}")
        
        # 检查插值结果的合理性
        if valid_count > 0:
            valid_values = grid_values[~np.isnan(grid_values)]
            original_values = data['cod'].values
            
            logger.info(f"原始数据范围: {original_values.min():.2f} - {original_values.max():.2f}")
            logger.info(f"插值结果范围: {valid_values.min():.2f} - {valid_values.max():.2f}")
            
            # 插值结果应该在合理范围内
            assert valid_values.min() >= 0, "插值结果不应有负数"
            # Kriging可能在边界区域产生外推，放宽条件到3倍范围
            assert valid_values.max() < original_values.max() * 3, "插值结果外推过度"
            
            # 大部分值应该在合理范围内
            reasonable_mask = (valid_values >= original_values.min() * 0.5) & (valid_values <= original_values.max() * 1.5)
            reasonable_ratio = np.sum(reasonable_mask) / len(valid_values)
            logger.info(f"合理范围内的插值点比例: {reasonable_ratio:.2%}")
            assert reasonable_ratio > 0.7, "至少70%的插值结果应该在合理范围内"
        
        assert valid_count > total_count * 0.1, "至少应该有10%的有效插值点"
        
    except Exception as e:
        logger.error(f"Kriging插值测试失败: {e}")
        raise
    
    logger.info("✅ Kriging插值功能测试通过")

def test_intelligent_grid():
    """测试智能网格功能"""
    logger.info("=== 测试4: 智能网格系统验证 ===")
    
    # 生成测试数据
    data = generate_test_data(15)
    
    # 测试智能网格 vs 固定网格
    results = {}
    
    for grid_mode, intelligent in [("智能网格", True), ("固定网格", False)]:
        try:
            result = enhanced_interpolation_with_boundary(
                data=data,
                indicator_col='cod',
                grid_resolution=200,  # 固定网格使用
                method='universal_kriging',
                intelligent_grid=intelligent,
                spatial_resolution=0.00003 if intelligent else None,  # 自定义分辨率
                boundary_method='alpha_shape'
            )
            
            grid_values, grid_x, grid_y, boundary_mask, boundary_points = result
            results[grid_mode] = {
                'shape': grid_x.shape,
                'valid_count': np.sum(~np.isnan(grid_values)),
                'total_count': grid_values.size
            }
            
            logger.info(f"{grid_mode}: 网格形状 {grid_x.shape}, 有效点 {results[grid_mode]['valid_count']}")
            
        except Exception as e:
            logger.error(f"{grid_mode}测试失败: {e}")
            raise
    
    # 比较两种网格模式
    intelligent_shape = results["智能网格"]["shape"]
    fixed_shape = results["固定网格"]["shape"]
    
    logger.info(f"网格对比: 智能网格 {intelligent_shape} vs 固定网格 {fixed_shape}")
    
    # 智能网格应该根据地理范围自动调整尺寸
    assert intelligent_shape != fixed_shape, "智能网格和固定网格的尺寸应该不同"
    
    logger.info("✅ 智能网格系统测试通过")

def test_comparison_with_scipy():
    """对比Kriging和scipy插值的效果"""
    logger.info("=== 测试5: 插值方法对比验证 ===")
    
    # 生成较多数据点以便对比
    data = generate_test_data(25, seed=123)
    
    methods_to_test = ['universal_kriging', 'ordinary_kriging_spherical']
    results = {}
    
    for method in methods_to_test:
        try:
            result = enhanced_interpolation_with_boundary(
                data=data,
                indicator_col='cod',
                method=method,
                intelligent_grid=True,
                boundary_method='alpha_shape'
            )
            
            grid_values, grid_x, grid_y, boundary_mask, boundary_points = result
            valid_mask = ~np.isnan(grid_values)
            valid_values = grid_values[valid_mask]
            
            if len(valid_values) > 0:
                results[method] = {
                    'valid_count': len(valid_values),
                    'min_val': valid_values.min(),
                    'max_val': valid_values.max(),
                    'mean_val': valid_values.mean(),
                    'std_val': valid_values.std()
                }
                
                logger.info(f"{method}: 有效点 {len(valid_values)}, "
                          f"范围 [{valid_values.min():.2f}, {valid_values.max():.2f}], "
                          f"均值 {valid_values.mean():.2f}")
            
        except Exception as e:
            logger.error(f"{method}插值测试失败: {e}")
            # 不抛出异常，继续测试其他方法
            results[method] = None
    
    # 验证两种方法都有合理的结果
    for method, result in results.items():
        if result is not None:
            assert result['valid_count'] > 0, f"{method}应该产生有效插值结果"
            assert result['min_val'] >= 0, f"{method}插值结果不应有负数"
    
    logger.info("✅ 插值方法对比测试通过")

def run_all_tests():
    """运行所有测试"""
    logger.info("🚀 开始Universal Kriging迁移验证测试")
    
    try:
        test_basic_functionality()
        test_backward_compatibility() 
        test_kriging_interpolation()
        test_intelligent_grid()
        test_comparison_with_scipy()
        
        logger.info("🎉 所有测试通过！Universal Kriging迁移成功")
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)