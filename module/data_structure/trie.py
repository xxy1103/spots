# -*- coding: utf-8 -*-
"""
Trie树数据结构实现
用于高效的字符串查找操作
"""

class TrieNode:
    """Trie树的节点类"""
    
    def __init__(self):
        self.children = {}  # 字典存储子节点
        self.is_end_of_word = False  # 标记是否为单词结尾
        self.data = None  # 存储与该单词关联的数据
        
class Trie:
    """Trie树类，支持插入、查找、删除和前缀查询操作"""
    
    def __init__(self):
        self.root = TrieNode()
        self.size = 0  # 记录存储的单词数量
    
    def insert(self, word, data=None):
        """
        向Trie树中插入一个单词及其关联数据
        
        Args:
            word (str): 要插入的单词
            data (any): 与单词关联的数据
        
        Returns:
            bool: 如果是新单词返回True，如果更新已存在单词返回False
        """
        if not word:
            return False
            
        node = self.root
        
        # 遍历单词的每个字符
        for char in word.lower():  # 转换为小写以实现大小写不敏感
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        # 检查是否为新单词
        is_new_word = not node.is_end_of_word
        
        # 标记单词结尾并存储数据
        node.is_end_of_word = True
        node.data = data
        
        if is_new_word:
            self.size += 1
            
        return is_new_word
    
    def search(self, word):
        """
        在Trie树中查找单词
        
        Args:
            word (str): 要查找的单词
            
        Returns:
            any: 如果找到返回关联的数据，否则返回None
        """
        if not word:
            return None
            
        node = self._find_node(word.lower())
        
        if node and node.is_end_of_word:
            return node.data
        return None
    
    def _find_node(self, word):
        """
        查找单词对应的节点
        
        Args:
            word (str): 要查找的单词
            
        Returns:
            TrieNode: 对应的节点，如果不存在返回None
        """
        node = self.root
        
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
            
        return node
    
    def starts_with(self, prefix):
        """
        查找以指定前缀开头的所有单词
        
        Args:
            prefix (str): 前缀字符串
            
        Returns:
            list: 包含所有匹配单词及其数据的列表
        """
        if not prefix:
            return []
            
        prefix_node = self._find_node(prefix.lower())
        if not prefix_node:
            return []
        
        # 从前缀节点开始收集所有单词
        results = []
        self._collect_words(prefix_node, prefix.lower(), results)
        return results
    
    def _collect_words(self, node, current_word, results):
        """
        递归收集从指定节点开始的所有单词
        
        Args:
            node (TrieNode): 当前节点
            current_word (str): 当前构建的单词
            results (list): 结果列表
        """
        if node.is_end_of_word:
            results.append({
                'word': current_word,
                'data': node.data
            })
        
        for char, child_node in node.children.items():
            self._collect_words(child_node, current_word + char, results)
    
    def delete(self, word):
        """
        从Trie树中删除单词
        
        Args:
            word (str): 要删除的单词
            
        Returns:
            bool: 如果成功删除返回True，否则返回False
        """
        if not word:
            return False
            
        return self._delete_helper(self.root, word.lower(), 0)
    
    def _delete_helper(self, node, word, index):
        """
        删除操作的递归辅助函数
        
        Args:
            node (TrieNode): 当前节点
            word (str): 要删除的单词
            index (int): 当前字符索引
            
        Returns:
            bool: 是否可以安全删除当前节点
        """
        if index == len(word):
            # 到达单词末尾
            if not node.is_end_of_word:
                return False  # 单词不存在
            
            node.is_end_of_word = False
            node.data = None
            self.size -= 1
            
            # 如果没有子节点，可以删除
            return len(node.children) == 0
        
        char = word[index]
        if char not in node.children:
            return False  # 单词不存在
        
        child_node = node.children[char]
        should_delete_child = self._delete_helper(child_node, word, index + 1)
        
        if should_delete_child:
            del node.children[char]
            
            # 如果当前节点不是单词结尾且没有其他子节点，可以删除
            return not node.is_end_of_word and len(node.children) == 0
        
        return False
    
    def get_all_words(self):
        """
        获取Trie树中的所有单词
        
        Returns:
            list: 包含所有单词及其数据的列表
        """
        results = []
        self._collect_words(self.root, "", results)
        return results
    
    def get_size(self):
        """
        获取Trie树中单词的数量
        
        Returns:
            int: 单词数量
        """
        return self.size
    
    def is_empty(self):
        """
        检查Trie树是否为空
        
        Returns:
            bool: 如果为空返回True，否则返回False
        """
        return self.size == 0
    
    def clear(self):
        """
        清空Trie树
        """
        self.root = TrieNode()
        self.size = 0


# 用户名专用的Trie树实现
class UsernameTrie(Trie):
    """
    专门用于用户名查找的Trie树
    支持用户ID和用户名的双向查找
    """
    
    def __init__(self):
        super().__init__()
        self.id_to_name = {}  # ID到用户名的映射
    
    def insert_user(self, user_id, username):
        """
        插入用户信息
        
        Args:
            user_id (int): 用户ID
            username (str): 用户名
            
        Returns:
            bool: 如果成功插入返回True，如果用户名已存在返回False
        """
        if self.search(username) is not None:
            return False  # 用户名已存在
        
        user_data = {
            "id": user_id,
            "name": username
        }
        
        # 插入到Trie树
        self.insert(username, user_data)
        
        # 添加ID到用户名的映射
        self.id_to_name[user_id] = username
        
        return True
    
    def search_by_username(self, username):
        """
        根据用户名查找用户信息
        
        Args:
            username (str): 用户名
            
        Returns:
            dict: 用户信息字典，如果不存在返回None
        """
        return self.search(username)
    
    def search_by_id(self, user_id):
        """
        根据用户ID查找用户信息
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            dict: 用户信息字典，如果不存在返回None
        """
        if user_id in self.id_to_name:
            username = self.id_to_name[user_id]
            return self.search(username)
        return None
    
    def delete_user(self, username):
        """
        删除用户
        
        Args:
            username (str): 用户名
            
        Returns:
            bool: 如果成功删除返回True，否则返回False
        """
        user_data = self.search(username)
        if user_data is None:
            return False
        
        user_id = user_data["id"]
        
        # 从Trie树中删除
        success = self.delete(username)
        
        if success and user_id in self.id_to_name:
            del self.id_to_name[user_id]
        
        return success
    
    def find_users_by_prefix(self, prefix):
        """
        根据前缀查找用户
        
        Args:
            prefix (str): 用户名前缀
            
        Returns:
            list: 匹配的用户信息列表
        """
        results = self.starts_with(prefix)
        return [result['data'] for result in results]


if __name__ == "__main__":
    # 测试代码
    trie = UsernameTrie()
    
    # 插入测试数据
    trie.insert_user(1, "alice")
    trie.insert_user(2, "bob")
    trie.insert_user(3, "charlie")
    trie.insert_user(4, "alice123")  # 应该插入失败，但这里名字不同
    
    # 测试查找
    print("查找 alice:", trie.search_by_username("alice"))
    print("查找 bob:", trie.search_by_username("bob"))
    print("查找 nonexistent:", trie.search_by_username("nonexistent"))
    
    # 测试前缀查找
    print("前缀 'al' 的用户:", trie.find_users_by_prefix("al"))
    
    # 测试ID查找
    print("查找ID 2:", trie.search_by_id(2))
    
    print("Trie树大小:", trie.get_size())
