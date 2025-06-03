# -*- coding: utf-8 -*-
"""
测试使用indexHeap的优化推荐算法
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from module.user_class import userManager
import time

def test_indexheap_recommendation():
    """
    测试基于indexHeap的推荐算法
    """
    print("=== 测试基于indexHeap的推荐算法 ===")
    
    user_id = 1
    top_k = 10
    
    print(f"用户ID: {user_id}")
    user = userManager.getUser(user_id)
    print(f"用户喜好类型: {user.likes_type}")
    
    # 测试景点推荐
    print(f"\n=== 景点推荐测试 (topK={top_k}) ===")
    start_time = time.time()
    spots_result = userManager.getRecommendSpots(user_id, top_k)
    spots_time = time.time() - start_time
    
    if spots_result:
        print(f"执行时间: {spots_time:.4f}秒")
        print(f"推荐景点数量: {len(spots_result)}")
        print("推荐景点:")
        for i, spot in enumerate(spots_result[:5], 1):  # 显示前5个
            print(f"  {i}. ID: {spot['id']}, 评分: {spot['score']}, 访问次数: {spot['visited_time']}")
    else:
        print("没有找到推荐景点")
    
    # 测试日记推荐
    print(f"\n=== 日记推荐测试 (topK={top_k}) ===")
    start_time = time.time()
    diaries_result = userManager.getRecommendDiaries(user_id, top_k)
    diaries_time = time.time() - start_time
    
    if diaries_result:
        print(f"执行时间: {diaries_time:.4f}秒")
        print(f"推荐日记数量: {len(diaries_result)}")
        print("推荐日记:")
        for i, diary in enumerate(diaries_result[:5], 1):  # 显示前5个
            print(f"  {i}. ID: {diary.id}, 标题: {diary.title[:30]}...")
    else:
        print("没有找到推荐日记")

def test_comparison_with_traditional():
    """
    对比indexHeap算法与传统算法
    """
    print(f"\n=== indexHeap算法 vs 传统算法对比 ===")
    
    user_id = 1
    top_k = 10
    
    # 测试景点推荐对比
    print(f"\n景点推荐对比 (topK={top_k}):")
    
    # indexHeap算法
    start_time = time.time()
    indexheap_spots = userManager.getRecommendSpots(user_id, top_k)
    indexheap_spots_time = time.time() - start_time
    
    # 传统算法
    start_time = time.time()
    traditional_spots = userManager.getRecommendSpotsTraditional(user_id, top_k)
    traditional_spots_time = time.time() - start_time
    
    print(f"  indexHeap算法: {indexheap_spots_time:.4f}秒, 返回{len(indexheap_spots) if indexheap_spots else 0}个景点")
    print(f"  传统算法: {traditional_spots_time:.4f}秒, 返回{len(traditional_spots) if traditional_spots else 0}个景点")
    
    # 对比前5个结果
    if indexheap_spots and traditional_spots:
        print("  前5个景点ID对比:")
        indexheap_ids = [spot['id'] for spot in indexheap_spots[:5]]
        traditional_ids = [spot['id'] for spot in traditional_spots[:5]]
        print(f"    indexHeap: {indexheap_ids}")
        print(f"    传统算法: {traditional_ids}")
        common = set(indexheap_ids) & set(traditional_ids)
        print(f"    共同推荐: {len(common)} 个景点")
    
    # 测试日记推荐对比
    print(f"\n日记推荐对比 (topK={top_k}):")
    
    # indexHeap算法
    start_time = time.time()
    indexheap_diaries = userManager.getRecommendDiaries(user_id, top_k)
    indexheap_diaries_time = time.time() - start_time
    
    # 传统算法
    start_time = time.time()
    traditional_diaries = userManager.getRecommendDiariesTraditional(user_id, top_k)
    traditional_diaries_time = time.time() - start_time
    
    print(f"  indexHeap算法: {indexheap_diaries_time:.4f}秒, 返回{len(indexheap_diaries) if indexheap_diaries else 0}个日记")
    print(f"  传统算法: {traditional_diaries_time:.4f}秒, 返回{len(traditional_diaries) if traditional_diaries else 0}个日记")
    
    # 对比前5个结果
    if indexheap_diaries and traditional_diaries:
        print("  前5个日记ID对比:")
        indexheap_ids = [diary.id for diary in indexheap_diaries[:5]]
        traditional_ids = [diary.id for diary in traditional_diaries[:5]]
        print(f"    indexHeap: {indexheap_ids}")
        print(f"    传统算法: {traditional_ids}")
        common = set(indexheap_ids) & set(traditional_ids)
        print(f"    共同推荐: {len(common)} 个日记")

def test_sorting_consistency():
    """
    测试排序一致性 - 验证value1相同时按value2排序
    """
    print(f"\n=== 排序一致性测试 ===")
    
    from module.data_structure.indexHeap import TopKHeap
    
    # 创建测试堆
    test_heap = TopKHeap()
    
    # 插入测试数据 - 包含相同value1的情况
    test_data = [
        (1, 4.8, 1000),  # 最高评分，低访问次数
        (2, 4.8, 2000),  # 最高评分，高访问次数
        (3, 4.7, 500),   # 次高评分
        (4, 4.8, 1500),  # 最高评分，中等访问次数
        (5, 4.6, 3000),  # 较低评分，最高访问次数
    ]
    
    print("插入测试数据:")
    for item_id, value1, value2 in test_data:
        test_heap.insert(item_id, value1, value2)
        print(f"  ID: {item_id}, value1(评分): {value1}, value2(访问次数): {value2}")
    
    # 获取排序结果
    print(f"\n排序结果 (按value1降序，value1相同时按value2降序):")
    sorted_results = test_heap.getTopK(5)
    for i, item in enumerate(sorted_results, 1):
        print(f"  {i}. ID: {item['id']}, value1: {item['value1']}, value2: {item['value2']}")
    
    # 验证排序正确性
    print(f"\n排序验证:")
    expected_order = [2, 4, 1, 3, 5]  # 期望的排序：4.8,2000 -> 4.8,1500 -> 4.8,1000 -> 4.7,500 -> 4.6,3000
    actual_order = [item['id'] for item in sorted_results]
    print(f"  期望顺序: {expected_order}")
    print(f"  实际顺序: {actual_order}")
    print(f"  排序正确: {'✓' if actual_order == expected_order else '✗'}")

if __name__ == "__main__":
    try:
        test_indexheap_recommendation()
        test_comparison_with_traditional()
        test_sorting_consistency()
    except Exception as e:
        print(f"测试出错: {e}")
        import traceback
        traceback.print_exc()
