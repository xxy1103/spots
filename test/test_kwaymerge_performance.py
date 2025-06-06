#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K路归并排序性能测试程序
比较三种不同方法的性能：
1. 完整归并方法 (k_way_merge_descending)
2. 迭代器方法 (get_top_k_with_iterators)
3. 优化堆方法 (get_top_k_with_heap_optimized)
"""

import time
import random
import sys
import os
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import matplotlib
import json

# 设置中文字体支持
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']  # 中文字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 正确显示负号

def setup_chinese_font():
    """
    设置matplotlib的中文字体支持
    """
    import platform
    
    # 获取系统类型
    system = platform.system()
    
    if system == "Windows":
        # Windows系统常用中文字体
        fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']
    elif system == "Darwin":  # macOS
        # macOS系统中文字体
        fonts = ['PingFang SC', 'Hiragino Sans GB', 'STSong', 'SimHei']
    else:  # Linux
        # Linux系统中文字体
        fonts = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'SimHei']
    
    # 添加默认字体作为备选
    fonts.extend(['DejaVu Sans', 'Arial', 'sans-serif'])
    
    # 设置字体
    matplotlib.rcParams['font.sans-serif'] = fonts
    matplotlib.rcParams['axes.unicode_minus'] = False
    matplotlib.rcParams['font.size'] = 10
    
    # 测试中文显示
    try:
        fig, ax = plt.subplots(figsize=(1, 1))
        ax.text(0.5, 0.5, '测试中文显示', ha='center', va='center')
        plt.close(fig)
        print("✅ 中文字体配置成功")
    except Exception as e:
        print(f"⚠️ 中文字体配置可能有问题: {e}")

# 添加模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入K路归并模块
try:
    from module.data_structure.kwaymerge import (
        k_way_merge_descending,
        get_top_k_with_iterators,
        get_top_k_with_heap_optimized
    )
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保heap.py和kwaymerge.py文件存在于正确的路径中")
    sys.exit(1)

class PerformanceTimer:
    """性能计时器"""
    def __init__(self):
        self.start_time = 0
        
    def start(self):
        self.start_time = time.time()
        
    def stop(self):
        return time.time() - self.start_time

def generate_test_data(num_lists: int, list_size: int, value_range: int = 1000) -> List[List[Dict[str, Any]]]:
    """
    生成测试数据
    
    Args:
        num_lists: 列表数量
        list_size: 每个列表的大小
        value_range: 值的范围
        
    Returns:
        包含多个已排序列表的列表
    """
    test_lists = []
    
    for i in range(num_lists):
        # 生成随机数据
        data = []
        for j in range(list_size):
            data.append({
                "id": f"L{i}_Item{j}",
                "value1": random.randint(1, value_range),
                "value2": random.randint(1, value_range // 2)
            })
        
        # 按value1降序，value2降序排序
        data.sort(key=lambda x: (-x['value1'], -x['value2']))
        test_lists.append(data)
    
    return test_lists

def verify_results_correctness(result1: List[Dict], result2: List[Dict], result3: List[Dict]) -> bool:
    """
    验证三种方法的结果是否一致
    
    Args:
        result1, result2, result3: 三种方法的结果
        
    Returns:
        bool: 结果是否一致
    """
    if len(result1) != len(result2) or len(result1) != len(result3):
        return False
    
    for i in range(len(result1)):
        if (result1[i]['id'] != result2[i]['id'] or 
            result1[i]['id'] != result3[i]['id'] or
            result1[i]['value1'] != result2[i]['value1'] or
            result1[i]['value1'] != result3[i]['value1'] or
            result1[i]['value2'] != result2[i]['value2'] or
            result1[i]['value2'] != result3[i]['value2']):
            return False
    
    return True

def run_performance_test(test_lists: List[List[Dict]], k_values: List[int]) -> Dict[str, Any]:
    """
    运行性能测试
    
    Args:
        test_lists: 测试数据
        k_values: 不同的k值列表
        
    Returns:
        测试结果字典
    """
    results = {
        'k_values': k_values,
        'complete_merge_times': [],
        'iterator_times': [],
        'heap_optimized_times': [],
        'num_lists': len(test_lists),
        'avg_list_size': sum(len(lst) for lst in test_lists) // len(test_lists),
        'correctness_verified': True
    }
    
    timer = PerformanceTimer()
    
    print(f"开始性能测试...")
    print(f"列表数量: {len(test_lists)}")
    print(f"平均列表大小: {results['avg_list_size']}")
    print(f"测试的k值: {k_values}")
    print("-" * 60)
    
    for k in k_values:
        print(f"\n测试 k = {k}:")
        
        # 测试完整归并方法
        timer.start()
        result1 = k_way_merge_descending(test_lists, limit=k)
        time1 = timer.stop()
        results['complete_merge_times'].append(time1)
        print(f"  完整归并方法: {time1:.6f} 秒")
        
        # 测试迭代器方法
        timer.start()
        result2 = get_top_k_with_iterators(test_lists, k)
        time2 = timer.stop()
        results['iterator_times'].append(time2)
        print(f"  迭代器方法:   {time2:.6f} 秒")
        
        # 测试优化堆方法
        timer.start()
        result3 = get_top_k_with_heap_optimized(test_lists, k)
        time3 = timer.stop()
        results['heap_optimized_times'].append(time3)
        print(f"  优化堆方法:   {time3:.6f} 秒")
        
        # 验证结果正确性
        if not verify_results_correctness(result1, result2, result3):
            print(f"  ❌ 警告: k={k}时结果不一致!")
            results['correctness_verified'] = False
        else:
            print(f"  ✅ 结果验证通过")
          # 显示性能比较
        fastest_time = min(time1, time2, time3)
        if fastest_time > 0:
            print(f"  性能比较:")
            print(f"    完整归并 vs 最快: {time1/fastest_time:.2f}x")
            print(f"    迭代器   vs 最快: {time2/fastest_time:.2f}x")
            print(f"    优化堆   vs 最快: {time3/fastest_time:.2f}x")
        else:
            print(f"  性能比较: 执行时间过快，无法准确测量")
    
    return results

def plot_performance_results(results: Dict[str, Any], save_path: str = None):
    """
    绘制性能测试结果图表
    
    Args:
        results: 测试结果
        save_path: 保存路径
    """
    plt.figure(figsize=(12, 8))
    
    k_values = results['k_values']
    
    # 绘制性能曲线
    plt.subplot(2, 2, 1)
    plt.plot(k_values, results['complete_merge_times'], 'o-', label='完整归并方法', linewidth=2)
    plt.plot(k_values, results['iterator_times'], 's-', label='迭代器方法', linewidth=2)
    plt.plot(k_values, results['heap_optimized_times'], '^-', label='优化堆方法', linewidth=2)
    plt.xlabel('k值')
    plt.ylabel('执行时间 (秒)')
    plt.title('K路归并性能比较')
    plt.legend()
    plt.grid(True, alpha=0.3)
      # 绘制性能比率
    plt.subplot(2, 2, 2)
    baseline_times = results['heap_optimized_times']  # 使用优化堆作为基准
    complete_ratios = [t1/t2 if t2 > 0 else 1 for t1, t2 in zip(results['complete_merge_times'], baseline_times)]
    iterator_ratios = [t1/t2 if t2 > 0 else 1 for t1, t2 in zip(results['iterator_times'], baseline_times)]
    
    plt.plot(k_values, complete_ratios, 'o-', label='完整归并 / 优化堆', linewidth=2)
    plt.plot(k_values, iterator_ratios, 's-', label='迭代器 / 优化堆', linewidth=2)
    plt.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='基准线')
    plt.xlabel('k值')
    plt.ylabel('性能比率')
    plt.title('相对性能比较 (以优化堆为基准)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 绘制时间复杂度分析
    plt.subplot(2, 2, 3)
    # 理论复杂度曲线
    import numpy as np
    k_theory = np.array(k_values)
    m = results['num_lists']
    
    # O(k * m) - 迭代器方法理论复杂度
    iterator_theory = k_theory * m
    iterator_theory = iterator_theory / iterator_theory[0] * results['iterator_times'][0]
    
    # O(k * log m) - 堆方法理论复杂度
    heap_theory = k_theory * np.log(m)
    heap_theory = heap_theory / heap_theory[0] * results['heap_optimized_times'][0]
    
    plt.plot(k_values, results['iterator_times'], 's-', label='迭代器方法(实际)', linewidth=2)
    plt.plot(k_values, iterator_theory, 's--', label='O(k*m)理论', alpha=0.7)
    plt.plot(k_values, results['heap_optimized_times'], '^-', label='优化堆方法(实际)', linewidth=2)
    plt.plot(k_values, heap_theory, '^--', label='O(k*log m)理论', alpha=0.7)
    
    plt.xlabel('k值')
    plt.ylabel('执行时间 (秒)')
    plt.title('实际性能 vs 理论复杂度')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 添加统计信息
    plt.subplot(2, 2, 4)
    plt.axis('off')
    
    # 计算平均性能提升
    avg_complete_time = sum(results['complete_merge_times']) / len(results['complete_merge_times'])
    avg_iterator_time = sum(results['iterator_times']) / len(results['iterator_times'])
    avg_heap_time = sum(results['heap_optimized_times']) / len(results['heap_optimized_times'])
    
    stats_text = f"""测试统计信息:
    
