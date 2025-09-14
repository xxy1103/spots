# -*- coding: utf-8 -*-
"""
推荐算法优化模块，专注于提高F1分数
实现多种优化策略来改进推荐质量
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import numpy as np
from collections import defaultdict, Counter
import math
import random
from module.user_class import userManager, UserManager
from module.Spot_class import spotManager
from module.diary_class import diaryManager
from module.data_structure.indexHeap import TopKHeap
from module.data_structure.heap import create_spot_iterator

class EnhancedRecommendationEngine:
    """增强的推荐引擎，实现多种优化策略"""
    
    def __init__(self):
        self.user_manager = userManager
        self.spot_manager = spotManager
        self.diary_manager = diaryManager
        
        # 预计算相关数据
        self._precompute_statistics()
        
    def _precompute_statistics(self):
        """预计算统计数据以优化推荐"""
        print("预计算推荐统计数据...")
        
        # 1. 计算用户-景点交互矩阵
        self.user_spot_interactions = defaultdict(set)
        self.spot_user_interactions = defaultdict(set)
        
        for user in self.user_manager.users:
            user_diaries = user.getDiaryList()
            for diary_id in user_diaries:
                diary = self.diary_manager.getDiary(diary_id)
                if diary and diary.spot_id:
                    self.user_spot_interactions[user.id].add(diary.spot_id)
                    self.spot_user_interactions[diary.spot_id].add(user.id)
        
        # 2. 计算景点流行度（访问频率）
        self.spot_popularity = {}
        for spot_id, users in self.spot_user_interactions.items():
            self.spot_popularity[spot_id] = len(users)
        
        # 3. 计算用户相似度矩阵（基于共同偏好类型）
        self.user_similarity = {}
        users_by_preference = defaultdict(list)
        
        for user in self.user_manager.users:
            for pref in user.likes_type:
                users_by_preference[pref].append(user.id)
        
        # 简化相似度计算
        for user in self.user_manager.users:
            similar_users = set()
            user_prefs = set(user.likes_type)
            
            for other_user in self.user_manager.users:
                if other_user.id != user.id:
                    other_prefs = set(other_user.likes_type)
                    if user_prefs & other_prefs:  # 有共同偏好
                        jaccard_sim = len(user_prefs & other_prefs) / len(user_prefs | other_prefs)
                        if jaccard_sim > 0.3:  # 相似度阈值
                            similar_users.add(other_user.id)
            
            self.user_similarity[user.id] = similar_users
        
        # 4. 计算景点类型权重
        self.type_weights = {}
        total_spots = len(self.spot_manager.spots)
        
        for spot_type, data in self.spot_manager.spotTypeDict.items():
            if 'heap' in data:
                type_count = data['heap'].size()
                # 稀有类型给更高权重
                self.type_weights[spot_type] = math.log(total_spots / max(type_count, 1))
        
        print("统计数据预计算完成")
    
    def diversified_recommendation(self, user_id, topK=10, diversity_factor=0.3):
        """
        多样化推荐算法，平衡准确性和多样性
        
        Args:
            user_id: 用户ID
            topK: 推荐数量
            diversity_factor: 多样性因子 (0-1)
        """
        user = self.user_manager.getUser(user_id)
        if not user:
            return None
        
        user_likes = user.likes_type
        if not user_likes:
            return []
        
        # 1. 获取基础推荐（高准确性）
        base_recommendations = self._get_weighted_recommendations(user_id, topK * 2)
        
        if not base_recommendations:
            return []
        
        # 2. 应用多样性选择
        diversified_results = self._apply_diversity_selection(
            base_recommendations, user_likes, topK, diversity_factor)
        
        return diversified_results
    
    def _get_weighted_recommendations(self, user_id, topK):
        """获取加权推荐结果"""
        user = self.user_manager.getUser(user_id)
        user_likes = user.likes_type
        
        merge_heap = TopKHeap()
        
        # 为每个偏好类型设置权重
        for spot_type in user_likes:
            spots_iter = create_spot_iterator(spot_type, self.spot_manager)
            type_weight = self.type_weights.get(spot_type, 1.0)
            
            for spot in spots_iter:
                spot_id = spot['id']
                base_score = spot['score']
                
                # 应用多种权重
                weighted_score = self._calculate_weighted_score(
                    user_id, spot_id, base_score, type_weight)
                
                merge_heap.insert(spot_id, weighted_score, spot['visited_time'])
        
        result_data = merge_heap.getTopK(topK)
        
        # 转换为标准格式
        result = []
        for item in result_data:
            spot_data = {
                'id': item['id'],
                'score': item['value1'],
                'visited_time': item['value2']
            }
            result.append(spot_data)
        
        return result
    
    def _calculate_weighted_score(self, user_id, spot_id, base_score, type_weight):
        """计算加权分数"""
        score = base_score
        
        # 1. 类型权重
        score *= type_weight
        
        # 2. 流行度调整（避免只推荐热门景点）
        popularity = self.spot_popularity.get(spot_id, 0)
        if popularity > 0:
            # 轻微降低过热门景点的权重
            popularity_factor = 1 / (1 + 0.1 * math.log(popularity + 1))
            score *= popularity_factor
        
        # 3. 协同过滤加成
        cf_boost = self._collaborative_filtering_boost(user_id, spot_id)
        score *= (1 + cf_boost)
        
        # 4. 个性化调整
        personalization_boost = self._personalization_boost(user_id, spot_id)
        score *= (1 + personalization_boost)
        
        return score
    
    def _collaborative_filtering_boost(self, user_id, spot_id):
        """协同过滤加成"""
        boost = 0.0
        similar_users = self.user_similarity.get(user_id, set())
        
        if similar_users:
            spot_visitors = self.spot_user_interactions.get(spot_id, set())
            common_visitors = similar_users & spot_visitors
            
            if common_visitors:
                # 相似用户访问过这个景点，给予加成
                boost = min(0.3, len(common_visitors) * 0.1)
        
        return boost
    
    def _personalization_boost(self, user_id, spot_id):
        """个性化加成"""
        boost = 0.0
        
        # 检查用户是否已经与该景点有交互
        user_visited_spots = self.user_spot_interactions.get(user_id, set())
        
        if spot_id in user_visited_spots:
            # 用户访问过，降低权重避免重复推荐
            boost = -0.2
        else:
            # 用户未访问过，正常推荐
            boost = 0.1
        
        return boost
    
    def _apply_diversity_selection(self, recommendations, user_likes, topK, diversity_factor):
        """应用多样性选择"""
        if len(recommendations) <= topK:
            return recommendations
        
        # 1. 按类型分组
        spots_by_type = defaultdict(list)
        for rec in recommendations:
            spot = self.spot_manager.getSpot(rec['id'])
            if spot:
                spots_by_type[spot.type].append(rec)
        
        # 2. 平衡选择
        selected = []
        type_quotas = self._calculate_type_quotas(user_likes, topK, diversity_factor)
        
        # 从每个类型选择配额数量的景点
        for spot_type, quota in type_quotas.items():
            type_spots = spots_by_type.get(spot_type, [])
            # 按分数排序选择前quota个
            type_spots.sort(key=lambda x: x['score'], reverse=True)
            selected.extend(type_spots[:quota])
        
        # 3. 如果还没达到topK，从剩余的高分景点中选择
        if len(selected) < topK:
            remaining = [rec for rec in recommendations if rec not in selected]
            remaining.sort(key=lambda x: x['score'], reverse=True)
            selected.extend(remaining[:topK - len(selected)])
        
        return selected[:topK]
    
    def _calculate_type_quotas(self, user_likes, topK, diversity_factor):
        """计算每个类型的配额"""
        quotas = {}
        
        if not user_likes:
            return quotas
        
        # 基础配额：平均分配
        base_quota = topK // len(user_likes)
        remaining = topK % len(user_likes)
        
        for i, spot_type in enumerate(user_likes):
            quota = base_quota
            if i < remaining:
                quota += 1
            quotas[spot_type] = max(1, quota)
        
        # 根据多样性因子调整
        if diversity_factor > 0.5:
            # 更注重多样性，进一步平均化
            avg_quota = topK // len(user_likes)
            for spot_type in quotas:
                quotas[spot_type] = max(1, avg_quota)
        
        return quotas
    
    def content_based_recommendation(self, user_id, topK=10):
        """
        基于内容的推荐算法
        重点关注景点属性匹配
        """
        user = self.user_manager.getUser(user_id)
        if not user:
            return None
        
        user_likes = user.likes_type
        if not user_likes:
            return []
        
        # 收集候选景点
        candidates = []
        
        for spot_type in user_likes:
            spots_of_type = self.spot_manager.getTopKByType(spot_type, k=-1)
            if spots_of_type:
                for spot in spots_of_type:
                    content_score = self._calculate_content_score(user, spot)
                    candidates.append({
                        'id': spot['id'],
                        'score': content_score,
                        'visited_time': spot.get('value2', spot.get('visited_time', 0))
                    })
        
        # 去重并排序
        unique_candidates = {}
        for candidate in candidates:
            spot_id = candidate['id']
            if spot_id not in unique_candidates or candidate['score'] > unique_candidates[spot_id]['score']:
                unique_candidates[spot_id] = candidate
        
        # 排序并返回前topK个
        sorted_candidates = sorted(unique_candidates.values(), 
                                 key=lambda x: x['score'], reverse=True)
        
        return sorted_candidates[:topK]
    
    def _calculate_content_score(self, user, spot):
        """计算基于内容的分数"""
        base_score = spot.get('value1', spot.get('score', 0))  # 兼容不同格式
        
        # 获取景点对象
        spot_obj = self.spot_manager.getSpot(spot['id'])
        if not spot_obj:
            return base_score
        
        score = base_score
        
        # 1. 类型匹配度
        if spot_obj.type in user.likes_type:
            score *= 1.2  # 匹配用户偏好的类型
        
        # 2. 评分权重
        if spot_obj.score >= 4.5:
            score *= 1.1  # 高评分景点
        elif spot_obj.score < 3.0:
            score *= 0.8  # 低评分景点降权
        
        # 3. 访问热度调整
        if spot_obj.visited_time > 100:
            score *= 1.05  # 热门景点小幅加成
        elif spot_obj.visited_time < 10:
            score *= 0.9   # 冷门景点降权
        
        return score
    
    def hybrid_recommendation(self, user_id, topK=10, weights=None):
        """
        混合推荐算法，结合多种策略
        
        Args:
            user_id: 用户ID
            topK: 推荐数量
            weights: 各算法权重 {'diversified': 0.4, 'content': 0.3, 'traditional': 0.3}
        """
        if weights is None:
            weights = {'diversified': 0.4, 'content': 0.3, 'traditional': 0.3}
        
        # 获取各算法的推荐结果
        diversified_recs = self.diversified_recommendation(user_id, topK * 2)
        content_recs = self.content_based_recommendation(user_id, topK * 2)
        traditional_recs = self.user_manager.getRecommendSpotsTraditional(user_id, topK * 2)
        
        # 合并和加权
        combined_scores = defaultdict(float)
        spot_data = {}
        
        # 处理多样化推荐结果
        if diversified_recs:
            for i, rec in enumerate(diversified_recs):
                spot_id = rec['id']
                # 位置权重：排名越靠前权重越高
                position_weight = 1.0 / (i + 1)
                combined_scores[spot_id] += weights['diversified'] * rec['score'] * position_weight
                spot_data[spot_id] = rec
        
        # 处理基于内容推荐结果
        if content_recs:
            for i, rec in enumerate(content_recs):
                spot_id = rec['id']
                position_weight = 1.0 / (i + 1)
                combined_scores[spot_id] += weights['content'] * rec['score'] * position_weight
                if spot_id not in spot_data:
                    spot_data[spot_id] = rec
        
        # 处理传统推荐结果
        if traditional_recs:
            for i, rec in enumerate(traditional_recs):
                spot_id = rec['id']
                position_weight = 1.0 / (i + 1)
                score = rec.get('value1', rec.get('score', 0))
                combined_scores[spot_id] += weights['traditional'] * score * position_weight
                if spot_id not in spot_data:
                    spot_data[spot_id] = {
                        'id': spot_id,
                        'score': score,
                        'visited_time': rec.get('value2', rec.get('visited_time', 0))
                    }
        
        # 排序并返回前topK个
        sorted_spots = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        result = []
        for spot_id, final_score in sorted_spots[:topK]:
            if spot_id in spot_data:
                rec_data = spot_data[spot_id].copy()
                rec_data['final_score'] = final_score
                result.append(rec_data)
        
        return result

# 扩展用户管理器，添加优化的推荐方法
class OptimizedUserManager(UserManager):
    """优化的用户管理器，包含增强的推荐算法"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enhanced_engine = EnhancedRecommendationEngine()
    
    def getRecommendSpotsOptimized(self, userId, topK=10, algorithm='hybrid'):
        """
        获取优化的推荐景点
        
        Args:
            userId: 用户ID
            topK: 推荐数量
            algorithm: 算法类型 ('hybrid', 'diversified', 'content')
        """
        if algorithm == 'hybrid':
            return self.enhanced_engine.hybrid_recommendation(userId, topK)
        elif algorithm == 'diversified':
            return self.enhanced_engine.diversified_recommendation(userId, topK)
        elif algorithm == 'content':
            return self.enhanced_engine.content_based_recommendation(userId, topK)
        else:
            # 默认使用原有的优化算法
            return self.getRecommendSpots(userId, topK)

