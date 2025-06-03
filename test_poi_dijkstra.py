#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POI搜索与Dijkstra距离计算测试脚本
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from module.data_structure.POiSearch import POISearch

def test_poi_search_with_dijkstra():
    """测试POI搜索与Dijkstra距离计算功能"""
    
    print("=" * 60)
    print("POI搜索与Dijkstra距离计算测试")
    print("=" * 60)
    
    # 初始化POI搜索
    poi_search = POISearch()
    
    # 测试位置：北京天安门广场
    location = "39.915,116.404"
    print(f"测试位置: {location} (天安门广场)")
    
    # 搜索附近的景点
    print("\n1. 搜索附近景点...")
    result, query = poi_search.search("景点", location, radius=1000)
    
    if result.get("status") == 0:
        total_found = result.get('total', 0)
        results_count = len(result.get('results', []))
        print(f"   ✓ 搜索成功，总共找到 {total_found} 个结果，返回 {results_count} 个")
        
        # 测试使用Dijkstra算法计算距离
        print("\n2. 使用Dijkstra算法计算距离...")
        pois_dijkstra = poi_search.get_poi_details(result, location, type="景点", use_dijkstra=True)
        
        # 测试使用直线距离计算
        print("\n3. 使用直线距离计算...")
        pois_haversine = poi_search.get_poi_details(result, location, type="景点", use_dijkstra=False)
        
        # 比较结果
        print("\n4. 距离计算结果比较:")
        print("-" * 80)
        print(f"{'序号':<4} {'景点名称':<20} {'Dijkstra距离(m)':<15} {'直线距离(m)':<12} {'差异(m)':<10}")
        print("-" * 80)
        
        for i, (poi_d, poi_h) in enumerate(zip(pois_dijkstra[:10], pois_haversine[:10]), 1):
            dijkstra_dist = poi_d.get('value1', 'N/A')
            haversine_dist = poi_h.get('value1', 'N/A')
            
            # 计算差异
            if isinstance(dijkstra_dist, (int, float)) and isinstance(haversine_dist, (int, float)):
                diff = abs(dijkstra_dist - haversine_dist)
                diff_str = f"{diff:.0f}"
            else:
                diff_str = "N/A"
            
            name = poi_d.get('name', '未知')[:18]  # 截断长名称
            print(f"{i:<4} {name:<20} {dijkstra_dist:<15} {haversine_dist:<12} {diff_str:<10}")
        
        # 统计信息
        print("\n5. 统计信息:")
        dijkstra_valid = sum(1 for poi in pois_dijkstra if isinstance(poi.get('value1'), (int, float)))
        haversine_valid = sum(1 for poi in pois_haversine if isinstance(poi.get('value1'), (int, float)))
        
        print(f"   Dijkstra成功计算距离的POI数量: {dijkstra_valid}/{len(pois_dijkstra)}")
        print(f"   直线距离成功计算距离的POI数量: {haversine_valid}/{len(pois_haversine)}")
        
        # 如果Dijkstra计算成功，显示详细信息
        if dijkstra_valid > 0:
            print("\n6. Dijkstra算法计算的详细信息:")
            for i, poi in enumerate(pois_dijkstra[:3], 1):
                if isinstance(poi.get('value1'), (int, float)):
                    print(f"\n   {i}. {poi['name']}")
                    print(f"      地址: {poi['address']}")
                    print(f"      距离: {poi['value1']} 米")
                    print(f"      坐标: ({poi['location'].get('lat'):.6f}, {poi['location'].get('lng'):.6f})")
        
    else:
        print(f"   ✗ 搜索失败: {result}")
        return False
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    return True

def test_poi_search_different_locations():
    """测试不同位置的POI搜索"""
    
    print("\n" + "=" * 60)
    print("不同位置POI搜索测试")
    print("=" * 60)
    
    poi_search = POISearch()
    
    # 测试不同的位置
    test_locations = [
        ("39.915,116.404", "北京天安门"),
        ("31.2304,121.4737", "上海外滩"),
        ("22.3193,114.1694", "香港中环")
    ]
    
    for location, location_name in test_locations:
        print(f"\n测试位置: {location_name}")
        result, query = poi_search.search("餐厅", location, radius=500)
        
        if result.get("status") == 0:
            pois = poi_search.get_poi_details(result, location, type="餐厅", use_dijkstra=True)
            valid_distances = sum(1 for poi in pois if isinstance(poi.get('value1'), (int, float)))
            print(f"   找到 {len(pois)} 个餐厅，{valid_distances} 个成功计算距离")
            
            if valid_distances > 0:
                # 显示最近的餐厅
                nearest_poi = min([poi for poi in pois if isinstance(poi.get('value1'), (int, float))], 
                                key=lambda x: x['value1'])
                print(f"   最近餐厅: {nearest_poi['name']} ({nearest_poi['value1']} 米)")
        else:
            print(f"   搜索失败: {result.get('message', '未知错误')}")

if __name__ == "__main__":
    try:
        # 运行基本测试
        success = test_poi_search_with_dijkstra()
        
        if success:
            # 运行扩展测试
            test_poi_search_different_locations()
            
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
