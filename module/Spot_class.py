from module.data_structure.hashtable import HashTable
from module.fileIo import spotIo, configIo
from module.data_structure.indexHeap import TopKHeap
from module.printLog import writeLog
from module.data_structure.quicksort import quicksort
from module.data_structure.merge import merge_sort
from module.diary_class import diaryManager
# 导入自定义 Set 类
from module.data_structure.set import MySet
import json


class Spot:
    """
    Spot类用于表示景点系统，包含景点查询、分类、排序等功能
    """
    def __init__(self):
        self.spotIo = spotIo
        self.spots = spotIo.getAllSpots()
        self.counts = spotIo.counts
        
        # 初始化哈希表，用于按名称检索景点
        hash_table_size = max(1000, self.counts * 2)
        self.hashTable = HashTable(hash_table_size)
        for spot in self.spots:
            self.hashTable.insert(spot)
        
        # 初始化景点分类字典
        spotTypes = configIo.getAllSpotTypes()
        self.spotTypeDict = {}
        for i in range(len(spotTypes)):
            self.spotTypeDict[spotTypes[i]] = {
                "heap": TopKHeap()  # 为每个类型创建单独的TopKHeap
            }

        self.spotDiaryHeapArray = [TopKHeap() for _ in range(self.counts)]
        # 初始化索引堆
        for spot in self.spots:
            diarys = spot["reviews"]["diary_ids"]
            for diary_id in diarys:
                diary = diaryManager.getDiary(diary_id)
                if diary:
                    self.spotDiaryHeapArray[spot["id"] - 1].insert(diary["id"], diary["score"], diary["visited_time"])

        # 对景点进行分类
        self._classify()
        writeLog("景点分类完成")
    
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
        :return: 包含名称中所有字符的景点对象列表 (字典)
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
        result_ids = MySet(spot['id'] for spot in first_char_spots)

        # 遍历关键词中的剩余字符
        for char in keys[1:]:
            # 获取包含当前字符的所有景点
            current_char_spots = self.hashTable.search(char)
            if not current_char_spots:
                # 如果任何一个后续字符没有匹配项，则交集为空
                return []

            # 创建当前字符的景点 ID 集合 (使用 MySet)
            current_ids = MySet(spot['id'] for spot in current_char_spots)

            # 计算与当前结果集的交集 (使用 MySet 的 intersection_update)
            result_ids.intersection_update(current_ids)

            # 如果交集为空，提前结束 (使用 is_empty 方法)
            if result_ids.is_empty():
                return []

        # 根据最终的 ID 集合获取景点对象列表
        # 使用 self.spots 列表直接访问，假设 ID 是从 1 开始且连续的
        # 迭代 MySet
        result_list = [self.spots[spot_id - 1] for spot_id in result_ids if 1 <= spot_id <= self.counts]

        return result_list

    def _classify(self):
        """
        对景点按类型进行分类
        """
        for i in range(len(self.spots)):
            spot = self.spots[i]
            spotType = spot["type"]
            if spotType not in self.spotTypeDict:
                self.spotTypeDict[spotType] = {
                    "heap": TopKHeap()  # 如果是新类型，也创建堆
                }
            # 添加到对应类型的堆中
            self.spotTypeDict[spotType]["heap"].insert(spot["id"], spot["score"], spot["visited_time"])
        writeLog("景点分类完成")
    
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
        if not heap_instance or not isinstance(heap_instance, TopKHeap):
            writeLog(f"错误：类型 '{spotType}' 的堆未正确初始化。")
            # 如果堆不存在或类型不正确，清空缓存并返回空列表
            return []


        # 从堆中获取所有元素（传入堆的大小作为k）
        if k == -1:
            length = heap_instance.size()
        else:
            length = min(k, heap_instance.size())
        all_sorted_spots = heap_instance.getTopK(length)
        writeLog(f"使用堆获取 '{spotType}' 类型的{length}个景点并排序完成")
        return all_sorted_spots


    def updateScore(self, spotId:int,  newScore:float, oldScore:float = 0)->float:
        """
        为指定景点添加评分
        """
        newScore = self.spotIo.updateScore(spotId, newScore, oldScore)
        if newScore < 0:
            writeLog(f"更新景点{spotId}评分失败")
            return -1
        
        #self.spotIo.spotReviewsAdd(spotId, diaryId)
        type = self.spotIo.getSpot(spotId)["type"]
        # 更新对应类型的堆
        self.spotTypeDict[type]["heap"].updateScore(spotId, newScore)
        writeLog(f"更新景点{spotId}的评分为{newScore}")
        return newScore
    
    def addVisitedTime(self, spotId):
        """
        增加指定景点的访问次数
        """
        newVisitedTime = self.spotIo.spotVisited(spotId)
        type = self.spotIo.getSpot(spotId)["type"]
        # 更新对应类型的堆
        self.spotTypeDict[type]["heap"].updateVisitedTime(spotId, newVisitedTime)
        writeLog(f"更新景点{spotId}的访问次数为{newVisitedTime}")
        return newVisitedTime
        
    def getAllSpotsSorted(self):
        """
        获取所有景点，并按评分和访问次数进行归并排序（降序）。
        通过迭代所有类型，获取每个类型的排序列表，然后逐步归并。
        :return: 排序后的景点列表
        """
        total_sorted_list = []
        # 遍历所有景点类型
        for spot_type in self.spotTypeDict.keys():
            # 获取该类型下所有已排序的景点 (k=-1)
            spots_of_type = self.getTopKByType(spot_type, k=-1)
            if spots_of_type: # 确保列表非空
                # 将当前类型的有序列表与总列表进行归并排序
                total_sorted_list = merge_sort(total_sorted_list, spots_of_type)
        
        writeLog("通过逐类型归并获取所有景点并完成排序")
        return total_sorted_list

    def getAllSortedByVisitedTime(self):
        """
        获取所有景点，并按访问次数进行归并排序（降序）
        :return: 排序后的景点列表
        """
        # 对 self.spots 的副本进行排序，以避免修改原始列表
        spots_to_sort = list(self.spots) 
        sorted_spots = quicksort(spots_to_sort, sort_key="visited_time")
        writeLog("获取所有景点并完成排序")
        return sorted_spots
    
    def saveSpots(self):
        """
        保存景点信息到文件
        """
        self.spotIo.saveSpots()
        writeLog("景点信息已保存")

spotManager = Spot()

if __name__ == "__main__":
    spot = Spot()
    # 获取每个类型前10个景点并保存索引
    t = spot.getTopKForEachType(10)
    print(t)
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
        print(f"ID: {s['id']}, Name: {s['name']}, Score: {s['score']}, Visited: {s['visited_time']}")