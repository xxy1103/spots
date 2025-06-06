# module/k_way_merge.py
"""
K-way merge sort algorithm using a MinHeap.
"""

# 假设 MinHeap 类位于 module/data_structure/heap.py
# 如果 k_way_merge.py 与 data_structure 目录同在 module 目录下，
# 可以使用相对导入。
from module.data_structure.heap import MinHeap
# 如果是从项目根目录运行，可能需要调整为:
# from module.data_structure.heap import MinHeap

def k_way_merge_descending(list_of_lists, limit=None):
    """
    对多个已排序的列表进行k路归并。每个子列表包含格式为
    {"id": ..., "value1": ..., "value2": ...} 的字典。
    归并结果为一个按照 'value1'（降序）、再按 'value2'（降序）排序的单一列表。

    假设 list_of_lists 中的每个子列表都已按 'value1' 降序、再按 'value2' 降序排序。

    参数:
        list_of_lists: k个已排序列表组成的列表。每个子列表包含若干字典。
        limit: 可选整数。如果指定，则在收集到 'limit' 个元素后停止归并。
               适用于获取前k个结果。

    返回:
        一个包含归并后元素（如指定则最多 'limit' 个），
        并按要求降序排序的列表。
    """
    if not list_of_lists:
        return []

    min_heap = MinHeap()
    result = []

    # Initialize the heap with the first element from each non-empty list
    # Heap stores tuples: (-value1, -value2, list_index, item_index_in_list, original_item_dict)
    # list_index and item_index_in_list help in tie-breaking if (-value1, -value2) are identical,
    # ensuring a more stable-like sort before comparing original_item_dict (which is avoided).
    for i, sub_list in enumerate(list_of_lists):
        if sub_list:
            item = sub_list[0]
            # Negate values for descending sort using MinHeap
            heap_item = (
                -item['value1'],
                -item['value2'],
                i,  # list_index for tie-breaking
                0,  # item_index_in_list for tie-breaking
                item # The actual dictionary
            )
            min_heap.push(heap_item)    # Merge process with optional limit
    while not min_heap.is_empty():
        # Check if we've reached the limit
        if limit is not None and len(result) >= limit:
            break
            
        neg_v1, neg_v2, list_idx, item_idx, current_item = min_heap.pop()
        result.append(current_item)

        # If there are more elements in the list from which current_item was taken,
        # add the next element to the heap.
        next_item_idx = item_idx + 1
        if next_item_idx < len(list_of_lists[list_idx]):
            next_item = list_of_lists[list_idx][next_item_idx]
            new_heap_item = (
                -next_item['value1'],
                -next_item['value2'],
                list_idx,
                next_item_idx,
                next_item
            )
            min_heap.push(new_heap_item)

    return result

def get_top_k_elements(list_of_lists, k):
    """
    获取前k个最大的元素的便捷函数
    
    Args:
        list_of_lists: 已排序的列表集合
        k: 需要的前k个元素数量
        
    Returns:
        包含前k个元素的列表
    """
    return k_way_merge_descending(list_of_lists, limit=k)

def get_top_k_with_iterators(list_of_lists, k):
    """
    使用迭代器思想获取Top-K元素，只需要k次比较
    每次从所有列表的当前位置中找出最大值，然后移动对应的指针
    
    Args:
        list_of_lists: k个已排序列表组成的列表（每个列表按value1降序，value2降序排序）
        k: 需要的前k个元素数量
        
    Returns:
        包含前k个最大元素的列表
        
    Time Complexity: O(k * m) where m is the number of lists
    Space Complexity: O(m)
    """
    if not list_of_lists or k <= 0:
        return []
    
    # 初始化迭代器列表，每个迭代器指向对应列表的当前位置
    iterators = []
    for i, lst in enumerate(list_of_lists):
        if lst:  # 只添加非空列表
            iterators.append({
                'list_idx': i,
                'current_idx': 0,
                'current_item': lst[0],
                'list_ref': lst
            })
    
    result = []
    
    # 进行k次迭代，每次找到当前最大值
    for _ in range(k):
        if not iterators:
            break
            
        # 找到当前所有迭代器中的最大值
        max_iterator_idx = 0
        max_item = iterators[0]['current_item']
        
        for i in range(1, len(iterators)):
            current_item = iterators[i]['current_item']
            # 比较规则：先比较value1，再比较value2（都是降序）
            if (current_item['value1'] > max_item['value1'] or 
                (current_item['value1'] == max_item['value1'] and 
                 current_item['value2'] > max_item['value2'])):
                max_iterator_idx = i
                max_item = current_item
        
        # 将最大值添加到结果中
        result.append(max_item)
        
        # 移动对应的迭代器到下一个位置
        selected_iterator = iterators[max_iterator_idx]
        selected_iterator['current_idx'] += 1
        
        # 检查是否还有下一个元素
        if selected_iterator['current_idx'] < len(selected_iterator['list_ref']):
            # 更新当前元素
            selected_iterator['current_item'] = selected_iterator['list_ref'][selected_iterator['current_idx']]
        else:
            # 如果该列表已遍历完，移除这个迭代器
            iterators.pop(max_iterator_idx)
    
    return result

