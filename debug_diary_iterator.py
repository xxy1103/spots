# -*- coding: utf-8 -*-
"""
调试日记迭代器问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from module.user_class import userManager
from module.Spot_class import spotManager

def debug_diary_iteration():
    """
    调试日记迭代器问题
    """
    print("=== 调试日记迭代器 ===")
    
    # 获取用户1的喜好类型
    user = userManager.getUser(1)
    print(f"用户1的喜好类型: {user.likes_type}")
    
    spot_type = user.likes_type[0]  # 获取第一个喜好类型
    print(f"调试景点类型: {spot_type}")
    
    # 获取该类型的景点
    spots_of_type = spotManager.getTopKByType(spot_type, k=5)  # 只获取前5个用于调试
    print(f"该类型的景点数量: {len(spots_of_type)}")
    
    # 检查每个景点的日记
    for i, spot in enumerate(spots_of_type):
        spot_id = spot["id"]
        print(f"\n景点 {i+1}: ID={spot_id}, 名称={spot.get('name', 'N/A')}")
        
        # 检查该景点的日记堆
        diary_heap = spotManager.spotDiaryHeapArray[spot_id-1]
        print(f"  日记堆类型: {type(diary_heap)}")
        
        # 获取日记
        diaries = diary_heap.getTopK(3)  # 获取前3个日记
        print(f"  日记数量: {len(diaries) if diaries else 0}")
        
        if diaries:
            for j, diary in enumerate(diaries):
                print(f"    日记 {j+1}: ID={diary.get('id', 'N/A')}, 评分={diary.get('score', 'N/A')}")
        else:
            print("    没有日记")

def test_diary_iterator():
    """
    测试日记迭代器
    """
    print("\n=== 测试日记迭代器 ===")
    
    from module.data_structure.heap import create_diary_iterator
    
    user = userManager.getUser(1)
    spot_type = user.likes_type[0]
    
    print(f"为类型 '{spot_type}' 创建日记迭代器...")
    
    try:
        diary_iter = create_diary_iterator(spot_type, spotManager)
        print("日记迭代器创建成功")
        
        # 尝试获取前几个日记
        count = 0
        for diary in diary_iter:
            print(f"  日记 {count+1}: ID={diary['id']}, 评分={diary['score']}")
            count += 1
            if count >= 5:  # 只获取前5个
                break
        
        if count == 0:
            print("迭代器没有返回任何日记")
    
    except Exception as e:
        print(f"日记迭代器测试出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_diary_iteration()
    test_diary_iterator()
