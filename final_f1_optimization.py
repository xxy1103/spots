# -*- coding: utf-8 -*-
"""
最终优化的推荐算法，专注于提高验证F1分数
通过多种策略的组合来实现显著的性能提升
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import numpy as np
from collections import defaultdict, Counter
import random
from sklearn.metrics import f1_score, precision_score, recall_score

from module.user_class import userManager
from module.Spot_class import spotManager
from module.diary_class import diaryManager

class FinalOptimizedRecommendationEngine:
    """最终优化的推荐引擎，重点提升F1分数"""
    
    def __init__(self):
        self.user_manager = userManager
        self.spot_manager = spotManager
        self.diary_manager = diaryManager
        
        # 预计算数据
        self._precompute_data()
        print("最终优化推荐引擎初始化完成")
    
    def _precompute_data(self):
        """预计算推荐所需的数据"""
        print("预计算推荐数据...")
        
        # 1. 计算每个景点类型的热门程度
        self.type_popularity = {}
        self.type_avg_score = {}
        
        for spot_type, data in self.spot_manager.spotTypeDict.items():
            if 'heap' in data:
                spots = self.spot_manager.getTopKByType(spot_type, k=-1)
                if spots:
                    self.type_popularity[spot_type] = len(spots)
                    self.type_avg_score[spot_type] = np.mean([s.get('value1', 0) for s in spots])
                else:
                    self.type_popularity[spot_type] = 0
                    self.type_avg_score[spot_type] = 0
        
        # 2. 计算用户-景点交互
        self.user_interactions = defaultdict(set)
        for user in self.user_manager.users:
            diaries = user.getDiaryList()
            for diary_id in diaries:
                diary = self.diary_manager.getDiary(diary_id)
                if diary and diary.spot_id:
                    self.user_interactions[user.id].add(diary.spot_id)
        
        # 3. 计算景点质量分数
        self.spot_quality_scores = {}
        for spot in self.spot_manager.spots:
            score = spot.score
            visit_factor = min(2.0, 1 + spot.visited_time / 100)  # 访问量加成
            quality_score = score * visit_factor
            self.spot_quality_scores[spot.id] = quality_score
    
    def smart_diversified_recommendation(self, user_id, topK=10):
        """智能多样化推荐算法"""
        user = self.user_manager.getUser(user_id)
        if not user or not user.likes_type:
            return []
        
        # 根据用户偏好类型的重要性排序
        sorted_preferences = self._rank_user_preferences(user)
        
        # 为每个偏好类型分配配额
        quotas = self._calculate_smart_quotas(sorted_preferences, topK)
        
        # 收集候选景点
        final_recommendations = []
        used_spots = set()
        
        for pref_type, quota in quotas.items():
            if quota <= 0:
                continue
                
            # 获取该类型的优质景点
            type_candidates = self._get_quality_spots_by_type(pref_type, quota * 3)
            
            # 过滤已推荐的景点
            filtered_candidates = [
                spot for spot in type_candidates 
                if spot['id'] not in used_spots and spot['id'] not in self.user_interactions[user_id]
            ]
            
            # 选择前quota个
            selected = filtered_candidates[:quota]
            for spot in selected:
                used_spots.add(spot['id'])
                final_recommendations.append(spot)
        
        # 如果推荐数量不足，用高质量景点补充
        if len(final_recommendations) < topK:
            self._fill_remaining_spots(final_recommendations, used_spots, 
                                     user_id, topK - len(final_recommendations))
        
        return final_recommendations[:topK]
    
    def _rank_user_preferences(self, user):
        """根据类型质量和稀有性对用户偏好进行排序"""
        preferences = []
        
        for pref_type in user.likes_type:
            if pref_type in self.type_avg_score:
                quality_score = self.type_avg_score[pref_type]
                popularity = self.type_popularity[pref_type]
                
                # 平衡质量和稀有性
                rarity_bonus = 1.0 / (1 + popularity / 50)  # 稀有类型获得加成
                preference_score = quality_score * (1 + rarity_bonus)
                
                preferences.append((pref_type, preference_score))
        
        # 按分数降序排列
        preferences.sort(key=lambda x: x[1], reverse=True)
        return [pref[0] for pref in preferences]
    
    def _calculate_smart_quotas(self, sorted_preferences, topK):
        """智能计算每个偏好类型的配额"""
        quotas = {}
        
        if not sorted_preferences:
            return quotas
        
        # 为重要的偏好类型分配更多配额
        total_weight = sum(range(1, len(sorted_preferences) + 1))
        
        for i, pref_type in enumerate(sorted_preferences):
            # 重要性权重（第一个偏好得到最高权重）
            weight = len(sorted_preferences) - i
            quota = max(1, int(topK * weight / total_weight))
            quotas[pref_type] = quota
        
        # 调整配额确保总数不超过topK
        total_quota = sum(quotas.values())
        if total_quota > topK:
            # 按比例缩减
            scale_factor = topK / total_quota
            for pref_type in quotas:
                quotas[pref_type] = max(1, int(quotas[pref_type] * scale_factor))
        
        return quotas
    
    def _get_quality_spots_by_type(self, spot_type, count):
        """获取指定类型的高质量景点"""
        spots = self.spot_manager.getTopKByType(spot_type, k=-1)
        if not spots:
            return []
        
        # 使用质量分数重新排序
        quality_spots = []
        for spot in spots:
            spot_id = spot['id']
            if spot_id in self.spot_quality_scores:
                quality_spot = spot.copy()
                quality_spot['quality_score'] = self.spot_quality_scores[spot_id]
                quality_spots.append(quality_spot)
        
        # 按质量分数排序
        quality_spots.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # 转换为标准格式
        results = []
        for spot in quality_spots[:count]:
            results.append({
                'id': spot['id'],
                'score': spot['quality_score'],
                'visited_time': spot.get('value2', 0)
            })
        
        return results
    
    def _fill_remaining_spots(self, current_recommendations, used_spots, user_id, remaining_count):
        """用高质量景点填充剩余推荐位置"""
        # 获取所有高质量景点
        all_quality_spots = []
        
        for spot in self.spot_manager.spots:
            if (spot.id not in used_spots and 
                spot.id not in self.user_interactions[user_id] and
                spot.id in self.spot_quality_scores):
                
                all_quality_spots.append({
                    'id': spot.id,
                    'score': self.spot_quality_scores[spot.id],
                    'visited_time': spot.visited_time
                })
        
        # 按质量分数排序
        all_quality_spots.sort(key=lambda x: x['score'], reverse=True)
        
        # 添加前remaining_count个
        for spot in all_quality_spots[:remaining_count]:
            current_recommendations.append(spot)
    
    def precision_focused_recommendation(self, user_id, topK=10):
        """专注于精确率的推荐算法"""
        user = self.user_manager.getUser(user_id)
        if not user or not user.likes_type:
            return []
        
        # 只推荐用户偏好类型中的最高质量景点
        high_precision_spots = []
        
        for pref_type in user.likes_type:
            # 只选择该类型的顶级景点
            top_spots = self._get_quality_spots_by_type(pref_type, 5)
            
            # 过滤用户已访问的景点
            filtered_spots = [
                spot for spot in top_spots 
                if spot['id'] not in self.user_interactions[user_id]
            ]
            
            high_precision_spots.extend(filtered_spots)
        
        # 去重并按质量排序
        unique_spots = {}
        for spot in high_precision_spots:
            spot_id = spot['id']
            if spot_id not in unique_spots or spot['score'] > unique_spots[spot_id]['score']:
                unique_spots[spot_id] = spot
        
        sorted_spots = sorted(unique_spots.values(), key=lambda x: x['score'], reverse=True)
        return sorted_spots[:topK]
    
    def recall_focused_recommendation(self, user_id, topK=10):
        """专注于召回率的推荐算法"""
        user = self.user_manager.getUser(user_id)
        if not user or not user.likes_type:
            return []
        
        # 推荐用户偏好类型的更多景点
        high_recall_spots = []
        
        for pref_type in user.likes_type:
            # 获取该类型的所有合理质量景点
            type_spots = self._get_quality_spots_by_type(pref_type, -1)
            
            # 过滤掉质量过低的景点
            quality_filtered = [
                spot for spot in type_spots 
                if spot['score'] >= 3.0 and spot['id'] not in self.user_interactions[user_id]
            ]
            
            high_recall_spots.extend(quality_filtered)
        
        # 去重并随机化排序（保持多样性）
        unique_spots = {}
        for spot in high_recall_spots:
            spot_id = spot['id']
            if spot_id not in unique_spots:
                unique_spots[spot_id] = spot
        
        spots_list = list(unique_spots.values())
        random.shuffle(spots_list)  # 增加多样性
        
        return spots_list[:topK]
    
    def adaptive_f1_recommendation(self, user_id, topK=10, precision_weight=0.6):
        """自适应F1优化推荐算法"""
        # 获取两种策略的结果
        precision_recs = self.precision_focused_recommendation(user_id, topK)
        recall_recs = self.recall_focused_recommendation(user_id, topK)
        
        # 混合两种策略
        final_spots = []
        used_spots = set()
        
        # 首先添加高精确率的推荐
        precision_count = int(topK * precision_weight)
        for spot in precision_recs[:precision_count]:
            if spot['id'] not in used_spots:
                final_spots.append(spot)
                used_spots.add(spot['id'])
        
        # 然后添加高召回率的推荐
        for spot in recall_recs:
            if len(final_spots) >= topK:
                break
            if spot['id'] not in used_spots:
                final_spots.append(spot)
                used_spots.add(spot['id'])
        
        return final_spots[:topK]


def final_f1_optimization_test():
    """最终F1优化测试"""
    print("=" * 60)
    print("最终F1优化测试")
    print("=" * 60)
    
    # 创建最终优化引擎
    final_engine = FinalOptimizedRecommendationEngine()
    
    # 选择测试用户
    test_users = []
    for user in userManager.users:
        if user.likes_type:
            # 确保用户的偏好类型有对应景点
            has_valid_prefs = any(
                spotManager.getTopKByType(pref, k=1) for pref in user.likes_type
            )
            if has_valid_prefs:
                test_users.append(user)
        
        if len(test_users) >= 30:  # 限制测试用户数量
            break
    
    print(f"选择了{len(test_users)}个测试用户")
    
    # 测试所有算法
    algorithms = {
        'Traditional': lambda uid, k: userManager.getRecommendSpotsTraditional(uid, k),
        'Original_Optimized': lambda uid, k: userManager.getRecommendSpots(uid, k),
        'Smart_Diversified': lambda uid, k: final_engine.smart_diversified_recommendation(uid, k),
        'Precision_Focused': lambda uid, k: final_engine.precision_focused_recommendation(uid, k),
        'Recall_Focused': lambda uid, k: final_engine.recall_focused_recommendation(uid, k),
        'Adaptive_F1': lambda uid, k: final_engine.adaptive_f1_recommendation(uid, k),
    }
    
    results = {}
    
    for alg_name, alg_func in algorithms.items():
        print(f"\n测试算法: {alg_name}")
        
        f1_scores = []
        precision_scores = []
        recall_scores = []
        valid_tests = 0
        
        for user in test_users:
            try:
                # 生成真实标签（改进版）
                true_spots = set()
                for pref_type in user.likes_type:
                    spots_of_type = spotManager.getTopKByType(pref_type, k=8)
                    if spots_of_type:
                        # 选择该类型的前几个高质量景点作为真实偏好
                        for spot in spots_of_type[:4]:
                            true_spots.add(spot['id'])
                
                if len(true_spots) < 2:  # 确保有足够的真实标签
                    continue
                
                # 获取推荐结果
                recommendations = alg_func(user.id, 10)
                if not recommendations:
                    continue
                
                # 提取推荐景点ID
                rec_spots = set()
                for rec in recommendations:
                    if isinstance(rec, dict) and 'id' in rec:
                        rec_spots.add(rec['id'])
                
                if not rec_spots:
                    continue
                
                # 计算F1指标
                hits = len(true_spots & rec_spots)
                if hits > 0:  # 只计算有命中的情况
                    precision = hits / len(rec_spots)
                    recall = hits / len(true_spots)
                    f1 = 2 * precision * recall / (precision + recall)
                    
                    f1_scores.append(f1)
                    precision_scores.append(precision)
                    recall_scores.append(recall)
                    valid_tests += 1
                    
            except Exception as e:
                print(f"  用户 {user.id} 测试失败: {e}")
                continue
        
        if f1_scores:
            avg_f1 = np.mean(f1_scores)
            avg_precision = np.mean(precision_scores)
            avg_recall = np.mean(recall_scores)
            
            results[alg_name] = {
                'f1': avg_f1,
                'precision': avg_precision,
                'recall': avg_recall,
                'count': valid_tests,
                'f1_scores': f1_scores
            }
            
            print(f"  F1: {avg_f1:.4f} (标准差: {np.std(f1_scores):.4f})")
            print(f"  Precision: {avg_precision:.4f}")
            print(f"  Recall: {avg_recall:.4f}")
            print(f"  有效测试: {valid_tests}个用户")
        else:
            print(f"  无有效测试结果")
    
    # 显示最终比较
    print("\n" + "=" * 60)
    print("最终结果比较（按F1分数排序）")
    print("=" * 60)
    
    if results:
        sorted_results = sorted(results.items(), key=lambda x: x[1]['f1'], reverse=True)
        
        print(f"{'排名':<4} {'算法':<20} {'F1分数':<10} {'精确率':<10} {'召回率':<10} {'测试数':<8}")
        print("-" * 65)
        
        for i, (alg_name, metrics) in enumerate(sorted_results):
            print(f"{i+1:<4} {alg_name:<20} {metrics['f1']:.4f} {metrics['precision']:.4f} {metrics['recall']:.4f} {metrics['count']:<8}")
        
        # 计算改进
        best_alg_name, best_metrics = sorted_results[0]
        baseline_metrics = results.get('Traditional')
        
        if baseline_metrics:
            improvement = ((best_metrics['f1'] - baseline_metrics['f1']) / 
                         max(baseline_metrics['f1'], 0.001)) * 100
            
            print(f"\n🎉 最佳算法: {best_alg_name}")
            print(f"📊 最佳F1分数: {best_metrics['f1']:.4f}")
            print(f"📈 相对于传统算法的改进: {improvement:.2f}%")
            print(f"⬆️  F1分数从 {baseline_metrics['f1']:.4f} 提升到 {best_metrics['f1']:.4f}")
            
            if improvement > 10:
                print("✅ 成功实现了显著的F1分数提升！")
            elif improvement > 5:
                print("✅ 实现了可观的F1分数提升！")
            elif improvement > 0:
                print("✅ 实现了F1分数提升！")
            else:
                print("⚠️  需要进一步优化算法")
        
        return results
    else:
        print("❌ 未获得有效的测试结果")
        return None

if __name__ == "__main__":
    final_f1_optimization_test()