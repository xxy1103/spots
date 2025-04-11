class HashTable:
    def __init__(self, size: int = 1000):
        """
        初始化哈希表
        :param size: 哈希表桶的数量，默认为1000
        """
        self.size = size
        # 初始化桶数组，每个桶初始为None
        self.buckets = [None] * size
        # 用于存储所有对象的字典，方便后续操作（可选，看需求）
        # self.objects = {}
    
    def _hash(self, key: str) -> int:
        """
        哈希函数，将汉字转换为桶索引
        :param key: 单个汉字
        :return: 桶索引
        """
        # 使用汉字的Unicode值对桶数量取模
        return ord(key) % self.size
    
    def insert(self, item: dict):
        """
        插入对象，将对象id添加到对象name中每个汉字对应的桶中
        :param item: 形如 {"id": 1, "name": "故宫博物馆"} 的对象
        """
        obj_id = item["id"]
        name = item["name"]
        
        # 可选：保存对象以便后续查找完整信息
        # self.objects[obj_id] = item
        
        for char in name:
            # 计算汉字的哈希值，确定桶索引
            index = self._hash(char)
            
            # 如果桶为空，初始化为列表
            if self.buckets[index] is None:
                self.buckets[index] = []
                
            # 查找桶中是否已有该汉字的节点
            found = False
            for node in self.buckets[index]:
                if node[0] == char:  # 找到对应汉字的节点
                    # 如果id不在列表中，添加id
                    if obj_id not in node[1]:
                        node[1].append(obj_id)
                    found = True
                    break
                    
            # 如果没有找到节点，创建新节点
            if not found:
                self.buckets[index].append((char, [obj_id]))
                
    def search(self, key: str) -> list:
        """
        查找包含指定汉字的对象id列表
        :param key: 要查找的汉字
        :return: 包含该汉字的所有对象id列表
        """
        index = self._hash(key)
        
        # 如果桶为空，返回空列表
        if self.buckets[index] is None:
            return []
            
        # 查找桶中是否有该汉字的节点
        for node in self.buckets[index]:
            if node[0] == key:
                return node[1]
                
        # 如果没有找到，返回空列表
        return []
    
    def delete(self, obj_id: int, name: str):
        """
        删除指定id和name的对象索引
        :param obj_id: 要删除的对象id
        :param name: 对象的名称
        """
        # 遍历对象名称中的每个汉字
        for char in name:
            index = self._hash(char)
            
            # 如果桶为空，继续下一个字符
            if self.buckets[index] is None:
                continue
                
            # 查找桶中的汉字节点
            for i, node in enumerate(self.buckets[index]):
                if node[0] == char:
                    if obj_id in node[1]:
                        node[1].remove(obj_id)
                        
                    # 如果节点的id列表为空，删除该节点
                    if not node[1]:
                        self.buckets[index].pop(i)
                        
                    break
        
        # 如果有存储完整对象，也要移除
        if hasattr(self, 'objects') and obj_id in self.objects:
            del self.objects[obj_id]
    
    


if __name__ == "__main__":
    # 创建哈希表实例
    hash_table = HashTable()

    # 插入示例数据
    objects = [
        {"id": 1, "name": "故宫博物馆"},
        {"id": 2, "name": "天安门"},
        {"id": 3, "name": "颐和园"},
        {"id": 4, "name": "故事会"}
    ]

    for obj in objects:
        hash_table.insert(obj)

    # 查找包含"故"字的所有对象id
    ids = hash_table.search("故")
    print(f"包含'故'字的对象ID: {ids}")  # 应该输出 [1, 4]

    # 删除对象测试
    hash_table.delete(4, "故事会")
    ids_after_delete = hash_table.search("故")
    print(f"删除后包含'故'字的对象ID: {ids_after_delete}")  # 应该只有 [1]