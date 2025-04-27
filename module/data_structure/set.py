class MySet:
    """
    一个简单的自定义集合类，使用字典实现。
    """
    def __init__(self, iterable=None):
        """
        初始化集合。可以从一个可迭代对象初始化。
        :param iterable: 可选的可迭代对象，用于初始化集合元素。
        """
        self._elements = {}  # 使用字典存储元素，键是元素，值可以是任意非None值（例如True）
        if iterable:
            for item in iterable:
                self.add(item)

    def add(self, item):
        """
        向集合中添加一个元素。
        :param item: 要添加的元素。
        """
        self._elements[item] = True

    def contains(self, item):
        """
        检查元素是否存在于集合中。
        :param item: 要检查的元素。
        :return: 如果元素存在则返回 True，否则返回 False。
        """
        return item in self._elements

    def remove(self, item):
        """
        从集合中移除一个元素。如果元素不存在，则引发 KeyError。
        :param item: 要移除的元素。
        """
        if item in self._elements:
            del self._elements[item]
        else:
            raise KeyError(f"Element {item} not found in the set")

    def intersection_update(self, other_set):
        """
        原地修改集合，仅保留同时存在于当前集合和另一个集合中的元素。
        :param other_set: 另一个 CustomSet 实例。
        """
        if not isinstance(other_set, MySet):
            raise TypeError("Can only perform intersection with another CustomSet")

        # 需要移除的元素列表
        items_to_remove = []
        for item in self._elements:
            if not other_set.contains(item):
                items_to_remove.append(item)

        # 执行移除
        for item in items_to_remove:
            self.remove(item)

    def __len__(self):
        """
        返回集合中元素的数量。
        """
        return len(self._elements)

    def is_empty(self):
        """
        检查集合是否为空。
        """
        return len(self._elements) == 0

    def __iter__(self):
        """
        返回集合元素的迭代器。
        """
        return iter(self._elements.keys())

    def __str__(self):
        """
        返回集合的字符串表示形式。
        """
        items = ', '.join(map(str, self._elements.keys()))
        return f"CustomSet({{{items}}})"

    def __repr__(self):
        """
        返回集合的官方字符串表示形式。
        """
        return self.__str__()

# 示例用法
if __name__ == '__main__':
    set1 = MySet([1, 2, 3, 4])
    set2 = MySet([3, 4, 5, 6])

    print(f"Set 1: {set1}")
    print(f"Set 2: {set2}")
    print(f"Length of Set 1: {len(set1)}")
    print(f"Does Set 1 contain 3? {set1.contains(3)}")
    print(f"Does Set 1 contain 5? {set1.contains(5)}")

    set1.add(5)
    print(f"Set 1 after adding 5: {set1}")

    try:
        set1.remove(2)
        print(f"Set 1 after removing 2: {set1}")
        set1.remove(10) # 这会引发 KeyError
    except KeyError as e:
        print(e)

    set1 = MySet([1, 2, 3, 4]) # 重置 set1
    set1.intersection_update(set2)
    print(f"Set 1 after intersection update with Set 2: {set1}")

    print("Iterating through the updated Set 1:")
    for element in set1:
        print(element)

    print(f"Is Set 1 empty? {set1.is_empty()}")
    empty_set = MySet()
    print(f"Is empty_set empty? {empty_set.is_empty()}")
