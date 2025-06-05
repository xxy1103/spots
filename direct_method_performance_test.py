#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
景点推荐算法性能测试程序 - 直接调用原始方法
对比传统K路归并算法与IndexHeap优化算法的实际执行性能
"""

import sys
import os
import time
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from collections import defaultdict
import gc
import psutil
import tracemalloc
from typing import List, Dict, Tuple
import json

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# 导入项目模块
try:
    from module.user_class import UserManager, userManager
    from module.Spot_class import spotManager
    from module.Model.Model import User
    print("✅ 成功导入项目模块")
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保在项目根目录下运行此脚本")
    sys.exit(1)

class PerformanceProfiler:
    """性能分析器，测量执行时间、内存使用等指标"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.start_time = None
        self.end_time = None
        self.peak_memory = 0
        self.start_memory = 0
    
    def start_profiling(self):
        """开始性能分析"""
        gc.collect()  # 强制垃圾回收
        tracemalloc.start()
        process = psutil.Process()
        self.start_memory = process.memory_info().rss / 1024 / 1024  # MB
        self.start_time = time.perf_counter()
    
    def end_profiling(self) -> Dict:
        """结束性能分析并返回结果"""
        self.end_time = time.perf_counter()
        
        # 获取内存信息
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        process = psutil.Process()
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            'execution_time': self.end_time - self.start_time,
            'peak_memory_mb': peak / 1024 / 1024,
            'memory_diff_mb': end_memory - self.start_memory,
            'start_memory_mb': self.start_memory,
            'end_memory_mb': end_memory
        }

