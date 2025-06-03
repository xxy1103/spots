#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间复杂度验证测试
验证不同堆复制方法的实际时间复杂度
"""

import sys
import os
import time
import matplotlib.pyplot as plt
import numpy as np

# 添加模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'module'))

from data_structure.indexHeap import TopKHeap

def generate_test_data(size):
    """生成测试数据"""
    return [
        {"id": i, "value1": np.random.uniform(1, 5), "value2": np.random.randint(1000, 10000)}
        for i in range(size)
    ]

def measure_copy_time(heap, copy_method, iterations=100):
    """测量复制方法的时间"""
    start_time = time.perf_counter()
    
    for _ in range(iterations):
        if copy_method == "slice":
            temp = heap.heap[:]
        elif copy_method == "copy":
            temp = heap.heap.copy()
        elif copy_method == "list":
            temp = list(heap.heap)
        elif copy_method == "fast_copy":
            temp = heap._fast_heap_copy()
        elif copy_method == "shallow_dict":
            temp = heap._shallow_heap_copy_dict()
    
    end_time = time.perf_counter()
    return (end_time - start_time) / iterations

def measure_getTopK_time(heap, k, iterations=50):
    """测量getTopK方法的时间"""
    start_time = time.perf_counter()
    
    for _ in range(iterations):
        result = heap.getTopK(k)
    
    end_time = time.perf_counter()
    return (end_time - start_time) / iterations

def complexity_analysis():
    """时间复杂度分析"""
    print("时间复杂度验证测试")
    print("=" * 50)
    
    # 测试不同大小的堆
    sizes = [100, 500, 1000, 2000, 5000, 10000]
    copy_methods = ["slice", "copy", "list", "fast_copy", "shallow_dict"]
    
    results = {method: [] for method in copy_methods}
    getTopK_results = []
    
    for size in sizes:
        print(f"\n测试堆大小: {size}")
        
        # 创建测试堆
        heap = TopKHeap()
        test_data = generate_test_data(size)
        
        for item in test_data:
            heap.insert(item["id"], item["value1"], item["value2"])
        
        # 测试复制方法
        print("  复制方法时间 (μs):")
        for method in copy_methods:
            time_taken = measure_copy_time(heap, method, iterations=100)
            results[method].append(time_taken * 1000000)  # 转换为微秒
            print(f"    {method:<12}: {time_taken * 1000000:.2f} μs")
        
        # 测试getTopK (k=10)
        getTopK_time = measure_getTopK_time(heap, k=10, iterations=50)
        getTopK_results.append(getTopK_time * 1000000)  # 转换为微秒
        print(f"  getTopK(10)    : {getTopK_time * 1000000:.2f} μs")
    
    # 分析线性增长
    print("\n" + "=" * 50)
    print("时间复杂度分析:")
    print("=" * 50)
    
    for method in copy_methods:
        times = results[method]
        # 计算增长率 (相对于第一个数据点)
        growth_rates = [times[i] / times[0] for i in range(len(times))]
        size_ratios = [sizes[i] / sizes[0] for i in range(len(sizes))]
        
        print(f"\n{method} 方法:")
        print("  大小比例 vs 时间比例:")
        for i, (size_ratio, time_ratio) in enumerate(zip(size_ratios, growth_rates)):
            print(f"    {size_ratio:4.1f}x size -> {time_ratio:4.1f}x time")
        
        # 计算平均线性度 (应该接近1.0表示O(n))
        if len(growth_rates) > 1:
            linearity = np.mean([growth_rates[i] / size_ratios[i] for i in range(1, len(growth_rates))])
            print(f"  平均线性度: {linearity:.2f} (1.0表示完美O(n))")
    
    # getTopK 复杂度分析
    print(f"\ngetTopK(10) 方法:")
    getTopK_growth_rates = [getTopK_results[i] / getTopK_results[0] for i in range(len(getTopK_results))]
    size_ratios = [sizes[i] / sizes[0] for i in range(len(sizes))]
    
    print("  大小比例 vs 时间比例:")
    for i, (size_ratio, time_ratio) in enumerate(zip(size_ratios, getTopK_growth_rates)):
        print(f"    {size_ratio:4.1f}x size -> {time_ratio:4.1f}x time")

def verify_theoretical_complexity():
    """验证理论时间复杂度"""
    print("\n" + "=" * 50)
    print("理论复杂度验证:")
    print("=" * 50)
    
    # 创建大堆进行测试
    size = 5000
    heap = TopKHeap()
    test_data = generate_test_data(size)
    
    for item in test_data:
        heap.insert(item["id"], item["value1"], item["value2"])
    
    print(f"堆大小: {size}")
    print("\ngetTopK 不同k值的时间复杂度:")
    
    k_values = [1, 5, 10, 25, 50, 100, 250, 500]
    
    for k in k_values:
        if k <= size:
            time_taken = measure_getTopK_time(heap, k, iterations=20)
            print(f"  k={k:3d}: {time_taken * 1000000:6.1f} μs")
    
    print("\n理论分析:")
    print("  - 复制堆: O(n) = O(5000) - 固定成本")
    print("  - k次提取: O(k log n) = O(k × log(5000)) ≈ O(k × 12.3)")
    print("  - 总计: O(n + k log n)")
    print("  - 当k很小时，主要是O(n)复制成本")
    print("  - 当k增大时，O(k log n)提取成本逐渐显现")

if __name__ == "__main__":
    complexity_analysis()
    verify_theoretical_complexity()
