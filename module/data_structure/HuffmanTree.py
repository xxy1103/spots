from module.data_structure.heap import MinHeap # 最小堆的特性完全符合构建哈夫曼树的过程，使用自定义的最小堆实现，不依赖heapq库
from collections import Counter # 用于统计字符频率
import struct

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq  # 字符出现频率
        self.left = None
        self.right = None

# 构建哈夫曼树
# 从频率最小的两个节点开始，从下至上构建
def build_huffman_tree(freq):
    """
    构建哈夫曼树
    Args:
        freq: 频率
    Returns:
        root: 根节点
    """
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
    """
    生成哈夫曼编码
    Args:
        root: 根节点
    Returns:
        codes: 哈夫曼编码字典
    """
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
def huffman_encoding(data, root=None, codes=None):
    """
    使用全局哈夫曼树压缩数据为真正的二进制格式
    
    Args:
        data: 待压缩数据
        root: 全局哈夫曼树根节点
        codes: 编码表
        
    Returns:
        tuple: 压缩后的二进制数据
    """
    # 在实际代码中对于用树还是编码表纯看编写时候的心情，于是都预留了位置
    if not data:
        print("数据为空，无法压缩")
        return bytes()
    
    # 如果只提供了树而没有编码表，则生成编码表
    if codes is None and root is not None:
        # 根据树生成编码表
        codes = generate_huffman_codes(root)
    # 啥都没有你压缩个屁，收拾er滚吧
    elif root is None and codes is  None:
        raise ValueError("必须提供哈夫曼树或编码表")
    
    # 检查编码表是否完整,输出错误信息
    for char in data:
        if char not in codes:
            raise ValueError(f"编码表中缺少字符: '{char}'")
    
    # 1. 先获取编码后的位序列
    bit_string = ''.join(codes[char] for char in data)
    
    # 2. 计算需要的填充位数，使总位数是8的倍数
    padding = 8 - (len(bit_string) % 8) if len(bit_string) % 8 != 0 else 0
    
    # 3. 添加填充位
    bit_string += '0' * padding
    
    # 4. 存储填充位数（1字节）
    padded_info = format(padding, '08b')
    bit_string = padded_info + bit_string
    
    # 5. 将位字符串转换为字节
    binary_data = bytearray()
    for i in range(0, len(bit_string), 8):
        byte = bit_string[i:i+8]
        binary_data.append(int(byte, 2))
    
    return bytes(binary_data)

# 对数据进行解压缩 - 修改为处理二进制数据
def huffman_decoding(binary_data, root):
    """
    解压缩二进制数据
    
    Args:
        binary_data: 压缩后的二进制数据
        root: 哈夫曼树的根节点
        
    Returns:
        str: 解压缩后的原始数据
    """
    if not binary_data or not root:
        return ""
    
    # 1. 提取填充信息
    padded_info = binary_data[0]
    
    # 2. 将二进制数据转换为位字符串
    bit_string = ""
    for byte in binary_data[1:]:  # 跳过第一个字节（填充信息）
        bits = bin(byte)[2:].zfill(8)  # 去掉'0b'前缀，并确保8位
        bit_string += bits
    
    # 3. 去除填充位
    bit_string = bit_string[:-padded_info] if padded_info > 0 else bit_string
    
    # 4. 使用哈夫曼树解码
    decoded_data = []
    current_node = root
    
    for bit in bit_string:
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right
        
        # 到达叶子节点
        if current_node.char is not None:
            decoded_data.append(current_node.char)
            current_node = root
    
    return ''.join(decoded_data)