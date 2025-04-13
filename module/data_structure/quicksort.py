def partition(arr, low, high):
    """
    分区函数，用于快速排序。

    Args:
        arr: 要排序的列表，元素为 {"id": ..., "visited_time": ...} 格式的字典。
        low: 列表的起始索引。
        high: 列表的结束索引。

    Returns:
        分区点的索引。
    """
    pivot = arr[high]['visited_time']  # 选择最后一个元素作为基准值
    i = low - 1  # i 指向小于等于基准值的元素的最后一个位置

    for j in range(low, high):
        # 如果当前元素的 visited_time 大于等于基准值（降序排列）
        if arr[j]['visited_time'] >= pivot:
            i = i + 1
            arr[i], arr[j] = arr[j], arr[i]  # 交换元素

    arr[i + 1], arr[high] = arr[high], arr[i + 1]  # 将基准值放到正确的位置
    return i + 1

def quicksort_recursive(arr, low, high):
    """
    快速排序的递归实现。

    Args:
        arr: 要排序的列表。
        low: 列表的起始索引。
        high: 列表的结束索引。
    """
    if low < high:
        # pi 是分区索引，arr[pi] 现在在正确的位置
        pi = partition(arr, low, high)

        # 分别对分区点左右两边的子列表进行排序
        quicksort_recursive(arr, low, pi - 1)
        quicksort_recursive(arr, pi + 1, high)

def quicksort(data_list):
    """
    对包含 {"id": ..., "visited_time": ...} 字典的列表进行快速排序（按 visited_time 降序）。

    Args:
        data_list: 要排序的列表。

    Returns:
        排序后的列表（原地排序，但也返回引用）。
    """
    if not data_list:
        return []
    n = len(data_list)
    quicksort_recursive(data_list, 0, n - 1)
    return data_list

# 示例用法
if __name__ == '__main__':
    data = [
        {"id": 1, "visited_time": 367},
        {"id": 2, "visited_time": 645},
        {"id": 3, "visited_time": 517},
        {"id": 4, "visited_time": 703},
        {"id": 5, "visited_time": 421}
    ]
    print("原始数据:", data)
    sorted_data = quicksort(data)
    print("按 visited_time 降序排序后:", sorted_data)

    data_empty = []
    print("空列表排序:", quicksort(data_empty))

    data_single = [{"id": 1, "visited_time": 100}]
    print("单元素列表排序:", quicksort(data_single))
