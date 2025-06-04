# -*- coding: utf-8 -*-
"""
创建测试用户来验证多类型推荐算法性能
"""
import sys
import os
import time

# 添加模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from module.user_class import userManager
from module.Spot_class import spotManager
import module.printLog as log

def create_test_user():
    """
    创建一个有多个喜好类型的测试用户
    """
    # 获取所有可用的景点类型
    available_types = list(spotManager.spotTypeDict.keys())
    print(f"可用景点类型: {available_types}")
    
    # 选择多个类型作为测试用户的喜好
    test_likes = available_types[:5]  # 选择前5个类型
    
    # 添加测试用户
    success = userManager.addUser(
        username="性能测试用户",
        password="test123",
        liketype=test_likes
    )
    
    if success:
        print(f"成功创建测试用户，喜好类型: {test_likes}")
        return userManager.counts  # 返回新用户的ID
    else:
        # 如果用户已存在，查找其ID
        user_info = userManager.searchUser("性能测试用户")
        if user_info:
            return user_info["id"]
        return None

def comprehensive_performance_test(user_id):
    """
    全面的性能测试
    """
    print("="*80)
    print("多类型用户推荐算法综合性能测试")
    print("="*80)
    
    user = userManager.getUser(user_id)
    if not user:
        print("测试用户不存在")
        return
    
    print(f"测试用户: {user.name}")
    print(f"用户喜好类型数量: {len(user.likes_type)}")
    print(f"用户喜好类型: {user.likes_type}")
    
    # 计算每个类型的景点数量
    type_counts = {}
    total_spots = 0
    for spot_type in user.likes_type:
        if spot_type in spotManager.spotTypeDict:
            count = spotManager.spotTypeDict[spot_type]["heap"].size()
            type_counts[spot_type] = count
            total_spots += count
            print(f"  - {spot_type}: {count} 个景点")
    
    print(f"总景点数: {total_spots}")
    print("-"*80)
    
    # 测试不同topK值的性能
    topk_values = [10, 20, 50, 100]
    
    print("性能对比测试:")
    print(f"{'TopK':<8} {'优化算法(ms)':<15} {'传统算法(ms)':<15} {'性能提升':<10} {'结果一致性':<10}")
    print("-"*80)
    
    for topk in topk_values:
        # 测试优化算法
        start_time = time.perf_counter()
        opt_results = userManager.getRecommendSpots(user_id, topk)
        opt_time = (time.perf_counter() - start_time) * 1000  # 转换为毫秒
        
        # 测试传统算法
        start_time = time.perf_counter()
        trad_results = userManager.getRecommendSpotsTraditional(user_id, topk)
        trad_time = (time.perf_counter() - start_time) * 1000  # 转换为毫秒
        
        # 计算性能提升
        improvement = ((trad_time - opt_time) / trad_time) * 100 if trad_time > 0 else 0
        
        # 检查结果一致性
        consistency = "一致"
        if opt_results and trad_results:
            opt_ids = [spot['id'] for spot in opt_results]
            trad_ids = [spot['id'] for spot in trad_results]
            if opt_ids != trad_ids:
                consistency = f"{len(set(opt_ids) & set(trad_ids))}/{min(len(opt_ids), len(trad_ids))}"
        
        print(f"{topk:<8} {opt_time:<15.3f} {trad_time:<15.3f} {improvement:<10.1f}% {consistency:<10}")
    
    print("-"*80)
    
    # 详细展示一个案例的结果
    print(f"\nTopK=20 详细结果对比:")
    opt_results = userManager.getRecommendSpots(user_id, 20)
    trad_results = userManager.getRecommendSpotsTraditional(user_id, 20)
    
    print("\n优化算法前10个结果:")
    for i, spot in enumerate((opt_results or [])[:10]):
        spot_obj = spotManager.getSpot(spot['id'])
        spot_name = spot_obj.name if spot_obj else "未知"
        print(f"  {i+1:2d}. ID:{spot['id']:3d}, 评分:{spot['score']:.2f}, 名称:{spot_name}")
    
    print("\n传统算法前10个结果:")
    for i, spot in enumerate((trad_results or [])[:10]):
        spot_obj = spotManager.getSpot(spot['id'])
        spot_name = spot_obj.name if spot_obj else "未知"
        print(f"  {i+1:2d}. ID:{spot['id']:3d}, 评分:{spot['value1']:.2f}, 名称:{spot_name}")

def algorithm_analysis():
    """
    算法复杂度理论分析
    """
    print("\n" + "="*80)
    print("算法复杂度理论分析")
    print("="*80)
    
    # 使用测试用户进行分析
    test_user = userManager.getUser(userManager.counts)  # 获取最后创建的用户
    if not test_user:
        return
    
    M = len(test_user.likes_type)  # 用户喜好类型数
    
    # 计算平均每类景点数
    total_spots = 0
    max_spots = 0
    for spot_type in test_user.likes_type:
        if spot_type in spotManager.spotTypeDict:
            count = spotManager.spotTypeDict[spot_type]["heap"].size()
            total_spots += count
            max_spots = max(max_spots, count)
    
    avg_N = total_spots // M if M > 0 else 0
    topK = 20
    
    print(f"参数分析:")
    print(f"  用户喜好类型数量 (M): {M}")
    print(f"  平均每类景点数 (N_avg): {avg_N}")
    print(f"  最大类景点数 (N_max): {max_spots}")
    print(f"  总景点数: {total_spots}")
    print(f"  推荐数量 (K): {topK}")
    
    import math
    log_M = math.log2(max(M, 1))
    log_N = math.log2(max(avg_N, 1))
    
    print(f"\n时间复杂度对比:")
    
    # 优化算法复杂度
    opt_complexity = (M + topK) * log_M
    print(f"优化算法: O((M + K) × log M)")
    print(f"  = O(({M} + {topK}) × log₂{M})")
    print(f"  = O({M + topK} × {log_M:.1f})")
    print(f"  ≈ O({opt_complexity:.0f})")
    
    # 传统算法复杂度
    trad_complexity = M * topK * log_N + topK * M * log_M
    print(f"\n传统算法: O(M × K × log N + K × M × log M)")
    print(f"  = O({M} × {topK} × log₂{avg_N} + {topK} × {M} × log₂{M})")
    print(f"  = O({M * topK} × {log_N:.1f} + {topK * M} × {log_M:.1f})")
    print(f"  = O({M * topK * log_N:.0f} + {topK * M * log_M:.0f})")
    print(f"  ≈ O({trad_complexity:.0f})")
    
    if opt_complexity > 0:
        improvement_ratio = trad_complexity / opt_complexity
        print(f"\n理论性能提升: {improvement_ratio:.1f}x")
        print(f"理论复杂度降低: {((trad_complexity - opt_complexity) / trad_complexity) * 100:.1f}%")

if __name__ == "__main__":
    try:
        # 创建测试用户
        test_user_id = create_test_user()
        
        if test_user_id:
            # 运行综合性能测试
            comprehensive_performance_test(test_user_id)
            
            # 运行算法分析
            algorithm_analysis()
        else:
            print("无法创建或找到测试用户")
            
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
