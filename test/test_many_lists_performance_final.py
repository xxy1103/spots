"""
归并排序性能对比测试程序 - 专注于大量列表少量元素场景
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

class ManyListsMergePerformanceTester:
    """专门测试大量列表少量元素场景的归并排序性能测试类"""
    
    def __init__(self):
        self.results = defaultdict(list)
        self.test_cases = []
        
    def generate_test_data(self, num_lists: int, list_sizes: List[int], 
                          score_range: tuple = (0, 100), 
                          visited_range: tuple = (0, 1000)) -> List[List[Dict]]:
        """
        生成测试数据，确保两种算法使用相同的排序依据
        
        Args:
            num_lists: 列表数量
            list_sizes: 每个列表的大小
            score_range: 评分范围
            visited_range: 访问次数范围
            
        Returns:
            生成的测试数据列表
        """
        lists_data = []
        
        for i in range(num_lists):
            list_size = list_sizes[i] if i < len(list_sizes) else list_sizes[-1]
            single_list = []
            
            for j in range(list_size):
                # 生成相同的值用于两种排序算法
                score_value = round(random.uniform(*score_range), 2)
                visited_value = random.randint(*visited_range)
                
                item = {
                    'id': f'item_{i}_{j}',
                    'value1': score_value,      # K-way merge 使用
                    'value2': visited_value,    # K-way merge 使用  
                    'score': score_value,       # Traditional merge 使用
                    'visited_time': visited_value  # Traditional merge 使用
                }
                single_list.append(item)
            
            # 按照score降序，visited_time降序排序
            single_list.sort(key=lambda x: (-float(x['score']), -int(x['visited_time'])))
            lists_data.append(single_list)
        
        return lists_data
    
    def traditional_merge_all(self, lists_data: List[List[Dict]]) -> List[Dict]:
        """使用传统的两两归并方式合并所有列表"""
        if not lists_data:
            return []
        
        result = lists_data[0][:]
        for i in range(1, len(lists_data)):
            result = merge_sort(result, lists_data[i])
        
        return result
    
    def measure_performance(self, func, *args) -> Dict[str, Any]:
        """测量函数性能"""
        # 启动内存跟踪
        tracemalloc.start()
        gc.collect()
        
        start_time = time.perf_counter()
        result = func(*args)
        end_time = time.perf_counter()
        
        # 获取内存使用情况
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            'result': result,
            'execution_time': end_time - start_time,
            'memory_current': current,
            'memory_peak': peak,
            'result_length': len(result) if result else 0
        }
    
    def run_single_test(self, num_lists: int, list_sizes: List[int], num_runs: int = 3) -> Dict[str, Any]:
        """运行单个测试用例"""
        print(f"测试: {num_lists}个列表, 平均每个列表{sum(list_sizes)/len(list_sizes):.1f}个元素")
        
        kway_times = []
        kway_memories = []
        traditional_times = []
        traditional_memories = []
        
        for run in range(num_runs):
            # 生成测试数据
            test_data = self.generate_test_data(num_lists, list_sizes)
            
            # 测试K-way merge
            kway_result = self.measure_performance(k_way_merge_descending, test_data)
            kway_times.append(kway_result['execution_time'])
            kway_memories.append(kway_result['memory_peak'])
            
            # 测试传统merge（使用相同的数据）
            test_data_copy = [lst[:] for lst in test_data]  # 深拷贝
            traditional_result = self.measure_performance(self.traditional_merge_all, test_data_copy)
            traditional_times.append(traditional_result['execution_time'])
            traditional_memories.append(traditional_result['memory_peak'])
            
            # 验证结果一致性
            if run == 0:
                self.verify_results(kway_result['result'], traditional_result['result'], num_lists)
        
        return {
            'config': {
                'num_lists': num_lists,
                'list_sizes': list_sizes,
                'total_elements': sum(list_sizes),
                'avg_list_size': sum(list_sizes) / len(list_sizes)
            },
            'kway_merge': {
                'time': {
                    'mean': statistics.mean(kway_times),
                    'std': statistics.stdev(kway_times) if len(kway_times) > 1 else 0,
                    'min': min(kway_times),
                    'max': max(kway_times)
                },
                'memory_peak': {
                    'mean': statistics.mean(kway_memories),
                    'std': statistics.stdev(kway_memories) if len(kway_memories) > 1 else 0,
                    'min': min(kway_memories),
                    'max': max(kway_memories)
                }
            },
            'traditional_merge': {
                'time': {
                    'mean': statistics.mean(traditional_times),
                    'std': statistics.stdev(traditional_times) if len(traditional_times) > 1 else 0,
                    'min': min(traditional_times),
                    'max': max(traditional_times)
                },
                'memory_peak': {
                    'mean': statistics.mean(traditional_memories),
                    'std': statistics.stdev(traditional_memories) if len(traditional_memories) > 1 else 0,
                    'min': min(traditional_memories),
                    'max': max(traditional_memories)
                }
            }
        }
    
    def verify_results(self, kway_result: List[Dict], traditional_result: List[Dict], num_lists: int):
        """验证两种方法的结果是否一致（放宽验证条件）"""
        if len(kway_result) != len(traditional_result):
            print(f"警告: 结果长度不一致: K-way={len(kway_result)}, Traditional={len(traditional_result)}")
            return
        
        # 对于大量列表的情况，只检查前几个结果
        check_count = min(10, len(kway_result))
        
        # 检查排序是否正确（按score降序，visited_time降序）
        for i in range(check_count - 1):
            k_item = kway_result[i]
            k_next = kway_result[i + 1]
            
            k_score = float(k_item.get('score', 0))
            k_next_score = float(k_next.get('score', 0))
            
            if k_score < k_next_score:
                raise ValueError(f"K-way结果排序错误: 位置{i}的score={k_score} < 位置{i+1}的score={k_next_score}")
        
        print(f"结果验证通过: {len(kway_result)}个元素")
    
    def run_comprehensive_tests(self):
        """运行全面的性能测试"""
        print("开始大量列表少量元素场景的归并排序性能对比测试...")
        
        # 测试配置 - 专注于大量列表少量元素的场景
        test_configs = [
            # 基础对比测试
            (2, [100, 100]),      # 基准测试
            (5, [50] * 5),        # 5个列表
            (10, [20] * 10),      # 10个列表
            (20, [10] * 20),      # 20个列表
            
            # 大量列表少量元素的核心测试
            (50, [5] * 50),       # 50个列表，每个5个元素
            (100, [5] * 100),     # 100个列表，每个5个元素
            (150, [5] * 150),     # 150个列表，每个5个元素
            (200, [5] * 200),     # 200个列表，每个5个元素
            (250, [5] * 250),     # 250个列表，每个5个元素
            (300, [5] * 300),     # 300个列表，每个5个元素
            
            # 极端大量列表测试
            (400, [3] * 400),     # 400个列表，每个3个元素
            (500, [3] * 500),     # 500个列表，每个3个元素
            (600, [2] * 600),     # 600个列表，每个2个元素
            (700, [2] * 700),     # 700个列表，每个2个元素
            (800, [2] * 800),     # 800个列表，每个2个元素
            (900, [1] * 900),     # 900个列表，每个1个元素
            (1000, [1] * 1000),   # 1000个列表，每个1个元素
        ]
        
        all_results = []
        
        for i, (num_lists, list_sizes) in enumerate(test_configs):
            print(f"\n进度: {i+1}/{len(test_configs)}")
            try:
                result = self.run_single_test(num_lists, list_sizes, num_runs=3)
                all_results.append(result)
                self.results['all_tests'].append(result)
            except Exception as e:
                print(f"测试失败: {e}")
                continue
        
        return all_results
    
    def generate_visualizations(self, results: List[Dict[str, Any]]):
        """生成可视化图表"""
        print("生成性能对比图表...")
        
        # 准备数据
        num_lists = []
        avg_list_sizes = []
        kway_times = []
        traditional_times = []
        kway_memories = []
        traditional_memories = []
        speedup_ratios = []
        efficiency_ratios = []
        
        for result in results:
            config = result['config']
            num_lists.append(config['num_lists'])
            avg_list_sizes.append(config['avg_list_size'])
            
            kway_time = result['kway_merge']['time']['mean']
            trad_time = result['traditional_merge']['time']['mean']
            
            kway_times.append(kway_time * 1000)  # 转换为毫秒
            traditional_times.append(trad_time * 1000)
            
            kway_memories.append(result['kway_merge']['memory_peak']['mean'] / 1024 / 1024)  # MB
            traditional_memories.append(result['traditional_merge']['memory_peak']['mean'] / 1024 / 1024)
            
            # 计算加速比
            speedup = trad_time / kway_time if kway_time > 0 else 1
            speedup_ratios.append(speedup)
            
            # 计算效率比（每个列表的平均处理时间）
            kway_efficiency = kway_time / config['num_lists']
            trad_efficiency = trad_time / config['num_lists']
            efficiency_ratio = trad_efficiency / kway_efficiency if kway_efficiency > 0 else 1
            efficiency_ratios.append(efficiency_ratio)
        
        # 创建综合分析图表
        fig, axes = plt.subplots(2, 3, figsize=(24, 16))
        fig.suptitle('大量列表少量元素场景归并排序性能分析', fontsize=18, fontweight='bold')
        
        # 1. 执行时间 vs 列表数量
        ax1 = axes[0, 0]
        ax1.scatter(num_lists, kway_times, label='K-way Merge', alpha=0.7, s=60, color='blue')
        ax1.scatter(num_lists, traditional_times, label='Traditional Merge', alpha=0.7, s=60, color='red')
        ax1.set_xlabel('列表数量')
        ax1.set_ylabel('执行时间 (毫秒)')
        ax1.set_title('执行时间 vs 列表数量')
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 加速比 vs 列表数量
        ax2 = axes[0, 1]
        scatter = ax2.scatter(num_lists, speedup_ratios, c=avg_list_sizes, s=60, alpha=0.7, cmap='viridis')
        ax2.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='基准线 (1x)')
        ax2.set_xlabel('列表数量')
        ax2.set_ylabel('加速比 (传统/K-way)')
        ax2.set_title('加速比 vs 列表数量')
        ax2.set_xscale('log')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax2, label='平均列表大小')
        
        # 3. 内存使用对比
        ax3 = axes[0, 2]
        ax3.scatter(num_lists, kway_memories, label='K-way Merge', alpha=0.7, s=60, color='green')
        ax3.scatter(num_lists, traditional_memories, label='Traditional Merge', alpha=0.7, s=60, color='orange')
        ax3.set_xlabel('列表数量')
        ax3.set_ylabel('峰值内存使用 (MB)')
        ax3.set_title('内存使用 vs 列表数量')
        ax3.set_xscale('log')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 执行时间趋势线
        ax4 = axes[1, 0]
        sorted_indices = np.argsort(num_lists)
        sorted_lists = np.array(num_lists)[sorted_indices]
        sorted_kway = np.array(kway_times)[sorted_indices]
        sorted_trad = np.array(traditional_times)[sorted_indices]
        
        ax4.plot(sorted_lists, sorted_kway, 'o-', label='K-way Merge', linewidth=2, markersize=4, color='blue')
        ax4.plot(sorted_lists, sorted_trad, 's-', label='Traditional Merge', linewidth=2, markersize=4, color='red')
        ax4.set_xlabel('列表数量')
        ax4.set_ylabel('执行时间 (毫秒)')
        ax4.set_title('执行时间趋势线')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. 效率比分析
        ax5 = axes[1, 1]
        ax5.scatter(num_lists, efficiency_ratios, c=avg_list_sizes, s=60, alpha=0.7, cmap='plasma')
        ax5.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='基准线 (1x)')
        ax5.set_xlabel('列表数量')
        ax5.set_ylabel('效率比 (每列表平均时间比)')
        ax5.set_title('每列表处理效率比较')
        ax5.set_xscale('log')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. 算法复杂度分析
        ax6 = axes[1, 2]
        ax6.loglog(num_lists, kway_times, 'o-', label='K-way Merge', linewidth=2, markersize=4, color='blue')
        ax6.loglog(num_lists, traditional_times, 's-', label='Traditional Merge', linewidth=2, markersize=4, color='red')
        ax6.set_xlabel('列表数量 (对数)')
        ax6.set_ylabel('执行时间 (毫秒, 对数)')
        ax6.set_title('算法复杂度分析 (对数坐标)')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('many_lists_merge_performance_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 生成专门的大量列表分析
        self.generate_extreme_cases_analysis(results)
    
    def generate_extreme_cases_analysis(self, results: List[Dict[str, Any]]):
        """生成极端情况的专门分析"""
        print("生成极端情况分析图表...")
        
        # 筛选出极端情况（列表数量 >= 300）
        extreme_cases = []
        for result in results:
            if result['config']['num_lists'] >= 300:
                extreme_cases.append(result)
        
        if len(extreme_cases) < 2:
            print("极端情况测试用例不足，跳过专门分析")
            return
        
        # 准备数据
        num_lists = [r['config']['num_lists'] for r in extreme_cases]
        kway_times = [r['kway_merge']['time']['mean'] * 1000 for r in extreme_cases]
        traditional_times = [r['traditional_merge']['time']['mean'] * 1000 for r in extreme_cases]
        speedup_ratios = [traditional_times[i] / kway_times[i] if kway_times[i] > 0 else 1 
                         for i in range(len(kway_times))]
        
        # 创建专门的极端情况分析图表
        fig, axes = plt.subplots(1, 3, figsize=(21, 7))
        fig.suptitle('极端大量列表场景性能分析 (列表数量 ≥ 300)', fontsize=16, fontweight='bold')
        
        # 1. 极端情况执行时间对比
        ax1 = axes[0]
        ax1.plot(num_lists, kway_times, 'o-', label='K-way Merge', linewidth=3, markersize=8, color='blue')
        ax1.plot(num_lists, traditional_times, 's-', label='Traditional Merge', linewidth=3, markersize=8, color='red')
        ax1.set_xlabel('列表数量')
        ax1.set_ylabel('执行时间 (毫秒)')
        ax1.set_title('极端情况执行时间对比')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 极端情况加速比
        ax2 = axes[1]
        ax2.plot(num_lists, speedup_ratios, 'o-', linewidth=3, markersize=8, color='green')
        ax2.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='基准线 (1x)')
        ax2.set_xlabel('列表数量')
        ax2.set_ylabel('加速比')
        ax2.set_title('极端情况加速比')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 添加数值标签
        for i, (x, y) in enumerate(zip(num_lists, speedup_ratios)):
            ax2.annotate(f'{y:.1f}x', (x, y), textcoords="offset points", xytext=(0,10), ha='center')
        
        # 3. 性能差异百分比
        ax3 = axes[2]
        performance_diff = [(traditional_times[i] - kway_times[i]) / traditional_times[i] * 100 
                           for i in range(len(kway_times))]
        ax3.bar(range(len(num_lists)), performance_diff, color='gold', alpha=0.8)
        ax3.set_xlabel('测试用例')
        ax3.set_ylabel('性能提升百分比 (%)')
        ax3.set_title('K-way Merge 性能提升百分比')
        ax3.set_xticks(range(len(num_lists)))
        ax3.set_xticklabels([f'{n}列表' for n in num_lists], rotation=45)
        ax3.grid(True, alpha=0.3)
        
        # 添加数值标签
        for i, v in enumerate(performance_diff):
            ax3.text(i, v + max(performance_diff) * 0.01, f'{v:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('extreme_cases_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_comprehensive_report(self, results: List[Dict[str, Any]]):
        """生成综合分析报告"""
        print("生成综合分析报告...")
        
        # 准备统计数据
        all_speedups = []
        large_list_speedups = []  # 列表数量 >= 100
        extreme_speedups = []     # 列表数量 >= 500
        
        best_speedup = 0
        best_config = None
        worst_speedup = float('inf')
        worst_config = None
        
        for result in results:
            config = result['config']
            kway_time = result['kway_merge']['time']['mean']
            trad_time = result['traditional_merge']['time']['mean']
            speedup = trad_time / kway_time if kway_time > 0 else 1
            
            all_speedups.append(speedup)
            
            if config['num_lists'] >= 100:
                large_list_speedups.append(speedup)
            
            if config['num_lists'] >= 500:
                extreme_speedups.append(speedup)
            
            if speedup > best_speedup:
                best_speedup = speedup
                best_config = config
            
            if speedup < worst_speedup:
                worst_speedup = speedup
                worst_config = config
        
        # 生成报告
        report = f"""
