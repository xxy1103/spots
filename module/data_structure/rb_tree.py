# 定义颜色常量
RED = "RED"
BLACK = "BLACK"

class Node:
    def __init__(self, key, value, color=RED, parent=None, left=None, right=None):
        self.key = key
        self.value = value
        self.color = color
        self.parent = parent
        self.left = left
        self.right = right
        # 在红黑树中，新插入的节点默认为红色

class RedBlackTree:
    def __init__(self):
        # 哨兵节点 T.nil
        self.TNULL = Node(None, None, color=BLACK)
        self.root = self.TNULL
        self.TNULL.parent = self.TNULL # 让哨兵节点的父节点指向自身，简化某些边界处理
        self.TNULL.left = self.TNULL
        self.TNULL.right = self.TNULL

    def search(self, value_to_search): # Parameter renamed for clarity, was 'key'
        """
        查找具有给定值的节点。
        """
        current = self.root
        while current != self.TNULL and value_to_search != current.value: # Compare with current.value
            if value_to_search < current.value: # Compare with current.value
                current = current.left
            else:
                current = current.right
        return current # 如果找不到，返回 TNULL

    def _left_rotate(self, x):
        """
        左旋操作。
        假设 y 是 x 的右孩子。
        """
        y = x.right
        x.right = y.left  # 将 y 的左子树转变为 x 的右子树
        if y.left != self.TNULL:
            y.left.parent = x

        y.parent = x.parent  # y 的父节点变为 x 的父节点
        if x.parent == self.TNULL: # 如果 x 是根节点
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y

        y.left = x  # x 成为 y 的左孩子
        x.parent = y

    def _right_rotate(self, y):
        """
        右旋操作。
        假设 x 是 y 的左孩子。
        """
        x = y.left
        y.left = x.right  # 将 x 的右子树转变为 y 的左子树
        if x.right != self.TNULL:
            x.right.parent = y

        x.parent = y.parent  # x 的父节点变为 y 的父节点
        if y.parent == self.TNULL: # 如果 y 是根节点
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x

        x.right = y  # y 成为 x 的右孩子
        y.parent = x

    def insert(self, key, value):
        """
        插入新的键值对。树将根据 'value' 排序。
        """
        # 创建新节点，默认为红色
        node = Node(key, value, color=RED, parent=self.TNULL, left=self.TNULL, right=self.TNULL)

        parent = self.TNULL
        current = self.root

        # 找到新节点的插入位置，根据 'value' 进行比较
        while current != self.TNULL:
            parent = current
            if node.value < current.value: # Compare node.value with current.value
                current = current.left
            elif node.value > current.value: # Compare node.value with current.value
                current = current.right
            else: # value 已存在，更新 key
                current.key = key
                return

        node.parent = parent # 设置新节点的父节点

        if parent == self.TNULL: # 如果树为空
            self.root = node
        elif node.value < parent.value: # Compare node.value with parent.value
            parent.left = node
        else:
            parent.right = node

        # 如果新节点的父节点是 TNULL (即树是空的，新节点是根节点)，
        # 则不需要修复，直接将其颜色置为黑色即可。
        if node.parent == self.TNULL:
            node.color = BLACK
            return

        # 如果新节点的祖父节点是 TNULL (即父节点是根节点)，
        # 也不需要复杂的修复，因为根节点总是黑色的，
        # 如果父节点是红色，则新节点也是红色，此时父节点是根，颜色为黑，不会出现红红相邻。
        # 但标准插入后修复逻辑会处理这种情况。

        # 调用修复函数，保持红黑树性质
        self._insert_fixup(node)

    def _insert_fixup(self, z):
        """
        修复插入操作后可能破坏的红黑树性质。
        z 是新插入的节点。
        """
        while z.parent.color == RED: # 父节点是红色，违反性质4 (如果一个节点是红色的，则它的两个子节点都是黑色的)
            if z.parent == z.parent.parent.left: # 父节点是祖父节点的左孩子
                y = z.parent.parent.right # y 是叔叔节点
                if y.color == RED: # Case 1: 叔叔节点是红色
                    z.parent.color = BLACK
                    y.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent # 将 z 指向祖父节点，继续向上检查
                else: # Case 2 & 3: 叔叔节点是黑色
                    if z == z.parent.right: # Case 2: z 是父节点的右孩子 (形成 "之" 字形)
                        z = z.parent
                        self._left_rotate(z) # 左旋，转换为 Case 3
                    # Case 3: z 是父节点的左孩子 (形成 "一" 字形)
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self._right_rotate(z.parent.parent)
            else: # 父节点是祖父节点的右孩子 (对称于上面的情况)
                y = z.parent.parent.left # y 是叔叔节点
                if y.color == RED: # Case 1
                    z.parent.color = BLACK
                    y.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                else:
                    if z == z.parent.left: # Case 2
                        z = z.parent
                        self._right_rotate(z) # 右旋
                    # Case 3
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self._left_rotate(z.parent.parent)
            if z == self.root: # 如果 z 上升到根节点，停止循环
                break
        self.root.color = BLACK # 性质2: 根节点是黑色的

    def _transplant(self, u, v):
        """
        用子树 v 替换子树 u。
        """
        if u.parent == self.TNULL:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    def _minimum(self, node):
        """
        查找以 node 为根的子树中的最小节点。
        """
        while node.left != self.TNULL:
            node = node.left
        return node

    def delete(self, value_to_delete): # Parameter renamed for clarity, was 'key'
        """
        删除具有给定值的节点。
        """
        z = self.search(value_to_delete) # Search will use value due to its modification
        if z == self.TNULL:
            # print(f"Value {value_to_delete} not found in the tree.")
            return # 值不存在

        y = z # y 是实际被删除或移动的节点
        y_original_color = y.color
        x = self.TNULL # x 是用来替换 y 的节点，或者在 y 没有孩子时指向 TNULL

        if z.left == self.TNULL: # z 最多只有一个右孩子
            x = z.right
            self._transplant(z, z.right)
        elif z.right == self.TNULL: # z 只有一个左孩子
            x = z.left
            self._transplant(z, z.left)
        else: # z 有两个孩子
            y = self._minimum(z.right) # y 是 z 的后继
            y_original_color = y.color
            x = y.right # x 是 y 的右孩子 (y 最多只有一个右孩子，因为它是最小的)

            if y.parent == z: # 如果 y 是 z 的直接右孩子
                x.parent = y # 即使 x 是 TNULL，其 parent 也需要正确设置
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y

            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color # y 继承 z 的颜色

        # 如果被删除/移动的节点 y 是黑色的，则可能破坏红黑树性质
        if y_original_color == BLACK:
            self._delete_fixup(x)

    def _delete_fixup(self, x):
        """
        修复删除操作后可能破坏的红黑树性质。
        x 是进入被删除节点位置的节点，它带有一重额外的黑色。
        """
        while x != self.root and x.color == BLACK:
            if x == x.parent.left: # x 是其父节点的左孩子
                w = x.parent.right # w 是 x 的兄弟节点
                if w.color == RED: # Case 1: x 的兄弟 w 是红色的
                    w.color = BLACK
                    x.parent.color = RED
                    self._left_rotate(x.parent)
                    w = x.parent.right # 更新兄弟节点，进入 Case 2, 3, or 4

                # 此时 w 必为黑色
                if w.left.color == BLACK and w.right.color == BLACK: # Case 2: x 的兄弟 w 是黑色的，且 w 的两个孩子都是黑色的
                    w.color = RED
                    x = x.parent # 将额外的黑色向上传递
                else:
                    if w.right.color == BLACK: # Case 3: x 的兄弟 w 是黑色的，w 的左孩子是红色的，右孩子是黑色的
                        w.left.color = BLACK
                        w.color = RED
                        self._right_rotate(w)
                        w = x.parent.right # 更新兄弟节点，进入 Case 4

                    # Case 4: x 的兄弟 w 是黑色的，且 w 的右孩子是红色的
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.right.color = BLACK
                    self._left_rotate(x.parent)
                    x = self.root # 完成修复，将 x 指向根节点以终止循环
            else: # x 是其父节点的右孩子 (对称于上面的情况)
                w = x.parent.left # w 是 x 的兄弟节点
                if w.color == RED: # Case 1
                    w.color = BLACK
                    x.parent.color = RED
                    self._right_rotate(x.parent)
                    w = x.parent.left

                if w.right.color == BLACK and w.left.color == BLACK: # Case 2
                    w.color = RED
                    x = x.parent
                else:
                    if w.left.color == BLACK: # Case 3
                        w.right.color = BLACK
                        w.color = RED
                        self._left_rotate(w)
                        w = x.parent.left
                    # Case 4
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.left.color = BLACK
                    self._right_rotate(x.parent)
                    x = self.root
        x.color = BLACK # 确保根节点或实际替换的节点最终是黑色的

    def inorder_traversal(self, node=None, result=None):
        """
        中序遍历红黑树 (用于测试和调试)。
        返回一个包含 (key, value, color) 元组的列表。
        """
        if node is None:
            node = self.root
        if result is None:
            result = []

        if node != self.TNULL:
            self.inorder_traversal(node.left, result)
            result.append((node.key, node.value, node.color))
            self.inorder_traversal(node.right, result)
        return result

    def get_all_keys(self, node=None, keys_list=None):
        """
        返回红黑树中所有原键的列表 (顺序由value决定)。
        """
        if node is None:
            node = self.root
        if keys_list is None:
            keys_list = []

        if node != self.TNULL:
            self.get_all_keys(node.left, keys_list)
            keys_list.append(node.key) # Still appends original key, but order is by value
            self.get_all_keys(node.right, keys_list)
        return keys_list

    def get_height(self, node=None):
        """
        计算树的高度 (用于测试和调试)。
        """
        if node is None:
            node = self.root
        if node == self.TNULL:
            return 0
        return 1 + max(self.get_height(node.left), self.get_height(node.right))

    def print_tree(self, node=None, level=0, prefix="Root:"):
        """
        打印树的结构 (用于测试和调试)。
        显示节点的 value 和 color。
        """
        if node is None:
            node = self.root

        if node != self.TNULL:
            print(" " * (level * 4) + prefix + str(node.value) + "(" + node.color + ") [key:" + str(node.key) + "]") # Display value for structure
            if node.left != self.TNULL or node.right != self.TNULL:
                self.print_tree(node.right, level + 1, "R---")
                self.print_tree(node.left, level + 1, "L---")