class DirectMethodPerformanceTester:
    """直接调用原始方法的推荐算法性能测试器"""
    
    def __init__(self):
        self.profiler = PerformanceProfiler()
        self.test_users = []
        self.results = {
            'traditional': defaultdict(list),
            'optimized': defaultdict(list)
        }
    
    def create_test_scenarios(self, num_scenarios: int = 30) -> List[Dict]:
        """创建测试场景"""
        print(f"🔄 创建 {num_scenarios} 个测试场景...")
        
        spot_types = [
            "历史建筑", "赏花胜地", "萌萌动物", "城市漫步", "夜游观景",
            "遛娃宝藏地", "展馆展览", "地标观景", "登高爬山", "踏青必去",
            "自然山水", "游乐场", "演出"
        ]
        
        test_scenarios = []
        
        for i in range(num_scenarios):
            # 随机选择1-5个喜好类型
            num_likes = random.randint(1, 5)
            likes = random.sample(spot_types, num_likes)
            
            scenario = {
                'scenario_id': f"scenario_{i}",
                'likes_type': likes,
                'description': f"场景{i}: 喜好{len(likes)}种类型 - {', '.join(likes)}"
            }
            test_scenarios.append(scenario)
        
        self.test_scenarios = test_scenarios
        print(f"✅ 成功创建 {len(test_scenarios)} 个测试场景")
        return test_scenarios
    
    def create_test_user(self, user_likes: List[str]) -> int:
        """创建测试用户并返回用户ID"""
        # 生成唯一的测试用户ID
        test_user_id = random.randint(100000, 999999)
        while any(u.id == test_user_id for u in userManager.users):
            test_user_id = random.randint(100000, 999999)
        
        test_user = User(
            id=test_user_id,
            name=f"test_user_{test_user_id}",
            password="test_password",
            likes_type=user_likes
        )
        # 临时添加到用户管理器中
        userManager.users.append(test_user)
        userManager.counts += 1
        return test_user_id
    
    def cleanup_test_user(self, user_id: int):
        """清理测试用户"""
        userManager.users = [u for u in userManager.users if u.id != user_id]
        userManager.counts = len(userManager.users)
    
    def run_traditional_algorithm(self, user_likes: List[str], topK: int) -> Tuple[List, Dict]:
        """运行传统算法并测量性能 - 直接调用原始方法"""
        self.profiler.start_profiling()
        test_user_id = None
        
        try:
            # 创建测试用户并直接调用传统方法
            test_user_id = self.create_test_user(user_likes)
            result = userManager.getRecommendSpotsTraditional(test_user_id, topK)
            if result is None:
                result = []
            
        except Exception as e:
            print(f"❌ 传统算法执行错误: {e}")
            result = []
        finally:
            # 确保清理测试用户
            if test_user_id:
                self.cleanup_test_user(test_user_id)
        
        metrics = self.profiler.end_profiling()
        return result, metrics
    
    def run_optimized_algorithm(self, user_likes: List[str], topK: int) -> Tuple[List, Dict]:
        """运行优化算法并测量性能 - 直接调用原始方法"""
        self.profiler.start_profiling()
        test_user_id = None
        
        try:
            # 创建测试用户并直接调用优化方法
            test_user_id = self.create_test_user(user_likes)
            result = userManager.getRecommendSpots(test_user_id, topK)
            if result is None:
                result = []
                
        except Exception as e:
            print(f"❌ 优化算法执行错误: {e}")
            result = []
        finally:
            # 确保清理测试用户
            if test_user_id:
                self.cleanup_test_user(test_user_id)
        
        metrics = self.profiler.end_profiling()
        return result, metrics
    
    def compare_results(self, traditional_result: List, optimized_result: List) -> Dict:
        """比较两种算法的结果一致性"""
        if not traditional_result and not optimized_result:
            return {
                'identical': True, 
                'similarity': 1.0, 
                'difference_count': 0,
                'traditional_count': 0,
                'optimized_count': 0
            }
        
        if not traditional_result or not optimized_result:
            return {
                'identical': False, 
                'similarity': 0.0, 
                'difference_count': max(len(traditional_result), len(optimized_result)),
                'traditional_count': len(traditional_result),
                'optimized_count': len(optimized_result)
            }
        
        # 提取ID集合进行比较
        traditional_ids = {item['id'] for item in traditional_result}
        optimized_ids = {item['id'] for item in optimized_result}
        
        intersection = traditional_ids & optimized_ids
        union = traditional_ids | optimized_ids
        
        similarity = len(intersection) / len(union) if union else 1.0
        identical = traditional_ids == optimized_ids
        difference_count = len(union) - len(intersection)
        
        return {
            'identical': identical,
            'similarity': similarity,
            'difference_count': difference_count,
            'traditional_count': len(traditional_result),
            'optimized_count': len(optimized_result)
        }
    
    def run_comprehensive_test(self, topK_values: List[int] = None, iterations: int = 3) -> Dict:
        """运行全面的性能测试"""
        if topK_values is None:
            topK_values = [5, 10, 20, 50]
        
        print("🚀 开始全面性能测试...")
        print(f"📊 测试参数: topK值={topK_values}, 测试场景数={len(self.test_scenarios)}, 每个场景重复={iterations}次")
        print("=" * 80)
        
        overall_results = {
            'traditional': defaultdict(lambda: defaultdict(list)),
            'optimized': defaultdict(lambda: defaultdict(list)),
            'comparison': defaultdict(lambda: defaultdict(list))
        }
        
        for topK in topK_values:
            print(f"\n🔍 测试 topK = {topK}")
            
            traditional_times = []
            optimized_times = []
            traditional_memories = []
            optimized_memories = []
            similarities = []
            
            for i, scenario in enumerate(self.test_scenarios):
                user_likes = scenario['likes_type']
                
                # 多次测试取平均值
                scenario_traditional_times = []
                scenario_optimized_times = []
                scenario_traditional_memories = []
                scenario_optimized_memories = []
                scenario_similarities = []
                
                for iteration in range(iterations):
                    # 测试传统算法
                    traditional_result, traditional_metrics = self.run_traditional_algorithm(user_likes, topK)
                    scenario_traditional_times.append(traditional_metrics['execution_time'])
                    scenario_traditional_memories.append(traditional_metrics['peak_memory_mb'])
                    
                    # 测试优化算法
                    optimized_result, optimized_metrics = self.run_optimized_algorithm(user_likes, topK)
                    scenario_optimized_times.append(optimized_metrics['execution_time'])
                    scenario_optimized_memories.append(optimized_metrics['peak_memory_mb'])
                    
                    # 比较结果
                    comparison = self.compare_results(traditional_result, optimized_result)
                    scenario_similarities.append(comparison['similarity'])
                
                # 记录平均值
                avg_traditional_time = np.mean(scenario_traditional_times)
                avg_optimized_time = np.mean(scenario_optimized_times)
                avg_traditional_memory = np.mean(scenario_traditional_memories)
                avg_optimized_memory = np.mean(scenario_optimized_memories)
                avg_similarity = np.mean(scenario_similarities)
                
                traditional_times.append(avg_traditional_time)
                optimized_times.append(avg_optimized_time)
                traditional_memories.append(avg_traditional_memory)
                optimized_memories.append(avg_optimized_memory)
                similarities.append(avg_similarity)
                
                if (i + 1) % 10 == 0:
                    print(f"  已完成 {i + 1}/{len(self.test_scenarios)} 个场景")
            
            # 计算总体统计
            avg_traditional = np.mean(traditional_times)
            avg_optimized = np.mean(optimized_times)
            speedup = avg_traditional / avg_optimized if avg_optimized > 0 else 0
            avg_similarity = np.mean(similarities)
            
            overall_results['traditional'][topK] = {
                'times': traditional_times,
                'avg_time': avg_traditional,
                'std_time': np.std(traditional_times),
                'memories': traditional_memories,
                'avg_memory': np.mean(traditional_memories),
                'std_memory': np.std(traditional_memories)
            }
            
            overall_results['optimized'][topK] = {
                'times': optimized_times,
                'avg_time': avg_optimized,
                'std_time': np.std(optimized_times),
                'memories': optimized_memories,
                'avg_memory': np.mean(optimized_memories),
                'std_memory': np.std(optimized_memories)
            }
            
            overall_results['comparison'][topK] = {
                'speedup': speedup,
                'similarities': similarities,
                'avg_similarity': avg_similarity,
                'std_similarity': np.std(similarities)
            }
            
            print(f"  ✅ topK={topK} 测试完成:")
            print(f"     传统算法平均时间: {avg_traditional*1000:.3f}ms")
            print(f"     优化算法平均时间: {avg_optimized*1000:.3f}ms")
            print(f"     性能提升倍数: {speedup:.2f}x")
            print(f"     结果相似度: {avg_similarity:.3f}")
        
        self.results = overall_results
        return overall_results
    
    def visualize_results(self, save_path: str = "direct_method_performance_analysis.png"):
        """可视化测试结果"""
        if not self.results['traditional'] or not self.results['optimized']:
            print("❌ 没有测试结果可供可视化")
            return
        
        topK_values = list(self.results['traditional'].keys())
        
        # 提取数据
        traditional_times = [self.results['traditional'][k]['avg_time'] * 1000 for k in topK_values]
        optimized_times = [self.results['optimized'][k]['avg_time'] * 1000 for k in topK_values]
        speedups = [self.results['comparison'][k]['speedup'] for k in topK_values]
        similarities = [self.results['comparison'][k]['avg_similarity'] for k in topK_values]
        
        # 创建图表
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. 执行时间对比
        x_pos = np.arange(len(topK_values))
        width = 0.35
        
        bars1 = ax1.bar(x_pos - width/2, traditional_times, width, 
                        label='传统算法(K路归并)', color='lightcoral', alpha=0.8)
        bars2 = ax1.bar(x_pos + width/2, optimized_times, width,
                        label='优化算法(IndexHeap)', color='lightblue', alpha=0.8)
        
        ax1.set_xlabel('TopK值')
        ax1.set_ylabel('平均执行时间 (毫秒)')
        ax1.set_title('直接调用方法的性能对比')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(topK_values)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=10)
        for bar in bars2:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=10)
        
        # 2. 性能提升倍数
        bars3 = ax2.bar(topK_values, speedups, color='lightgreen', alpha=0.8)
        ax2.set_xlabel('TopK值')
        ax2.set_ylabel('性能提升倍数')
        ax2.set_title('优化算法相对传统算法的性能提升')
        ax2.grid(True, alpha=0.3)
        
        for bar in bars3:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}x', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # 3. 时间复杂度趋势
        ax3.plot(topK_values, traditional_times, 'o-', label='传统算法', 
                 color='red', linewidth=3, markersize=8)
        ax3.plot(topK_values, optimized_times, 's-', label='优化算法', 
                 color='blue', linewidth=3, markersize=8)
        
        ax3.set_xlabel('TopK值')
        ax3.set_ylabel('执行时间 (毫秒)')
        ax3.set_title('执行时间随TopK值变化趋势')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 结果相似度
        bars4 = ax4.bar(topK_values, similarities, color='orange', alpha=0.8)
        ax4.set_xlabel('TopK值')
        ax4.set_ylabel('结果相似度')
        ax4.set_title('两种算法结果相似度对比')
        ax4.set_ylim([0, 1.1])
        ax4.grid(True, alpha=0.3)
        
        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=11)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 性能对比图表已保存至: {save_path}")
        plt.show()
    
    def generate_report(self, save_path: str = "direct_method_performance_report.md"):
        """生成详细的性能分析报告"""
        if not self.results['traditional']:
            print("❌ 没有测试结果可供生成报告")
            return
        
        topK_values = list(self.results['traditional'].keys())
        
        report_content = f"""# 景点推荐算法性能测试报告 - 直接调用原始方法

## 测试概述

本报告分析了个性化旅游系统中景点推荐算法的实际性能表现，通过直接调用原始方法对比了传统K路归并算法与基于IndexHeap的优化算法。

### 测试环境
- 测试场景数量: {len(self.test_scenarios)}个不同的用户喜好组合
- TopK测试值: {topK_values}
- 每个场景重复测试: 3次
- 测试方法: 直接调用UserManager中的原始方法

## 性能测试结果

### 平均执行时间对比 (毫秒)

| TopK | 传统算法 | 优化算法 | 性能提升 | 提升率 |
|------|----------|----------|----------|---------|
"""
        
        for topK in topK_values:
            traditional_time = self.results['traditional'][topK]['avg_time'] * 1000
            optimized_time = self.results['optimized'][topK]['avg_time'] * 1000
            speedup = self.results['comparison'][topK]['speedup']
            improvement = ((traditional_time - optimized_time) / traditional_time * 100) if traditional_time > 0 else 0
            
            report_content += f"| {topK} | {traditional_time:.3f} | {optimized_time:.3f} | {speedup:.2f}x | {improvement:.1f}% |\n"
        
        report_content += f"""

### 关键发现

1. **整体性能表现**: 在所有TopK值下的平均性能对比
2. **算法稳定性**: 通过多次重复测试验证结果的一致性
3. **结果准确性**: 两种算法结果的相似度分析

### 内存使用分析

"""
        
        for topK in topK_values:
            traditional_memory = self.results['traditional'][topK]['avg_memory']
            optimized_memory = self.results['optimized'][topK]['avg_memory']
            
            report_content += f"- **TopK={topK}**: 传统算法 {traditional_memory:.2f}MB, 优化算法 {optimized_memory:.2f}MB\\n"
        
        report_content += f"""

### 结果相似度分析

"""
        
        for topK in topK_values:
            similarity = self.results['comparison'][topK]['avg_similarity']
            report_content += f"- **TopK={topK}**: 平均相似度 {similarity:.3f}\\n"
        
        report_content += f"""

## 结论

通过直接调用原始方法的测试，我们验证了两种推荐算法在实际应用中的性能表现。测试结果显示了优化算法在不同场景下的实际效果。

---

**报告生成时间**: {time.strftime("%Y-%m-%d %H:%M:%S")}  
**测试版本**: 直接方法调用性能测试 v1.0
"""
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📝 详细性能分析报告已保存至: {save_path}")

def main():
    """主函数"""
    print("=" * 80)
    print("🔬 景点推荐算法性能测试 - 直接调用原始方法")
    print("=" * 80)
    
    try:
        # 创建测试器
        tester = DirectMethodPerformanceTester()
        
        # 创建测试场景
        tester.create_test_scenarios(num_scenarios=20)  # 使用较少的场景以加快测试
        
        # 运行性能测试
        print("\n🚀 开始性能测试...")
        results = tester.run_comprehensive_test(
            topK_values=[5, 10, 20, 50],
            iterations=3
        )
        
        # 生成可视化图表
        print("\n📊 生成性能分析图表...")
        tester.visualize_results()
        
        # 生成详细报告
        print("\n📝 生成详细性能报告...")
        tester.generate_report()
        
        print("\n" + "=" * 80)
        print("✅ 性能测试完成！")
        print("已生成:")
        print("- 性能对比图表: direct_method_performance_analysis.png")
        print("- 详细分析报告: direct_method_performance_report.md")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
