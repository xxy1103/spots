#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
堆复制性能测试
比较不同复制方法的性能表现
"""

import time
import random
import sys
import os
import matplotlib.pyplot as plt
import numpy as np

# 添加模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'module'))

from module.data_structure.indexHeap import TopKHeap

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

def generate_test_data(size):
    """生成测试数据"""
    data = []
    for i in range(size):
        data.append({
            "id": i,
            "value1": round(random.uniform(1.0, 5.0), 2),
            "value2": random.randint(1000, 10000)
        })
    return data

def test_copy_methods(heap, iterations=1000):
    """测试不同复制方法的性能"""
    
    # 测试1: 使用.copy()方法
    start_time = time.time()
    for _ in range(iterations):
        temp = heap.heap.copy()
    copy_time = time.time() - start_time
    
    # 测试2: 使用切片[:]
    start_time = time.time()
    for _ in range(iterations):
        temp = heap.heap[:]
    slice_time = time.time() - start_time
    
    # 测试3: 使用_fast_heap_copy方法
    start_time = time.time()
    for _ in range(iterations):
        temp = heap._fast_heap_copy()
    fast_copy_time = time.time() - start_time
    
    # 测试4: 使用列表构造器
    start_time = time.time()
    for _ in range(iterations):
        temp = list(heap.heap)
    list_constructor_time = time.time() - start_time
    
    # 测试5: 使用浅复制字典方法
    start_time = time.time()
    for _ in range(iterations):
        temp = heap._shallow_heap_copy_dict()
    shallow_dict_time = time.time() - start_time
    
    return {
        "copy()": copy_time,
        "切片[:]": slice_time,
        "_fast_heap_copy()": fast_copy_time,
        "list()构造器": list_constructor_time,
        "浅复制字典": shallow_dict_time
    }

def test_getTopK_performance(heap, k_values, iterations=100):
    """测试getTopK方法在不同k值下的性能"""
    results = {}
    
    for k in k_values:
        start_time = time.time()
        for _ in range(iterations):
            result = heap.getTopK(k)
        end_time = time.time()
        
        results[f"k={k}"] = (end_time - start_time) / iterations
        
    return results

def plot_copy_performance(all_results, test_sizes):
    """绘制复制方法性能对比图表"""
    
    # 准备数据
    methods = list(all_results[test_sizes[0]].keys())
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('堆复制方法性能对比分析', fontsize=16, fontweight='bold')
    
    # 1. 不同堆大小下各方法的执行时间对比
    ax1 = axes[0, 0]
    for method in methods:
        times = [all_results[size][method] for size in test_sizes]
        ax1.plot(test_sizes, times, marker='o', linewidth=2, markersize=6, label=method)
    
    ax1.set_xlabel('堆大小', fontsize=12)
    ax1.set_ylabel('执行时间 (秒)', fontsize=12)
    ax1.set_title('不同堆大小下的执行时间对比', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    
    # 2. 柱状图 - 最大堆大小下的性能对比
    ax2 = axes[0, 1]
    max_size = max(test_sizes)
    times = [all_results[max_size][method] for method in methods]
    
    bars = ax2.bar(range(len(methods)), times, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
    ax2.set_xlabel('复制方法', fontsize=12)
    ax2.set_ylabel('执行时间 (秒)', fontsize=12)
    ax2.set_title(f'堆大小={max_size}时的性能对比', fontsize=14)
    ax2.set_xticks(range(len(methods)))
    ax2.set_xticklabels(methods, rotation=45, ha='right')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 在柱状图上添加数值标签
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.6f}s', ha='center', va='bottom', fontsize=10)
      # 3. 相对性能倍数图 (以最快方法为基准)
    ax3 = axes[1, 0]
    
    relative_performance = {}
    for size in test_sizes:
        fastest_time = min(all_results[size].values())
        # 避免除零错误
        if fastest_time == 0:
            fastest_time = 1e-8
        relative_performance[size] = {}
        for method in methods:
            method_time = all_results[size][method]
            if method_time == 0:
                method_time = 1e-8
            relative_performance[size][method] = method_time / fastest_time
    
    for method in methods:
        ratios = [relative_performance[size][method] for size in test_sizes]
        ax3.plot(test_sizes, ratios, marker='s', linewidth=2, markersize=6, label=method)
    
    ax3.set_xlabel('堆大小', fontsize=12)
    ax3.set_ylabel('相对性能倍数 (相对最快方法)', fontsize=12)
    ax3.set_title('相对性能倍数对比', fontsize=14)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_xscale('log')
    ax3.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='基准线')
    
    # 4. 热力图 - 不同堆大小下各方法的性能表现
    ax4 = axes[1, 1]
      # 准备热力图数据
    heatmap_data = np.zeros((len(methods), len(test_sizes)))
    for i, method in enumerate(methods):
        for j, size in enumerate(test_sizes):
            time_val = all_results[size][method]
            # 避免零值导致的问题
            if time_val == 0:
                time_val = 1e-8
            heatmap_data[i, j] = time_val
    
    # 归一化到0-1范围以便颜色映射
    normalized_data = (heatmap_data - np.min(heatmap_data)) / (np.max(heatmap_data) - np.min(heatmap_data))
    
    im = ax4.imshow(normalized_data, cmap='RdYlGn_r', aspect='auto')
    ax4.set_xticks(range(len(test_sizes)))
    ax4.set_xticklabels(test_sizes)
    ax4.set_yticks(range(len(methods)))
    ax4.set_yticklabels(methods)
    ax4.set_xlabel('堆大小', fontsize=12)
    ax4.set_ylabel('复制方法', fontsize=12)
    ax4.set_title('性能热力图 (红色=慢, 绿色=快)', fontsize=14)
    
    # 添加数值标注
    for i in range(len(methods)):
        for j in range(len(test_sizes)):
            text = ax4.text(j, i, f'{heatmap_data[i, j]:.4f}s',
                           ha="center", va="center", color="black", fontsize=8)
    
    plt.tight_layout()
    plt.savefig('heap_copy_performance_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_topk_performance(all_topk_results, test_sizes):
    """绘制TopK性能对比图表"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('TopK方法性能分析', fontsize=16, fontweight='bold')
    
    # 1. 不同k值的性能对比
    ax1_data = {}
    for size in test_sizes:
        if size in all_topk_results:
            for k_desc, time_val in all_topk_results[size].items():
                if k_desc not in ax1_data:
                    ax1_data[k_desc] = []
                ax1_data[k_desc].append(time_val)
    
    for k_desc, times in ax1_data.items():
        if len(times) == len(test_sizes):
            ax1.plot(test_sizes, times, marker='o', linewidth=2, markersize=6, label=k_desc)
    
    ax1.set_xlabel('堆大小', fontsize=12)
    ax1.set_ylabel('平均执行时间 (秒)', fontsize=12)
    ax1.set_title('不同k值下的TopK性能', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    
    # 2. 最大堆大小下不同k值的性能对比
    max_size = max([size for size in test_sizes if size in all_topk_results])
    if max_size in all_topk_results:
        k_values = list(all_topk_results[max_size].keys())
        times = list(all_topk_results[max_size].values())
        
        bars = ax2.bar(range(len(k_values)), times, color='skyblue')
        ax2.set_xlabel('k值', fontsize=12)
        ax2.set_ylabel('平均执行时间 (秒)', fontsize=12)
        ax2.set_title(f'堆大小={max_size}时不同k值的性能', fontsize=14)
        ax2.set_xticks(range(len(k_values)))
        ax2.set_xticklabels(k_values, rotation=45, ha='right')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标签
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.6f}s', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('topk_performance_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_performance_summary(all_results, test_sizes):
    """生成性能总结报告"""
    
    print("\n" + "=" * 60)
    print("性能分析总结报告")
    print("=" * 60)
    
    # 找出每个堆大小下最快的方法
    print("\n最优复制方法推荐:")
    print("-" * 40)
    
    for size in test_sizes:
        fastest_method = min(all_results[size], key=all_results[size].get)
        fastest_time = all_results[size][fastest_method]
        print(f"堆大小 {size:>6}: {fastest_method:<15} ({fastest_time:.6f}s)")
    
    # 计算平均性能排名
    print("\n平均性能排名:")
    print("-" * 40)
    
    method_avg_times = {}
    methods = list(all_results[test_sizes[0]].keys())
    
    for method in methods:
        avg_time = sum(all_results[size][method] for size in test_sizes) / len(test_sizes)
        method_avg_times[method] = avg_time
    
    sorted_methods = sorted(method_avg_times.items(), key=lambda x: x[1])
    
    for rank, (method, avg_time) in enumerate(sorted_methods, 1):
        print(f"{rank}. {method:<15}: {avg_time:.6f}s (平均)")
    
    # 复杂度分析
    print("\n时间复杂度分析:")
    print("-" * 40)
    
    for method in methods:
        times = [all_results[size][method] for size in test_sizes]
        
        # 简单的复杂度估算 (基于最后两个数据点)
        if len(times) >= 2:
            ratio = times[-1] / times[-2]
            size_ratio = test_sizes[-1] / test_sizes[-2]
            
            if ratio < size_ratio * 0.5:
                complexity = "接近 O(1) 或 O(log n)"
            elif ratio < size_ratio * 1.5:
                complexity = "接近 O(n)"
            else:
                complexity = "可能 O(n log n) 或更高"
            
            print(f"{method:<15}: {complexity}")

