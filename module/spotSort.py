from fileIo import spotIo, getAllSpotTypes
from indexHeap import TopKHeap
from printLog import writeLog
from printLog import writeLog
import json

class SpotSort:
    def __init__(self,spotsio:spotIo,spotType):
        self.spotsio = spotsio 
        self.spots = spotsio.getAllSpots()  #引用相等
        spotTypes = spotType
        self.spotTypeDict = {}
        for i in range(len(spotTypes)):
            self.spotTypeDict[spotTypes[i]] = {
                "ids": [], 
                "top_10": [],
                "heap": TopKHeap()  # 为每个类型创建单独的TopKHeap
            }
        
    def classify(self):
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
        writeLog("分类完成")
        
    def getTopKForEachType(self, k=10):
        """为每个景点类型获取前K个评分最高的景点ID"""
        for spotType in self.spotTypeDict:
            topK = self.spotTypeDict[spotType]["heap"].getTopK(k)
            self.spotTypeDict[spotType]["top_10"] = topK
        writeLog("获取每个类型的前K个景点完成")
        return self.spotTypeDict
    def addScore(self,spotId,score):
        newScore =  self.spotsio.addScore(spotId,score)
        type = self.spotsio.getSpot(spotId)["type"]
        # 更新对应类型的堆
        self.spotTypeDict[type]["heap"].updateScore(spotId, newScore)
        writeLog(f"更新景点{spotId}的评分为{newScore}")
        return newScore
    def addVisitedTime(self,spotId):
        newVisitedTime =  self.spotsio.spotVisited(spotId)
        type = self.spotsio.getSpot(spotId)["type"]
        # 更新对应类型的堆
        self.spotTypeDict[type]["heap"].updateVisitedTime(spotId, newVisitedTime)
        writeLog(f"更新景点{spotId}的访问次数为{newVisitedTime}")
        return newVisitedTime

if __name__ == "__main__":
    spoyio = spotIo() 
    SportSort = SpotSort(spotsio=spoyio, spotType=getAllSpotTypes())
    SportSort.classify()
    res = SportSort.getTopKForEachType(10)
    save_data = {}
    for type_name in res:
        save_data[type_name] = {
            "ids": res[type_name]["ids"],  # 使用:而不是=
            "top_10": res[type_name]["top_10"]  # 使用:而不是=
        }
    with open("index/global/type_index.json", "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=4)

