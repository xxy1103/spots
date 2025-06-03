# -*- coding: utf-8 -*-
"""
测试优化推荐算法的性能对比
"""
import time
import sys
import os

# 添加模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from module.user_class import userManager
from module.Spot_class import spotManager
import module.printLog as log

def test_recommendation_performance():
    """
    测试推荐算法性能对比
    """
    print("="*60)
    print("推荐算法性能测试")
    print("="*60)
    
    # 测试用户ID（假设存在）
    test_user_id = 1
    test_topK = 10
    
    # 确保用户存在
    user = userManager.getUser(test_user_id)
    if user is None:
        print(f"测试用户 {test_user_id} 不存在")
        return
    
    print(f"测试用户: {user.name}")
    print(f"用户喜好类型: {user.likes_type}")
    print(f"请求推荐数量: {test_topK}")
    print("-"*60)
    
    # 测试优化算法
    print("测试优化算法（堆优化）...")
    start_time = time.time()
    optimized_results = userManager.getRecommendSpots(test_user_id, test_topK)
    optimized_time = time.time() - start_time
    
    print(f"优化算法执行时间: {optimized_time:.6f} 秒")
    print(f"返回结果数量: {len(optimized_results) if optimized_results else 0}")
    
    # 测试传统算法
    print("\n测试传统算法（K路归并）...")
    start_time = time.time()
    traditional_results = userManager.getRecommendSpotsTraditional(test_user_id, test_topK)
    traditional_time = time.time() - start_time
    
    print(f"传统算法执行时间: {traditional_time:.6f} 秒")
    print(f"返回结果数量: {len(traditional_results) if traditional_results else 0}")
    
    # 性能提升计算
    if traditional_time > 0:
        improvement = ((traditional_time - optimized_time) / traditional_time) * 100
        print(f"\n性能提升: {improvement:.2f}%")
        print(f"速度倍率: {traditional_time / optimized_time:.2f}x")
    
    print("-"*60)
    
    # 结果对比
    print("结果对比:")
    if optimized_results and traditional_results:
        print("\n优化算法前5个结果:")
        for i, spot in enumerate(optimized_results[:5]):
            print(f"  {i+1}. ID:{spot['id']}, Score:{spot['score']:.2f}")
        
        print("\n传统算法前5个结果:")
        for i, spot in enumerate(traditional_results[:5]):
            print(f"  {i+1}. ID:{spot['id']}, Score:{spot['value1']:.2f}")
        
        # 检查结果一致性
        opt_ids = [spot['id'] for spot in optimized_results]
        trad_ids = [spot['id'] for spot in traditional_results]
        
        if opt_ids == trad_ids:
            print("\n✓ 两种算法结果顺序完全一致")
        else:
            common_ids = set(opt_ids) & set(trad_ids)
            print(f"\n共同推荐景点数: {len(common_ids)}/{min(len(opt_ids), len(trad_ids))}")
    
    print("="*60)

def test_different_topk_values():
    """
    测试不同topK值的性能表现
    """
    print("\n不同topK值性能测试")
    print("="*60)
    
    test_user_id = 1
    topk_values = [5, 10, 20, 50]
    
    for topk in topk_values:
        print(f"\nTopK = {topk}:")
        
        # 优化算法
        start_time = time.time()
        opt_results = userManager.getRecommendSpots(test_user_id, topk)
        opt_time = time.time() - start_time
        
        # 传统算法
        start_time = time.time()
        trad_results = userManager.getRecommendSpotsTraditional(test_user_id, topk)
        trad_time = time.time() - start_time
        
        improvement = ((trad_time - opt_time) / trad_time) * 100 if trad_time > 0 else 0
        
        print(f"  优化算法: {opt_time:.6f}s, 传统算法: {trad_time:.6f}s")
        print(f"  性能提升: {improvement:.2f}%")

def test_algorithm_complexity():
    """
    测试算法复杂度分析
    """
    print("\n算法复杂度理论分析")
    print("="*60)
    
    # 获取测试数据
    test_user = userManager.getUser(1)
    if test_user:
        M = len(test_user.likes_type)  # 用户喜好类型数
        topK = 10
        
        # 估算每个类型的景点数
        total_spots = 0
        for spot_type in test_user.likes_type:
            if spot_type in spotManager.spotTypeDict:
                heap_size = spotManager.spotTypeDict[spot_type]["heap"].size()
                total_spots += heap_size
        
        avg_N = total_spots // M if M > 0 else 0
        
        print(f"用户喜好类型数量 (M): {M}")
        print(f"平均每类景点数 (N): {avg_N}")
        print(f"请求推荐数量 (K): {topK}")
        print(f"总景点数: {total_spots}")
        
        print("\n理论时间复杂度:")
        print(f"优化算法: O((M + K) × log M) ≈ O({M + topK} × {log_estimate(M):.1f}) = O({(M + topK) * log_estimate(M):.0f})")
        print(f"传统算法: O(M × K × log N + K × M × log M) ≈ O({M * topK * log_estimate(avg_N) + topK * M * log_estimate(M):.0f})")

def log_estimate(n):
    """估算log值"""
    import math
    return math.log2(max(n, 1))

if __name__ == "__main__":
    try:
        test_recommendation_performance()
        test_different_topk_values()
        test_algorithm_complexity()
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
