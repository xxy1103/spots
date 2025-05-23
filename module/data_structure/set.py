class MySet:
    """
    一个简单的自定义集合类，支持哈希和非哈希元素。
    """
    def __init__(self, iterable=None):
        """
        初始化集合。可以从一个可迭代对象初始化。
        :param iterable: 可选的可迭代对象，用于初始化集合元素。
        """
        self._elements = {}  # 键是元素或元素ID，值是元素本身
        self._unhashable_elements = []  # 存储不可哈希的元素
        if iterable:
            for item in iterable:
                self.add(item)

    def add(self, item):
        """
        向集合中添加一个元素。
        :param item: 要添加的元素。
        """
        try:
            # 尝试将元素作为键
            hash(item)
            self._elements[item] = True
        except TypeError:
            # 如果元素不可哈希，则存储在列表中
            if item not in self._unhashable_elements:
                self._unhashable_elements.append(item)

    def contains(self, item):
        """
        检查元素是否存在于集合中。
        :param item: 要检查的元素。
        :return: 如果元素存在则返回 True，否则返回 False。
        """
        try:
            # 尝试在字典中查找
            hash(item)
            return item in self._elements
        except TypeError:
            # 对于不可哈希元素，在列表中查找
            return item in self._unhashable_elements

    def remove(self, item):
        """
        从集合中移除一个元素。如果元素不存在，则引发 KeyError。
        :param item: 要移除的元素。
        """
        try:
            # 尝试从字典中移除
            hash(item)
            if item in self._elements:
                del self._elements[item]
            else:
                raise KeyError(f"Element {item} not found in the set")
        except TypeError:
            # 对于不可哈希元素，从列表中移除
            if item in self._unhashable_elements:
                self._unhashable_elements.remove(item)
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

        # 执行字典元素的移除
        for item in items_to_remove:
            self.remove(item)
            
        # 对于不可哈希元素
        unhashable_to_remove = []
        for item in self._unhashable_elements:
            if not other_set.contains(item):
                unhashable_to_remove.append(item)
                
        # 执行不可哈希元素的移除
        for item in unhashable_to_remove:
            self._unhashable_elements.remove(item)

    def __len__(self):
        """
        返回集合中元素的数量。
        """
        return len(self._elements) + len(self._unhashable_elements)

    def is_empty(self):
        """
        检查集合是否为空。
        """
        return len(self._elements) == 0 and len(self._unhashable_elements) == 0

    def __iter__(self):
        """
        返回集合元素的迭代器。
        """
        # 先返回可哈希元素，再返回不可哈希元素
        for item in self._elements.keys():
            yield item
        for item in self._unhashable_elements:
            yield item

    def __str__(self):
        """
        返回集合的字符串表示形式。
        """
        all_items = list(self._elements.keys()) + self._unhashable_elements
        items = ', '.join(map(str, all_items))
        return f"CustomSet({{{items}}})"

    def __repr__(self):
        """
        返回集合的官方字符串表示形式。
        """
        return self.__str__()
    
    def __getitem__(self, index):
        """
        支持通过索引访问集合中的元素。
        :param index: 要访问的元素的索引。
        :return: 集合中指定索引处的元素。
        :raises IndexError: 如果索引超出范围。
        """
        all_items = list(self._elements.keys()) + self._unhashable_elements
        if 0 <= index < len(all_items):
            return all_items[index]
        else:
            raise IndexError("MySet index out of range")
            
    def to_list(self):
        """
        将集合转换为列表并返回。
        :return: 包含集合所有元素的列表。
        """
        return list(self._elements.keys()) + self._unhashable_elements

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
