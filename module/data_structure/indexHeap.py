

class TopKHeap:
    """
    优化的索引最大堆，专注于获取前K个最大元素
    - 按score降序排序
    - score相同时按visited_time降序排序
    - 支持通过ID高效更新数据
    - 提供O(k log n)复杂度获取前k个元素的方法
    """
    def __init__(self):
        self.heap = []  # 堆数组
        self.index_map = {}  # ID到堆位置的映射
        
    def size(self):
        return len(self.heap)
        
    def isEmpty(self):
        return len(self.heap) == 0
    
    def getTopK(self, k=10):
        """
        获取前k个最大元素，时间复杂度O(k log n)
        不改变原堆结构
        """
        if k <= 0 or self.isEmpty():
            return []
            
        # 创建堆的副本
        temp_heap = self.heap.copy()
        result = []
        
        # 只提取k个元素或堆的大小，取较小值
        extract_count = min(k, len(temp_heap))
        
        for _ in range(extract_count):
            # 提取当前最大元素
            max_item = temp_heap[0]
            result.append(max_item.copy())  # 复制一份添加到结果
            
            # 替换堆顶元素并下沉
            if len(temp_heap) > 1:
                temp_heap[0] = temp_heap.pop()
                self._siftDown(temp_heap, 0)
            else:
                temp_heap.pop()
                
        return result
    
    def insert(self, item_id, score, visited_time):
        """插入新元素"""
        item = {"id": item_id, "score": score, "visited_time": visited_time}
        self.heap.append(item)
        current = len(self.heap) - 1
        self.index_map[item_id] = current
        self._siftUp(current)
    
    def updateScore(self, item_id, new_score):
        """更新分数 (+0.1)"""
        if item_id not in self.index_map:
            return False
        
        index = self.index_map[item_id]
        old_score = self.heap[index]["score"]
        self.heap[index]["score"] = new_score
        
        # 根据新旧分数决定上浮或下沉
        if new_score > old_score:
            self._siftUp(index)
        else:
            self._siftDown(self.heap, index)
        return True
    
    def updateVisitedTime(self, item_id, increment=1):
        """更新访问次数 (+1)"""
        if item_id not in self.index_map:
            return False
            
        index = self.index_map[item_id]
        self.heap[index]["visited_time"] = increment
        
        # 访问次数增加，可能需要上浮
        self._siftUp(index)
        return True
    
    def _siftUp(self, index):
        """上浮操作"""
        parent = (index - 1) // 2
        
        while index > 0 and self._compare(self.heap[index], self.heap[parent]) > 0:
            # 交换元素
            self._swap(index, parent)
            # 更新索引
            index = parent
            parent = (index - 1) // 2
    
    def _siftDown(self, heap, index):
        """下沉操作"""
        size = len(heap)
        largest = index
        left = 2 * index + 1
        right = 2 * index + 2
        
        # 比较左子节点
        if left < size and self._compare(heap[left], heap[largest]) > 0:
            largest = left
            
        # 比较右子节点
        if right < size and self._compare(heap[right], heap[largest]) > 0:
            largest = right
            
        # 如果最大值不是当前节点，则交换并继续下沉
        if largest != index:
            heap[index], heap[largest] = heap[largest], heap[index]
            
            # 如果这是实际堆而非临时堆，更新索引映射
            if heap is self.heap:
                self.index_map[heap[index]["id"]] = index
                self.index_map[heap[largest]["id"]] = largest
                
            self._siftDown(heap, largest)
    
    def _swap(self, i, j):
        """交换堆中的两个元素并更新索引映射"""
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.index_map[self.heap[i]["id"]] = i
        self.index_map[self.heap[j]["id"]] = j
    
    def _compare(self, a, b):
        """比较两个元素：先比较score，score相同则比较visited_time
        返回值 > 0 表示a应该排在b前面（即a更大）
        """
        if a["score"] != b["score"]:
            return float(a["score"]) - float(b["score"])  # score降序
        return a["visited_time"] - b["visited_time"]  # visited_time降序


# 使用示例
def main():
    # 创建时间戳和用户名记录
    print("Current Date and Time (UTC): 2025-04-04 03:09:49")
    print("User: xxy1103\n")
    
    # 创建索引堆
    heap = TopKHeap()
    
    # 插入示例数据
    data = [
        {"id": 12, "score": 4.9, "visited_time": 7823},
        {"id": 45, "score": 4.8, "visited_time": 5346},
        {"id": 132, "score": 4.7, "visited_time": 9217},
        {"id": 76, "score": 4.4, "visited_time": 2458},
        {"id": 89, "score": 4.2, "visited_time": 6790},
        # 假设有更多数据...
    ]
    
    for item in data:
        heap.insert(item["id"], item["score"], item["visited_time"])
    
    # 获取前3名（示例）
    print("Top 3 项目:")
    top_items = heap.getTopK(3)
    for i, item in enumerate(top_items, 1):
        print(f"排名 {i}: ID={item['id']}, Score={item['score']}, Visited={item['visited_time']}")
    
    # 更新某些项目
    print("\n更新 ID=76 的分数 (4.4 -> 4.5):")
    heap.updateScore(76, 4.5)
    
    print("增加 ID=89 的访问次数 (+1):")
    heap.updateVisitedTime(89)
    
    # 再次获取前3名
    print("\n更新后 Top 3 项目:")
    top_items = heap.getTopK(3)
    for i, item in enumerate(top_items, 1):
        print(f"排名 {i}: ID={item['id']}, Score={item['score']}, Visited={item['visited_time']}")
    
    # 展示如何获取前10名
    print("\n获取前10名项目的方法示例:")
    print("top_ten = heap.getTop_k(10)")


if __name__ == "__main__":
    main()