def get_top_k_with_heap_optimized(list_of_lists, k):
    """
    使用堆的优化版本，明确只进行k次堆操作
    相比原始版本，这个版本在获取Top-K时更加高效
    
    Args:
        list_of_lists: k个已排序列表组成的列表
        k: 需要的前k个元素数量
        
    Returns:
        包含前k个最大元素的列表
        
    Time Complexity: O(k * log m) where m is the number of lists
    Space Complexity: O(m)
    """
    if not list_of_lists or k <= 0:
        return []

    min_heap = MinHeap()
    result = []

    # 初始化堆 - 只添加每个列表的第一个元素
    for i, sub_list in enumerate(list_of_lists):
        if sub_list:
            item = sub_list[0]
            heap_item = (
                -item['value1'],
                -item['value2'],
                i,
                0,
                item
            )
            min_heap.push(heap_item)

    # 只进行k次操作
    for _ in range(k):
        if min_heap.is_empty():
            break
            
        neg_v1, neg_v2, list_idx, item_idx, current_item = min_heap.pop()
        result.append(current_item)

        # 添加来自同一列表的下一个元素
        next_item_idx = item_idx + 1
        if next_item_idx < len(list_of_lists[list_idx]):
            next_item = list_of_lists[list_idx][next_item_idx]
            new_heap_item = (
                -next_item['value1'],
                -next_item['value2'],
                list_idx,
                next_item_idx,
                next_item
            )
            min_heap.push(new_heap_item)

    return result

if __name__ == '__main__':
    # Example Usage (requires MinHeap to be accessible)
    # Assuming MinHeap class is defined in module.data_structure.heap


    list1 = [
        {"id": "A1", "value1": 100, "value2": 5},
        {"id": "A2", "value1": 90, "value2": 10},
        {"id": "A3", "value1": 80, "value2": 1}
    ] # Sorted descending
    list2 = [
        {"id": "B1", "value1": 100, "value2": 3},
        {"id": "B2", "value1": 85, "value2": 20},
    ] # Sorted descending
    list3 = [
        {"id": "C1", "value1": 95, "value2": 8},
        {"id": "C2", "value1": 90, "value2": 12},
        {"id": "C3", "value1": 70, "value2": 5}
    ] # Sorted descending
    list_empty = []
    list_single = [{"id": "D1", "value1": 110, "value2": 1}]


    all_lists = [list1, list2, list3, list_empty, list_single]
        # Need to ensure MinHeap is correctly imported for this test to run.
    # If module.data_structure.heap.MinHeap is not found, this will fail.
    # For testing, you might need to adjust PYTHONPATH or use a placeholder.
    # For the purpose of this response, assume MinHeap is available via the import.
    
    # 测试完整归并
    print("完整归并结果:")
    merged_list = k_way_merge_descending(all_lists)
    for item in merged_list:
        print(item)
    
    print("\n" + "="*50 + "\n")
    
    # 测试限制前3个元素
    print("仅获取前3个元素:")
    top_3 = k_way_merge_descending(all_lists, limit=3)
    for item in top_3:
        print(item)    
    print("\n" + "="*50 + "\n")
    
    # 使用便捷函数获取前5个元素
    print("使用便捷函数获取前5个元素:")
    top_5 = get_top_k_elements(all_lists, 5)
    for item in top_5:
        print(item)
    
    print("\n" + "="*50 + "\n")
    
    # 测试迭代器方法
    print("使用迭代器方法获取前3个元素:")
    top_3_iterators = get_top_k_with_iterators(all_lists, 3)
    for item in top_3_iterators:
        print(item)
    
    print("\n" + "="*50 + "\n")
    
    # 测试优化的堆方法
    print("使用优化堆方法获取前3个元素:")
    top_3_heap_opt = get_top_k_with_heap_optimized(all_lists, 3)
    for item in top_3_heap_opt:
        print(item)

    # Expected output order (example):
    # {"id": "D1", "value1": 110, "value2": 1}
    # {"id": "A1", "value1": 100, "value2": 5}
    # {"id": "B1", "value1": 100, "value2": 3}
    # {"id": "C1", "value1": 95, "value2": 8}
    # {"id": "C2", "value1": 90, "value2": 12}
    # {"id": "A2", "value1": 90, "value2": 10}
    # {"id": "B2", "value1": 85, "value2": 20}
    # {"id": "C3", "value1": 70, "value2": 5}
    # {"id": "A3", "value1": 80, "value2": 1}