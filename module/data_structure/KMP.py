def build_next(pattern):
    """构建KMP算法的next数组（失效函数）
    
    Args:
        pattern: 模式串
        
    Returns:
        next数组
    """
    if not pattern:
        return []
    
    next_array = [0] * len(pattern)
    j = 0 # 前缀长度

    for i in range(1, len(pattern)): # i为后缀指针，在后len-1个字符中移动

        # 这个while循环会一直往前寻找前缀，直到找到一个匹配的前缀长度
        # 或者j为0（即没有前缀匹配），这样就可以精简地处理 aaaaaab 这种拥有连续相同前缀的情况
        while j > 0 and pattern[i] != pattern[j]: # 不匹配时重新开始寻找前缀
            j = next_array[j - 1]
        
        if pattern[i] == pattern[j]: # 如果匹配，前缀长度加1，后缀的指针在for循环中递增
            j += 1
            
        next_array[i] = j # 记录当前位置的公共前后缀长度

    return next_array

def kmp_search(text, pattern):
    """使用KMP算法搜索模式串在文本中是否存在
    
    Args:
        text: 主串（进行搜索的文本）
        pattern: 模式串（搜索词）
        
    Returns:
        bool: 如果找到返回True，否则返回False
    """
    if not pattern: # 搜索词为空
        return False
    if not text or len(pattern) > len(text): # 搜索词大于原文
        return False
    
    next_array = build_next(pattern)
    j = 0  # pattern的指针
    
    # 这里外层用for循环，同时完成定义和主串指针递增
    for i in range(len(text)):  # text的指针
        while j > 0 and text[i] != pattern[j]: # 如果不匹配，通过next数组回溯
            j = next_array[j - 1]
        
        if text[i] == pattern[j]:
            j += 1
        
        if j == len(pattern):
            return True  # 找到完整匹配
    
    return False