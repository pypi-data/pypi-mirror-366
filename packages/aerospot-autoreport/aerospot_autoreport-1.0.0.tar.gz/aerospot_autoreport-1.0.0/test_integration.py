#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KML边界功能集成测试
"""

import os
import sys
import json

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from autoreport.config_validator import load_and_validate_config
from autoreport.core.resource_manager import ResourceManager
from autoreport.utils.path import PathManager

def test_config_loading():
    """测试配置加载和KML URL验证"""
    print("=" * 50)
    print("测试配置加载和KML URL验证")
    print("=" * 50)
    
    try:
        config = load_and_validate_config("test.json")
        
        print("✓ 配置文件加载成功")
        
        # 检查KML边界URL配置
        kml_url = config.get("company_info", {}).get("kml_boundary_url")
        if kml_url:
            print(f"✓ 发现KML边界URL配置: {kml_url}")
            
            # 检查本地文件是否存在
            if os.path.exists(kml_url):
                print(f"✓ KML文件存在: {kml_url}")
            else:
                print(f"✗ KML文件不存在: {kml_url}")
                return False
        else:
            print("✗ 未发现KML边界URL配置")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return False

def test_resource_management():
    """测试资源管理器对KML文件的处理"""
    print("\n" + "=" * 50)
    print("测试资源管理器对KML文件的处理")
    print("=" * 50)
    
    try:
        # 初始化路径管理器和资源管理器
        path_manager = PathManager("./AutoReportResults")
        resource_manager = ResourceManager(path_manager, cache_enabled=False)
        
        # 测试获取KML资源
        kml_path = "./test.kml"
        
        if os.path.exists(kml_path):
            result_path = resource_manager.get_resource(kml_path, "kml_boundary")
            print(f"✓ KML资源获取成功: {result_path}")
            
            # 验证结果路径指向正确的文件
            if os.path.exists(result_path):
                print(f"✓ 返回的KML文件路径有效: {result_path}")
                return True
            else:
                print(f"✗ 返回的KML文件路径无效: {result_path}")
                return False
        else:
            print(f"✗ 测试KML文件不存在: {kml_path}")
            return False
        
    except Exception as e:
        print(f"✗ 资源管理器测试失败: {e}")
        return False

def test_maps_integration_mock():
    """模拟测试地图生成器的KML集成"""
    print("\n" + "=" * 50)
    print("模拟测试地图生成器的KML集成")
    print("=" * 50)
    
    try:
        # 导入maps模块来验证KML功能
        from autoreport.processor.maps import enhanced_interpolation_with_neighborhood
        import pandas as pd
        import numpy as np
        
        # 创建测试数据
        test_data = pd.DataFrame({
            'longitude': [120.261, 120.265, 120.270],
            'latitude': [31.516, 31.518, 31.520],
            'nh3n': [0.5, 0.8, 0.3]
        })
        
        kml_path = "./test.kml"
        
        if os.path.exists(kml_path):
            print("✓ 准备调用enhanced_interpolation_with_neighborhoods函数（KML边界方法）")
            
            # 测试KML边界方法调用（不实际执行完整插值以节省时间）
            try:
                # 只验证函数可以被调用，参数可以被接受
                result = enhanced_interpolation_with_neighborhood(
                    test_data,
                    grid_resolution=50,  # 降低分辨率以加快测试
                    boundary_method='kml',
                    kml_boundary_path=kml_path,
                    indicator_col='nh3n'
                )
                
                if result and len(result) == 5:  # 期望返回5个元素的元组
                    print("✓ KML边界方法调用成功")
                    print(f"  - 返回结果类型: {type(result)}")
                    print(f"  - 返回元素数量: {len(result)}")
                    return True
                else:
                    print("✗ KML边界方法返回结果格式不正确")
                    return False
                    
            except Exception as e:
                print(f"✗ KML边界方法调用失败: {e}")
                return False
        else:
            print(f"✗ 测试KML文件不存在: {kml_path}")
            return False
        
    except ImportError as e:
        print(f"✗ 导入模块失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 地图集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("KML边界功能集成测试")
    
    tests = [
        ("配置加载和验证", test_config_loading),
        ("资源管理器处理", test_resource_management),
        ("地图生成器集成", test_maps_integration_mock)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n正在运行: {test_name}")
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✓ {test_name}: 通过")
            else:
                print(f"✗ {test_name}: 失败")
                
        except Exception as e:
            print(f"✗ {test_name}: 异常 - {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("集成测试结果汇总")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有集成测试通过！KML边界功能已成功集成。")
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，需要进一步检查。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)