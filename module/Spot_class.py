from data_structure.hashtable import HashTable 
from fileIo import SpotIo, getAllSpotTypes
from data_structure.set import IntSet
from data_structure.indexHeap import TopKHeap
from printLog import writeLog
import json


class Spot:
    """
    Spot类用于表示景点系统，包含景点查询、分类、排序等功能
    """
    def __init__(self, spotIo):
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
        self.classify()
    
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
    
    def classify(self):
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
        
    def getTopKForEachType(self, k=10):
        """
        为每个景点类型获取前K个评分最高的景点ID
        """
        for spotType in self.spotTypeDict:
            topK = self.spotTypeDict[spotType]["heap"].getTopK(k)
            self.spotTypeDict[spotType]["top_10"] = topK
        writeLog("获取每个类型的前K个景点完成")
        return self.spotTypeDict
    
    def getTopKByType(self, spotType, k=10):
        """
        获取特定类型景点的前K个评分最高的景点
        
        :param spotType: 景点类型
        :param k: 需要获取的景点数量，默认为10
        :return: 指定类型的前K个景点ID列表，如果类型不存在则返回空列表
        """
        if spotType not in self.spotTypeDict:
            writeLog(f"找不到类型为 '{spotType}' 的景点")
            return []
        
        # 如果top_10列表为空，则重新获取
        if not self.spotTypeDict[spotType]["top_10"]:
            self.spotTypeDict[spotType]["top_10"] = self.spotTypeDict[spotType]["heap"].getTopK(k)
            
        # 如果需要的k与已有的不同，则重新获取
        elif len(self.spotTypeDict[spotType]["top_10"]) != k:
            self.spotTypeDict[spotType]["top_10"] = self.spotTypeDict[spotType]["heap"].getTopK(k)
            
        writeLog(f"获取 '{spotType}' 类型的前{k}个景点完成")
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

if __name__ == "__main__":
    spotIo = SpotIo()
    spot = Spot(spotIo=spotIo)
    # 获取每个类型前10个景点并保存索引
    t = spot.getTopKForEachType(10)
    print(t)
    # 获取"自然风光"类型的前10个评分最高的景点
    a = natural_spots = spot.getTopKByType("历史建筑")
    print(a)

    # 获取"历史古迹"类型的前5个评分最高的景点
    b = historical_spots = spot.getTopKByType("历史古迹", 5)
    print(b)