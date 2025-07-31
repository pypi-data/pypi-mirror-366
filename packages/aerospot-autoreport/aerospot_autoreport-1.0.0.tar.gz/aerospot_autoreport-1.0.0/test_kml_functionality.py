#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的KML功能测试脚本
"""

import os
import sys
import numpy as np

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from autoreport.utils.kml import (
    KMLParser, 
    validate_kml_file, 
    get_kml_boundary_points,
    create_kml_boundary_mask
)

def test_kml_parser():
    """测试KML解析器"""
    print("测试KML解析器...")
    
    kml_path = "./test.kml"
    if not os.path.exists(kml_path):
        print(f"KML文件不存在: {kml_path}")
        return False
    
    try:
        # 测试KML解析
        parser = KMLParser(kml_path)
        coordinates = parser.extract_coordinates()
        
        print(f"提取到 {len(coordinates)} 个几何图形")
        if coordinates:
            print(f"第一个几何图形有 {len(coordinates[0])} 个坐标点")
            print(f"坐标范围: {coordinates[0][:3]}...")  # 打印前3个坐标
        
        # 测试边界框
        bbox = parser.get_bounding_box()
        if bbox:
            print(f"边界框: {bbox}")
        
        return True
        
    except Exception as e:
        print(f"KML解析失败: {e}")
        return False

def test_kml_validation():
    """测试KML文件验证"""
    print("\n测试KML文件验证...")
    
    kml_path = "./test.kml"
    is_valid = validate_kml_file(kml_path)
    print(f"KML文件验证结果: {'有效' if is_valid else '无效'}")
    
    return is_valid

def test_kml_boundary_points():
    """测试KML边界点获取"""
    print("\n测试KML边界点获取...")
    
    kml_path = "./test.kml"
    boundary_points = get_kml_boundary_points(kml_path)
    
    if boundary_points is not None:
        print(f"获取到 {len(boundary_points)} 个边界点")
        print(f"边界点类型: {type(boundary_points)}")
        print(f"边界点形状: {boundary_points.shape}")
        print(f"前3个边界点: {boundary_points[:3]}")
        return True
    else:
        print("未能获取边界点")
        return False

def test_kml_boundary_mask():
    """测试KML边界掩码创建"""
    print("\n测试KML边界掩码创建...")
    
    kml_path = "./test.kml"
    
    # 创建测试网格
    lon_min, lon_max = 120.26, 120.27
    lat_min, lat_max = 31.515, 31.522
    
    grid_lon, grid_lat = np.meshgrid(
        np.linspace(lon_min, lon_max, 10),
        np.linspace(lat_min, lat_max, 10)
    )
    
    try:
        mask = create_kml_boundary_mask(grid_lon, grid_lat, kml_path)
        print(f"掩码形状: {mask.shape}")
        print(f"掩码类型: {mask.dtype}")
        print(f"有效点数量: {np.sum(mask)}")
        print(f"总点数量: {mask.size}")
        print(f"有效率: {np.sum(mask)/mask.size:.2%}")
        
        return True
        
    except Exception as e:
        print(f"创建KML边界掩码失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("KML功能测试")
    print("=" * 50)
    
    tests = [
        test_kml_parser,
        test_kml_validation,
        test_kml_boundary_points,
        test_kml_boundary_mask
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"测试异常: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print("=" * 50)
    
    test_names = [
        "KML解析器",
        "KML文件验证", 
        "KML边界点获取",
        "KML边界掩码创建"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{i+1}. {name}: {status}")
    
    success_count = sum(results)
    total_count = len(results)
    print(f"\n总计: {success_count}/{total_count} 个测试通过")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)