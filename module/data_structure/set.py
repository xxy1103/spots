class IntSet:
    """
    一个简单的整数集合类，实现基本的集合操作
    """
    def __init__(self, elements=None):
        """
        初始化集合
        :param elements: 可选的初始元素列表
        """
        self.elements = []
        if elements:
            for element in elements:
                self.add(element)
    
    def add(self, element):
        """
        添加元素到集合
        :param element: 要添加的整数元素
        :return: None
        """
        if not isinstance(element, int):
            raise TypeError("集合只能包含整数元素")
        
        if element not in self.elements:
            self.elements.append(element)
    
    def remove(self, element):
        """
        从集合中删除元素
        :param element: 要删除的元素
        :return: None
        :raises ValueError: 如果元素不在集合中
        """
        if element in self.elements:
            self.elements.remove(element)
        else:
            raise ValueError(f"元素 {element} 不在集合中")
    
    def discard(self, element):
        """
        从集合中删除元素，如果元素不存在则不进行操作
        :param element: 要删除的元素
        :return: None
        """
        if element in self.elements:
            self.elements.remove(element)
    
    def contains(self, element):
        """
        检查元素是否在集合中
        :param element: 要检查的元素
        :return: 布尔值
        """
        return element in self.elements
    
    def union(self, other_set):
        """
        返回两个集合的并集
        :param other_set: 另一个集合
        :return: 新的集合
        """
        result = IntSet(self.elements)
        for element in other_set.elements:
            result.add(element)
        return result
    
    def intersection(self, other_set):
        """
        返回两个集合的交集
        :param other_set: 另一个集合
        :return: 新的集合
        """
        result = IntSet()
        for element in self.elements:
            if element in other_set.elements:
                result.add(element)
        return result
    
    def difference(self, other_set):
        """
        返回两个集合的差集（self - other_set）
        :param other_set: 另一个集合
        :return: 新的集合
        """
        result = IntSet()
        for element in self.elements:
            if element not in other_set.elements:
                result.add(element)
        return result
    
    def clear(self):
        """
        清空集合
        :return: None
        """
        self.elements = []
    
    def size(self):
        """
        返回集合中元素的数量
        :return: 整数
        """
        return len(self.elements)
    
    def is_empty(self):
        """
        检查集合是否为空
        :return: 布尔值
        """
        return len(self.elements) == 0
    
    def get_all_elements(self):
        """
        返回集合中所有元素的列表
        :return: 整数列表
        """
        return self.elements.copy()
    
    def __str__(self):
        """
        返回集合的字符串表示
        :return: 字符串
        """
        return "{" + ", ".join(str(e) for e in self.elements) + "}"
    
    def __repr__(self):
        """
        返回集合的字符串表示
        :return: 字符串
        """
        return self.__str__()