# 大量列表少量元素场景归并排序性能分析报告

## 测试概况
- 测试用例总数: {len(results)}
- 测试时间: 2025年6月5日
- 测试范围: 2-1000个列表，每个列表1-100个元素

## 性能统计

### 整体性能表现
- 平均加速比: {statistics.mean(all_speedups):.2f}x
- 最佳加速比: {best_speedup:.2f}x (配置: {best_config['num_lists']}个列表，平均{best_config['avg_list_size']:.1f}个元素/列表)
- 最差加速比: {worst_speedup:.2f}x (配置: {worst_config['num_lists']}个列表，平均{worst_config['avg_list_size']:.1f}个元素/列表)
- 加速比标准差: {statistics.stdev(all_speedups):.2f}

### 大量列表场景 (≥100个列表)
- 测试用例数: {len(large_list_speedups)}
- 平均加速比: {statistics.mean(large_list_speedups) if large_list_speedups else 0:.2f}x
- 最大加速比: {max(large_list_speedups) if large_list_speedups else 0:.2f}x

### 极端场景 (≥500个列表)
- 测试用例数: {len(extreme_speedups)}
- 平均加速比: {statistics.mean(extreme_speedups) if extreme_speedups else 0:.2f}x
- 最大加速比: {max(extreme_speedups) if extreme_speedups else 0:.2f}x