def main():
    print("堆复制性能测试与分析")
    print("=" * 50)
    
    # 测试不同大小的堆
    test_sizes = [100, 1000, 5000, 10000]
    all_results = {}
    all_topk_results = {}
    
    for size in test_sizes:
        print(f"\n测试堆大小: {size}")
        print("-" * 30)
        
        # 创建并填充堆
        heap = TopKHeap()
        test_data = generate_test_data(size)
        
        for item in test_data:
            heap.insert(item["id"], item["value1"], item["value2"])
        
        # 测试复制方法性能
        copy_results = test_copy_methods(heap, iterations=1000)
        all_results[size] = copy_results
        
        print("复制方法性能 (1000次操作):")
        fastest_time = max(min(copy_results.values()), 1e-8)
        
        for method, time_taken in copy_results.items():
            if time_taken > 0:
                speedup = fastest_time / time_taken
                print(f"  {method:<15}: {time_taken:.6f}s (相对最快: {speedup:.2f}x)")
            else:
                print(f"  {method:<15}: {time_taken:.6f}s (几乎瞬时完成)")
        
        # 测试getTopK性能
        if size >= 1000:
            k_values = [10, 50, 100, size//10]
        else:
            k_values = [10, size//4, size//2]
            
        topk_results = test_getTopK_performance(heap, k_values, iterations=100)
        all_topk_results[size] = topk_results
        
        print("\ngetTopK方法性能 (100次操作):")
        for k_desc, avg_time in topk_results.items():
            print(f"  {k_desc:<15}: {avg_time:.6f}s")
    
    # 生成图表
    print("\n正在生成性能分析图表...")
    plot_copy_performance(all_results, test_sizes)
    plot_topk_performance(all_topk_results, test_sizes)
    
    # 生成总结报告
    generate_performance_summary(all_results, test_sizes)
    
    print("\n" + "=" * 50)
    print("性能优化建议:")
    print("1. 对于小堆(<1000元素): 使用切片[:]是最快的复制方法")
    print("2. 对于大堆且k值很小: 考虑使用heapq.nlargest")
    print("3. 避免使用深度复制，除非绝对必要")
    print("4. 当k值接近堆大小时，直接排序可能更高效")
    print("5. 图表已保存为 'heap_copy_performance_analysis.png' 和 'topk_performance_analysis.png'")

if __name__ == "__main__":
    main()
