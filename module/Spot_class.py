from module.data_structure.hashtable import HashTable 
from module.fileIo import spotIo, getAllSpotTypes
from module.data_structure.set import ItemSet
from module.data_structure.indexHeap import TopKHeap
from module.printLog import writeLog
from module.data_structure.quicksort import quicksort
from module.data_structure.merge import merge_sort
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
        spotTypes = getAllSpotTypes()
        self.spotTypeDict = {}
        for i in range(len(spotTypes)):
            self.spotTypeDict[spotTypes[i]] = {
                "ids": [], 
                "top_10": [],
                "heap": TopKHeap()  # 为每个类型创建单独的TopKHeap
            }
        
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
            # print(f"No spots found containing the character: {keys[0]}") # 可以取消注释以进行调试
            return []

        # 使用第一个字符的结果初始化结果集合
        result_set = ItemSet(first_char_spots)

        # 遍历关键词中的剩余字符
        for char in keys[1:]:
            # 获取包含当前字符的所有景点
            current_char_spots = self.hashTable.search(char)
            if not current_char_spots:
                # 如果任何一个后续字符没有匹配项，则交集为空
                # print(f"No spots found containing the character: {char}") # 可以取消注释以进行调试
                return []

            # 创建当前字符的景点集合
            current_set = ItemSet(current_char_spots)

            # 计算与当前结果集的交集
            result_set = result_set.intersection(current_set)

            # 如果交集为空，提前结束
            if result_set.is_empty():
                # print(f"No spots found containing all characters from: {keys}") # 可以取消注释以进行调试
                return []

        # 将最终集合中的元素转换为列表并返回
        result_list = result_set.get_all_elements()
        # if not result_list: # 再次检查，虽然理论上不会到这里如果上面判断了 is_empty
        #      print(f"No spots found containing all characters from: {keys}") # 可以取消注释以进行调试

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
                    "ids": [], 
                    "top_10": [],
                    "heap": TopKHeap()  # 如果是新类型，也创建堆
                }
            self.spotTypeDict[spotType]["ids"].append(spot["id"])
            # 添加到对应类型的堆中
            self.spotTypeDict[spotType]["heap"].insert(spot["id"], spot["score"], spot["visited_time"])
        writeLog("景点分类完成")
    #    感觉没什么用，所以注释掉了
    # def getTopKForEachType(self, k=10):
    #     """
    #     为每个景点类型获取前K个评分最高的景点ID
    #     """
    #     for spotType in self.spotTypeDict:
    #         topK = self.spotTypeDict[spotType]["heap"].getTopK(k)
    #         self.spotTypeDict[spotType]["top_10"] = topK
    #     writeLog("获取每个类型的前K个景点完成")
    #     return self.spotTypeDict
    
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
            self.spotTypeDict[spotType]["top_10"] = [] 
            return []

        # 当 k = -1 时，获取该类型所有景点并排序
        if k == -1:
            # 从堆中获取所有元素（传入堆的大小作为k）
            all_sorted_spots = heap_instance.getTopK(heap_instance.size())
            writeLog(f"使用堆获取 '{spotType}' 类型的所有景点并排序完成")
            return all_sorted_spots

        # --- 处理 k > 0 的现有逻辑 (使用缓存) ---
        # 确保 "top_10" 键存在，如果不存在则初始化为空列表
        if "top_10" not in self.spotTypeDict[spotType]:
            self.spotTypeDict[spotType]["top_10"] = []
            
        # 如果缓存的 top_10 列表为空，或者请求的 k 与缓存的大小不同
        cached_top_k = self.spotTypeDict[spotType]["top_10"]
        if not cached_top_k or len(cached_top_k) != k:
             # 从堆中获取 Top K 结果并更新缓存
             self.spotTypeDict[spotType]["top_10"] = heap_instance.getTopK(k)
             writeLog(f"从堆获取并缓存 '{spotType}' 类型的前{k}个景点")
        else:
             writeLog(f"从缓存获取 '{spotType}' 类型的前{k}个景点")
            
        # 返回缓存的 Top K 列表
        return self.spotTypeDict[spotType]["top_10"]
    
    def addScore(self, spotId, score):
        """
        为指定景点添加评分
        """
        newScore = self.spotIo.addScore(spotId, score)
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
        
    def saveTypeIndex(self, filepath="index/global/type_index.json"):
        """
        将景点分类结果保存到JSON文件中
        """
        save_data = {}
        for type_name in self.spotTypeDict:
            save_data[type_name] = {
                "ids": self.spotTypeDict[type_name]["ids"],
                "top_10": self.spotTypeDict[type_name]["top_10"]
            }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=4)
        writeLog(f"景点分类索引已保存至{filepath}")

    def getAllSpotsSorted(self):
        """
        获取所有景点，并按评分和访问次数进行归并排序（降序）
        :return: 排序后的景点列表
        """
        # 对 self.spots 的副本进行排序，以避免修改原始列表
        spots_to_sort = list(self.spots) 
        # --- Use the imported merge_sort function ---
        sorted_spots = merge_sort(spots_to_sort) 
        writeLog("获取所有景点并完成排序")
        return sorted_spots

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