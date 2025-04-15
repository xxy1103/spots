def partition(arr, low, high, sort_key=None):
    """
    分区函数，用于快速排序。

    Args:
        arr: 要排序的列表，元素为 {"id": ..., "score": ..., "visited_time": ...} 格式的字典。
        low: 列表的起始索引。
        high: 列表的结束索引。
        sort_key: 排序依据的键 ('visited_time' 或 None)。
                  None 表示默认排序（score 降序, visited_time 降序）。
                  'visited_time' 表示仅按 visited_time 降序。

    Returns:
        分区点的索引。
    """
    pivot_element = arr[high]
    i = low - 1  # i 指向小于等于基准值的元素的最后一个位置 (根据排序规则调整)

    for j in range(low, high):
        should_swap = False
        if sort_key == 'visited_time':
            # 只按 visited_time 降序比较
            if arr[j]['visited_time'] >= pivot_element['visited_time']:
                should_swap = True
        else:
            # 默认排序：先 score 降序，再 visited_time 降序
            if arr[j]['score'] > pivot_element['score']:
                should_swap = True
            elif arr[j]['score'] == pivot_element['score']:
                if arr[j]['visited_time'] >= pivot_element['visited_time']:
                    should_swap = True

        if should_swap:
            i = i + 1
            arr[i], arr[j] = arr[j], arr[i]  # 交换元素

    arr[i + 1], arr[high] = arr[high], arr[i + 1]  # 将基准值放到正确的位置
    return i + 1

def quicksort_recursive(arr, low, high, sort_key=None):
    """
    快速排序的递归实现。

    Args:
        arr: 要排序的列表。
        low: 列表的起始索引。
        high: 列表的结束索引。
        sort_key: 排序依据的键。
    """
    if low < high:
        # pi 是分区索引，arr[pi] 现在在正确的位置
        pi = partition(arr, low, high, sort_key)

        # 分别对分区点左右两边的子列表进行排序
        quicksort_recursive(arr, low, pi - 1, sort_key)
        quicksort_recursive(arr, pi + 1, high, sort_key)

def quicksort(data_list, sort_key=None):
    """
    对包含 {"id": ..., "score": ..., "visited_time": ...} 字典的列表进行快速排序。

    Args:
        data_list: 要排序的列表。
        sort_key: 排序依据的键 ('visited_time' 或 None)。
                  None 表示默认排序（score 降序, visited_time 降序）。
                  'visited_time' 表示仅按 visited_time 降序。

    Returns:
        排序后的列表（原地排序，但也返回引用）。
    """
    if not data_list:
        return []
    n = len(data_list)
    quicksort_recursive(data_list, 0, n - 1, sort_key)
    return data_list

# 示例用法
if __name__ == '__main__':
    data = [
        {"id": 1, "score": 85, "visited_time": 367},
        {"id": 2, "score": 90, "visited_time": 645},
        {"id": 3, "score": 85, "visited_time": 517},
        {"id": 4, "score": 90, "visited_time": 703},
        {"id": 5, "score": 70, "visited_time": 421}
    ]
    print("原始数据:", data)

    # 复制一份数据进行默认排序
    data_copy_default = [d.copy() for d in data]
    sorted_data_default = quicksort(data_copy_default)
    print("\n默认排序 (score 降序, visited_time 降序):", sorted_data_default)
    # 预期结果:
    # [
    #     {'id': 4, 'score': 90, 'visited_time': 703},
    #     {'id': 2, 'score': 90, 'visited_time': 645},
    #     {'id': 3, 'score': 85, 'visited_time': 517},
    #     {'id': 1, 'score': 85, 'visited_time': 367},
    #     {'id': 5, 'score': 70, 'visited_time': 421}
    # ]


    # 复制一份数据进行 visited_time 排序
    data_copy_visited = [d.copy() for d in data]
    sorted_data_visited = quicksort(data_copy_visited, sort_key='visited_time')
    print("\n按 visited_time 降序排序:", sorted_data_visited)
    # 预期结果:
    # [
    #     {'id': 4, 'score': 90, 'visited_time': 703},
    #     {'id': 2, 'score': 90, 'visited_time': 645},
    #     {'id': 3, 'score': 85, 'visited_time': 517},
    #     {'id': 5, 'score': 70, 'visited_time': 421},
    #     {'id': 1, 'score': 85, 'visited_time': 367}
    # ]


    data_empty = []
    print("\n空列表排序:", quicksort(data_empty))
    print("空列表按 visited_time 排序:", quicksort(data_empty, sort_key='visited_time'))

    data_single = [{"id": 1, "score": 100, "visited_time": 50}]
    print("\n单元素列表默认排序:", quicksort([d.copy() for d in data_single]))
    print("单元素列表按 visited_time 排序:", quicksort([d.copy() for d in data_single], sort_key='visited_time'))