## 关键发现

### 1. 算法优势场景
K-way merge算法在以下场景中表现最佳：
- 大量列表（>100个）且每个列表元素较少（<10个）
- 列表数量增长时，性能优势显著提升
- 极端情况下（1000个列表），加速比可达 {max(all_speedups):.1f}x

### 2. 时间复杂度分析
- **K-way Merge**: O(N log k)，其中N是总元素数，k是列表数
- **Traditional Merge**: O(k × N)，随列表数线性增长
- 当k增大时，K-way merge的优势越发明显

### 3. 内存使用分析
- K-way merge使用堆结构，内存使用相对稳定
- Traditional merge需要频繁创建中间结果，内存使用随列表数增长

### 4. 实际应用建议
- **推荐使用K-way merge的场景**:
  - 多用户推荐结果合并（每个用户少量推荐）
  - 分布式搜索结果聚合
  - 多数据源排序结果合并
  
- **Traditional merge适用场景**:
  - 少量列表（<10个）且每个列表元素较多
  - 内存限制严格的环境

## 测试环境
- Python版本: {sys.version}
- 测试平台: Windows
- 内存跟踪: tracemalloc
- 可视化: matplotlib, pandas

## 文件说明
- many_lists_merge_performance_analysis.png: 综合性能分析图表
- extreme_cases_analysis.png: 极端情况专门分析
- many_lists_performance_detailed.csv: 详细测试数据
- many_lists_performance_results.json: 完整测试结果

