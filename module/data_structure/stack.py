# filepath: d:\windows\desktop\数据结构课设\个性化旅游系统\module\data_structure\stack.py

class Stack:
    """
    栈的基本实现
    支持出栈(pop)、入栈(push)、判断栈是否为空(is_empty)、获取栈顶元素(peek)、获取栈大小(size)等基本操作
    """
    def __init__(self,holes=[]):
        """
        初始化一个空栈
        """
        self.items = holes

    def is_empty(self):
        """
        判断栈是否为空
        
        Returns:
            bool: 如果栈为空返回True，否则返回False
        """
        return len(self.items) == 0
    
    def push(self, item):
        """
        将元素入栈
        
        Args:
            item: 要入栈的元素
        """
        self.items.append(item)
        
    def pop(self):
        """
        将栈顶元素出栈
        
        Returns:
            栈顶元素，如果栈为空则抛出异常
        
        Raises:
            IndexError: 当栈为空时抛出
        """
        if self.is_empty():
            raise IndexError("从空栈中弹出")
        return self.items.pop()
    
    def peek(self):
        """
        获取栈顶元素但不出栈
        
        Returns:
            栈顶元素，如果栈为空则抛出异常
            
        Raises:
            IndexError: 当栈为空时抛出
        """
        if self.is_empty():
            raise IndexError("空栈无法查看栈顶元素")
        return self.items[-1]
    
    def size(self):
        """
        获取栈的大小
        
        Returns:
            int: 栈中元素的数量
        """
        return len(self.items)
    
    def clear(self):
        """
        清空栈
        """
        self.items = []
        
    def __str__(self):
        """
        返回栈的字符串表示
        
        Returns:
            str: 栈的字符串表示
        """
        return str(self.items)
    
    def __repr__(self):
        """
        返回栈的正式字符串表示
        
        Returns:
            str: 栈的正式字符串表示
        """
        return f"Stack({self.items})"


# 测试代码
if __name__ == "__main__":
    stack = Stack()
    
    # 测试入栈
    stack.push(1)
    stack.push(2)
    stack.push(3)
    
    print(f"栈内元素: {stack}")
    print(f"栈大小: {stack.size()}")
    print(f"栈顶元素: {stack.peek()}")
    
    # 测试出栈
    print(f"出栈元素: {stack.pop()}")
    print(f"出栈后栈内元素: {stack}")
    
    # 测试清空栈
    stack.clear()
    print(f"清空后栈是否为空: {stack.is_empty()}")