# 示例用法:
if __name__ == '__main__':
    rbt = RedBlackTree()

    # 注意：现在树是按字符串value排序的 ("value_X")
    # 搜索和删除时，也应该使用这些字符串value
    keys_and_values_to_insert = [
        (10, "value_10"), (20, "value_20"), (30, "value_05"), # value_05会较小
        (15, "value_15"), (25, "value_25"), (5, "value_01"),  # value_01会最小
        (1, "value_07"), (7, "value_12"), (12, "value_17"),
        (17, "value_22"), (22, "value_27"), (27, "value_35"),
        (35, "value_40")
    ]
    print("Inserting items (key, value):", keys_and_values_to_insert)
    for key, value in keys_and_values_to_insert:
        rbt.insert(key, value)
        # print(f"After inserting ({key}, {value}):")
        # rbt.print_tree()
        # print("-" * 30)

    print("\\nFinal tree structure:")
    rbt.print_tree() # print_tree now shows value
    
    # inorder_traversal 返回 (key, value, color) 元组列表，按 value 排序
    traversal_result = rbt.inorder_traversal()
    print("\\nInorder traversal (sorted by value):", traversal_result)
    print("Just values from traversal:", [item[1] for item in traversal_result])


    print("Tree height:", rbt.get_height())
    
    # get_all_keys 返回原始key的列表，但顺序是根据value排序的
    all_original_keys = rbt.get_all_keys()
    print("All original keys (order determined by value sorting):", all_original_keys)

    # 搜索现在基于 value
    print("\\nSearching for value 'value_15':", rbt.search("value_15").key if rbt.search("value_15") != rbt.TNULL else "Not found")
    print("Searching for value 'value_100':", rbt.search("value_100").key if rbt.search("value_100") != rbt.TNULL else "Not found")

    values_to_delete = ["value_01", "value_12", "value_22", "value_35", "value_05", "value_15", "value_25", "value_40", "value_10", "value_20"]
    print("\\nDeleting values:", values_to_delete)
    for val_del in values_to_delete:
        print(f"Deleting value {val_del}...")
        rbt.delete(val_del) # Delete is by value
        # print(f"After deleting {val_del}:")
        # rbt.print_tree()
        # print("Inorder traversal:", rbt.inorder_traversal())
        # print("-" * 30)

    print("\\nFinal tree structure after deletions:")
    rbt.print_tree()
    traversal_after_delete = rbt.inorder_traversal()
    print("Inorder traversal after deletions (sorted by value):", traversal_after_delete)
    print("Just values from traversal after deletions:", [item[1] for item in traversal_after_delete])
    print("Tree height after deletions:", rbt.get_height())
    print("All original keys after deletions:", rbt.get_all_keys())

    # Test deleting non-existent value
    print("\\nDeleting non-existent value 'value_100':")
    rbt.delete("value_100")
    rbt.print_tree()

    # Test inserting after deletions
    print("\\nInserting (50, 'value_50') and (60, 'value_60'):")
    rbt.insert(50, "value_50")
    rbt.insert(60, "value_60")
    rbt.print_tree()
    print("Inorder traversal:", rbt.inorder_traversal())
    print("All original keys after re-insertion:", rbt.get_all_keys())
