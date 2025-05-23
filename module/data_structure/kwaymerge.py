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

def k_way_merge_descending(list_of_lists):
    """
    Performs a k-way merge on a list of lists, where each inner list
    contains dictionaries of the format {"id": ..., "value1": ..., "value2": ...}.
    The merge results in a single list sorted by 'value1' (descending),
    then 'value2' (descending).

    Each list in list_of_lists is assumed to be already sorted in
    descending order by 'value1', then 'value2'.

    Args:
        list_of_lists: A list of k sorted lists. Each inner list contains
                       dictionaries.

    Returns:
        A single list containing all dictionaries from list_of_lists,
        sorted in descending order as specified.
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
            min_heap.push(heap_item)

    # Merge process
    while not min_heap.is_empty():
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
    
    merged_list = k_way_merge_descending(all_lists)
    print("Merged and sorted list:")
    for item in merged_list:
        print(item)

    # Expected output order (example):
    # {"id": "D1", "value1": 110, "value2": 1}
    # {"id": "A1", "value1": 100, "value2": 5}
    # {"id": "B1", "value1": 100, "value2": 3}
    # {"id": "C1", "value1": 95, "value2": 8}
    # {"id": "C2", "value1": 90, "value2": 12}
    # {"id": "A2", "value1": 90, "value2": 10}
    # {"id": "B2", "value1": 85, "value2": 20}
    # {"id": "