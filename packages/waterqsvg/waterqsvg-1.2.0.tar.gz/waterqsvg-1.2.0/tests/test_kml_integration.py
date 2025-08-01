#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试KML功能集成

验证KML边界检测功能是否正确集成到WaterQSVG项目中
"""

import os
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

# 添加src到路径
current_dir = Path(__file__).parent
src_path = current_dir.parent / "src"
import sys
sys.path.insert(0, str(src_path))

from waterqsvg.interpolation.kml_boundary import (
    KMLParser, 
    validate_kml_file,
    get_kml_boundary_points,
    create_kml_boundary_mask
)
from waterqsvg.interpolation.enhanced_interpolation import enhanced_interpolation_with_boundary


class TestKMLIntegration(unittest.TestCase):
    """测试KML功能集成"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试用的KML文件内容
        self.test_kml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>测试边界</name>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              120.1,31.1,0 120.2,31.1,0 120.2,31.2,0 120.1,31.2,0 120.1,31.1,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>'''
        
        # 创建临时KML文件
        self.temp_dir = tempfile.mkdtemp()
        self.kml_path = os.path.join(self.temp_dir, "test_boundary.kml")
        with open(self.kml_path, 'w', encoding='utf-8') as f:
            f.write(self.test_kml_content)
        
        # 创建测试数据
        self.test_data = pd.DataFrame({
            'longitude': [120.11, 120.12, 120.18, 120.19],
            'latitude': [31.11, 31.18, 31.12, 31.19],
            'cod': [15.2, 18.7, 12.3, 20.1]
        })
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_kml_parser_basic(self):
        """测试KML解析器基础功能"""
        parser = KMLParser(self.kml_path)
        
        # 测试坐标提取
        coordinate_sets = parser.extract_coordinates()
        self.assertGreater(len(coordinate_sets), 0, "应该能提取到坐标信息")
        
        coords = coordinate_sets[0]
        self.assertEqual(len(coords), 5, "应该有5个坐标点（包括闭合点）")
        
        # 验证坐标值
        expected_first_coord = (120.1, 31.1)
        self.assertEqual(coords[0], expected_first_coord, "第一个坐标点应该正确")
    
    def test_kml_validation(self):
        """测试KML文件验证"""
        # 测试有效的KML文件
        self.assertTrue(validate_kml_file(self.kml_path), "测试KML文件应该是有效的")
        
        # 测试不存在的文件
        self.assertFalse(validate_kml_file("/nonexistent/file.kml"), "不存在的文件应该返回False")
    
    def test_get_kml_boundary_points(self):
        """测试获取KML边界点"""
        boundary_points = get_kml_boundary_points(self.kml_path)
        
        self.assertIsNotNone(boundary_points, "应该能获取到边界点")
        self.assertEqual(boundary_points.shape[1], 2, "边界点应该是2D坐标")
        self.assertGreater(len(boundary_points), 0, "应该有边界点")
        
        # 验证数据类型
        self.assertIsInstance(boundary_points, np.ndarray, "应该返回numpy数组")
    
    def test_create_kml_boundary_mask(self):
        """测试创建KML边界掩码"""
        # 创建测试网格
        x = np.linspace(120.0, 120.3, 50)
        y = np.linspace(31.0, 31.3, 50)
        grid_x, grid_y = np.meshgrid(x, y)
        
        # 创建KML边界掩码
        mask = create_kml_boundary_mask(grid_x, grid_y, self.kml_path)
        
        self.assertEqual(mask.shape, grid_x.shape, "掩码形状应该与网格一致")
        self.assertIsInstance(mask, np.ndarray, "应该返回numpy数组")
        self.assertEqual(mask.dtype, bool, "掩码应该是布尔类型")
        
        # 验证有一些True值（在边界内）
        self.assertTrue(np.any(mask), "应该有一些点在KML边界内")
    
    def test_enhanced_interpolation_with_kml(self):
        """测试增强插值与KML边界集成"""
        try:
            # 使用KML边界方法进行插值
            result = enhanced_interpolation_with_boundary(
                data=self.test_data,
                indicator_col='cod',
                grid_resolution=20,  # 使用较小的分辨率以加快测试
                boundary_method='kml',
                kml_boundary_path=self.kml_path
            )
            
            grid_values, grid_x, grid_y, boundary_mask, boundary_points = result
            
            # 验证返回值
            self.assertIsNotNone(grid_values, "应该有插值结果")
            self.assertIsNotNone(grid_x, "应该有网格X坐标")
            self.assertIsNotNone(grid_y, "应该有网格Y坐标")
            self.assertIsNotNone(boundary_mask, "应该有边界掩码")
            self.assertIsNotNone(boundary_points, "应该有边界点")
            
            # 验证形状一致性
            self.assertEqual(grid_values.shape, grid_x.shape, "插值结果形状应该与网格一致")
            self.assertEqual(grid_values.shape, grid_y.shape, "插值结果形状应该与网格一致")
            self.assertEqual(boundary_mask.shape, grid_x.shape, "边界掩码形状应该与网格一致")
            
            # 验证有有效的插值数据
            valid_data = grid_values[~np.isnan(grid_values)]
            self.assertGreater(len(valid_data), 0, "应该有有效的插值数据")
            
        except Exception as e:
            self.fail(f"KML插值集成测试失败: {str(e)}")
    
    def test_kml_fallback_mechanism(self):
        """测试KML回退机制"""
        # 测试无效的KML路径，应该回退到alpha_shape
        invalid_kml_path = "/nonexistent/file.kml"
        
        result = enhanced_interpolation_with_boundary(
            data=self.test_data,
            indicator_col='cod',
            grid_resolution=20,
            boundary_method='kml',
            kml_boundary_path=invalid_kml_path
        )
        
        # 即使KML文件无效，也应该有结果（通过回退机制）
        grid_values, grid_x, grid_y, boundary_mask, boundary_points = result
        self.assertIsNotNone(grid_values, "回退机制应该提供插值结果")
        self.assertIsNotNone(boundary_points, "回退机制应该提供边界点")
    
    def test_kml_method_without_path(self):
        """测试没有提供KML路径时的行为"""
        # 当使用kml方法但没有提供路径时，应该回退到alpha_shape
        result = enhanced_interpolation_with_boundary(
            data=self.test_data,
            indicator_col='cod',
            grid_resolution=20,
            boundary_method='kml',
            kml_boundary_path=None  # 没有提供KML路径
        )
        
        grid_values, grid_x, grid_y, boundary_mask, boundary_points = result
        self.assertIsNotNone(grid_values, "应该有回退的插值结果")
        self.assertIsNotNone(boundary_points, "应该有回退的边界点")


if __name__ == '__main__':
    # 设置测试日志级别
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    unittest.main(verbosity=2)