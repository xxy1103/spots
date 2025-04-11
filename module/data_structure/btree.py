import os
import json
import pickle
import printLog as log

class BTreeNode:
    def __init__(self, leaf=True, t=3):
        """
        初始化一个B树节点
        leaf: 是否为叶子节点
        t: B树的最小度数，决定了节点中最大和最小的关键字数量
        """
        self.leaf = leaf      # 是否为叶子节点
        self.keys = []        # 关键字列表，每个关键字是一个字典 {id:, name:""}
        self.children = []    # 子节点列表
        self.t = t           # B树的最小度数
        
    def is_full(self):
        """检查节点是否已满"""
        return len(self.keys) == 2 * self.t - 1


class BTree:
    def __init__(self, t=3):
        """
        初始化B树
        t: B树的最小度数
        """
        self.root = BTreeNode(leaf=True, t=t)
        self.t = t
    
    def search(self, name):
        """按名称搜索"""
        return self._search_node(self.root, name)
    
    def _search_node(self, node, name):
        """在指定节点中搜索名称"""
        i = 0
        # 找到第一个大于等于name的关键字位置
        while i < len(node.keys) and name > node.keys[i]["name"]:
            i += 1
        
        # 如果找到匹配的关键字
        if i < len(node.keys) and name == node.keys[i]["name"]:
            return node.keys[i]
        
        # 如果是叶子节点且没找到，返回None
        if node.leaf:
            return None
        
        # 如果不是叶子节点，递归搜索对应的子节点
        return self._search_node(node.children[i], name)
    
    def insert(self, data):
        """向B树中插入数据"""
        # 如果根节点已满，需要分裂根节点
        if self.root.is_full():
            new_root = BTreeNode(leaf=False, t=self.t)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
        
        self._insert_non_full(self.root, data)
    
    def _insert_non_full(self, node, data):
        """向未满的节点中插入数据"""
        i = len(node.keys) - 1
        
        # 如果是叶子节点，直接插入
        if node.leaf:
            # 找到合适的位置插入关键字
            while i >= 0 and data["name"] < node.keys[i]["name"]:
                i -= 1
            node.keys.insert(i + 1, data)
        else:
            # 找到合适的子节点
            while i >= 0 and data["name"] < node.keys[i]["name"]:
                i -= 1
            i += 1
            
            # 如果子节点已满，先分裂
            if node.children[i].is_full():
                self._split_child(node, i)
                # 确定插入到哪个子节点
                if data["name"] > node.keys[i]["name"]:
                    i += 1
            
            # 递归插入到子节点
            self._insert_non_full(node.children[i], data)
    
    def _split_child(self, parent, index):
        """分裂parent的第index个子节点"""
        t = self.t
        child = parent.children[index]
        new_child = BTreeNode(leaf=child.leaf, t=t)
        
        # 将child的后半部分关键字移动到new_child
        parent.keys.insert(index, child.keys[t-1])
        parent.children.insert(index + 1, new_child)
        
        new_child.keys = child.keys[t:]
        child.keys = child.keys[:t-1]
        
        # 如果不是叶子节点，还需要移动子节点
        if not child.leaf:
            new_child.children = child.children[t:]
            child.children = child.children[:t]
    
    def print_tree(self):
        """打印整个B树（按层次遍历）"""
        if not self.root:
            print("Empty tree")
            return
        
        queue = [self.root]
        level = 0
        
        while queue:
            size = len(queue)
            print(f"Level {level}:")
            
            for _ in range(size):
                node = queue.pop(0)
                keys_str = [f"{k['id']}:{k['name']}" for k in node.keys]
                print(f"  Node: {keys_str}")
                
                if not node.leaf:
                    queue.extend(node.children)
            
            level += 1
            print()
    def save_to_file(self, filename):
        """
        将B树保存到文件
        :param filename: 文件名（不含路径）
        :return: 是否保存成功
        """
        try:
            # 确保目录存在
            save_dir = "index/global/"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # 完整的文件路径
            filepath = os.path.join(save_dir, filename)
            
            # 使用pickle序列化整个B树
            with open(filepath, 'wb') as f:
                pickle.dump(self, f)
                
            log.writeLog(f"B树已保存到 {filepath}")
            return True
        except Exception as e:
            log.writeLog(f"保存B树失败: {str(e)}")
            return False
    
    @staticmethod
    def load_from_file(filename):
        """
        从文件加载B树
        :param filename: 文件名（不含路径）
        :return: 加载的B树对象，如果加载失败则返回None
        """
        try:
            # 完整的文件路径
            filepath = os.path.join("index/global/", filename)
            
            # 检查文件是否存在
            if not os.path.exists(filepath):
                log.writeLog(f"B树文件不存在: {filepath}")
                return None
                
            # 使用pickle加载B树
            with open(filepath, 'rb') as f:
                btree = pickle.load(f)
                
            log.writeLog(f"B树已从 {filepath} 加载")
            return btree
        except Exception as e:
            log.writeLog(f"加载B树失败: {str(e)}")
            return None

# 示例用法更新
if __name__ == "__main__":
    btree = BTree(t=2)  # 最小度数为2的B树
    
    # 插入一些测试数据（包含中英文）
    test_data = [
        {"id": 1, "name": "apple"},
        {"id": 2, "name": "banana"},
        {"id": 3, "name": "橙子"},
        {"id": 4, "name": "苹果"},
        {"id": 5, "name": "西瓜"},
        {"id": 6, "name": "grape"},
        {"id": 7, "name": "梨子"},
        {"id": 8, "name": "cherry"}
    ]
    
    for data in test_data:
        btree.insert(data)
    
    # 打印B树结构
    print("B树结构:")
    btree.print_tree()
    
    # 测试搜索
    search_name = "苹果"
    result = btree.search(search_name)
    if result:
        print(f"找到: {result}")
    else:
        print(f"未找到: {search_name}")
    
    # 保存B树到文件
    save_success = btree.save_to_file("name_index.btree")
    print(f"保存B树: {'成功' if save_success else '失败'}")
    
    # 从文件加载B树
    loaded_btree = BTree.load_from_file("name_index.btree")
    if loaded_btree:
        print("加载的B树结构:")
        loaded_btree.print_tree()
        
        # 测试加载的B树搜索功能
        search_name = "西瓜"
        result = loaded_btree.search(search_name)
        if result:
            print(f"在加载的B树中找到: {result}")
        else:
            print(f"在加载的B树中未找到: {search_name}")