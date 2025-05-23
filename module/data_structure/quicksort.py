def partition(arr, low, high, sort_key=None):
    """
    分区函数，用于快速排序。

    Args:
        arr: 要排序的列表，元素为 {"id": ..., "value1": ..., "value2": ...} 格式的字典。
        low: 列表的起始索引。
        high: 列表的结束索引。
        sort_key: 主排序键 ('value1' 或 'value2' 或 None)。
                  None 或 'value1': 主排序键为 'value1' (降序), 次排序键为 'value2' (降序)。
                  'value2': 主排序键为 'value2' (降序), 次排序键为 'value1' (降序)。

    Returns:
        分区点的索引。
    """
    pivot_element = arr[high]
    i = low - 1  # i 指向小于等于基准值的元素的最后一个位置 (根据排序规则调整)

    primary_key_name = 'value1'
    secondary_key_name = 'value2'

    if sort_key == 'value2':
        primary_key_name = 'value2'
        secondary_key_name = 'value1'
    # Default (sort_key is None or 'value1') uses 'value1' as primary, 'value2' as secondary.

    for j in range(low, high):
        should_swap = False
        # 比较主排序键 (降序)
        if arr[j][primary_key_name] > pivot_element[primary_key_name]:
            should_swap = True
        elif arr[j][primary_key_name] == pivot_element[primary_key_name]:
            # 如果主排序键相同，比较次排序键 (降序)
            if arr[j][secondary_key_name] >= pivot_element[secondary_key_name]:
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
        sort_key: 主排序键。
    """
    if low < high:
        # pi 是分区索引，arr[pi] 现在在正确的位置
        pi = partition(arr, low, high, sort_key)

        # 分别对分区点左右两边的子列表进行排序
        quicksort_recursive(arr, low, pi - 1, sort_key)
        quicksort_recursive(arr, pi + 1, high, sort_key)

def quicksort(data_list, sort_key=None):
    """
    对包含 {"id": ..., "value1": ..., "value2": ...} 字典的列表进行快速排序。

    Args:
        data_list: 要排序的列表。
        sort_key: 主排序键 ('value1' 或 'value2' 或 None)。
                  None 或 'value1': 主排序键为 'value1' (降序), 次排序键为 'value2' (降序)。
                  'value2': 主排序键为 'value2' (降序), 次排序键为 'value1' (降序)。

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
        {"id": 1, "value1": 85, "value2": 367},
        {"id": 2, "value1": 90, "value2": 645},
        {"id": 3, "value1": 85, "value2": 517},
        {"id": 4, "value1": 90, "value2": 703},
        {"id": 5, "value1": 70, "value2": 421}
    ]
    print("原始数据:", data)

    # 复制一份数据进行默认排序 (value1 主, value2 次)
    data_copy_default = [d.copy() for d in data]
    sorted_data_default = quicksort(data_copy_default) # sort_key=None or 'value1'
    print("\n默认排序 (value1 降序, value2 降序):", sorted_data_default)
    # 预期结果:
    # [
    #     {'id': 4, 'value1': 90, 'value2': 703},
    #     {'id': 2, 'value1': 90, 'value2': 645},
    #     {'id': 3, 'value1': 85, 'value2': 517},
    #     {'id': 1, 'value1': 85, 'value2': 367},
    #     {'id': 5, 'value1': 70, 'value2': 421}
    # ]

    # 复制一份数据进行 value2 主排序, value1 次排序
    data_copy_value2_primary = [d.copy() for d in data]
    sorted_data_value2_primary = quicksort(data_copy_value2_primary, sort_key='value2')
    print("\n按 value2 降序 (主), value1 降序 (次) 排序:", sorted_data_value2_primary)
    # 预期结果:
    # [
    #     {'id': 4, 'value1': 90, 'value2': 703},
    #     {'id': 2, 'value1': 90, 'value2': 645},
    #     {'id': 3, 'value1': 85, 'value2': 517},
    #     {'id': 1, 'value1': 85, 'value2': 367}, # value1 85 > 70 for same value2 if that was the case
    #     {'id': 5, 'value1': 70, 'value2': 421}
    # ]
    # Corrected expectation for value2 primary:
    # [
    #     {'id': 4, 'value1': 90, 'value2': 703},
    #     {'id': 2, 'value1': 90, 'value2': 645},
    #     {'id': 3, 'value1': 85, 'value2': 517},
    #     {'id': 5, 'value1': 70, 'value2': 421},
    #     {'id': 1, 'value1': 85, 'value2': 367}
    # ]


    data_empty = []
    print("\n空列表排序:", quicksort(data_empty))
    print("空列表按 value2 主键排序:", quicksort(data_empty, sort_key='value2'))

    data_single = [{"id": 1, "value1": 100, "value2": 50}]
    print("\n单元素列表默认排序:", quicksort([d.copy() for d in data_single]))
    print("单元素列表按 value2 主键排序:", quicksort([d.copy() for d in data_single], sort_key='value2'))