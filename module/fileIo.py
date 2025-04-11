# 本类用于获取data中的数组，所用输入可以调用此类，统一方法

import os
import json
import printLog as log

dataPath = r"data/"

class UserIo:
    def __init__(self):
        self.usersPath = os.path.join(dataPath,r"users/users.json")
        with open(self.usersPath,"r",encoding="utf-8") as f:
            usersData = json.load(f)
        self.users = usersData["users"]
        self.counts = usersData["counts"]

    def getAlluser(self):
        """
        获取所有用户的json文件
        :return: 所有用户的json信息列表
        """
        return self.users
    def getUser(self, userId:int):
        """
        获取指定用户的json文件
        :param userId: 用户id
        :return: 用户的json信息
        """
        
        if userId > self.counts:
            return None
        user = self.users[userId-1]
        return user
    def getCount(self):
        """
        返回用户总数
        """
        return self.counts;
    def addUser(self, user):
        """
        添加用户
        :param user: 用户信息
        """
        user["id"] = self.counts + 1
        self.users.append(user)
        self.counts += 1
        self.__saveUsers()
        log.writeLog(f"添加用户：{user['name']}到文件")
    def __saveUsers(self):
        """
        保存用户信息到文件`
        """
        usersData = {
            "counts": self.counts,
            "users": self.users
        }
        with open(self.usersPath, "w", encoding="utf-8") as f:
            json.dump(usersData, f, ensure_ascii=False, indent=4)
    def deleteUser(self, userId:int):
        """
        删除用户
        :param userId: 用户id
        """
        if userId > self.counts:
            return False
        del self.users[userId-1]
        self.counts -= 1
        self.__saveUsers()
        log.writeLog(f"删除用户：{userId}")
        

def getAllSpotTypes():
    """
    获取所有景点类型的json文件
    :return: 所有景点类型的json信息列表
    """
    spotTypesPath = os.path.join(dataPath, r"config/spot_types.json")
    with open(spotTypesPath, "r", encoding="utf-8") as f:
        spotTypes = json.load(f)
    return spotTypes

class SpotIo:
    def __init__(self):
        self.spotsPath = os.path.join(dataPath,r"scenic_spots/spots.json")
        with open(self.spotsPath,"r",encoding="utf-8") as f:
            spotsData = json.load(f)
        self.spots = spotsData["spots"]
        self.counts = spotsData["counts"]
        
    def getAllSpots(self):
        """
        获取所有景点的json文件
        :return: 所有景点的json信息列表
        """
        return self.spots
    def getSpot(self,spotId:int):
        """
        获取单个景点的参数
        """
        if spotId > self.counts:
            return None
        return self.spots[spotId-1]
    def addScore(self,spotId:int,score:float)->float:
        """
        更新景点的评分
        """
        try:
            spot = self.getSpot(spotId)
            sumScore = float(spot["score"])*spot["score_count"]
            sumScore += score
            spot["score_count"]+=1
            spot["score"] = sumScore / spot["score_count"]

            return spot["score"]
        except:
            return -1.0
    def spotVisited(self,spotId:int)->int:
        """
        当已经景区被访问了，跟新被访问次数
        """
        try:
            spot = self.getSpot(spotId)
            spot["visited_time"]+=1
            return spot["visited_time"]
        except:
            return -1
    def spotReviewsAdd(self,spotId:int)->bool:
        """
        当景区日记增加，加一
        """
        try:
            spot = self.getSpot(spotId)
            spot["reviews"]+=1
            return True
        except:
            return False
    def saveSpots(self):
        """
        保存景点信息到文件
        """
        spotsData = {
            "counts": self.counts,
            "spots": self.spots
        }
        with open(self.spotsPath, "w", encoding="utf-8") as f:
            json.dump(spotsData, f, ensure_ascii=False, indent=4)


        

def __testUserIo():
    userIo = userIo()
    # 获取所有用户的json文件
    userId = 22
    users = userIo.getAlluser()
    print(users[userId])    
    print(userIo.getUser(userId))
    user = {
            "name": "300****165",
            "id": 3465,
            "password": 123456,
            "likes_type": "历史建筑",
            "reviews": [
                [
                    352,
                    8
                ]
            ]
        }
    userIo.addUser(user)
    print(userIo.getCount())
    userIo.deleteUser(userIo.getCount())
    print(userIo.getCount())


def __testSpotIo(spotIo):
    spotIo = spotIo()
    spotId = 100
    spots = spotIo.getAllSpots()
    print(spots[spotId])
    print(spotIo.getSpot(spotId))
    print(spotIo.updateScore(spotId, 4.5))
    print(spotIo.spotVisited(spotId))
    print(spotIo.spotReviewsAdd(spotId))
    spotIo.saveSpots()


    

    
