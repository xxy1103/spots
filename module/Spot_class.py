from module.data_structure.hashtable import HashTable 
from module.fileIo import spotIo, getAllSpotTypes
from module.data_structure.set import IntSet
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
        查找包含指定字符串中每个字符的所有对象ID列表
        :param keys: 要查找的字符串
        :return: 包含该字符串所有字符的对象ID列表的交集
        """
        # 如果关键词为空，返回空列表
        if not keys:
            return []
        
        # 确保关键词非空后获取第一个字符的ID列表
        if len(keys) == 0:
            return []
        first_ids = self.hashTable.search(keys[0])
        result_ids = IntSet(first_ids)
        
        # 遍历关键词中的每个字符
        for char in keys[1:]:
            # 获取包含当前字符的所有ID
            ids = IntSet(self.hashTable.search(char))
            
            # 取交集
            result_ids = result_ids.intersection(ids)
            if result_ids.is_empty():
                break
        
        # 将结果转换为列表并返回
        result = result_ids.get_all_elements()
        if not result:
            print(f"No spots found for the given keys: {keys}")
        return result
    
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

        # 当 k = -1 时，获取该类型所有景点并排序
        if k == -1:
            ids = self.spotTypeDict[spotType].get("ids", [])
            # 获取所有景点的详细信息
            spots_of_type = [self.getSpot(spot_id) for spot_id in ids]
            # 过滤掉可能存在的None值
            spots_of_type = [spot for spot in spots_of_type if spot] 
            
            # 按评分（降序）和访问次数（降序）排序
            # 使用 .get() 提供默认值以增加健壮性
            sorted_spots = sorted(
                spots_of_type, 
                key=lambda spot: (float(spot.get('score', 0.0)), int(spot.get('visited_time', 0))), 
                reverse=True # 降序排序
            )
            writeLog(f"获取 '{spotType}' 类型的所有景点并排序完成")
            return sorted_spots

        # --- 处理 k > 0 的现有逻辑 ---
        # 确保 "top_10" 键存在，如果不存在则初始化为空列表
        if "top_10" not in self.spotTypeDict[spotType]:
            self.spotTypeDict[spotType]["top_10"] = []
            
        # 如果缓存的 top_10 列表为空，或者请求的 k 与缓存的大小不同
        if not self.spotTypeDict[spotType]["top_10"] or len(self.spotTypeDict[spotType]["top_10"]) != k:
            # 确保 "heap" 键存在并且是一个 TopKHeap 实例
            heap_instance = self.spotTypeDict[spotType].get("heap")
            if heap_instance and isinstance(heap_instance, TopKHeap):
                 # 从堆中获取 Top K 结果并更新缓存
                 self.spotTypeDict[spotType]["top_10"] = heap_instance.getTopK(k)
            else:
                 # 如果堆不存在或类型不正确，记录错误并清空缓存
                 writeLog(f"错误：类型 '{spotType}' 的堆未正确初始化。")
                 self.spotTypeDict[spotType]["top_10"] = []
            
        writeLog(f"获取 '{spotType}' 类型的前{k}个景点完成")
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
        sorted_spots = quicksort(spots_to_sort)
        writeLog("获取所有景点并完成排序")
        return sorted_spots


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