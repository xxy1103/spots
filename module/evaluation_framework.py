# -*- coding: utf-8 -*-
"""
推荐系统F1评估框架
用于评估景点和日记推荐算法的准确性，并提供F1分数等指标
"""

import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from sklearn.model_selection import KFold
import random
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

# 导入系统模块
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from module.user_class import userManager
from module.Spot_class import spotManager  
from module.diary_class import diaryManager
from module.Model.Model import User

class RecommendationEvaluator:
    """推荐系统评估器，用于计算F1分数和其他评估指标"""
    
    def __init__(self, test_ratio=0.2, random_seed=42):
        """
        初始化评估器
        
        Args:
            test_ratio: 测试集比例
            random_seed: 随机种子
        """
        self.test_ratio = test_ratio
        self.random_seed = random_seed
        random.seed(random_seed)
        np.random.seed(random_seed)
        
        # 创建日志记录器
        self.logger = self._setup_logger()
        
        # 存储评估结果
        self.evaluation_results = {}
        
        # 获取所有用户和景点数据
        self.all_users = userManager.users
        self.all_spots = spotManager.spots
        self.all_diaries = diaryManager.diaries
        
        self.logger.info(f"评估器初始化完成: {len(self.all_users)}个用户, {len(self.all_spots)}个景点, {len(self.all_diaries)}个日记")
    
    def _setup_logger(self):
        """设置日志记录器"""
        logger = logging.getLogger('RecommendationEvaluator')
        logger.setLevel(logging.INFO)
        
        # 创建文件处理器
        log_file = f"evaluation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def generate_ground_truth_data(self, method='user_preference'):
        """
        生成用于评估的真实标签数据
        
        Args:
            method: 生成方法 ('user_preference', 'interaction_based', 'rating_based')
            
        Returns:
            Dict: 包含用户真实偏好的字典
        """
        self.logger.info(f"开始生成真实标签数据，方法: {method}")
        
        ground_truth = {}
        
        if method == 'user_preference':
            # 基于用户偏好类型生成真实标签
            for user in self.all_users:
                user_id = user.id
                user_likes = user.likes_type
                
                # 获取用户偏好类型的所有景点
                true_spots = []
                for spot_type in user_likes:
                    spots_of_type = spotManager.getTopKByType(spot_type, k=-1)
                    if spots_of_type:
                        # 降低评分阈值，选择评分较高的景点作为真实偏好
                        high_rated_spots = [spot for spot in spots_of_type if spot.get('score', 0) >= 3.0]
                        if not high_rated_spots:
                            # 如果没有高评分景点，选择该类型的前50%景点
                            top_half = max(1, len(spots_of_type) // 2)
                            high_rated_spots = spots_of_type[:top_half]
                        true_spots.extend([spot['id'] for spot in high_rated_spots])
                
                ground_truth[user_id] = {
                    'relevant_spots': list(set(true_spots)),
                    'user_preferences': user_likes
                }
                
        elif method == 'interaction_based':
            # 基于用户交互历史生成真实标签
            for user in self.all_users:
                user_id = user.id
                
                # 获取用户的日记列表（表示用户访问过的景点）
                user_diaries = user.getDiaryList()
                visited_spots = []
                
                for diary_id in user_diaries:
                    diary = diaryManager.getDiary(diary_id)
                    if diary and diary.spot_id:
                        visited_spots.append(diary.spot_id)
                
                ground_truth[user_id] = {
                    'relevant_spots': list(set(visited_spots)),
                    'interaction_count': len(user_diaries)
                }
                
        elif method == 'rating_based':
            # 基于用户评分生成真实标签
            for user in self.all_users:
                user_id = user.id
                
                # 获取用户高评分的日记对应的景点
                high_rated_spots = []
                user_diaries = user.getDiaryList()
                
                for diary_id in user_diaries:
                    diary = diaryManager.getDiary(diary_id)
                    if diary and diary.spot_id:
                        # 获取用户对该日记的评分
                        user_rating = user.getDiaryScore(diary_id)
                        if user_rating >= 3.0:  # 降低评分阈值
                            high_rated_spots.append(diary.spot_id)
                
                ground_truth[user_id] = {
                    'relevant_spots': list(set(high_rated_spots)),
                    'rating_method': 'threshold_4.0'
                }
        
        # 过滤掉没有相关景点的用户
        ground_truth = {uid: data for uid, data in ground_truth.items() 
                       if data.get('relevant_spots') and len(data['relevant_spots']) > 0}
        
        self.logger.info(f"真实标签生成完成，有效用户数: {len(ground_truth)}")
        
        # 保存真实标签数据
        self._save_ground_truth(ground_truth, method)
        
        return ground_truth
    
    def _save_ground_truth(self, ground_truth, method):
        """保存真实标签数据到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ground_truth_{method}_{timestamp}.json"
        
        # 转换为可序列化的格式
        serializable_data = {}
        for user_id, data in ground_truth.items():
            serializable_data[str(user_id)] = data
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"真实标签数据已保存到: {filename}")
    
    def evaluate_spot_recommendations(self, ground_truth, topK_values=[10, 20, 50], 
                                    algorithm='optimized'):
        """
        评估景点推荐算法的F1分数
        
        Args:
            ground_truth: 真实标签数据
            topK_values: 不同的推荐数量
            algorithm: 推荐算法类型 ('optimized', 'traditional')
            
        Returns:
            Dict: 评估结果
        """
        self.logger.info(f"开始评估景点推荐算法，算法类型: {algorithm}")
        
        results = {
            'algorithm': algorithm,
            'topK_results': {},
            'overall_metrics': {}
        }
        
        for topK in topK_values:
            self.logger.info(f"评估TopK={topK}的推荐结果")
            
            all_predictions = []
            all_ground_truth = []
            user_metrics = []
            
            valid_users = 0
            total_users = len(ground_truth)
            
            for user_id, true_data in ground_truth.items():
                try:
                    # 获取推荐结果
                    if algorithm == 'optimized':
                        recommendations = userManager.getRecommendSpots(user_id, topK)
                    else:
                        recommendations = userManager.getRecommendSpotsTraditional(user_id, topK)
                    
                    if not recommendations:
                        continue
                    
                    # 提取推荐的景点ID
                    recommended_spots = [rec['id'] for rec in recommendations]
                    true_spots = set(true_data['relevant_spots'])
                    
                    # 创建二进制标签
                    all_spot_ids = list(set(recommended_spots + list(true_spots)))
                    
                    y_true = [1 if spot_id in true_spots else 0 for spot_id in all_spot_ids]
                    y_pred = [1 if spot_id in recommended_spots else 0 for spot_id in all_spot_ids]
                    
                    all_predictions.extend(y_pred)
                    all_ground_truth.extend(y_true)
                    
                    # 计算单个用户的指标
                    if len(set(y_true)) > 1:  # 确保有正负样本
                        user_precision = precision_score(y_true, y_pred, zero_division=0)
                        user_recall = recall_score(y_true, y_pred, zero_division=0)
                        user_f1 = f1_score(y_true, y_pred, zero_division=0)
                        
                        user_metrics.append({
                            'user_id': user_id,
                            'precision': user_precision,
                            'recall': user_recall,
                            'f1': user_f1,
                            'relevant_count': len(true_spots),
                            'recommended_count': len(recommended_spots),
                            'hit_count': len(set(recommended_spots) & true_spots)
                        })
                        
                        valid_users += 1
                        
                except Exception as e:
                    self.logger.warning(f"用户 {user_id} 评估失败: {e}")
                    continue
            
            # 计算整体指标
            if all_predictions and all_ground_truth and len(set(all_ground_truth)) > 1:
                overall_precision = precision_score(all_ground_truth, all_predictions, zero_division=0)
                overall_recall = recall_score(all_ground_truth, all_predictions, zero_division=0)
                overall_f1 = f1_score(all_ground_truth, all_predictions, zero_division=0)
                overall_accuracy = accuracy_score(all_ground_truth, all_predictions)
                
                # 计算平均指标
                if user_metrics:
                    avg_precision = np.mean([m['precision'] for m in user_metrics])
                    avg_recall = np.mean([m['recall'] for m in user_metrics])
                    avg_f1 = np.mean([m['f1'] for m in user_metrics])
                else:
                    avg_precision = avg_recall = avg_f1 = 0.0
                
                results['topK_results'][topK] = {
                    'overall_precision': overall_precision,
                    'overall_recall': overall_recall,
                    'overall_f1': overall_f1,
                    'overall_accuracy': overall_accuracy,
                    'avg_precision': avg_precision,
                    'avg_recall': avg_recall,
                    'avg_f1': avg_f1,
                    'valid_users': valid_users,
                    'total_users': total_users,
                    'user_metrics': user_metrics
                }
                
                self.logger.info(f"TopK={topK} - F1分数: {overall_f1:.4f}, 平均F1: {avg_f1:.4f}")
            else:
                self.logger.warning(f"TopK={topK} - 无法计算指标，数据不足")
                results['topK_results'][topK] = {
                    'error': 'insufficient_data',
                    'valid_users': valid_users,
                    'total_users': total_users
                }
        
        # 计算最佳topK
        valid_results = {k: v for k, v in results['topK_results'].items() 
                        if 'overall_f1' in v}
        
        if valid_results:
            best_topK = max(valid_results.keys(), 
                          key=lambda k: valid_results[k]['overall_f1'])
            results['overall_metrics'] = {
                'best_topK': best_topK,
                'best_f1': valid_results[best_topK]['overall_f1'],
                'best_precision': valid_results[best_topK]['overall_precision'],
                'best_recall': valid_results[best_topK]['overall_recall']
            }
        
        return results
    
    def cross_validate_recommendations(self, ground_truth, cv_folds=5, topK=20):
        """
        使用交叉验证评估推荐算法
        
        Args:
            ground_truth: 真实标签数据
            cv_folds: 交叉验证折数
            topK: 推荐数量
            
        Returns:
            Dict: 交叉验证结果
        """
        self.logger.info(f"开始{cv_folds}折交叉验证，TopK={topK}")
        
        # 准备用户列表
        user_ids = list(ground_truth.keys())
        kf = KFold(n_splits=cv_folds, shuffle=True, random_state=self.random_seed)
        
        cv_results = {
            'optimized': {'f1_scores': [], 'precision_scores': [], 'recall_scores': []},
            'traditional': {'f1_scores': [], 'precision_scores': [], 'recall_scores': []}
        }
        
        for fold, (train_idx, test_idx) in enumerate(kf.split(user_ids)):
            self.logger.info(f"运行第{fold + 1}折验证")
            
            # 获取测试用户
            test_users = [user_ids[i] for i in test_idx]
            test_ground_truth = {uid: ground_truth[uid] for uid in test_users}
            
            # 评估两种算法
            for algorithm in ['optimized', 'traditional']:
                results = self.evaluate_spot_recommendations(
                    test_ground_truth, [topK], algorithm)
                
                if topK in results['topK_results'] and 'overall_f1' in results['topK_results'][topK]:
                    metrics = results['topK_results'][topK]
                    cv_results[algorithm]['f1_scores'].append(metrics['overall_f1'])
                    cv_results[algorithm]['precision_scores'].append(metrics['overall_precision'])
                    cv_results[algorithm]['recall_scores'].append(metrics['overall_recall'])
                else:
                    # 如果评估失败，添加0分
                    cv_results[algorithm]['f1_scores'].append(0.0)
                    cv_results[algorithm]['precision_scores'].append(0.0)
                    cv_results[algorithm]['recall_scores'].append(0.0)
        
        # 计算平均指标和标准差
        summary = {}
        for algorithm in ['optimized', 'traditional']:
            f1_scores = cv_results[algorithm]['f1_scores']
            precision_scores = cv_results[algorithm]['precision_scores']
            recall_scores = cv_results[algorithm]['recall_scores']
            
            summary[algorithm] = {
                'mean_f1': np.mean(f1_scores),
                'std_f1': np.std(f1_scores),
                'mean_precision': np.mean(precision_scores),
                'std_precision': np.std(precision_scores),
                'mean_recall': np.mean(recall_scores),
                'std_recall': np.std(recall_scores),
                'fold_results': cv_results[algorithm]
            }
        
        self.logger.info(f"交叉验证完成")
        self.logger.info(f"优化算法平均F1: {summary['optimized']['mean_f1']:.4f} ± {summary['optimized']['std_f1']:.4f}")
        self.logger.info(f"传统算法平均F1: {summary['traditional']['mean_f1']:.4f} ± {summary['traditional']['std_f1']:.4f}")
        
        return summary
    
    def run_comprehensive_evaluation(self, ground_truth_method='user_preference'):
        """
        运行全面的评估流程
        
        Args:
            ground_truth_method: 真实标签生成方法
            
        Returns:
            Dict: 完整的评估结果
        """
        self.logger.info("开始全面评估流程")
        
        # 1. 生成真实标签
        ground_truth = self.generate_ground_truth_data(ground_truth_method)
        
        if not ground_truth:
            self.logger.error("无法生成有效的真实标签数据")
            return None
        
        # 2. 评估不同topK的性能
        self.logger.info("评估不同TopK值的性能")
        optimized_results = self.evaluate_spot_recommendations(
            ground_truth, [5, 10, 20, 50], 'optimized')
        traditional_results = self.evaluate_spot_recommendations(
            ground_truth, [5, 10, 20, 50], 'traditional')
        
        # 3. 交叉验证
        self.logger.info("进行交叉验证")
        cv_results = self.cross_validate_recommendations(ground_truth, cv_folds=5, topK=20)
        
        # 4. 汇总结果
        final_results = {
            'timestamp': datetime.now().isoformat(),
            'ground_truth_method': ground_truth_method,
            'ground_truth_size': len(ground_truth),
            'optimized_algorithm': optimized_results,
            'traditional_algorithm': traditional_results,
            'cross_validation': cv_results,
            'summary': {
                'best_algorithm': None,
                'improvement_percentage': 0.0,
                'best_f1_score': 0.0
            }
        }
        
        # 确定最佳算法
        opt_best_f1 = optimized_results.get('overall_metrics', {}).get('best_f1', 0)
        trad_best_f1 = traditional_results.get('overall_metrics', {}).get('best_f1', 0)
        
        if opt_best_f1 > trad_best_f1:
            final_results['summary']['best_algorithm'] = 'optimized'
            final_results['summary']['best_f1_score'] = opt_best_f1
            improvement = ((opt_best_f1 - trad_best_f1) / max(trad_best_f1, 0.001)) * 100
        else:
            final_results['summary']['best_algorithm'] = 'traditional'
            final_results['summary']['best_f1_score'] = trad_best_f1
            improvement = ((trad_best_f1 - opt_best_f1) / max(opt_best_f1, 0.001)) * 100
        
        final_results['summary']['improvement_percentage'] = improvement
        
        # 保存结果
        self._save_evaluation_results(final_results)
        
        return final_results
    
    def _save_evaluation_results(self, results):
        """保存评估结果到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"评估结果已保存到: {filename}")
        
        # 生成简要报告
        self._generate_summary_report(results)
    
    def _generate_summary_report(self, results):
        """生成评估摘要报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"evaluation_summary_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 推荐系统F1评估报告\n\n")
            f.write(f"**评估时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n")
            
            f.write("## 评估概要\n\n")
            summary = results.get('summary', {})
            f.write(f"- **最佳算法**: {summary.get('best_algorithm', 'N/A')}\n")
            f.write(f"- **最佳F1分数**: {summary.get('best_f1_score', 0):.4f}\n")
            f.write(f"- **性能提升**: {summary.get('improvement_percentage', 0):.2f}%\n")
            f.write(f"- **评估用户数**: {results.get('ground_truth_size', 0)}\n\n")
            
            f.write("## 交叉验证结果\n\n")
            cv_results = results.get('cross_validation', {})
            for algorithm in ['optimized', 'traditional']:
                if algorithm in cv_results:
                    cv_data = cv_results[algorithm]
                    f.write(f"### {algorithm.title()} 算法\n")
                    f.write(f"- **平均F1分数**: {cv_data.get('mean_f1', 0):.4f} ± {cv_data.get('std_f1', 0):.4f}\n")
                    f.write(f"- **平均精确率**: {cv_data.get('mean_precision', 0):.4f} ± {cv_data.get('std_precision', 0):.4f}\n")
                    f.write(f"- **平均召回率**: {cv_data.get('mean_recall', 0):.4f} ± {cv_data.get('std_recall', 0):.4f}\n\n")
            
            f.write("## 建议\n\n")
            best_f1 = summary.get('best_f1_score', 0)
            if best_f1 < 0.3:
                f.write("F1分数较低，建议：\n")
                f.write("1. 改进特征工程，增加更多用户偏好特征\n")
                f.write("2. 调整推荐算法参数\n")
                f.write("3. 增加训练数据质量\n")
                f.write("4. 考虑集成学习方法\n")
            elif best_f1 < 0.6:
                f.write("F1分数中等，有改进空间：\n")
                f.write("1. 优化算法超参数\n")
                f.write("2. 增加个性化权重\n")
                f.write("3. 改进相似度计算方法\n")
            else:
                f.write("F1分数良好，可考虑：\n")
                f.write("1. 微调算法细节\n")
                f.write("2. 增加多样性考虑\n")
                f.write("3. 实施在线学习\n")
        
        self.logger.info(f"评估摘要报告已生成: {report_file}")


def main():
    """主函数，运行完整的评估流程"""
    print("=" * 60)
    print("推荐系统F1评估框架")
    print("=" * 60)
    
    # 创建评估器
    evaluator = RecommendationEvaluator()
    
    try:
        # 运行全面评估
        results = evaluator.run_comprehensive_evaluation('user_preference')
        
        if results:
            print("\n" + "=" * 60)
            print("评估完成！主要结果：")
            print("=" * 60)
            
            summary = results.get('summary', {})
            print(f"最佳算法: {summary.get('best_algorithm', 'N/A')}")
            print(f"最佳F1分数: {summary.get('best_f1_score', 0):.4f}")
            print(f"性能提升: {summary.get('improvement_percentage', 0):.2f}%")
            
            cv_results = results.get('cross_validation', {})
            if cv_results:
                print("\n交叉验证结果:")
                for algorithm in ['optimized', 'traditional']:
                    if algorithm in cv_results:
                        cv_data = cv_results[algorithm]
                        print(f"{algorithm.title()}: F1={cv_data.get('mean_f1', 0):.4f}±{cv_data.get('std_f1', 0):.4f}")
        else:
            print("评估失败，请检查日志获取详细信息")
            
    except Exception as e:
        print(f"评估过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()