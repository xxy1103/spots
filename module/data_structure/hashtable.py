class HashTable:
    def __init__(self, size: int = 1000):
        """
        初始化哈希表
        :param size: 哈希表桶的数量，默认为1000
        """
        self.size = size
        # 初始化桶数组，每个桶初始为None
        self.buckets = [None] * size
        # 用于存储所有对象的字典，方便通过id快速查找对象（可选）
        self.objects_by_id = {}

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
        插入对象，将对象添加到对象name中每个汉字对应的桶中
        :param item: 形如 {"id": 1, "name": "故宫博物馆", ...} 的对象
        """
        if "id" not in item or "name" not in item:
            raise ValueError("Item must contain 'id' and 'name' keys")

        obj_id = item["id"]
        name = item["name"]
        
        # 创建只包含 id 和 name 的新字典
        filtered_item = {"id": obj_id, "name": name}

        # 存储过滤后的对象，方便通过id查找
        self.objects_by_id[obj_id] = filtered_item

        for char in name:
            # 计算汉字的哈希值，确定桶索引
            index = self._hash(char)

            # 如果桶为空，初始化为列表
            if self.buckets[index] is None:
                self.buckets[index] = []

            # 查找桶中是否已有该汉字的节点
            node_found = False
            for node in self.buckets[index]:
                if node[0] == char:  # 找到对应汉字的节点
                    # 检查对象是否已存在于列表中（基于id）
                    if not any(existing_item['id'] == obj_id for existing_item in node[1]):
                        # 插入过滤后的对象
                        node[1].append(filtered_item)
                    node_found = True
                    break

            # 如果没有找到该汉字的节点，创建新节点
            if not node_found:
                # 插入过滤后的对象
                self.buckets[index].append((char, [filtered_item]))

    def search(self, key: str) -> list[dict]:
        """
        查找包含指定汉字的对象列表
        :param key: 要查找的汉字
        :return: 包含该汉字的所有对象列表
        """
        index = self._hash(key)

        # 如果桶为空，返回空列表
        if self.buckets[index] is None:
            return []

        # 查找桶中是否有该汉字的节点
        for node in self.buckets[index]:
            if node[0] == key:
                # 返回与该汉字关联的对象列表副本，防止外部修改
                return list(node[1])

        # 如果没有找到，返回空列表
        return []

    def delete(self, obj_id: int):
        """
        根据对象id删除其在哈希表中的所有索引项
        :param obj_id: 要删除的对象id
        """
        # 首先尝试从 objects_by_id 获取对象信息，特别是name
        if obj_id not in self.objects_by_id:
            # 如果对象不存在，则无需删除
            print(f"Warning: Object with id {obj_id} not found for deletion.")
            return

        item_to_delete = self.objects_by_id[obj_id]
        name = item_to_delete["name"]

        # 遍历对象名称中的每个汉字
        for char in name:
            index = self._hash(char)

            # 如果桶为空，继续下一个字符
            if self.buckets[index] is None:
                continue

            # 查找桶中的汉字节点
            node_index_to_remove = -1
            for i, node in enumerate(self.buckets[index]):
                if node[0] == char:
                    # 查找并移除具有指定id的对象
                    item_index_to_remove = -1
                    for j, stored_item in enumerate(node[1]):
                        if stored_item['id'] == obj_id:
                            item_index_to_remove = j
                            break
                    if item_index_to_remove != -1:
                        node[1].pop(item_index_to_remove)

                    # 如果移除对象后，该汉字的列表为空，则标记该节点以便稍后删除
                    if not node[1]:
                        node_index_to_remove = i
                    break # 处理完当前字符对应的节点即可

            # 如果节点需要被删除（因为其对象列表为空）
            if node_index_to_remove != -1:
                self.buckets[index].pop(node_index_to_remove)
                # 如果删除节点后桶变空，可以设置为None（可选）
                # if not self.buckets[index]:
                #     self.buckets[index] = None


        # 从 objects_by_id 中移除对象
        del self.objects_by_id[obj_id]


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

    # 查找包含"故"字的所有对象
    items_with_gu = hash_table.search("故")
    print(f"包含'故'字的对象: {items_with_gu}")
    # 应该输出 [{'id': 1, 'name': '故宫博物馆'}, {'id': 4, 'name': '故事会'}] 或类似顺序

    # 查找包含"门"字的所有对象
    items_with_men = hash_table.search("门")
    print(f"包含'门'字的对象: {items_with_men}")
    # 应该输出 [{'id': 2, 'name': '天安门'}]

    # 删除对象测试 (通过 id 删除)
    hash_table.delete(4)
    items_with_gu_after_delete = hash_table.search("故")
    print(f"删除ID 4后包含'故'字的对象: {items_with_gu_after_delete}")
    # 应该只输出 [{'id': 1, 'name': '故宫博物馆'}]

    items_with_shi_after_delete = hash_table.search("事")
    print(f"删除ID 4后包含'事'字的对象: {items_with_shi_after_delete}") # 应该输出 []

    items_with_hui_after_delete = hash_table.search("会")
    print(f"删除ID 4后包含'会'字的对象: {items_with_hui_after_delete}") # 应该输出 []

    # 测试删除不存在的对象
    hash_table.delete(10) # 应打印警告信息

    # 再次插入和查找
    hash_table.insert({"id": 5, "name": "天坛公园"})
    items_with_tian = hash_table.search("天")
    print(f"再次插入后包含'天'字的对象: {items_with_tian}")
    # 应该输出 [{'id': 2, 'name': '天安门'}, {'id': 5, 'name': '天坛公园'}] 或类似顺序