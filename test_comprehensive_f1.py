# -*- coding: utf-8 -*-
"""
全面的F1评估脚本，测试所有推荐算法的性能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from module.user_class import userManager
from module.Spot_class import spotManager  
from module.diary_class import diaryManager
from module.optimization_algorithms import OptimizedUserManager, EnhancedRecommendationEngine
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import time
import json
from datetime import datetime

class ComprehensiveF1Evaluator:
    """全面的F1评估器"""
    
    def __init__(self):
        # 原始管理器
        self.original_manager = userManager
        
        # 优化管理器
        self.optimized_manager = OptimizedUserManager(userManager.users, userManager.counts)
        self.optimized_manager.btree = userManager.btree
        self.optimized_manager.username_trie = userManager.username_trie
        
        # 测试用户（选择有偏好且偏好类型存在的用户）
        self.test_users = self._select_test_users(50)  # 选择50个测试用户
        
        print(f"初始化完成，选择了{len(self.test_users)}个测试用户")
    
    def _select_test_users(self, max_users):
        """选择适合测试的用户"""
        valid_users = []
        
        for user in userManager.users:
            if not user.likes_type:
                continue
            
            # 检查用户偏好是否存在对应景点
            has_valid_preference = False
            for pref in user.likes_type:
                spots = spotManager.getTopKByType(pref, k=1)
                if spots:
                    has_valid_preference = True
                    break
            
            if has_valid_preference:
                valid_users.append(user)
                
            if len(valid_users) >= max_users:
                break
        
        return valid_users
    
    def generate_ground_truth(self, user):
        """为单个用户生成真实标签"""
        true_spots = set()
        
        for spot_type in user.likes_type:
            spots_of_type = spotManager.getTopKByType(spot_type, k=10)  # 每个类型前10个
            if spots_of_type:
                for spot in spots_of_type[:5]:  # 只取前5个作为真实偏好
                    true_spots.add(spot['id'])
        
        return true_spots
    
    def evaluate_algorithm(self, algorithm_name, algorithm_func, topK=10):
        """评估单个算法"""
        print(f"评估算法: {algorithm_name}")
        
        f1_scores = []
        precision_scores = []
        recall_scores = []
        execution_times = []
        valid_users = 0
        
        for user in self.test_users:
            try:
                # 生成真实标签
                true_spots = self.generate_ground_truth(user)
                if not true_spots:
                    continue
                
                # 执行推荐算法并计时
                start_time = time.time()
                recommendations = algorithm_func(user.id, topK)
                execution_time = time.time() - start_time
                execution_times.append(execution_time)
                
                if not recommendations:
                    continue
                
                # 提取推荐景点ID
                rec_spots = set()
                for rec in recommendations:
                    if isinstance(rec, dict):
                        spot_id = rec.get('id')
                        if spot_id:
                            rec_spots.add(spot_id)
                
                if not rec_spots:
                    continue
                
                # 计算指标
                all_spots = true_spots | rec_spots
                y_true = [1 if spot in true_spots else 0 for spot in all_spots]
                y_pred = [1 if spot in rec_spots else 0 for spot in all_spots]
                
                if len(set(y_true)) > 1:  # 确保有正负样本
                    f1 = f1_score(y_true, y_pred, zero_division=0)
                    precision = precision_score(y_true, y_pred, zero_division=0)
                    recall = recall_score(y_true, y_pred, zero_division=0)
                    
                    f1_scores.append(f1)
                    precision_scores.append(precision)
                    recall_scores.append(recall)
                    valid_users += 1
                    
            except Exception as e:
                print(f"  用户 {user.id} 评估失败: {e}")
                continue
        
        # 计算统计结果
        if f1_scores:
            result = {
                'algorithm': algorithm_name,
                'valid_users': valid_users,
                'total_users': len(self.test_users),
                'avg_f1': np.mean(f1_scores),
                'std_f1': np.std(f1_scores),
                'avg_precision': np.mean(precision_scores),
                'std_precision': np.std(precision_scores),
                'avg_recall': np.mean(recall_scores),
                'std_recall': np.std(recall_scores),
                'avg_execution_time': np.mean(execution_times),
                'std_execution_time': np.std(execution_times),
                'f1_scores': f1_scores,
                'precision_scores': precision_scores,
                'recall_scores': recall_scores
            }
            
            print(f"  F1: {result['avg_f1']:.4f}±{result['std_f1']:.4f}")
            print(f"  Precision: {result['avg_precision']:.4f}±{result['std_precision']:.4f}")
            print(f"  Recall: {result['avg_recall']:.4f}±{result['std_recall']:.4f}")
            print(f"  执行时间: {result['avg_execution_time']:.4f}±{result['std_execution_time']:.4f}s")
            print(f"  有效用户: {valid_users}/{len(self.test_users)}")
            
            return result
        else:
            print("  无有效评估结果")
            return None
    
    def run_comprehensive_evaluation(self):
        """运行全面评估"""
        print("=" * 60)
        print("开始全面F1评估")
        print("=" * 60)
        
        # 定义所有要测试的算法
        algorithms = {
            'Traditional': lambda uid, k: self.original_manager.getRecommendSpotsTraditional(uid, k),
            'Original_Optimized': lambda uid, k: self.original_manager.getRecommendSpots(uid, k),
            'Hybrid': lambda uid, k: self.optimized_manager.getRecommendSpotsOptimized(uid, k, 'hybrid'),
            'Diversified': lambda uid, k: self.optimized_manager.getRecommendSpotsOptimized(uid, k, 'diversified'),
            'Content_Based': lambda uid, k: self.optimized_manager.getRecommendSpotsOptimized(uid, k, 'content'),
        }
        
        results = {}
        
        # 评估每个算法
        for name, func in algorithms.items():
            result = self.evaluate_algorithm(name, func, topK=10)
            if result:
                results[name] = result
            print()
        
        # 生成比较报告
        self.generate_comparison_report(results)
        
        # 生成可视化图表
        self.generate_visualization(results)
        
        return results
    
    def generate_comparison_report(self, results):
        """生成比较报告"""
        print("=" * 60)
        print("算法比较报告")
        print("=" * 60)
        
        if not results:
            print("无有效评估结果")
            return
        
        # 排序算法（按F1分数）
        sorted_algorithms = sorted(results.items(), 
                                 key=lambda x: x[1]['avg_f1'], reverse=True)
        
        print("算法性能排名（按平均F1分数）:")
        print("-" * 60)
        print(f"{'排名':<4} {'算法':<15} {'F1分数':<12} {'精确率':<12} {'召回率':<12} {'执行时间(ms)':<12}")
        print("-" * 60)
        
        for i, (name, result) in enumerate(sorted_algorithms):
            f1_str = f"{result['avg_f1']:.4f}±{result['std_f1']:.3f}"
            precision_str = f"{result['avg_precision']:.4f}±{result['std_precision']:.3f}"
            recall_str = f"{result['avg_recall']:.4f}±{result['std_recall']:.3f}"
            time_str = f"{result['avg_execution_time']*1000:.2f}±{result['std_execution_time']*1000:.2f}"
            
            print(f"{i+1:<4} {name:<15} {f1_str:<12} {precision_str:<12} {recall_str:<12} {time_str:<12}")
        
        print("-" * 60)
        
        # 计算改进
        if len(sorted_algorithms) >= 2:
            best_alg = sorted_algorithms[0]
            baseline_alg = None
            
            # 找到传统算法作为基线
            for name, result in sorted_algorithms:
                if 'Traditional' in name:
                    baseline_alg = (name, result)
                    break
            
            if baseline_alg:
                improvement = ((best_alg[1]['avg_f1'] - baseline_alg[1]['avg_f1']) / 
                             max(baseline_alg[1]['avg_f1'], 0.001)) * 100
                print(f"\n最佳算法 {best_alg[0]} 相对于传统算法的改进: {improvement:.2f}%")
                print(f"F1分数从 {baseline_alg[1]['avg_f1']:.4f} 提升到 {best_alg[1]['avg_f1']:.4f}")
        
        # 保存详细结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_f1_evaluation_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细结果已保存到: {filename}")
    
    def generate_visualization(self, results):
        """生成可视化图表"""
        if not results:
            return
        
        print("生成可视化图表...")
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('推荐算法F1评估结果对比', fontsize=16, fontweight='bold')
        
        algorithms = list(results.keys())
        f1_means = [results[alg]['avg_f1'] for alg in algorithms]
        f1_stds = [results[alg]['std_f1'] for alg in algorithms]
        precision_means = [results[alg]['avg_precision'] for alg in algorithms]
        recall_means = [results[alg]['avg_recall'] for alg in algorithms]
        
        # 1. F1分数对比
        bars1 = ax1.bar(algorithms, f1_means, yerr=f1_stds, capsize=5, alpha=0.7)
        ax1.set_title('F1分数对比')
        ax1.set_ylabel('F1分数')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)
        
        # 为每个柱子添加数值标签
        for bar, mean in zip(bars1, f1_means):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{mean:.3f}', ha='center', va='bottom')
        
        # 2. 精确率 vs 召回率
        ax2.scatter(precision_means, recall_means, s=100, alpha=0.7)
        for i, alg in enumerate(algorithms):
            ax2.annotate(alg, (precision_means[i], recall_means[i]), 
                        xytext=(5, 5), textcoords='offset points')
        ax2.set_xlabel('精确率')
        ax2.set_ylabel('召回率')
        ax2.set_title('精确率 vs 召回率')
        ax2.grid(True, alpha=0.3)
        
        # 3. 执行时间对比
        exec_times = [results[alg]['avg_execution_time'] * 1000 for alg in algorithms]
        exec_stds = [results[alg]['std_execution_time'] * 1000 for alg in algorithms]
        bars3 = ax3.bar(algorithms, exec_times, yerr=exec_stds, capsize=5, alpha=0.7, color='orange')
        ax3.set_title('平均执行时间对比')
        ax3.set_ylabel('执行时间 (毫秒)')
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, alpha=0.3)
        
        # 4. F1分数分布箱线图
        f1_data = [results[alg]['f1_scores'] for alg in algorithms]
        bp = ax4.boxplot(f1_data, labels=algorithms, patch_artist=True)
        ax4.set_title('F1分数分布')
        ax4.set_ylabel('F1分数')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True, alpha=0.3)
        
        # 设置箱线图颜色
        colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink']
        for patch, color in zip(bp['boxes'], colors[:len(bp['boxes'])]):
            patch.set_facecolor(color)
        
        plt.tight_layout()
        
        # 保存图表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_filename = f"f1_evaluation_charts_{timestamp}.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"图表已保存到: {chart_filename}")

def main():
    """主函数"""
    print("推荐系统F1评估 - 全面测试")
    print("=" * 60)
    
    try:
        evaluator = ComprehensiveF1Evaluator()
        results = evaluator.run_comprehensive_evaluation()
        
        if results:
            print("\n评估完成！")
            
            # 找出最佳算法
            best_alg = max(results.items(), key=lambda x: x[1]['avg_f1'])
            print(f"最佳算法: {best_alg[0]}")
            print(f"最佳F1分数: {best_alg[1]['avg_f1']:.4f}")
            
            # 如果有传统算法结果，显示改进
            if 'Traditional' in results:
                improvement = ((best_alg[1]['avg_f1'] - results['Traditional']['avg_f1']) / 
                             max(results['Traditional']['avg_f1'], 0.001)) * 100
                print(f"相对于传统算法的改进: {improvement:.2f}%")
        else:
            print("评估失败，未获得有效结果")
            
    except Exception as e:
        print(f"评估过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()