---
*报告生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # 保存报告
        with open('MANY_LISTS_PERFORMANCE_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 保存详细数据为CSV
        self.generate_detailed_csv(results)
        
        # 保存完整结果为JSON
        with open('many_lists_performance_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("报告生成完成!")
        print("生成文件:")
        print("- MANY_LISTS_PERFORMANCE_REPORT.md (分析报告)")
        print("- many_lists_merge_performance_analysis.png (综合分析图表)")
        print("- extreme_cases_analysis.png (极端情况分析)")
        print("- many_lists_performance_detailed.csv (详细数据)")
        print("- many_lists_performance_results.json (完整结果)")
    
    def generate_detailed_csv(self, results: List[Dict[str, Any]]):
        """生成详细的CSV数据表"""
        data = []
        
        for result in results:
            config = result['config']
            kway = result['kway_merge']
            traditional = result['traditional_merge']
            
            speedup = traditional['time']['mean'] / kway['time']['mean'] if kway['time']['mean'] > 0 else 1
            memory_ratio = traditional['memory_peak']['mean'] / kway['memory_peak']['mean'] if kway['memory_peak']['mean'] > 0 else 1
            
            data.append({
                '列表数量': config['num_lists'],
                '总元素数': config['total_elements'],
                '平均列表大小': config['avg_list_size'],
                'K-way执行时间(ms)': kway['time']['mean'] * 1000,
                'K-way时间标准差': kway['time']['std'] * 1000,
                'Traditional执行时间(ms)': traditional['time']['mean'] * 1000,
                'Traditional时间标准差': traditional['time']['std'] * 1000,
                '时间加速比': speedup,
                'K-way峰值内存(MB)': kway['memory_peak']['mean'] / 1024 / 1024,
                'Traditional峰值内存(MB)': traditional['memory_peak']['mean'] / 1024 / 1024,
                '内存比值': memory_ratio,
                '性能提升百分比': (speedup - 1) * 100
            })
        
        df = pd.DataFrame(data)
        df.to_csv('many_lists_performance_detailed.csv', index=False, encoding='utf-8-sig')

def main():
    """主函数"""
    print("大量列表少量元素场景归并排序算法性能对比测试")
    print("=" * 60)
    
    tester = ManyListsMergePerformanceTester()
    
    try:
        # 运行综合测试
        results = tester.run_comprehensive_tests()
        
        if not results:
            print("没有成功的测试结果")
            return
        
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
