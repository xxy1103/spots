# -*- coding: utf-8 -*-
"""
简化的F1评估测试脚本，用于调试和初步评估
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from module.user_class import userManager
from module.Spot_class import spotManager  
from module.diary_class import diaryManager
import random
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score

def simple_f1_test():
    """简单的F1评估测试"""
    print("=" * 50)
    print("简化F1评估测试")
    print("=" * 50)
    
    # 获取前10个用户进行测试
    test_users = userManager.users[:10] 
    total_f1_opt = []
    total_f1_trad = []
    
    for user in test_users:
        print(f"\n测试用户: {user.name} (ID: {user.id})")
        print(f"用户偏好: {user.likes_type}")
        
        # 生成简单的真实标签 - 基于用户偏好类型
        true_spots = set()
        for spot_type in user.likes_type:
            spots_of_type = spotManager.getTopKByType(spot_type, k=5)  # 每个类型取前5个
            if spots_of_type:
                for spot in spots_of_type:
                    true_spots.add(spot['id'])
        
        if not true_spots:
            print("  没有找到真实偏好景点，跳过")
            continue
        
        print(f"  真实偏好景点数: {len(true_spots)}")
        
        # 测试两种算法
        topK = 10
        
        # 优化算法
        try:
            opt_recommendations = userManager.getRecommendSpots(user.id, topK)
            if opt_recommendations:
                opt_rec_spots = set([rec['id'] for rec in opt_recommendations])
                
                # 计算F1分数
                all_spots = true_spots | opt_rec_spots
                y_true = [1 if spot in true_spots else 0 for spot in all_spots]
                y_pred = [1 if spot in opt_rec_spots else 0 for spot in all_spots]
                
                if len(set(y_true)) > 1:  # 确保有正负样本
                    f1_opt = f1_score(y_true, y_pred, zero_division=0)
                    precision_opt = precision_score(y_true, y_pred, zero_division=0)
                    recall_opt = recall_score(y_true, y_pred, zero_division=0)
                    total_f1_opt.append(f1_opt)
                    
                    hits_opt = len(true_spots & opt_rec_spots)
                    print(f"  优化算法 - F1: {f1_opt:.3f}, P: {precision_opt:.3f}, R: {recall_opt:.3f}, 命中: {hits_opt}")
                else:
                    print("  优化算法 - 无法计算F1 (缺少正负样本)")
            else:
                print("  优化算法 - 无推荐结果")
        except Exception as e:
            print(f"  优化算法错误: {e}")
            
        # 传统算法
        try:
            trad_recommendations = userManager.getRecommendSpotsTraditional(user.id, topK)
            if trad_recommendations:
                trad_rec_spots = set([rec['id'] for rec in trad_recommendations])
                
                # 计算F1分数
                all_spots = true_spots | trad_rec_spots
                y_true = [1 if spot in true_spots else 0 for spot in all_spots]
                y_pred = [1 if spot in trad_rec_spots else 0 for spot in all_spots]
                
                if len(set(y_true)) > 1:  # 确保有正负样本
                    f1_trad = f1_score(y_true, y_pred, zero_division=0)
                    precision_trad = precision_score(y_true, y_pred, zero_division=0)
                    recall_trad = recall_score(y_true, y_pred, zero_division=0)
                    total_f1_trad.append(f1_trad)
                    
                    hits_trad = len(true_spots & trad_rec_spots)
                    print(f"  传统算法 - F1: {f1_trad:.3f}, P: {precision_trad:.3f}, R: {recall_trad:.3f}, 命中: {hits_trad}")
                else:
                    print("  传统算法 - 无法计算F1 (缺少正负样本)")
            else:
                print("  传统算法 - 无推荐结果")
        except Exception as e:
            print(f"  传统算法错误: {e}")
    
    # 总结结果
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    
    if total_f1_opt:
        avg_f1_opt = np.mean(total_f1_opt)
        print(f"优化算法平均F1: {avg_f1_opt:.4f} (测试用户数: {len(total_f1_opt)})")
    else:
        print("优化算法无有效F1分数")
    
    if total_f1_trad:
        avg_f1_trad = np.mean(total_f1_trad)
        print(f"传统算法平均F1: {avg_f1_trad:.4f} (测试用户数: {len(total_f1_trad)})")
    else:
        print("传统算法无有效F1分数")
    
    if total_f1_opt and total_f1_trad:
        improvement = ((avg_f1_opt - avg_f1_trad) / max(avg_f1_trad, 0.001)) * 100
        print(f"性能改进: {improvement:.2f}%")
        
        if avg_f1_opt > avg_f1_trad:
            print("优化算法表现更好")
        else:
            print("传统算法表现更好")
    
    return {
        'opt_f1_scores': total_f1_opt,
        'trad_f1_scores': total_f1_trad,
        'avg_opt_f1': np.mean(total_f1_opt) if total_f1_opt else 0,
        'avg_trad_f1': np.mean(total_f1_trad) if total_f1_trad else 0
    }

if __name__ == "__main__":
    simple_f1_test()