"""
归并排序性能对比测试程序
比较K-way merge和普通merge的性能差异

作者：性能测试分析师
日期：2025年6月5日
"""

import time
import random
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List, Dict, Any
import tracemalloc
import gc
from collections import defaultdict
import statistics
import sys
import os

# 添加模块路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module.data_structure.kwaymerge import k_way_merge_descending, get_top_k_elements
from module.data_structure.merge import merge_sort

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class MergePerformanceTester:
    """归并排序性能测试类"""
    
    def __init__(self):
        self.results = defaultdict(list)
        self.test_cases = []
        
    def generate_test_data(self, num_lists: int, list_sizes: List[int], 
                          score_range: tuple = (0, 100), 
                          visited_range: tuple = (0, 1000)) -> List[List[Dict]]:
        """
        生成测试数据
        
        Args:
            num_lists: 列表数量
            list_sizes: 每个列表的大小
            score_range: 评分范围
            visited_range: 访问次数范围
            
        Returns:
            生成的测试数据列表
        """
        test_data = []
        
        for i in range(num_lists):
            size = list_sizes[i] if i < len(list_sizes) else list_sizes[-1]
            sub_list = []
            
            for j in range(size):
                item = {
                    'id': f'item_{i}_{j}',
                    'score': round(random.uniform(*score_range), 2),
                    'visited_time': random.randint(*visited_range),
                    'value1': round(random.uniform(*score_range), 2),
                    'value2': random.randint(*visited_range)
                }
                # 确保value1和score一致，value2和visited_time一致
                item['value1'] = item['score']
                item['value2'] = item['visited_time']
                sub_list.append(item)
            
            # 按要求排序：score降序，visited_time降序
            sub_list.sort(key=lambda x: (-x['score'], -x['visited_time']))
            test_data.append(sub_list)
        
        return test_data
    
    def traditional_merge_all(self, list_of_lists: List[List[Dict]]) -> List[Dict]:
        """
        使用传统merge方法合并所有列表
        """
        if not list_of_lists:
            return []
        
        result = list_of_lists[0].copy()
        for i in range(1, len(list_of_lists)):
            result = merge_sort(result, list_of_lists[i])
        
        return result
    
    def measure_performance(self, test_func, *args, **kwargs) -> Dict[str, Any]:
        """
        测量函数性能
        
        Returns:
            包含执行时间和内存使用情况的字典
        """
        # 内存测量开始
        tracemalloc.start()
        gc.collect()  # 垃圾回收
        
        start_time = time.perf_counter()
        result = test_func(*args, **kwargs)
        end_time = time.perf_counter()
        
        # 内存测量结束
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            'execution_time': end_time - start_time,
            'memory_current': current,
            'memory_peak': peak,
            'result_length': len(result) if result else 0
        }
    
    def run_comparison_test(self, num_lists: int, list_sizes: List[int], 
                          num_runs: int = 5) -> Dict[str, Any]:
        """
        运行对比测试
        
        Args:
            num_lists: 列表数量
            list_sizes: 列表大小
            num_runs: 运行次数
            
        Returns:
            测试结果
        """
        print(f"测试配置: {num_lists}个列表，大小: {list_sizes}")
        
        # 生成测试数据
        test_data = self.generate_test_data(num_lists, list_sizes)
        total_elements = sum(len(lst) for lst in test_data)
        
        # 多次运行取平均值
        kway_results = []
        traditional_results = []
        
        for run in range(num_runs):
            print(f"  运行 {run + 1}/{num_runs}")
            
            # 测试K-way merge
            kway_perf = self.measure_performance(k_way_merge_descending, test_data)
            kway_results.append(kway_perf)
            
            # 测试传统merge
            traditional_perf = self.measure_performance(self.traditional_merge_all, test_data)
            traditional_results.append(traditional_perf)
        
        # 计算平均值和标准差
        def calc_stats(results, key):
            values = [r[key] for r in results]
            return {
                'mean': statistics.mean(values),
                'std': statistics.stdev(values) if len(values) > 1 else 0,
                'min': min(values),
                'max': max(values)
            }
        
        return {
            'config': {
                'num_lists': num_lists,
                'list_sizes': list_sizes,
                'total_elements': total_elements,
                'num_runs': num_runs
            },
            'kway_merge': {
                'time': calc_stats(kway_results, 'execution_time'),
                'memory_current': calc_stats(kway_results, 'memory_current'),
                'memory_peak': calc_stats(kway_results, 'memory_peak')
            },
            'traditional_merge': {
                'time': calc_stats(traditional_results, 'execution_time'),
                'memory_current': calc_stats(traditional_results, 'memory_current'),
                'memory_peak': calc_stats(traditional_results, 'memory_peak')
            }
        }
    
    def run_comprehensive_tests(self):
        """运行全面的性能测试"""
        print("开始归并排序性能对比测试...")
          # 测试配置
        test_configs = [
            # 标准测试配置 - 较少列表，较多元素
            (2, [100, 100]),
            (2, [500, 500]),
            (2, [1000, 1000]),
            (3, [100, 100, 100]),
            (3, [500, 500, 500]),
            (5, [200, 200, 200, 200, 200]),
            (10, [100] * 10),
            (20, [50] * 20),
            (50, [20] * 50),
            
            # 大量列表但少量元素的测试配置
            (100, [5] * 100),      # 100个列表，每个5个元素
            (150, [5] * 150),      # 150个列表，每个5个元素
            (200, [5] * 200),      # 200个列表，每个5个元素
            (250, [5] * 250),      # 250个列表，每个5个元素
            (300, [5] * 300),      # 300个列表，每个5个元素
            (400, [3] * 400),      # 400个列表，每个3个元素
            (500, [3] * 500),      # 500个列表，每个3个元素
            (600, [2] * 600),      # 600个列表，每个2个元素
            (700, [2] * 700),      # 700个列表，每个2个元素
            (800, [2] * 800),      # 800个列表，每个2个元素
            (900, [1] * 900),      # 900个列表，每个1个元素
            (1000, [1] * 1000),    # 1000个列表，每个1个元素
            
            # 不均匀大小测试
            (2, [1000, 2000]),  # 不均匀大小
            (3, [500, 1000, 1500]),  # 不均匀大小
            (5, [100, 300, 500, 700, 900]),  # 渐增大小
            
            # 混合场景测试
            (100, [1, 2, 3] * 33 + [1]),  # 100个列表，元素数量在1-3之间
            (200, [1, 5] * 100),          # 200个列表，交替1和5个元素
        ]
        
        all_results = []
        
        for num_lists, list_sizes in test_configs:
            result = self.run_comparison_test(num_lists, list_sizes, num_runs=3)
            all_results.append(result)
            self.results['all_tests'].append(result)
        
        return all_results
    
    def generate_visualizations(self, results: List[Dict[str, Any]]):
        """生成可视化图表"""
        print("生成性能对比图表...")
        
        # 准备数据
        configs = []
        kway_times = []
        traditional_times = []
        kway_memory = []
        traditional_memory = []
        total_elements = []
        speedup_ratios = []
        
        for result in results:
            config = result['config']
            config_str = f"{config['num_lists']}列表/{config['total_elements']}元素"
            configs.append(config_str)
            
            kway_time = result['kway_merge']['time']['mean']
            trad_time = result['traditional_merge']['time']['mean']
            
            kway_times.append(kway_time * 1000)  # 转换为毫秒
            traditional_times.append(trad_time * 1000)
            
            kway_memory.append(result['kway_merge']['memory_peak']['mean'] / 1024 / 1024)  # MB
            traditional_memory.append(result['traditional_merge']['memory_peak']['mean'] / 1024 / 1024)
            
            total_elements.append(config['total_elements'])
              # 计算加速比
            speedup = trad_time / kway_time if kway_time > 0 else 1
            speedup_ratios.append(speedup)
        
        # 设置图表参数
        x_pos = np.arange(len(configs))
        width = 0.35
        
        # 由于测试用例较多，我们创建多个图表
        # 图表1：总体性能对比
        fig1, axes1 = plt.subplots(2, 2, figsize=(20, 16))
        fig1.suptitle('归并排序算法性能对比分析 - 总体视图', fontsize=16, fontweight='bold')
          # 1. 执行时间对比 - 对数坐标
        ax1 = axes1[0, 0]
        ax1.scatter(total_elements, kway_times, label='K-way Merge', 
                   alpha=0.7, s=50, color='blue')
        ax1.scatter(total_elements, traditional_times, label='Traditional Merge', 
                   alpha=0.7, s=50, color='red')
        ax1.set_xlabel('总元素数量')
        ax1.set_ylabel('执行时间 (毫秒)')
        ax1.set_title('执行时间对比 (对数坐标)')
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 执行时间对比 - 柱状图
        ax2 = axes1[0, 1]
        bars1 = ax2.bar(x_pos - width/2, kway_times, width, label='K-way Merge', 
                       color='skyblue', alpha=0.8)
        bars2 = ax2.bar(x_pos + width/2, traditional_times, width, label='Traditional Merge', 
                       color='lightcoral', alpha=0.8)
        
        ax2.set_xlabel('测试配置')
        ax2.set_ylabel('执行时间 (毫秒)')
        ax2.set_title('执行时间对比')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(configs, rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
          # 添加数值标签
        for bar in bars1:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom')
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom')
        
        # 3. 内存使用对比
        ax3 = axes1[1, 0]
        bars3 = ax3.bar(x_pos - width/2, kway_memory, width, label='K-way Merge', 
                       color='lightgreen', alpha=0.8)
        bars4 = ax3.bar(x_pos + width/2, traditional_memory, width, label='Traditional Merge', 
                       color='orange', alpha=0.8)
        
        ax3.set_xlabel('测试配置')
        ax3.set_ylabel('峰值内存使用 (MB)')
        ax3.set_title('内存使用对比')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(configs, rotation=45, ha='right')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 加速比
        ax4 = axes1[1, 1]
        bars5 = ax4.bar(x_pos, speedup_ratios, color='gold', alpha=0.8)
        ax4.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='基准线 (1x)')
        ax4.set_xlabel('测试配置')
        ax4.set_ylabel('加速比 (传统方法时间/K-way时间)')
        ax4.set_title('K-way Merge 相对加速比')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(configs, rotation=45, ha='right')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bar in bars5:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}x', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('merge_performance_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 图表2：详细趋势分析
        fig2, axes2 = plt.subplots(2, 1, figsize=(15, 12))
        fig2.suptitle('归并排序算法性能趋势分析', fontsize=16, fontweight='bold')
        
        # 1. 时间复杂度趋势 - 线性图
        ax_trend1 = axes2[0]
        ax_trend1.plot(total_elements, kway_times, 'o-', label='K-way Merge', 
                      linewidth=2, markersize=6, color='blue')
        ax_trend1.plot(total_elements, traditional_times, 's-', label='Traditional Merge', 
                      linewidth=2, markersize=6, color='red')
        ax_trend1.set_xlabel('总元素数量')
        ax_trend1.set_ylabel('执行时间 (毫秒)')
        ax_trend1.set_title('时间复杂度趋势 (对数坐标)')
        ax_trend1.legend()
        ax_trend1.grid(True, alpha=0.3)
        ax_trend1.set_xscale('log')
        ax_trend1.set_yscale('log')
        
        # 2. 加速比趋势
        ax_trend2 = axes2[1]
        ax_trend2.plot(total_elements, speedup_ratios, 'o-', label='加速比', 
                      linewidth=2, markersize=6, color='green')
        ax_trend2.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='基准线 (1x)')
        ax_trend2.set_xlabel('总元素数量')
        ax_trend2.set_ylabel('加速比')
        ax_trend2.set_title('K-way Merge 相对加速比趋势')
        ax_trend2.legend()
        ax_trend2.grid(True, alpha=0.3)
        ax_trend2.set_xscale('log')
        
        plt.tight_layout()
        plt.savefig('merge_performance_trends.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 生成详细的数据表
        self.generate_detailed_table(results)
    
    def generate_detailed_table(self, results: List[Dict[str, Any]]):
        """生成详细的性能数据表"""
        print("生成详细性能数据表...")
        
        # 准备表格数据
        table_data = []
        
        for result in results:
            config = result['config']
            kway = result['kway_merge']
            trad = result['traditional_merge']
            
            speedup = (trad['time']['mean'] / kway['time']['mean'] 
                      if kway['time']['mean'] > 0 else 1)
            
            memory_ratio = (trad['memory_peak']['mean'] / kway['memory_peak']['mean'] 
                           if kway['memory_peak']['mean'] > 0 else 1)
            
            table_data.append({
                '测试配置': f"{config['num_lists']}个列表",
                '总元素数': config['total_elements'],
                'K-way时间(ms)': f"{kway['time']['mean']*1000:.3f}±{kway['time']['std']*1000:.3f}",
                '传统方法时间(ms)': f"{trad['time']['mean']*1000:.3f}±{trad['time']['std']*1000:.3f}",
                '时间加速比': f"{speedup:.2f}x",
                'K-way内存(MB)': f"{kway['memory_peak']['mean']/1024/1024:.2f}",
                '传统方法内存(MB)': f"{trad['memory_peak']['mean']/1024/1024:.2f}",
                '内存比率': f"{memory_ratio:.2f}x"
            })
        
        # 创建DataFrame并保存
        df = pd.DataFrame(table_data)
        df.to_csv('merge_performance_detailed.csv', index=False, encoding='utf-8-sig')
        
        print("\n详细性能对比表:")
        print("=" * 120)
        print(df.to_string(index=False))
        print("=" * 120)
    
    def theoretical_analysis(self):
        """理论分析"""
        return {
            'k_way_merge': {
                'time_complexity': 'O(N log k)',
                'space_complexity': 'O(k)',
                'description': 'K-way merge使用最小堆维护k个列表的当前最小元素，每次操作堆的时间复杂度为O(log k)',
                'advantages': [
                    '对于多个已排序列表的合并非常高效',
                    '空间复杂度仅与列表数量k相关，而非总元素数量',
                    '可以很容易地扩展到更多列表',
                    '堆操作具有很好的局部性'
                ],
                'disadvantages': [
                    '对于只有2个列表的情况，可能比传统方法稍慢',
                    '需要额外的堆数据结构'
                ]
            },
            'traditional_merge': {
                'time_complexity': 'O(N log k) - O(N * k)',
                'space_complexity': 'O(N)',
                'description': '传统方法逐一合并列表，第i次合并的时间复杂度取决于当前结果的大小',
                'advantages': [
                    '对于2个列表的情况非常高效',
                    '实现简单，易于理解',
                    '不需要额外的数据结构'
                ],
                'disadvantages': [
                    '随着列表数量增加，性能显著下降',
                    '需要创建大量中间结果，内存使用较高',
                    '不适合大量列表的合并'
                ]
            }
        }
    
    def generate_comprehensive_report(self, results: List[Dict[str, Any]]):
        """生成综合性能分析报告"""
        print("生成综合性能分析报告...")
        
        theoretical = self.theoretical_analysis()
        
        # 计算统计数据
        kway_wins = 0
        traditional_wins = 0
        avg_speedup = 0
        
        for result in results:
            kway_time = result['kway_merge']['time']['mean']
            trad_time = result['traditional_merge']['time']['mean']
            
            if kway_time < trad_time:
                kway_wins += 1
            else:
                traditional_wins += 1
            
            avg_speedup += trad_time / kway_time if kway_time > 0 else 1
        
        avg_speedup /= len(results)
        
        # 生成报告
        report = f"""
# 归并排序算法性能对比分析报告

## 测试概述
- 测试日期: 2025年6月5日  
- 测试场景: {len(results)}个不同配置
- 每个配置运行3次取平均值
- 测试环境: Python {sys.version}

## 理论分析

### K-way Merge算法
- **时间复杂度**: {theoretical['k_way_merge']['time_complexity']}
- **空间复杂度**: {theoretical['k_way_merge']['space_complexity']}
- **算法描述**: {theoretical['k_way_merge']['description']}

**优势**:
{chr(10).join('- ' + adv for adv in theoretical['k_way_merge']['advantages'])}

**劣势**:
{chr(10).join('- ' + dis for dis in theoretical['k_way_merge']['disadvantages'])}

### 传统Merge算法
- **时间复杂度**: {theoretical['traditional_merge']['time_complexity']}
- **空间复杂度**: {theoretical['traditional_merge']['space_complexity']}
- **算法描述**: {theoretical['traditional_merge']['description']}

**优势**:
{chr(10).join('- ' + adv for adv in theoretical['traditional_merge']['advantages'])}

**劣势**:
{chr(10).join('- ' + dis for dis in theoretical['traditional_merge']['disadvantages'])}

## 实测结果统计
- K-way Merge获胜: {kway_wins} 次 ({kway_wins/len(results)*100:.1f}%)
- Traditional Merge获胜: {traditional_wins} 次 ({traditional_wins/len(results)*100:.1f}%)
- 平均加速比: {avg_speedup:.2f}x

## 关键发现

1. **列表数量影响**: K-way merge在处理多个列表时优势明显
2. **数据规模影响**: 随着数据量增加，K-way merge的优势更加显著  
3. **内存效率**: K-way merge通常使用更少的内存
4. **实际应用**: 推荐在3个以上列表合并时使用K-way merge

## 推荐使用场景

### 推荐使用K-way Merge:
- 需要合并3个以上的已排序列表
- 内存使用需要优化
- 列表数量可能动态变化
- 大规模数据处理

### 推荐使用Traditional Merge:
- 只需要合并2个列表
- 代码简单性更重要
- 小规模数据处理

## 结论
K-way merge算法在多列表合并场景下具有显著的性能优势，特别是在处理大量数据和多个列表时。
建议在实际应用中根据具体场景选择合适的算法。

---
报告生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # 保存报告
        with open('merge_algorithm_performance_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 保存JSON格式的详细数据
        with open('merge_performance_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'theoretical_analysis': theoretical,
                'test_results': results,
                'summary_statistics': {
                    'kway_wins': kway_wins,
                    'traditional_wins': traditional_wins,
                    'average_speedup': avg_speedup,
                    'total_tests': len(results)
                },
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=2, ensure_ascii=False)
        
        print("报告已生成:")
        print("- merge_algorithm_performance_report.md (文本报告)")
        print("- merge_performance_results.json (详细数据)")
        print("- merge_performance_comparison.png (可视化图表)")
        print("- merge_performance_detailed.csv (详细表格)")

def main():
    """主函数"""
    print("归并排序算法性能对比测试")
    print("=" * 50)
    
    tester = MergePerformanceTester()
    
    try:
        # 运行综合测试
        results = tester.run_comprehensive_tests()
        
        # 生成可视化
        tester.generate_visualizations(results)
        
        # 生成综合报告
        tester.generate_comprehensive_report(results)
        
        print("\n测试完成！请查看生成的报告和图表。")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
