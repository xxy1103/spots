# -*- coding: utf-8 -*-
"""
测试优化后的日记推荐算法
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from module.user_class import userManager
import time

def test_diary_recommendation_performance():
    """
    测试日记推荐算法的性能
    """
    print("=== 日记推荐算法性能测试 ===")
    
    # 假设用户ID为1
    user_id = 1
    top_k = 10
    
    # 测试优化算法
    print(f"\n测试堆优化算法（用户ID: {user_id}, topK: {top_k}）...")
    start_time = time.time()
    
    try:
        optimized_diaries = userManager.getRecommendDiaries(user_id, top_k)
        optimized_time = time.time() - start_time
        
        print(f"堆优化算法执行时间: {optimized_time:.4f}秒")
        print(f"返回日记数量: {len(optimized_diaries) if optimized_diaries else 0}")
        
        if optimized_diaries:
            print("\n推荐的日记:")
            for i, diary in enumerate(optimized_diaries[:5], 1):  # 只显示前5个
                print(f"  {i}. 日记ID: {diary.id}, 标题: {diary.title[:30]}...")
    
    except Exception as e:
        print(f"堆优化算法执行出错: {e}")
        return
    
    # 测试传统算法
    print(f"\n测试传统算法（用户ID: {user_id}, topK: {top_k}）...")
    start_time = time.time()
    
    try:
        traditional_diaries = userManager.getRecommendDiariesTraditional(user_id, top_k)
        traditional_time = time.time() - start_time
        
        print(f"传统算法执行时间: {traditional_time:.4f}秒")
        print(f"返回日记数量: {len(traditional_diaries) if traditional_diaries else 0}")
        
        if traditional_diaries:
            print("\n推荐的日记:")
            for i, diary in enumerate(traditional_diaries[:5], 1):  # 只显示前5个
                print(f"  {i}. 日记ID: {diary.id}, 标题: {diary.title[:30]}...")
    
    except Exception as e:
        print(f"传统算法执行出错: {e}")
        return
    
    # 性能对比
    if 'optimized_time' in locals() and 'traditional_time' in locals():
        print(f"\n=== 性能对比 ===")
        print(f"堆优化算法时间: {optimized_time:.4f}秒")
        print(f"传统算法时间: {traditional_time:.4f}秒")
        if traditional_time > 0:
            speedup = traditional_time / optimized_time
            print(f"性能提升: {speedup:.2f}倍")

def test_algorithm_correctness():
    """
    测试算法正确性 - 比较两种算法的结果
    """
    print("\n=== 算法正确性测试 ===")
    
    user_id = 1
    top_k = 5
    
    try:
        optimized_result = userManager.getRecommendDiaries(user_id, top_k)
        traditional_result = userManager.getRecommendDiariesTraditional(user_id, top_k)
        
        if not optimized_result or not traditional_result:
            print("警告: 其中一个算法没有返回结果")
            return
        
        print(f"堆优化算法返回 {len(optimized_result)} 个日记")
        print(f"传统算法返回 {len(traditional_result)} 个日记")
        
        # 比较前几个结果的ID
        optimized_ids = [diary.id for diary in optimized_result[:top_k]]
        traditional_ids = [diary.id for diary in traditional_result[:top_k]]
        
        print(f"堆优化算法前{min(top_k, len(optimized_ids))}个日记ID: {optimized_ids}")
        print(f"传统算法前{min(top_k, len(traditional_ids))}个日记ID: {traditional_ids}")
        
        # 检查结果的相似度
        common_ids = set(optimized_ids) & set(traditional_ids)
        print(f"共同推荐的日记数量: {len(common_ids)}")
        
    except Exception as e:
        print(f"正确性测试出错: {e}")

if __name__ == "__main__":
    try:
        test_diary_recommendation_performance()
        test_algorithm_correctness()
    except Exception as e:
        print(f"测试执行出错: {e}")
        import traceback
        traceback.print_exc()
