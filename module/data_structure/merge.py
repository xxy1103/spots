# --- 归并排序辅助函数 ---
def merge(left, right):
    """
    合并两个已排序列表的辅助函数
    按评分（降序）和访问次数（降序）排序
    """
    merged = []
    left_index, right_index = 0, 0

    while left_index < len(left) and right_index < len(right):
        # 比较评分，评分高的在前
        left_score = float(left[left_index].get('score', 0.0))
        right_score = float(right[right_index].get('score', 0.0))
        
        if left_score > right_score:
            merged.append(left[left_index])
            left_index += 1
        elif left_score < right_score:
            merged.append(right[right_index])
            right_index += 1
        else:
            # 评分相同，比较访问次数，访问次数多的在前
            left_visited = int(left[left_index].get('visited_time', 0))
            right_visited = int(right[right_index].get('visited_time', 0))
            if left_visited >= right_visited:
                merged.append(left[left_index])
                left_index += 1
            else:
                merged.append(right[right_index])
                right_index += 1
    
    # 添加剩余元素
    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return merged

def merge_sort(spots_list):
    """
    归并排序主函数
    按评分（降序）和访问次数（降序）排序
    """
    if len(spots_list) <= 1:
        return spots_list

    mid = len(spots_list) // 2
    left_half = merge_sort(spots_list[:mid])
    right_half = merge_sort(spots_list[mid:])

    return merge(left_half, right_half)