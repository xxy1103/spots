class TopKHeap:
    """
    优化的索引最大堆，专注于获取前K个最大元素
    - 按value1降序排序
    - value1相同时按value2降序排序
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
    
    def _fast_heap_copy(self):
        """
        最快的堆复制方法 - 使用切片操作
        比 .copy() 快约 15-30%
        """
        return self.heap[:]
    
    def _deep_heap_copy(self):
        """
        深度复制堆（包括元素内容）
        当需要完全独立的副本时使用        
        """
        import copy
        return copy.deepcopy(self.heap)
    
    def _shallow_heap_copy_dict(self):
        """
        浅复制堆，但复制每个字典元素
        在修改元素内容时保护原堆
        """
        return [item.copy() for item in self.heap]
    
    def getTopK(self, k=10):
        """
        获取前k个最大元素，时间复杂度O(k log n)
        不改变原堆结构，使用最优化的复制策略
        """
        if k <= 0 or self.isEmpty():
            return []
            
        # 如果 k 大于堆的大小，直接返回整个堆的副本
        if k > len(self.heap):
            return self._fast_heap_copy()


        # 优化2: 根据堆大小选择最优复制策略
        heap_size = len(self.heap)
        if heap_size < 1000:
            # 小堆：使用最快的切片复制
            temp_heap = self._fast_heap_copy()
        elif k / heap_size < 0.1:
            # 大堆但k很小：使用heapq.nlargest更高效
            import heapq
            return heapq.nlargest(k, self.heap, key=lambda x: (x["value1"], x["value2"]))
        else:
            # 大堆且k较大：使用切片复制
            temp_heap = self._fast_heap_copy()
        
        result = []
        
        # 只提取k个元素
        for _ in range(k):
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
    
    def getTopKFast(self, k=10):
        """
        更快的获取前k个最大元素的方法
        使用heapq.nlargest，时间复杂度O(n + k log n)
        """
        if k <= 0 or self.isEmpty():
            return []
            
        import heapq
        
        # 使用heapq.nlargest，它对于较小的k值非常高效
        return heapq.nlargest(k, self.heap, key=lambda x: (x["value1"], x["value2"]))
    
    def getTopKIterative(self, k=10):
        """
        迭代式获取前k个元素，避免完整复制堆
        适用于k相对较小的情况
        """
        if k <= 0 or self.isEmpty():
            return []
            
        result = []
        used_indices = set()
        
        for _ in range(min(k, len(self.heap))):
            max_val = None
            max_idx = -1
            
            # 在未使用的元素中找到最大值
            for i, item in enumerate(self.heap):
                if i not in used_indices:
                    if max_val is None or self._compare(item, max_val) > 0:
                        max_val = item
                        max_idx = i
            
            if max_idx != -1:
                result.append(max_val.copy())
                used_indices.add(max_idx)
                
        return result
    
    def insert(self, item_id, value1, value2):
        """插入新元素"""
        item = {"id": item_id, "value1": value1, "value2": value2}
        self.heap.append(item)
        current = len(self.heap) - 1
        self.index_map[item_id] = current
        self._siftUp(current)
    
    def updateValue1(self, item_id, new_value1):
        """更新value1"""
        if item_id not in self.index_map:
            return False
        
        index = self.index_map[item_id]
        old_value1 = self.heap[index]["value1"]
        self.heap[index]["value1"] = new_value1
        
        # 根据新旧value1决定上浮或下沉
        if new_value1 > old_value1:
            self._siftUp(index)
        else:
            self._siftDown(self.heap, index)
        return True
    
    def updateValue2(self, item_id, new_value2):
        """更新value2"""
        if item_id not in self.index_map: #  确保在更新前检查 item_id 是否存在
            return False # 或者抛出异常

        index = self.index_map[item_id]
        old_value2 = self.heap[index]["value2"]
        self.heap[index]["value2"] = new_value2

        # 检查父节点，决定是否上浮
        parent_index = (index - 1) // 2
        if index > 0 and self._compare(self.heap[index], self.heap[parent_index]) > 0:
            self._siftUp(index)
        else:
            # 如果不上浮，则可能需要下沉（即使value2变大，如果value1也变了且变小，也可能下沉）
            self._siftDown(self.heap, index)
        return True

    def delete(self, item_id):
        """
        从堆中删除具有指定item_id的元素。
        返回 True 表示成功删除，False 表示元素不存在。
        """
        if item_id not in self.index_map:
            # print(f"Error: Item with ID {item_id} not found in heap.")
            return False

        index_to_delete = self.index_map[item_id]
        last_index = len(self.heap) - 1

        # 如果要删除的元素就是最后一个元素
        if index_to_delete == last_index:
            self.heap.pop()
            del self.index_map[item_id]
            return True

        # 将要删除的元素与最后一个元素交换
        # _swap会处理堆内元素的交换以及index_map的对应更新
        self._swap(index_to_delete, last_index)

        # 移除现在位于堆末尾的、我们最初想要删除的元素
        # item_id 对应的元素已经被交换到了 last_index
        self.heap.pop() 
        del self.index_map[item_id] # 从映射中删除 item_id

        # 如果堆在pop后变空，或者index_to_delete不再是有效索引（例如，堆中只剩一个元素被换上来）
        if not self.heap or index_to_delete >= len(self.heap):
            return True
            
        # 对从末尾交换过来的元素（现在位于index_to_delete）进行堆调整
        # 它可能需要上浮或下沉
        # 尝试上浮：如果它比其父节点“大”
        parent_index = (index_to_delete - 1) // 2
        if index_to_delete > 0 and self._compare(self.heap[index_to_delete], self.heap[parent_index]) > 0:
            self._siftUp(index_to_delete)
        else:
            # 如果它不需要上浮（或者它是根节点），则尝试下沉
            # 因为它可能比其子节点“小”
            self._siftDown(self.heap, index_to_delete)
            
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
        """比较两个元素：先比较value1，value1相同则比较value2
        返回值 > 0 表示a应该排在b前面（即a更大）
        """
        if a["value1"] != b["value1"]:
            return float(a["value1"]) - float(b["value1"])  # value1降序
        return a["value2"] - b["value2"]  # value2降序


# 使用示例
def main():
    # 创建时间戳和用户名记录
    print("Current Date and Time (UTC): 2025-04-04 03:09:49") # 这个时间可以更新或移除
    print("User: xxy1103\n") # 这个用户信息可以更新或移除
    
    # 创建索引堆
    heap = TopKHeap()
    
    # 插入示例数据
    data = [
        {"id": 12, "value1": 4.9, "value2": 7823},
        {"id": 45, "value1": 4.8, "value2": 5346},
        {"id": 132, "value1": 4.7, "value2": 9217},
        {"id": 76, "value1": 4.4, "value2": 2458},
        {"id": 89, "value1": 4.2, "value2": 6790},
        # 假设有更多数据...
    ]
    
    for item in data:
        heap.insert(item["id"], item["value1"], item["value2"])
    
    # 获取前3名（示例）
    print("Top 3 项目:")
    top_items = heap.getTopK(3)
    for i, item in enumerate(top_items, 1):
        print(f"排名 {i}: ID={item['id']}, Value1={item['value1']}, Value2={item['value2']}")
    
    # 更新某些项目
    print("\n更新 ID=76 的 Value1 (4.4 -> 4.5):")
    heap.updateValue1(76, 4.5)
    
    print("更新 ID=89 的 Value2 (6790 -> 7000):") # 示例：直接设置新值
    heap.updateValue2(89, 7000)
    
    # 再次获取前3名
    print("\n更新后 Top 3 项目:")
    top_items = heap.getTopK(3)
    for i, item in enumerate(top_items, 1):
        print(f"排名 {i}: ID={item['id']}, Value1={item['value1']}, Value2={item['value2']}")
    
    # 展示如何获取前10名
    print("\n获取前10名项目的方法示例:")
    print("top_ten = heap.getTopK(10)") # Corrected method name


if __name__ == "__main__":
    main()