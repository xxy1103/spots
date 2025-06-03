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

# 添加模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'module'))

from module.data_structure.indexHeap import TopKHeap

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

def main():
    print("堆复制性能测试")
    print("=" * 50)
    
    # 测试不同大小的堆
    test_sizes = [100, 1000, 5000, 10000]
    
    for size in test_sizes:
        print(f"\n测试堆大小: {size}")
        print("-" * 30)
        
        # 创建并填充堆
        heap = TopKHeap()
        test_data = generate_test_data(size)
        
        for item in test_data:            heap.insert(item["id"], item["value1"], item["value2"])
        
        # 测试复制方法性能
        copy_results = test_copy_methods(heap, iterations=1000)
        
        print("复制方法性能 (1000次操作):")
        fastest_time = max(min(copy_results.values()), 1e-8)  # 避免除零错误
        
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
        
        print("\ngetTopK方法性能 (100次操作):")
        for k_desc, avg_time in topk_results.items():
            print(f"  {k_desc:<15}: {avg_time:.6f}s")
    
    print("\n" + "=" * 50)
    print("性能优化建议:")
    print("1. 对于小堆(<1000元素): 使用切片[:]是最快的复制方法")
    print("2. 对于大堆且k值很小: 考虑使用heapq.nlargest")
    print("3. 避免使用深度复制，除非绝对必要")
    print("4. 当k值接近堆大小时，直接排序可能更高效")

if __name__ == "__main__":
    main()
