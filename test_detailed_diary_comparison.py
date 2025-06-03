# -*- coding: utf-8 -*-
"""
详细对比两种日记推荐算法
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from module.user_class import userManager
import time

def detailed_algorithm_comparison():
    """
    详细对比两种算法的推荐结果
    """
    print("=== 详细算法对比 ===")
    
    user_id = 1
    top_k = 10
    
    # 测试堆优化算法
    print(f"\n堆优化算法结果 (topK={top_k}):")
    start_time = time.time()
    optimized_result = userManager.getRecommendDiaries(user_id, top_k)
    optimized_time = time.time() - start_time
    
    if optimized_result:
        print(f"执行时间: {optimized_time:.4f}秒")
        for i, diary in enumerate(optimized_result, 1):
            print(f"  {i}. ID: {diary.id}, 标题: {diary.title[:30]}...")
    
    # 测试传统算法
    print(f"\n传统算法结果 (topK={top_k}):")
    start_time = time.time()
    traditional_result = userManager.getRecommendDiariesTraditional(user_id, top_k)
    traditional_time = time.time() - start_time
    
    if traditional_result:
        print(f"执行时间: {traditional_time:.4f}秒")
        for i, diary in enumerate(traditional_result, 1):
            print(f"  {i}. ID: {diary.id}, 标题: {diary.title[:30]}...")
    
    # 分析结果
    print(f"\n=== 结果分析 ===")
    if optimized_result and traditional_result:
        optimized_ids = set(diary.id for diary in optimized_result)
        traditional_ids = set(diary.id for diary in traditional_result)
        
        print(f"堆优化算法推荐的日记ID: {sorted(list(optimized_ids))}")
        print(f"传统算法推荐的日记ID: {sorted(list(traditional_ids))}")
        
        common = optimized_ids & traditional_ids
        only_optimized = optimized_ids - traditional_ids
        only_traditional = traditional_ids - optimized_ids
        
        print(f"共同推荐: {len(common)} 个日记 {sorted(list(common))}")
        print(f"仅堆优化算法推荐: {len(only_optimized)} 个日记 {sorted(list(only_optimized))}")
        print(f"仅传统算法推荐: {len(only_traditional)} 个日记 {sorted(list(only_traditional))}")

def test_different_topk_values():
    """
    测试不同topK值下的性能
    """
    print(f"\n=== 不同topK值性能测试 ===")
    
    user_id = 1
    topk_values = [5, 10, 20, 50]
    
    for topk in topk_values:
        print(f"\ntopK = {topk}:")
        
        # 堆优化算法
        start_time = time.time()
        optimized_result = userManager.getRecommendDiaries(user_id, topk)
        optimized_time = time.time() - start_time
        
        # 传统算法
        start_time = time.time()
        traditional_result = userManager.getRecommendDiariesTraditional(user_id, topk)
        traditional_time = time.time() - start_time
        
        optimized_count = len(optimized_result) if optimized_result else 0
        traditional_count = len(traditional_result) if traditional_result else 0
        
        print(f"  堆优化: {optimized_time:.4f}秒, 返回{optimized_count}个")
        print(f"  传统算法: {traditional_time:.4f}秒, 返回{traditional_count}个")
        
        if traditional_time > 0 and optimized_time > 0:
            speedup = traditional_time / optimized_time
            print(f"  性能提升: {speedup:.2f}倍")

if __name__ == "__main__":
    try:
        detailed_algorithm_comparison()
        test_different_topk_values()
    except Exception as e:
        print(f"测试出错: {e}")
        import traceback
        traceback.print_exc()
