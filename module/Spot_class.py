from module.data_structure.hashtable import HashTable
from module.fileIo import spotIo, configIo
from module.data_structure.indexHeap import TopKHeap
from module.printLog import writeLog
from module.data_structure.quicksort import quicksort
from module.data_structure.merge import merge_sort
from module.Model.Model import Diary, User, Reviews, Spot
from module.data_structure.kwaymerge import k_way_merge_descending
from module.diary_class import diaryManager
# 导入自定义 Set 类
from module.data_structure.set import MySet
import json


class SpotManager:
    """
    Spot类用于表示景点系统，包含景点查询、分类、排序等功能
    """
    def __init__(self, spots_data=None, counts_data=None, hashTable_data=None, spotTypeDict_data=None, spotDiaryHeapArray_data=None):

        self.spots = spots_data  # List of Spot objects
        self.counts = counts_data
        self.hashTable = hashTable_data  # Built by from_dict
        self.spotTypeDict = spotTypeDict_data  # Heaps are initially empty from from_dict
        self.spotDiaryHeapArray = spotDiaryHeapArray_data  # Built by from_dict

        # Populate heaps in self.spotTypeDict using self.spots (which are Spot objects)
        for spot_obj in self.spots:
            spot_type = spot_obj.type
            self.spotTypeDict[spot_type]["heap"].insert(spot_obj.id, spot_obj.score, spot_obj.visited_time)
        writeLog("景点分类完成 (from_dict path)")

    
    @classmethod
    def from_dict(cls, data: dict): # data is from spotIo.load_spots()
        counts = data["counts"]
        spots_json_list = data["spots"] # list of spot dicts from JSON
        
        sdk_spots = []
        for spot_json_item in spots_json_list:
            spot_obj = Spot.from_dict(spot_json_item)
            sdk_spots.append(spot_obj)
        
        hash_table_size = max(1000, counts * 2)
        sdk_hash_table = HashTable(hash_table_size)
        for spot_obj in sdk_spots:
            item = {"id": spot_obj.id, "name": spot_obj.name,"value1":spot_obj.score,"value2":spot_obj.visited_time} # As per original from_dict logic
            sdk_hash_table.insert(item)
        
        spotTypes_list = configIo.getAllSpotTypes()
        sdk_spotTypeDict = {}
        for spotType_name in spotTypes_list:
            sdk_spotTypeDict[spotType_name] = {
                "heap": TopKHeap() # Heaps will be populated in __init__
            }
        
        sdk_spotDiaryHeapArray = [TopKHeap() for _ in range(counts)]
        for spot_obj in sdk_spots:
            diary_ids_list = spot_obj.reviews.getDiaryIds()
            for diary_id_val in diary_ids_list:
                diary_data = diaryManager.getDiary(diary_id_val)
                if diary_data:
                    sdk_spotDiaryHeapArray[spot_obj.id - 1].insert(diary_data.id, diary_data.score, diary_data.visited_time)

        return cls( 
            spots_data=sdk_spots,
            counts_data=counts,
            hashTable_data=sdk_hash_table,
            spotTypeDict_data=sdk_spotTypeDict,
            spotDiaryHeapArray_data=sdk_spotDiaryHeapArray
        )


    def getSpot(self, spotId):
        """
        获取单个景点的参数
        """
        if spotId < 1 or spotId > self.counts:
            return None
        return self.spots[spotId - 1]
    
    def getSpotByName(self, keys:str)->list:
        """
        查找名称包含指定字符串中每个字符的所有景点对象列表
        :param keys: 要查找的字符串 (例如 "故宫")
        :return: 包含指定字符串中每个字符的所有景点对象列表
        """
        # 如果关键词为空，直接返回空列表
        if not keys:
            return []

        # 获取第一个字符匹配的景点
        first_char_spots = self.hashTable.search(keys[0])
        if not first_char_spots:
            # 如果第一个字符就没有匹配项，则不可能有交集
            return []

        # 使用第一个字符的结果初始化结果 ID 集合 (使用 MySet)
        result_ids = MySet(spot for spot in first_char_spots)

        # 遍历关键词中的剩余字符
        for char in keys[1:]:
            # 获取包含当前字符的所有景点
            current_char_spots = self.hashTable.search(char)
            if not current_char_spots:
                # 如果任何一个后续字符没有匹配项，则交集为空
                return []

            # 创建当前字符的景点 ID 集合 (使用 MySet)
            current_ids = MySet(spot for spot in current_char_spots)

            # 计算与当前结果集的交集 (使用 MySet 的 intersection_update)
            result_ids.intersection_update(current_ids)

            # 如果交集为空，提前结束 (使用 is_empty 方法)
            if result_ids.is_empty():
                return []

        # 根据最终的 ID 集合获取景点对象列表
        # 使用 self.spots 列表直接访问，假设 ID 是从 1 开始且连续的
        # 迭代 MySet


        return result_ids.to_list()  # 返回包含指定字符串中每个字符的所有景点字典


    def getTopKByType(self, spotType, k=10):
        """
        获取特定类型景点的前K个评分最高的景点, 或当k=-1时获取所有排序后的景点
        
        :param spotType: 景点类型
        :param k: 需要获取的景点数量，默认为10。如果k=-1，则返回该类型所有排序后的景点。
        :return: 指定类型的前K个景点列表，或所有排序后的景点列表，如果类型不存在则返回空列表
        """
        if spotType not in self.spotTypeDict:
            writeLog(f"找不到类型为 '{spotType}' 的景点")
            return []

        # --- 统一使用堆实例 ---
        heap_instance = self.spotTypeDict[spotType].get("heap")

       
        if k == -1:     # 获取所有排序后的景点
            length = heap_instance.size()
        else:           # 获取前K个景点
            length = min(k, heap_instance.size())
        all_sorted_spots = heap_instance.getTopK(length)
        writeLog(f"使用堆获取 '{spotType}' 类型的{length}个景点并排序完成")



        return all_sorted_spots  


    def updateScore(self, spotId:int,  newScore:float)->float:
        """
        为指定景点添加评分
        """
        # newScore = self.spotIo.updateScore(spotId, newScore, oldScore)
        # if newScore < 0:
        #     writeLog(f"更新景点{spotId}评分失败")
        #     return -1
        
        # #self.spotIo.spotReviewsAdd(spotId, diaryId)
        # type = self.spotIo.getSpot(spotId)["type"]
        # # 更新对应类型的堆
        # self.spotTypeDict[type]["heap"].updateScore(spotId, newScore)
        # writeLog(f"更新景点{spotId}的评分为{newScore}")
        # return newScore
        spot = self.getSpot(spotId)
        if spot is None:
            writeLog(f"景点{spotId}不存在")
            return -1
        # 更新评分
        # 更新索引堆
        type = spot.type
        if self.spotTypeDict[type]["heap"].updateValue1(spotId, newScore):
            writeLog(f"更新景点{spotId}的评分为{newScore}")
            return newScore
        else:
            writeLog(f"更新景点{spotId}的评分失败")
            return -1

    def addVisitedTime(self, spotId):
        """
        增加指定景点的访问次数
        """

        spot = self.getSpot(spotId)
        if spot is None:
            writeLog(f"景点{spotId}不存在")
            return -1
        # 增加访问次数
        spot.visited()
        # 更新索引堆
        type = spot.type
        if self.spotTypeDict[type]["heap"].updateValue2(spotId, spot.visited_time): 
            writeLog(f"增加景点{spotId}的访问次数为{spot.visited_time}")
            return spot.visited_time
        else:
            writeLog(f"增加景点{spotId}的访问次数失败")
            return -1

    def getAllSpotsSorted(self):
        """
        获取所有景点，并按评分和访问次数进行归并排序（降序）。
        通过迭代所有类型，获取每个类型的排序列表，然后逐步归并。
        :return: 排序后的景点列表
        """

        all_lists = []
        for spot_type in self.spotTypeDict.keys():
            # 获取该类型下所有已排序的景点 (k=-1)
            spots_of_type = self.getTopKByType(spot_type, k=-1)
            if spots_of_type:  # 确保列表非空
                all_lists.append(spots_of_type)

        # 使用 k-way merge 进行归并排序
        sorted_spots = k_way_merge_descending(all_lists)
        writeLog("通过逐类型归并获取所有景点并完成排序")
        # 将排序后的景点转换为对象
      
        return sorted_spots # 返回字典


    def getAllSortedByVisitedTime(self):
        """
        获取所有景点，并按访问次数进行归并排序（降序）
        :return: 排序后的景点列表
        """
        # 对 self.spots 的副本进行排序，以避免修改原始列表
        
        spots_to_sort = []
        for spot in self.spots:
            spots_to_sort.append({
                "id": spot.id,
                "value1": spot.score,
                "value2": spot.visited_time
            })

        sorted_spots = quicksort(spots_to_sort, sort_key="value2")
        writeLog("获取所有景点并完成排序")

        return sorted_spots # 返回字典