def test_optimized_algorithms():
    """测试优化算法的性能"""
    print("=" * 60)
    print("测试优化推荐算法")
    print("=" * 60)
    
    # 创建优化的用户管理器
    opt_manager = OptimizedUserManager(userManager.users, userManager.counts)
    opt_manager.btree = userManager.btree
    opt_manager.username_trie = userManager.username_trie
    
    # 测试前5个用户
    test_users = userManager.users[:5]
    
    for user in test_users:
        if not user.likes_type:
            continue
            
        print(f"\n用户: {user.name} (偏好: {user.likes_type})")
        
        # 测试不同算法
        algorithms = ['traditional', 'hybrid', 'diversified', 'content']
        
        for alg in algorithms:
            try:
                if alg == 'traditional':
                    recs = userManager.getRecommendSpotsTraditional(user.id, 10)
                else:
                    recs = opt_manager.getRecommendSpotsOptimized(user.id, 10, alg)
                
                if recs:
                    avg_score = np.mean([rec.get('score', rec.get('value1', 0)) for rec in recs])
                    print(f"  {alg:12}: {len(recs):2d}个推荐, 平均分: {avg_score:.3f}")
                else:
                    print(f"  {alg:12}: 无推荐结果")
            except Exception as e:
                print(f"  {alg:12}: 错误 - {e}")

if __name__ == "__main__":
    test_optimized_algorithms()