class MinHeap:
    """
    一个简单的最小堆实现，不依赖 heapq 库。
    """
    def __init__(self):
        self._heap = []

    def _parent(self, i):
        return (i - 1) // 2

    def _left_child(self, i):
        return 2 * i + 1

    def _right_child(self, i):
        return 2 * i + 2

    def _swap(self, i, j):
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]

    def _sift_up(self, i):
        """将索引 i 处的元素向上调整以维护堆属性"""
        parent_index = self._parent(i)
        while i > 0 and self._heap[i] < self._heap[parent_index]:
            self._swap(i, parent_index)
            i = parent_index
            parent_index = self._parent(i)

    def _sift_down(self, i):
        """将索引 i 处的元素向下调整以维护堆属性"""
        max_index = i
        left = self._left_child(i)
        if left < len(self._heap) and self._heap[left] < self._heap[max_index]:
            max_index = left

        right = self._right_child(i)
        if right < len(self._heap) and self._heap[right] < self._heap[max_index]:
            max_index = right

        if i != max_index:
            self._swap(i, max_index)
            self._sift_down(max_index) # 递归调整

    def push(self, item):
        """向堆中添加一个元素"""
        self._heap.append(item)
        self._sift_up(len(self._heap) - 1)

    def pop(self):
        """移除并返回堆中的最小元素"""
        if not self._heap:
            raise IndexError("pop from an empty heap")
        if len(self._heap) == 1:
            return self._heap.pop()

        min_item = self._heap[0]
        # 将最后一个元素移到根部
        self._heap[0] = self._heap.pop()
        # 向下调整以恢复堆属性
        self._sift_down(0)
        return min_item

    def peek(self):
        """查看堆顶元素（最小元素），不移除"""
        if not self._heap:
            raise IndexError("peek from an empty heap")
        return self._heap[0]

    def heapify(self, iterable):
        """将一个可迭代对象转换为堆"""
        self._heap = list(iterable)
        # 从最后一个非叶子节点开始向上调整
        start_index = self._parent(len(self._heap) - 1)
        for i in range(start_index, -1, -1):
            self._sift_down(i)

    def __len__(self):
        return len(self._heap)

    def is_empty(self):
        return len(self._heap) == 0

    def __str__(self):
        return str(self._heap)

    def __repr__(self):
        return f"MinHeap({self._heap})"

# 简单测试
if __name__ == '__main__':
    # 测试 push 和 pop
    h = MinHeap()
    h.push(5)
    h.push(3)
    h.push(8)
    h.push(1)
    print("Heap after pushes:", h) # Expected: MinHeap([1, 3, 8, 5]) or similar structure

    print("Popped:", h.pop()) # Expected: 1
    print("Heap after pop:", h)
    print("Popped:", h.pop()) # Expected: 3
    print("Heap after pop:", h)
    print("Peek:", h.peek()) # Expected: 5
    print("Heap size:", len(h)) # Expected: 2

    # 测试 heapify
    data = [9, 2, 7, 4, 5, 6, 8, 1, 3]
    h2 = MinHeap()
    h2.heapify(data)
    print("Heapified from list:", h2)
    sorted_data = []
    while not h2.is_empty():
            sorted_data.append(h2.pop())
    print("Sorted data using heap:", sorted_data) # Expected: [1, 2, 3, 4, 5, 6, 7, 8, 9]



class SpotIterator:
    """
    景点迭代器，用于按分数降序迭代特定类型的景点
    """
    def __init__(self, spot_type, spot_manager):
        self.spot_type = spot_type
        self.spot_manager = spot_manager
        self.current_index = 0
        self.spots_data = None
        self._initialize()
    
    def _initialize(self):
        """初始化迭代器，获取该类型的所有景点数据"""
        if self.spot_type not in self.spot_manager.spotTypeDict:
            self.spots_data = []
            return
        
        # 获取该类型所有景点的排序数据
        heap_instance = self.spot_manager.spotTypeDict[self.spot_type].get("heap")
        if heap_instance and heap_instance.size() > 0:
            # 获取所有景点数据（已按分数排序）
            self.spots_data = heap_instance.getTopK(heap_instance.size())
        else:
            self.spots_data = []
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current_index >= len(self.spots_data):
            raise StopIteration
        
        spot_data = self.spots_data[self.current_index]
        self.current_index += 1
        
        # 返回景点数据，包含id和score等信息
        return {
            'id': spot_data['id'],
            'score': spot_data['value1'],
            'visited_time': spot_data['value2']
        }


def create_spot_iterator(spot_type, spot_manager):
    """
    创建景点迭代器的工厂函数
    """
    return SpotIterator(spot_type, spot_manager)


class DiaryIterator:
    """
    日记迭代器 - 为特定景点类型的所有景点的日记提供按评分排序的迭代器
    """
    def __init__(self, spot_type, spot_manager):
        self.spot_type = spot_type
        self.spot_manager = spot_manager
        self.spots_of_type = spot_manager.getTopKByType(spot_type, k=-1)  # 获取该类型的所有景点
        self.current_spot_index = 0
        self.current_diary_list = []
        self.current_diary_index = 0
        self._advance_to_next_valid_spot()
    
    def _advance_to_next_valid_spot(self):
        """推进到下一个有日记的景点"""
        while self.current_spot_index < len(self.spots_of_type):
            spot = self.spots_of_type[self.current_spot_index]
            spot_id = spot["id"]
            
            # 获取该景点的日记堆
            diary_heap = self.spot_manager.spotDiaryHeapArray[spot_id - 1]
            
            # 获取该景点的所有日记 - 使用一个足够大的数字而不是-1
            if diary_heap.size() > 0:
                self.current_diary_list = diary_heap.getTopK(diary_heap.size())  # 获取所有日记
            else:
                self.current_diary_list = []
            
            self.current_diary_index = 0
            
            # 检查这个景点是否有日记
            if self.current_diary_list and len(self.current_diary_list) > 0:
                return  # 找到有效的景点和日记
            else:
                # 这个景点没有日记，继续下一个
                self.current_spot_index += 1
                continue
        
        # 如果到达这里，说明没有更多景点或日记了
        self.current_diary_list = []
        self.current_diary_index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        # 检查当前景点是否还有日记
        if (self.current_diary_index >= len(self.current_diary_list) or 
            not self.current_diary_list):
            
            # 当前景点的日记已耗尽，移动到下一个景点
            self.current_spot_index += 1
            self._advance_to_next_valid_spot()
            
            # 如果没有更多日记，抛出 StopIteration
            if (self.current_diary_index >= len(self.current_diary_list) or 
                not self.current_diary_list):
                raise StopIteration
        
        # 返回当前日记
        current_diary = self.current_diary_list[self.current_diary_index]
        self.current_diary_index += 1
        
        # 转换为标准格式
        return {
            'id': current_diary['id'],
            'score': current_diary['value1'],  # 评分存储在 value1 中
            'visited_time': current_diary['value2'],  # 访问次数存储在 value2 中
            'type': self.spot_type
        }


def create_diary_iterator(spot_type, spot_manager):
    """
    创建日记迭代器的工厂函数
    """
    return DiaryIterator(spot_type, spot_manager)
