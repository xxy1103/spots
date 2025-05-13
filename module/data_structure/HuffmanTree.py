from module.data_structure.heap import MinHeap # 最小堆的特性完全符合构建哈夫曼树的过程，使用自定义的最小堆实现，不依赖heapq库
from collections import Counter # 用于统计字符频率

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq  # 字符出现频率
        self.left = None
        self.right = None

# 构建哈夫曼树
# 从频率最小的两个节点开始，从下至上构建
def build_huffman_tree(freq):
    # 创建节点列表
    nodes = [Node(char, freq) for char, freq in freq.items()]
    
    # 创建最小堆
    heap = MinHeap()
    
    # 将节点转换为堆
    heap_items = [(node.freq, i, node) for i, node in enumerate(nodes)]
    heap.heapify(heap_items)
    
    # 构建哈夫曼树
    while len(heap) > 1: # 循环至根节点
        # 寻找频率最小的两个节点
        freq1, _, left = heap.pop()
        freq2, _, right = heap.pop()
        # 合并节点
        merged_node = Node(None, freq1 + freq2) # 内部节点不储存数据
        merged_node.left = left
        merged_node.right = right
        
        # 将新节点推入堆
        heap.push((merged_node.freq, len(nodes), merged_node))
        nodes.append(merged_node)  # 生成唯一 idx
    
    # 返回根节点
    if not heap.is_empty():
        return heap.peek()[2]
    return None

# 递归生成哈夫曼编码
def generate_huffman_codes(root):
    codes = {}
    
    # 使用内部函数，免于每次递归传递所有codes字典
    def _generate_codes(node, current_code):
        # 终止条件
        if node is None:
            return
        # 只有叶子节点才生成编码
        if node.char is not None:
            codes[node.char] = current_code
        # 左0右1
        _generate_codes(node.left, current_code + "0")
        _generate_codes(node.right, current_code + "1")
    
    _generate_codes(root, "")
    return codes

# 对数据进行无损压缩
def huffman_encoding(data):
    if not data:
        return "", None
    
    # 统计字符频率
    freq = Counter(data)
    # 构建哈夫曼树
    root = build_huffman_tree(freq)
    # 生成哈夫曼编码
    codes = generate_huffman_codes(root)
    
    # 编码数据
    encoded_data = ''.join(codes[char] for char in data)
    return encoded_data, root

# 对数据进行解压缩
def huffman_decoding(encoded_data, root):
    if not encoded_data or not root:
        return ""
    
    decoded_data = []
    current_node = root
    
    for bit in encoded_data:
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right
        
        if current_node.char is not None:
            decoded_data.append(current_node.char)
            current_node = root
    
    return ''.join(decoded_data)