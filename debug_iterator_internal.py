# -*- coding: utf-8 -*-
"""
详细调试日记迭代器内部状态
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from module.user_class import userManager
from module.Spot_class import spotManager
from module.data_structure.heap import create_diary_iterator

def debug_iterator_internal():
    """
    调试迭代器内部状态
    """
    print("=== 调试迭代器内部状态 ===")
    
    user = userManager.getUser(1)
    spot_type = user.likes_type[0]
    
    # 创建迭代器
    diary_iter = create_diary_iterator(spot_type, spotManager)
    
    print(f"迭代器创建完成")
    print(f"景点类型: {spot_type}")
    print(f"总景点数: {len(diary_iter.spots_of_type)}")
    print(f"当前景点索引: {diary_iter.current_spot_index}")
    print(f"当前日记列表长度: {len(diary_iter.current_diary_list)}")
    print(f"当前日记索引: {diary_iter.current_diary_index}")
    
    # 如果有日记，打印前几个
    if diary_iter.current_diary_list:
        print(f"前几个日记:")
        for i, diary in enumerate(diary_iter.current_diary_list[:3]):
            print(f"  日记 {i+1}: {diary}")
    else:
        print("当前日记列表为空")
        
        # 手动检查第一个景点的日记
        if diary_iter.spots_of_type:
            first_spot = diary_iter.spots_of_type[0]
            spot_id = first_spot["id"]
            print(f"\n手动检查第一个景点 (ID: {spot_id}) 的日记:")
            
            diary_heap = spotManager.spotDiaryHeapArray[spot_id - 1]
            diaries = diary_heap.getTopK(3)
            print(f"手动获取的日记数量: {len(diaries)}")
            for i, diary in enumerate(diaries):
                print(f"  日记 {i+1}: {diary}")

def test_iterator_manually():
    """
    手动测试迭代器
    """
    print("\n=== 手动测试迭代器 ===")
    
    user = userManager.getUser(1)
    spot_type = user.likes_type[0]
    
    diary_iter = create_diary_iterator(spot_type, spotManager)
    
    print("尝试手动调用 __next__:")
    try:
        first_diary = next(diary_iter)
        print(f"成功获取第一个日记: {first_diary}")
    except StopIteration:
        print("迭代器立即抛出 StopIteration")
    except Exception as e:
        print(f"迭代器出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_iterator_internal()
    test_iterator_manually()
