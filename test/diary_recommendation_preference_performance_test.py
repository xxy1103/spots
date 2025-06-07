"""
日记推荐系统用户偏好标签数量性能测试
测试不同偏好标签数量（0-5）对推荐算法性能的影响
"""

import sys
import os
import time
import random
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import json
from datetime import datetime

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 导入必要的模块
from module.user_class import UserManager
from module.diary_class import DiaryManager
from module.Spot_class import SpotManager
from module.Model.Model import User

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class DiaryRecommendationPreferenceTest:
    def __init__(self):
        """初始化测试环境"""
        # 使用全局管理器实例
        from module.user_class import userManager
        from module.diary_class import diaryManager  
        from module.Spot_class import spotManager
        
        self.user_manager = userManager
        self.diary_manager = diaryManager
        self.spot_manager = spotManager
        
        # 测试配置
        self.preference_counts = list(range(0, 6))  # 0-5个偏好标签
        self.test_iterations = 10  # 每种情况测试10次
        self.topK = 20  # 推荐日记数量
        
        # 可用的偏好类型
        self.available_preferences = [
            "自然风光", "历史文化", "美食体验", "休闲娱乐", 
            "户外运动", "购物观光", "艺术展览", "宗教文化"
        ]
          # 测试结果存储
        self.test_results = defaultdict(list)        
        self.performance_metrics = {}
        
    def create_test_user(self, preference_count):
        """创建具有指定偏好数量的测试用户"""
        if preference_count == 0:
            likes_type = []
        else:
            # 随机选择指定数量的偏好类型
            likes_type = random.sample(self.available_preferences, 
                                     min(preference_count, len(self.available_preferences)))
        
        # 使用现有用户数量+1作为用户ID，确保能被getUser方法找到
        user_id = len(self.user_manager.users) + 1
        test_user = User(
            user_id=user_id,
            name=f"测试用户_{preference_count}偏好_{user_id}",
            password="test123",
            likes_type=likes_type
        )
        return test_user
    def measure_recommendation_performance(self, user, iterations=1):
        """测量推荐算法性能"""
        times = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            
            try:
                # 执行日记推荐算法
                recommended_diaries = self.user_manager.getRecommendDiariesTraditional(
                    user.id, self.topK
                )
                
                end_time = time.perf_counter()
                execution_time = (end_time - start_time) * 1000  # 转换为毫秒
                times.append(execution_time)
                
            except Exception as e:
                print(f"推荐算法执行错误: {e}")
                times.append(0)  # 记录为0表示失败
        
        return times
    
    def run_comprehensive_test(self):
        """运行综合性能测试"""
        print("开始日记推荐系统偏好标签数量性能测试...")
        print("=" * 60)
        
        total_tests = len(self.preference_counts) * self.test_iterations
        current_test = 0
        
        for preference_count in self.preference_counts:
            print(f"\n测试偏好标签数量: {preference_count}")
            print("-" * 40)
            
            test_times = []
            
            for iteration in range(self.test_iterations):
                current_test += 1
                progress = (current_test / total_tests) * 100
                print(f"进度: {progress:.1f}% - 第{iteration + 1}次测试")
                
                # 创建测试用户
                test_user = self.create_test_user(preference_count)
                  # 先注册用户到系统中
                self.user_manager.users.append(test_user)
                
                # 测量性能
                times = self.measure_recommendation_performance(test_user, 1)
                if times and times[0] > 0:
                    test_times.extend(times)
                
                # 清理测试用户
                if test_user in self.user_manager.users:
                    self.user_manager.users.remove(test_user)
            
            # 存储结果
            self.test_results[preference_count] = test_times
            
            if test_times:
                avg_time = np.mean(test_times)
                std_time = np.std(test_times)
                min_time = np.min(test_times)
                max_time = np.max(test_times)
                
                print(f"平均执行时间: {avg_time:.3f} ms")
                print(f"标准差: {std_time:.3f} ms")
                print(f"最小时间: {min_time:.3f} ms")
                print(f"最大时间: {max_time:.3f} ms")
                
                self.performance_metrics[preference_count] = {
                    'average': avg_time,
                    'std': std_time,
                    'min': min_time,
                    'max': max_time,
                    'count': len(test_times)
                }
            else:
                print("测试失败，无有效数据")
                self.performance_metrics[preference_count] = {
                    'average': 0,
                    'std': 0,
                    'min': 0,
                    'max': 0,
                    'count': 0
                }
    
    def generate_visualizations(self):
        """生成性能分析图表"""
        print("\n生成性能分析图表...")
        
        # 准备数据
        preference_counts = []
        avg_times = []
        std_times = []
        
        for count in self.preference_counts:
            if count in self.performance_metrics:
                preference_counts.append(count)
                avg_times.append(self.performance_metrics[count]['average'])
                std_times.append(self.performance_metrics[count]['std'])
        
        # 创建图表
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('日记推荐系统偏好标签数量性能分析', fontsize=16, fontweight='bold')
        
        # 1. 平均执行时间趋势图
        ax1.plot(preference_counts, avg_times, 'b-o', linewidth=2, markersize=8)
        ax1.fill_between(preference_counts, 
                        [avg - std for avg, std in zip(avg_times, std_times)],
                        [avg + std for avg, std in zip(avg_times, std_times)],
                        alpha=0.3)
        ax1.set_xlabel('偏好标签数量')
        ax1.set_ylabel('平均执行时间 (ms)')
        ax1.set_title('平均执行时间 vs 偏好标签数量')
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(preference_counts)
        
        # 2. 执行时间分布箱线图
        box_data = [self.test_results[count] for count in preference_counts if self.test_results[count]]
        if box_data:
            bp = ax2.boxplot(box_data, labels=preference_counts, patch_artist=True)
            for patch in bp['boxes']:
                patch.set_facecolor('lightblue')
        ax2.set_xlabel('偏好标签数量')
        ax2.set_ylabel('执行时间 (ms)')
        ax2.set_title('执行时间分布')
        ax2.grid(True, alpha=0.3)
        
        # 3. 性能变化率分析
        if len(avg_times) > 1:
            change_rates = [(avg_times[i] - avg_times[0]) / avg_times[0] * 100 
                           for i in range(len(avg_times))]
            ax3.bar(preference_counts, change_rates, alpha=0.7, 
                   color=['red' if x > 0 else 'green' for x in change_rates])
            ax3.set_xlabel('偏好标签数量')
            ax3.set_ylabel('性能变化率 (%)')
            ax3.set_title('相对于0偏好的性能变化')
            ax3.grid(True, alpha=0.3)
            ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            ax3.set_xticks(preference_counts)
        
        # 4. 算法复杂度分析
        if len(preference_counts) > 2:
            # 拟合多项式
            coeffs = np.polyfit(preference_counts, avg_times, 2)
            polynomial = np.poly1d(coeffs)
            x_smooth = np.linspace(min(preference_counts), max(preference_counts), 100)
            y_smooth = polynomial(x_smooth)
            
            ax4.scatter(preference_counts, avg_times, color='red', s=50, label='实测数据')
            ax4.plot(x_smooth, y_smooth, 'b--', label='二次拟合')
            ax4.set_xlabel('偏好标签数量')
            ax4.set_ylabel('平均执行时间 (ms)')
            ax4.set_title('算法复杂度趋势分析')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图表
        chart_path = os.path.join(current_dir, 'diary_recommendation_preference_performance.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存至: {chart_path}")
        
        return chart_path
    
    def generate_report(self, chart_path):
        """生成详细的性能分析报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(current_dir, f'diary_recommendation_preference_analysis_{timestamp}.md')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 日记推荐系统偏好标签数量性能分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write(f"**测试版本**: 偏好标签数量性能测试 v1.0\n\n")
            
            f.write("## 测试概述\n\n")
            f.write("本报告分析了日记推荐系统在不同用户偏好标签数量（0-5个）下的性能表现。")
            f.write("通过系统性的性能测试，评估偏好标签数量对推荐算法执行时间的影响。\n\n")
            
            f.write("## 测试配置\n\n")
            f.write(f"- **偏好标签数量范围**: 0-5个\n")
            f.write(f"- **每种情况测试次数**: {self.test_iterations}次\n")
            f.write(f"- **推荐日记数量**: {self.topK}条\n")
            f.write(f"- **测试总次数**: {len(self.preference_counts) * self.test_iterations}次\n\n")
            
            f.write("## 详细测试结果\n\n")
            f.write("| 偏好标签数量 | 平均时间(ms) | 标准差(ms) | 最小时间(ms) | 最大时间(ms) | 测试次数 |\n")
            f.write("|-------------|-------------|-----------|-------------|-------------|----------|\n")
            
            for count in self.preference_counts:
                if count in self.performance_metrics:
                    metrics = self.performance_metrics[count]
                    f.write(f"| {count} | {metrics['average']:.3f} | {metrics['std']:.3f} | "
                           f"{metrics['min']:.3f} | {metrics['max']:.3f} | {metrics['count']} |\n")
            
            f.write("\n## 性能分析\n\n")
            
            # 计算性能趋势
            if len(self.performance_metrics) >= 2:
                avg_times = [self.performance_metrics[count]['average'] 
                           for count in sorted(self.performance_metrics.keys())]
                
                f.write("### 主要发现\n\n")
                
                # 性能变化分析
                if avg_times[0] > 0:
                    max_increase = ((max(avg_times) - avg_times[0]) / avg_times[0]) * 100
                    f.write(f"1. **性能变化幅度**: 相比0偏好标签，最大性能变化为 {max_increase:.1f}%\n")
                
                # 线性度分析
                if len(avg_times) > 2:
                    correlation = np.corrcoef(range(len(avg_times)), avg_times)[0, 1]
                    f.write(f"2. **线性相关性**: 偏好数量与执行时间的相关系数为 {correlation:.3f}\n")
                
                # 稳定性分析
                std_values = [self.performance_metrics[count]['std'] 
                            for count in sorted(self.performance_metrics.keys())]
                avg_std = np.mean(std_values)
                f.write(f"3. **算法稳定性**: 平均标准差为 {avg_std:.3f}ms\n")
            
            f.write("\n### 算法复杂度分析\n\n")
            f.write("根据测试结果分析，日记推荐算法的时间复杂度特征如下：\n\n")
            
            if len(self.performance_metrics) >= 3:
                preference_list = sorted(self.performance_metrics.keys())
                times_list = [self.performance_metrics[count]['average'] for count in preference_list]
                
                # 分析增长趋势
                if len(times_list) > 2:
                    diff1 = [times_list[i+1] - times_list[i] for i in range(len(times_list)-1)]
                    diff2 = [diff1[i+1] - diff1[i] for i in range(len(diff1)-1)]
                    
                    if all(d >= -0.1 for d in diff1):  # 单调递增（允许小误差）
                        if all(abs(d) < 0.5 for d in diff2):  # 二阶差分接近0
                            f.write("- **线性复杂度**: 执行时间与偏好数量呈线性关系\n")
                        else:
                            f.write("- **非线性复杂度**: 执行时间增长呈现非线性特征\n")
                    else:
                        f.write("- **不规则复杂度**: 执行时间变化不遵循明显的数学规律\n")
            
            f.write("\n### 性能优化建议\n\n")
            f.write("基于测试结果，提出以下优化建议：\n\n")
            
            # 根据实际结果给出建议
            if len(self.performance_metrics) >= 2:
                max_time = max(self.performance_metrics[count]['average'] 
                             for count in self.performance_metrics.keys())
                min_time = min(self.performance_metrics[count]['average'] 
                             for count in self.performance_metrics.keys())
                
                if max_time > min_time * 2:
                    f.write("1. **算法优化**: 偏好数量对性能影响显著，建议优化K路归并算法\n")
                    f.write("2. **缓存机制**: 对于常用偏好组合，建议实施结果缓存\n")
                    f.write("3. **并行处理**: 考虑对不同偏好类型的推荐进行并行计算\n")
                else:
                    f.write("1. **性能稳定**: 算法在不同偏好数量下表现稳定\n")
                    f.write("2. **可扩展性良好**: 当前实现可以很好地处理偏好数量变化\n")
            
            f.write("\n## 测试环境信息\n\n")
            f.write(f"- **操作系统**: Windows\n")
            f.write(f"- **Python版本**: {sys.version.split()[0]}\n")
            f.write(f"- **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            f.write(f"\n## 图表说明\n\n")
            f.write("![性能分析图表](diary_recommendation_preference_performance.png)\n\n")
            f.write("图表包含四个部分：\n")
            f.write("1. **左上**: 平均执行时间趋势，显示偏好数量与性能的关系\n")
            f.write("2. **右上**: 执行时间分布箱线图，展示数据的分散程度\n")
            f.write("3. **左下**: 性能变化率，显示相对于0偏好的性能变化\n")
            f.write("4. **右下**: 算法复杂度趋势分析，包含拟合曲线\n\n")
            
            f.write("## 结论\n\n")
            f.write("本次测试全面评估了日记推荐系统在不同偏好标签数量下的性能表现。")
            f.write("测试结果为系统优化和用户体验改进提供了重要的数据支撑。\n")
        
        print(f"分析报告已生成: {report_path}")
        return report_path
    
    def save_test_data(self):
        """保存测试数据为JSON格式"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_path = os.path.join(current_dir, f'diary_recommendation_preference_test_data_{timestamp}.json')
        
        test_data = {
            'timestamp': timestamp,
            'test_config': {
                'preference_counts': self.preference_counts,
                'test_iterations': self.test_iterations,
                'topK': self.topK
            },
            'test_results': dict(self.test_results),
            'performance_metrics': self.performance_metrics
        }
        
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"测试数据已保存: {data_path}")
        return data_path

def main():
    """主函数"""
    print("日记推荐系统偏好标签数量性能测试")
    print("=" * 50)
    
    # 创建测试实例
    test = DiaryRecommendationPreferenceTest()
    
    try:
        # 运行测试
        test.run_comprehensive_test()
        
        # 生成可视化图表
        chart_path = test.generate_visualizations()
        
        # 保存测试数据
        data_path = test.save_test_data()
        
        # 生成分析报告
        report_path = test.generate_report(chart_path)
        
        print("\n" + "=" * 50)
        print("测试完成！生成的文件：")
        print(f"- 图表: {chart_path}")
        print(f"- 报告: {report_path}")
        print(f"- 数据: {data_path}")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