列表数量: {results['num_lists']}
平均列表大小: {results['avg_list_size']}
测试的k值范围: {min(k_values)} - {max(k_values)}

平均执行时间:
• 完整归并: {avg_complete_time:.6f}s
• 迭代器方法: {avg_iterator_time:.6f}s  
• 优化堆方法: {avg_heap_time:.6f}s

性能提升:
• 迭代器 vs 完整归并: {avg_complete_time/avg_iterator_time if avg_iterator_time > 0 else float('inf'):.2f}x
• 优化堆 vs 完整归并: {avg_complete_time/avg_heap_time if avg_heap_time > 0 else float('inf'):.2f}x
• 优化堆 vs 迭代器: {avg_iterator_time/avg_heap_time if avg_heap_time > 0 else float('inf'):.2f}x

结果正确性: {'✅ 通过' if results['correctness_verified'] else '❌ 失败'}
"""
    
    plt.text(0.05, 0.95, stats_text, transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"性能测试图表已保存到: {save_path}")
    
    plt.show()

def save_results_to_file(results: Dict[str, Any], filepath: str):
    """保存测试结果到JSON文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"测试结果已保存到: {filepath}")

def main():
    """主测试函数"""
    # 首先设置中文字体
    setup_chinese_font()
    
    print("=" * 60)
    print("K路归并排序性能测试程序")
    print("=" * 60)
    
    # 测试配置
    test_configs = [
        {
            'name': '小规模测试',
            'num_lists': 5,
            'list_size': 100,
            'k_values': [1, 5, 10, 20, 50],
            'value_range': 1000
        },
        {
            'name': '中等规模测试',
            'num_lists': 10,
            'list_size': 500,
            'k_values': [1, 10, 25, 50, 100, 200],
            'value_range': 5000
        },
        {
            'name': '大规模测试',
            'num_lists': 20,
            'list_size': 1000,
            'k_values': [1, 20, 50, 100, 200, 500],
            'value_range': 10000
        }
    ]
    
    all_results = {}
    
    for config in test_configs:
        print(f"\n{'='*20} {config['name']} {'='*20}")
        
        # 生成测试数据
        print("生成测试数据...")
        test_lists = generate_test_data(
            config['num_lists'], 
            config['list_size'], 
            config['value_range']
        )
        
        # 运行性能测试
        results = run_performance_test(test_lists, config['k_values'])
        all_results[config['name']] = results
        
        # 绘制性能图表
        plot_save_path = f"kwaymerge_performance_{config['name'].replace(' ', '_')}.png"
        plot_performance_results(results, plot_save_path)
        
        # 保存详细结果
        result_save_path = f"kwaymerge_results_{config['name'].replace(' ', '_')}.json"
        save_results_to_file(results, result_save_path)
      # 生成综合报告
    print(f"\n{'='*60}")
    print("综合性能报告")
    print(f"{'='*60}")
    
    for name, results in all_results.items():
        print(f"\n{name}:")
        avg_complete = sum(results['complete_merge_times']) / len(results['complete_merge_times'])
        avg_iterator = sum(results['iterator_times']) / len(results['iterator_times'])
        avg_heap = sum(results['heap_optimized_times']) / len(results['heap_optimized_times'])
        
        print(f"  平均性能 - 完整归并: {avg_complete:.6f}s")
        print(f"  平均性能 - 迭代器:   {avg_iterator:.6f}s")  
        print(f"  平均性能 - 优化堆:   {avg_heap:.6f}s")
        print(f"  最优方法: {'迭代器' if avg_iterator <= avg_heap else '优化堆'}")
        
        # 安全的除法计算
        if avg_iterator > 0 and avg_heap > 0:
            improvement = max(avg_complete/avg_iterator, avg_complete/avg_heap)
            print(f"  性能提升: {improvement:.2f}x")
        else:
            print(f"  性能提升: 无法计算（时间过短）")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
