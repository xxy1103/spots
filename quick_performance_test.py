#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速性能验证测试程序
用于快速测试两种推荐算法的基本性能差异
"""

import sys
import os
import time
import random

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from module.user_class import userManager
    from module.Spot_class import spotManager
    print("✅ 成功导入项目模块")
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    sys.exit(1)

def quick_performance_test():
    """快速性能测试"""
    print("🔬 快速性能测试")
    print("=" * 50)
    
    # 测试参数
    spot_types = [
        "遛娃宝藏地",
        "遛娃宝藏地",
        "遛娃宝藏地",
        "遛娃宝藏地",

    ]
    topK_values = [10, 20, 50]
    test_iterations = 5
    
    for topK in topK_values:
        print(f"\n🔍 测试 TopK = {topK}")
        
        traditional_times = []
        optimized_times = []
        
        for i in range(test_iterations):
            # 随机选择用户喜好
            user_likes = random.sample(spot_types, random.randint(2, 4))
            
            # 测试传统算法
            start_time = time.perf_counter()
            try:
                sorted_recommended_spots = []
                for spot_type in user_likes:
                    spots_of_type = spotManager.getTopKByType(spot_type)
                    if spots_of_type:
                        sorted_recommended_spots.append(spots_of_type)
                
                import module.data_structure.kwaymerge as kwaymerge
                merged_list = kwaymerge.k_way_merge_descending(sorted_recommended_spots, topK)
                traditional_result = merged_list[:topK] if merged_list else []
                traditional_time = time.perf_counter() - start_time
                traditional_times.append(traditional_time)
            except Exception as e:
                print(f"❌ 传统算法错误: {e}")
                traditional_times.append(0)
            
            # 测试优化算法
            start_time = time.perf_counter()
            try:
                from module.data_structure.indexHeap import TopKHeap
                from module.data_structure.heap import create_spot_iterator
                
                merge_heap = TopKHeap()
                for spot_type in user_likes:
                    spots_iter = create_spot_iterator(spot_type, spotManager)
                    for spot in spots_iter:
                        spot_id = spot['id']
                        merge_heap.insert(spot_id, spot['score'], spot['visited_time'])
                
                result_data = merge_heap.getTopK(topK)
                optimized_result = [{'id': item['id'], 'score': item['value1'], 'visited_time': item['value2']} for item in result_data]
                optimized_time = time.perf_counter() - start_time
                optimized_times.append(optimized_time)
            except Exception as e:
                print(f"❌ 优化算法错误: {e}")
                optimized_times.append(0)
        
        # 计算平均时间
        avg_traditional = sum(traditional_times) / len(traditional_times) if traditional_times else 0
        avg_optimized = sum(optimized_times) / len(optimized_times) if optimized_times else 0
        
        speedup = avg_traditional / avg_optimized if avg_optimized > 0 else 0
        
        print(f"  传统算法平均时间: {avg_traditional*1000:.3f}ms")
        print(f"  优化算法平均时间: {avg_optimized*1000:.3f}ms")
        print(f"  性能提升倍数: {speedup:.2f}x")
        
        if speedup > 1:
            print(f"  ✅ 优化算法更快")
        elif speedup < 1 and speedup > 0:
            print(f"  ⚠️ 传统算法更快")
        else:
            print(f"  ❌ 测试异常")

if __name__ == "__main__":
    quick_performance_test()
