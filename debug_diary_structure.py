# -*- coding: utf-8 -*-
"""
进一步调试日记数据结构
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from module.user_class import userManager
from module.Spot_class import spotManager

def debug_diary_data_structure():
    """
    调试日记数据结构
    """
    print("=== 调试日记数据结构 ===")
    
    user = userManager.getUser(1)
    spot_type = user.likes_type[0]
    
    # 获取该类型的第一个景点
    spots_of_type = spotManager.getTopKByType(spot_type, k=1)
    spot = spots_of_type[0]
    spot_id = spot["id"]
    
    print(f"景点ID: {spot_id}")
    
    # 获取该景点的日记堆
    diary_heap = spotManager.spotDiaryHeapArray[spot_id-1]
    print(f"日记堆类型: {type(diary_heap)}")
    print(f"日记堆大小: {diary_heap.size()}")
    
    # 获取日记详细信息
    diaries = diary_heap.getTopK(5)
    print(f"获取到 {len(diaries)} 个日记")
    
    for i, diary in enumerate(diaries):
        print(f"\n日记 {i+1}:")
        print(f"  完整数据: {diary}")
        for key, value in diary.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    debug_diary_data_structure()
