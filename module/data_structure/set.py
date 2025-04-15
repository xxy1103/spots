class ItemSet:
    """
    一个简单的对象集合类，基于对象的 'id' 存储和操作，实现基本的集合操作。
    对象格式为: {"id": ..., "name": ...}
    """
    def __init__(self, items=None):
        """
        初始化集合
        :param items: 可选的初始对象列表，每个对象应为 {"id": ..., "name": ...} 格式
        """
        # 使用字典以id为键存储对象，提高查找效率
        self._items_by_id = {}
        if items:
            for item in items:
                self.add(item)

    def add(self, item: dict):
        """
        添加对象到集合
        :param item: 要添加的对象，格式为 {"id": ..., "name": ...}
        :return: None
        :raises TypeError: 如果对象格式不正确
        :raises ValueError: 如果对象缺少 'id' 或 'name' 键
        """
        if not isinstance(item, dict):
            raise TypeError("集合只能包含字典格式的对象")
        if "id" not in item or "name" not in item:
            raise ValueError("对象必须包含 'id' 和 'name' 键")

        item_id = item["id"]
        if item_id not in self._items_by_id:
            self._items_by_id[item_id] = item

    def remove(self, item_id):
        """
        根据对象id从集合中删除对象
        :param item_id: 要删除的对象的id
        :return: None
        :raises KeyError: 如果具有该id的对象不在集合中
        """
        if item_id in self._items_by_id:
            del self._items_by_id[item_id]
        else:
            raise KeyError(f"ID为 {item_id} 的对象不在集合中")

    def discard(self, item_id):
        """
        根据对象id从集合中删除对象，如果对象不存在则不进行操作
        :param item_id: 要删除的对象的id
        :return: None
        """
        if item_id in self._items_by_id:
            del self._items_by_id[item_id]

    def contains(self, item_id):
        """
        检查具有指定id的对象是否在集合中
        :param item_id: 要检查的对象的id
        :return: 布尔值
        """
        return item_id in self._items_by_id

    def union(self, other_set):
        """
        返回两个集合的并集
        :param other_set: 另一个 ItemSet 实例
        :return: 新的 ItemSet 集合
        :raises TypeError: 如果 other_set 不是 ItemSet 类型
        """
        if not isinstance(other_set, ItemSet):
            raise TypeError("操作对象必须是 ItemSet 类型")
        
        result = ItemSet(self.get_all_elements()) # 从当前集合开始
        for item_id, item in other_set._items_by_id.items():
            result.add(item) # add 方法会自动处理重复（基于id）
        return result

    def intersection(self, other_set):
        """
        返回两个集合的交集
        :param other_set: 另一个 ItemSet 实例
        :return: 新的 ItemSet 集合
        :raises TypeError: 如果 other_set 不是 ItemSet 类型
        """
        if not isinstance(other_set, ItemSet):
            raise TypeError("操作对象必须是 ItemSet 类型")

        result = ItemSet()
        # 遍历较小的集合以提高效率
        if self.size() < other_set.size():
            smaller_set = self
            larger_set = other_set
        else:
            smaller_set = other_set
            larger_set = self

        for item_id, item in smaller_set._items_by_id.items():
            if larger_set.contains(item_id):
                result.add(item)
        return result

    def difference(self, other_set):
        """
        返回两个集合的差集（self - other_set）
        :param other_set: 另一个 ItemSet 实例
        :return: 新的 ItemSet 集合
        :raises TypeError: 如果 other_set 不是 ItemSet 类型
        """
        if not isinstance(other_set, ItemSet):
            raise TypeError("操作对象必须是 ItemSet 类型")

        result = ItemSet()
        for item_id, item in self._items_by_id.items():
            if not other_set.contains(item_id):
                result.add(item)
        return result

    def clear(self):
        """
        清空集合
        :return: None
        """
        self._items_by_id = {}

    def size(self):
        """
        返回集合中对象的数量
        :return: 整数
        """
        return len(self._items_by_id)

    def is_empty(self):
        """
        检查集合是否为空
        :return: 布尔值
        """
        return len(self._items_by_id) == 0

    def get_all_elements(self) -> list[dict]:
        """
        返回集合中所有对象的列表副本
        :return: 对象列表
        """
        return list(self._items_by_id.values())

    def get_all_ids(self) -> list:
        """
        返回集合中所有对象 ID 的列表副本
        :return: ID 列表
        """
        return list(self._items_by_id.keys())

    def __str__(self):
        """
        返回集合的字符串表示
        :return: 字符串
        """
        # 为了简洁，可以只显示id，或者显示完整的对象字符串
        # return "{" + ", ".join(str(id) for id in self._items_by_id.keys()) + "}"
        return "{" + ", ".join(str(item) for item in self._items_by_id.values()) + "}"

    def __repr__(self):
        """
        返回集合的字符串表示
        :return: 字符串
        """
        # 使用更明确的表示法
        items_repr = ", ".join(repr(item) for item in self._items_by_id.values())
        return f"ItemSet([{items_repr}])"

# --- 示例用法 ---
if __name__ == "__main__":
    set1 = ItemSet([
        {"id": 1, "name": "故宫"},
        {"id": 2, "name": "天安门"}
    ])
    set2 = ItemSet([
        {"id": 2, "name": "天安门广场"}, # ID 相同，name 不同，会被视为同一个元素
        {"id": 3, "name": "颐和园"}
    ])

    print(f"Set 1: {set1}")
    print(f"Set 2: {set2}")

    # 添加
    set1.add({"id": 4, "name": "长城"})
    print(f"Set 1 after add: {set1}")
    try:
        set1.add({"id": 1, "name": "紫禁城"}) # 添加已存在的 ID，不会改变集合
    except ValueError as e:
        print(e)
    print(f"Set 1 after adding existing ID: {set1}")

    # 包含
    print(f"Set 1 contains ID 2: {set1.contains(2)}")
    print(f"Set 1 contains ID 5: {set1.contains(5)}")

    # 删除
    set1.remove(4)
    print(f"Set 1 after remove ID 4: {set1}")
    set1.discard(5) # 删除不存在的 ID，无事发生
    print(f"Set 1 after discard ID 5: {set1}")
    try:
        set1.remove(10) # 删除不存在的 ID，会报错
    except KeyError as e:
        print(e)

    # 集合操作
    union_set = set1.union(set2)
    print(f"Union: {union_set}")
    print(f"Union size: {union_set.size()}")

    intersection_set = set1.intersection(set2)
    print(f"Intersection: {intersection_set}")

    difference_set = set1.difference(set2)
    print(f"Difference (Set1 - Set2): {difference_set}")

    difference_set2 = set2.difference(set1)
    print(f"Difference (Set2 - Set1): {difference_set2}")

    # 获取元素
    print(f"All elements in Set 1: {set1.get_all_elements()}")
    print(f"All IDs in Set 1: {set1.get_all_ids()}")

    # 清空
    set1.clear()
    print(f"Set 1 after clear: {set1}")
    print(f"Set 1 is empty: {set1.is_empty()}")