spotManager = SpotManager.from_dict(spotIo.load_spots())

def test_Spot(SpotManagerInstance): # Changed argument name for clarity
    # spot = SpotManagerInstance # Use the passed instance
    # The test function seems to create its own instance, which might be intended for isolated testing.
    # For now, let's assume it wants to use the global spotManager or a fresh one.
    # If it's meant to test the global one, it should just use `spotManager`.
    # If it's meant to test `from_dict` again, it's redundant with the global one.
    # Let's assume it's for testing methods on an existing manager.
    spot = spotManager # Use the globally initialized one for the test.
    
    # getTopKForEachType is not defined in the provided code. Commenting out.
    # t = spot.getTopKForEachType(10) 
    # print(t)
    # 获取"自然风光"类型的前10个评分最高的景点
    a = natural_spots = spot.getTopKByType("历史建筑")
    print(a)

    # 获取"历史古迹"类型的前5个评分最高的景点
    b = historical_spots = spot.getTopKByType("历史古迹", 5)
    print(b)

    # 获取所有景点并排序
    all_sorted = spot.getAllSpotsSorted()
    print("\nAll spots sorted by score and visited time:")
    # 打印前几个看看效果
    for s in all_sorted[:5]: 
        print(f"ID: {s['id']}, Score: {s['value1']}, Visited: {s['value2']}")

if __name__ == "__main__":
    test_Spot(spotManager) # Pass the global instance