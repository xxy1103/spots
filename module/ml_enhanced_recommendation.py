# -*- coding: utf-8 -*-
"""
机器学习增强的推荐算法，使用协同过滤和矩阵分解技术来提高F1分数
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from scipy.sparse import csr_matrix
import pandas as pd
from collections import defaultdict
import random

from module.user_class import userManager
from module.Spot_class import spotManager
from module.diary_class import diaryManager

class MLEnhancedRecommendationEngine:
    """机器学习增强的推荐引擎"""
    
    def __init__(self):
        self.user_manager = userManager
        self.spot_manager = spotManager
        self.diary_manager = diaryManager
        
        # 构建用户-景点交互矩阵
        self.user_spot_matrix, self.user_to_idx, self.spot_to_idx = self._build_interaction_matrix()
        
        # 训练SVD模型
        self.svd_model = self._train_svd_model()
        
        # 计算用户和景点的相似度矩阵
        self.user_similarity_matrix = self._compute_user_similarity()
        self.spot_similarity_matrix = self._compute_spot_similarity()
        
        print("ML增强推荐引擎初始化完成")
    
    def _build_interaction_matrix(self):
        """构建用户-景点交互矩阵"""
        print("构建用户-景点交互矩阵...")
        
        # 收集所有交互数据
        interactions = []
        user_ids = set()
        spot_ids = set()
        
        for user in self.user_manager.users:
            user_ids.add(user.id)
            user_diaries = user.getDiaryList()
            
            for diary_id in user_diaries:
                diary = self.diary_manager.getDiary(diary_id)
                if diary and diary.spot_id:
                    spot_ids.add(diary.spot_id)
                    # 使用评分作为交互强度，如果没有评分则用默认值
                    rating = user.getDiaryScore(diary_id)
                    if rating == 0:
                        rating = 3.5  # 默认中性评分
                    interactions.append((user.id, diary.spot_id, rating))
        
        # 为每个用户的偏好类型添加隐式交互
        for user in self.user_manager.users:
            for pref_type in user.likes_type:
                spots_of_type = self.spot_manager.getTopKByType(pref_type, k=10)
                if spots_of_type:
                    for spot in spots_of_type[:3]:  # 只取前3个高分景点
                        spot_id = spot['id']
                        spot_ids.add(spot_id)
                        # 添加隐式正面交互（基于偏好类型）
                        implicit_rating = min(5.0, spot.get('value1', 3.0) + 0.5)
                        interactions.append((user.id, spot_id, implicit_rating))
        
        # 创建索引映射
        user_to_idx = {uid: idx for idx, uid in enumerate(sorted(user_ids))}
        spot_to_idx = {sid: idx for idx, sid in enumerate(sorted(spot_ids))}
        
        # 构建稀疏矩阵
        rows, cols, data = [], [], []
        interaction_dict = defaultdict(list)
        
        for user_id, spot_id, rating in interactions:
            interaction_dict[(user_id, spot_id)].append(rating)
        
        # 对重复交互取平均值
        for (user_id, spot_id), ratings in interaction_dict.items():
            if user_id in user_to_idx and spot_id in spot_to_idx:
                rows.append(user_to_idx[user_id])
                cols.append(spot_to_idx[spot_id])
                data.append(np.mean(ratings))
        
        matrix = csr_matrix((data, (rows, cols)), 
                           shape=(len(user_ids), len(spot_ids)))
        
        print(f"交互矩阵构建完成: {matrix.shape}, 非零元素: {matrix.nnz}")
        return matrix, user_to_idx, spot_to_idx
    
    def _train_svd_model(self):
        """训练SVD模型进行矩阵分解"""
        print("训练SVD模型...")
        
        # 使用TruncatedSVD进行降维
        n_components = min(50, min(self.user_spot_matrix.shape) - 1)
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        svd.fit(self.user_spot_matrix)
        
        print(f"SVD模型训练完成，降维到 {n_components} 维")
        return svd
    
    def _compute_user_similarity(self):
        """计算用户相似度矩阵"""
        print("计算用户相似度矩阵...")
        
        # 使用SVD降维后的用户特征计算相似度
        user_features = self.svd_model.transform(self.user_spot_matrix)
        similarity_matrix = cosine_similarity(user_features)
        
        print("用户相似度矩阵计算完成")
        return similarity_matrix
    
    def _compute_spot_similarity(self):
        """计算景点相似度矩阵"""
        print("计算景点相似度矩阵...")
        
        # 转置矩阵计算景点特征
        spot_features = self.svd_model.transform(self.user_spot_matrix.T)
        similarity_matrix = cosine_similarity(spot_features)
        
        print("景点相似度矩阵计算完成")
        return similarity_matrix
    
    def collaborative_filtering_recommendation(self, user_id, topK=10):
        """协同过滤推荐"""
        if user_id not in self.user_to_idx:
            return []
        
        user_idx = self.user_to_idx[user_id]
        
        # 找到最相似的用户
        user_similarities = self.user_similarity_matrix[user_idx]
        similar_users = np.argsort(user_similarities)[::-1][1:11]  # 前10个最相似用户（排除自己）
        
        # 获取相似用户喜欢的景点
        spot_scores = defaultdict(float)
        user_spots = set(self.user_spot_matrix[user_idx].indices)  # 用户已交互的景点
        
        for similar_user_idx in similar_users:
            similarity = user_similarities[similar_user_idx]
            if similarity <= 0:
                continue
                
            # 获取相似用户的景点评分
            user_row = self.user_spot_matrix[similar_user_idx]
            for spot_idx in user_row.indices:
                if spot_idx not in user_spots:  # 推荐用户未交互过的景点
                    rating = user_row[0, spot_idx]
                    spot_scores[spot_idx] += similarity * rating
        
        # 按分数排序并返回topK个景点
        sorted_spots = sorted(spot_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 转换回景点ID
        idx_to_spot = {idx: sid for sid, idx in self.spot_to_idx.items()}
        results = []
        
        for spot_idx, score in sorted_spots[:topK]:
            if spot_idx in idx_to_spot:
                spot_id = idx_to_spot[spot_idx]
                spot_obj = self.spot_manager.getSpot(spot_id)
                if spot_obj:
                    results.append({
                        'id': spot_id,
                        'score': score,
                        'visited_time': spot_obj.visited_time,
                        'cf_score': score
                    })
        
        return results
    
    def matrix_factorization_recommendation(self, user_id, topK=10):
        """矩阵分解推荐"""
        if user_id not in self.user_to_idx:
            return []
        
        user_idx = self.user_to_idx[user_id]
        
        # 使用SVD重构用户对所有景点的评分
        user_vector = self.user_spot_matrix[user_idx].toarray()
        reconstructed = self.svd_model.inverse_transform(
            self.svd_model.transform(user_vector.reshape(1, -1))
        )[0]
        
        # 找到用户未交互过的景点
        user_spots = set(self.user_spot_matrix[user_idx].indices)
        candidates = []
        
        idx_to_spot = {idx: sid for sid, idx in self.spot_to_idx.items()}
        
        for spot_idx, predicted_rating in enumerate(reconstructed):
            if spot_idx not in user_spots and spot_idx in idx_to_spot:
                spot_id = idx_to_spot[spot_idx]
                spot_obj = self.spot_manager.getSpot(spot_id)
                if spot_obj:
                    candidates.append({
                        'id': spot_id,
                        'score': predicted_rating,
                        'visited_time': spot_obj.visited_time,
                        'mf_score': predicted_rating
                    })
        
        # 按预测评分排序
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[:topK]
    
    def hybrid_ml_recommendation(self, user_id, topK=10, cf_weight=0.4, mf_weight=0.4, content_weight=0.2):
        """混合机器学习推荐"""
        # 获取三种推荐结果
        cf_recs = self.collaborative_filtering_recommendation(user_id, topK * 2)
        mf_recs = self.matrix_factorization_recommendation(user_id, topK * 2)
        content_recs = self._get_content_based_recommendations(user_id, topK * 2)
        
        # 合并结果
        spot_scores = defaultdict(lambda: {'score': 0, 'count': 0, 'data': None})
        
        # 处理协同过滤结果
        for i, rec in enumerate(cf_recs):
            spot_id = rec['id']
            position_weight = 1.0 / (i + 1)
            spot_scores[spot_id]['score'] += cf_weight * rec['score'] * position_weight
            spot_scores[spot_id]['count'] += 1
            spot_scores[spot_id]['data'] = rec
        
        # 处理矩阵分解结果
        for i, rec in enumerate(mf_recs):
            spot_id = rec['id']
            position_weight = 1.0 / (i + 1)
            spot_scores[spot_id]['score'] += mf_weight * rec['score'] * position_weight
            spot_scores[spot_id]['count'] += 1
            if spot_scores[spot_id]['data'] is None:
                spot_scores[spot_id]['data'] = rec
        
        # 处理基于内容的结果
        for i, rec in enumerate(content_recs):
            spot_id = rec['id']
            position_weight = 1.0 / (i + 1)
            spot_scores[spot_id]['score'] += content_weight * rec['score'] * position_weight
            spot_scores[spot_id]['count'] += 1
            if spot_scores[spot_id]['data'] is None:
                spot_scores[spot_id]['data'] = rec
        
        # 归一化分数并排序
        for spot_id in spot_scores:
            if spot_scores[spot_id]['count'] > 0:
                spot_scores[spot_id]['score'] /= spot_scores[spot_id]['count']
        
        sorted_spots = sorted(spot_scores.items(), 
                            key=lambda x: x[1]['score'], reverse=True)
        
        # 构建最终结果
        results = []
        for spot_id, data in sorted_spots[:topK]:
            if data['data']:
                result = data['data'].copy()
                result['hybrid_score'] = data['score']
                results.append(result)
        
        return results
    
    def _get_content_based_recommendations(self, user_id, topK):
        """获取基于内容的推荐（简化版）"""
        user = self.user_manager.getUser(user_id)
        if not user or not user.likes_type:
            return []
        
        candidates = []
        for pref_type in user.likes_type:
            spots_of_type = self.spot_manager.getTopKByType(pref_type, k=topK)
            if spots_of_type:
                for spot in spots_of_type:
                    candidates.append({
                        'id': spot['id'],
                        'score': spot.get('value1', 0),
                        'visited_time': spot.get('value2', 0)
                    })
        
        # 去重并排序
        unique_spots = {}
        for candidate in candidates:
            spot_id = candidate['id']
            if spot_id not in unique_spots or candidate['score'] > unique_spots[spot_id]['score']:
                unique_spots[spot_id] = candidate
        
        sorted_candidates = sorted(unique_spots.values(), 
                                 key=lambda x: x['score'], reverse=True)
        return sorted_candidates[:topK]


def enhanced_f1_test():
    """测试增强的机器学习推荐算法的F1性能"""
    print("=" * 60)
    print("机器学习增强推荐算法F1测试")
    print("=" * 60)
    
    # 创建ML推荐引擎
    ml_engine = MLEnhancedRecommendationEngine()
    
    # 选择测试用户
    test_users = [user for user in userManager.users[:20] 
                  if user.likes_type and any(spotManager.getTopKByType(pref, k=1) 
                                           for pref in user.likes_type)]
    
    print(f"选择了{len(test_users)}个测试用户")
    
    # 测试不同算法
    algorithms = {
        'Traditional': lambda uid, k: userManager.getRecommendSpotsTraditional(uid, k),
        'ML_Collaborative': lambda uid, k: ml_engine.collaborative_filtering_recommendation(uid, k),
        'ML_MatrixFactorization': lambda uid, k: ml_engine.matrix_factorization_recommendation(uid, k),
        'ML_Hybrid': lambda uid, k: ml_engine.hybrid_ml_recommendation(uid, k),
    }
    
    results = {}
    
    for alg_name, alg_func in algorithms.items():
        print(f"\n测试算法: {alg_name}")
        
        f1_scores = []
        precision_scores = []
        recall_scores = []
        
        for user in test_users:
            try:
                # 生成真实标签
                true_spots = set()
                for pref_type in user.likes_type:
                    spots_of_type = spotManager.getTopKByType(pref_type, k=5)
                    if spots_of_type:
                        for spot in spots_of_type[:3]:
                            true_spots.add(spot['id'])
                
                if not true_spots:
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
                all_spots = true_spots | rec_spots
                y_true = [1 if spot in true_spots else 0 for spot in all_spots]
                y_pred = [1 if spot in rec_spots else 0 for spot in all_spots]
                
                if len(set(y_true)) > 1:
                    from sklearn.metrics import f1_score, precision_score, recall_score
                    f1 = f1_score(y_true, y_pred, zero_division=0)
                    precision = precision_score(y_true, y_pred, zero_division=0)
                    recall = recall_score(y_true, y_pred, zero_division=0)
                    
                    f1_scores.append(f1)
                    precision_scores.append(precision)
                    recall_scores.append(recall)
                    
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
                'count': len(f1_scores)
            }
            
            print(f"  F1: {avg_f1:.4f}")
            print(f"  Precision: {avg_precision:.4f}")
            print(f"  Recall: {avg_recall:.4f}")
            print(f"  有效测试: {len(f1_scores)}个用户")
        else:
            print(f"  无有效测试结果")
    
    # 显示最终比较
    print("\n" + "=" * 60)
    print("最终结果比较")
    print("=" * 60)
    
    if results:
        sorted_results = sorted(results.items(), key=lambda x: x[1]['f1'], reverse=True)
        
        for i, (alg_name, metrics) in enumerate(sorted_results):
            print(f"{i+1}. {alg_name}: F1={metrics['f1']:.4f}, "
                  f"P={metrics['precision']:.4f}, R={metrics['recall']:.4f}")
        
        # 计算最佳算法的改进
        if len(sorted_results) >= 2:
            best_f1 = sorted_results[0][1]['f1']
            baseline_f1 = results.get('Traditional', {}).get('f1', 0)
            
            if baseline_f1 > 0:
                improvement = ((best_f1 - baseline_f1) / baseline_f1) * 100
                print(f"\n最佳算法相对于传统算法的改进: {improvement:.2f}%")
                print(f"F1分数从 {baseline_f1:.4f} 提升到 {best_f1:.4f}")
            
    return results

if __name__ == "__main__":
    enhanced_f1_test()