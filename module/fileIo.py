# 本类用于获取data中的数组，所用输入可以调用此类，统一方法

import os
import json
import datetime
import module.printLog as log

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
        log.writeLog(f"添加用户：{user['name']}到文件")
        # 为便于测试，不需要实际保存，先注释掉save的调用
        # self.saveUsers()
        return user["id"]
    def saveUsers(self):
        """
        保存用户信息到文件`
        """
        usersData = {
            "counts": self.counts,
            "users": self.users
        }
        with open(self.usersPath, "w", encoding="utf-8") as f:
            json.dump(usersData, f, ensure_ascii=False, indent=4)
    # 尚未设计注销功能，先不用理会
    def deleteUser(self, userId:int):
        """
        删除用户
        :param userId: 用户id
        """
        if userId > self.counts:
            return False
        del self.users[userId-1]
        self.counts -= 1
        log.writeLog(f"删除用户：{userId}")

class ConfigIo:
    def __init__(self):
        self.configPath = os.path.join(dataPath, r"config/config.json")
        
    def getAllSpotTypes(self):
        """
        获取所有景点类型的json文件
        :return: 所有景点类型的json信息列表
        """
        with open(self.configPath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["spot_types"]
    def getAllPoiTypes(self):
        """
        获取所有兴趣点类型的json文件
        :return: 所有兴趣点类型的json信息列表
        """
        with open(self.configPath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["POI_types"]

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
    def updateScore(self,spotId:int,newScore:float,oldScore:float = 0)->float:
        """
        更新景点的评分
        """
        try:
            spot = self.getSpot(spotId)
            sumScore = float(spot["score"])*spot["score_count"]
            sumScore += newScore - oldScore
            if oldScore != 0:
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

    # Add和Decrease方法主要是保持评论数增减的一致性，
    # 这样在SpotIo和DiaryIo中都有增减评论数的代码，避免出现“ouch，我是不是少了更新评论数的代码”的情况出现。
    def spotReviewsAdd(self, spotId:int, save_immediately=False)->bool:
        """
        当景区添加新日记时，增加景点的评论数量
    
        Args:
            spotId: 景点ID
            save_immediately: 是否立即保存到文件，默认为False
        
        Returns:
            bool: 更新成功返回True，失败返回False
        """
        try:
            spot = self.getSpot(spotId)
            if not spot:
                log.writeLog(f"景点 {spotId} 不存在，无法更新评论数")
                return False

            if "reviews" not in spot:
                spot["reviews"] = 0

            spot["reviews"] += 1
            
            # 只在需要时保存
            if save_immediately:
                self.saveSpots()
                
            log.writeLog(f"景点 {spotId} 的评论数更新为 {spot['reviews']}")
            return True
        except Exception as e:
            log.writeLog(f"更新景点 {spotId} 评论数失败: {str(e)}")
            return False

    def spotReviewsDecrease(self, spotId:int, save_immediately=False)->bool:
        """
        当景区删除日记时，减少景点的评论数量
    
        Args:
            spotId: 景点ID
            save_immediately: 是否立即保存到文件，默认为False
    
        Returns:
            bool: 更新成功返回True，失败返回False
        """
        try:
            spot = self.getSpot(spotId)
            if not spot:
                log.writeLog(f"景点 {spotId} 不存在，无法更新评论数")
                return False

            if "reviews" not in spot:
                spot["reviews"] = 0
                log.writeLog(f"景点 {spotId} 没有评论字段，已初始化为0")
                return True

            # 确保评论数不会小于0
            if spot["reviews"] > 0:
                spot["reviews"] -= 1
            
            # 只在需要时保存
            if save_immediately:
                self.saveSpots()
                
            log.writeLog(f"景点 {spotId} 的评论数更新为 {spot['reviews']}")
            return True
        except Exception as e:
            log.writeLog(f"更新景点 {spotId} 评论数失败: {str(e)}")
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


class DiaryIo:
    def __init__(self):
        """初始化日记IO类"""
        self.spotIo = spotIo
        self.userIo = userIo
        
        # 集中存储路径
        self.diaries_path = os.path.join(dataPath, "diaries", "diaries.json")
        self.reviews_base_path = os.path.join(dataPath, "diaries", "reviews")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.diaries_path), exist_ok=True)
        os.makedirs(self.reviews_base_path, exist_ok=True)
        
        # 加载日记数据
        self.diaries = []
        self.diary_count = 0
        self._loadDiaries()
        
        log.writeLog("日记IO系统初始化完成")
    
    def _loadDiaries(self):
        """从diaries.json加载所有日记数据"""
        if os.path.exists(self.diaries_path):
            try:
                with open(self.diaries_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.diaries = data.get("diaries", [])
                    self.diary_count = data.get("counts", len(self.diaries))
                log.writeLog(f"已加载 {self.diary_count} 条日记")
            except Exception as e:
                log.writeLog(f"加载日记文件失败: {str(e)}")
                self.diaries = []
                self.diary_count = 0
        else:
            # 文件不存在，创建空数据
            self.diaries = []
            self.diary_count = 0
            self._saveDiaries()
            log.writeLog("已创建新的日记数据文件")
    
    def _saveDiaries(self):
        """保存日记数据到文件"""
        try:
            data = {
                "counts": self.diary_count,
                "diaries": self.diaries
            }
            with open(self.diaries_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            log.writeLog(f"已保存 {self.diary_count} 条日记到文件")
            return True
        except Exception as e:
            log.writeLog(f"保存日记文件失败: {str(e)}")
            return False
    
    def _getDiaryImagePath(self, diary_id):
        """获取日记图片存储路径"""
        return os.path.join(self.reviews_base_path, f"diary_{diary_id}", "images")
    
    def getAllDiaries(self):
        """获取所有日记"""
        return self.diaries
    
    def getDiary(self, diary_id):
        """获取单个日记"""
        for diary in self.diaries:
            if diary["id"] == diary_id:
                return diary
        return None
    
    def getSpotDiaries(self, spot_id):
        """获取指定景点的所有日记"""
        return [diary for diary in self.diaries if diary["spot_id"] == spot_id]
    
    def getUserDiaries(self, user_id):
        """获取指定用户的所有日记"""
        return [diary for diary in self.diaries if diary["user_id"] == user_id]
    
    def addDiary(self, user_id, spot_id, title, content, images=None):
        """添加新日记"""
        if images is None:
            images = []
            
        # 检查景点是否存在
        spot = self.spotIo.getSpot(spot_id)
        if not spot:
            log.writeLog(f"景点 {spot_id} 不存在，无法添加日记")
            return -1
        
        # 检查用户是否存在
        user = self.userIo.getUser(user_id)
        if not user:
            log.writeLog(f"用户 {user_id} 不存在，无法添加日记")
            return -1
        
        # 创建新日记
        diary_id = self.diary_count
        new_diary = {
            "id": diary_id,
            "name": user.get("name", ""),
            "user_id": user_id,
            "spot_id": spot_id,
            "content": content,
            "title": title,
            "time": datetime.datetime.now().strftime("%Y-%m-%d"),
            "score": 0,
            "score_count": 0,
            "visited_time": 0,
            "img_list": []
        }
        
        # 处理图片
        if images:
            # 创建图片目录
            img_dir = self._getDiaryImagePath(diary_id)
            os.makedirs(img_dir, exist_ok=True)
            
            # 保存图片路径
            for i, img_data in enumerate(images):
                img_path = os.path.join(img_dir, f"{diary_id}_{i}.jpg")
                new_diary["img_list"].append(img_path)
                # 实际的图片保存由前端处理
        
        # 添加到日记列表
        self.diaries.append(new_diary)
        self.diary_count += 1
        
        # 保存到文件
        if self._saveDiaries():
            # 更新景点评论数，不立即保存
            self.spotIo.spotReviewsAdd(spot_id, save_immediately=False)
            
            # 更新用户评论记录 - 修改这里的存储格式
            if "reviews" not in user:
                # 创建新的结构
                user["reviews"] = {
                    "total": 1,
                    "diary_ids": [diary_id]
                }
            else:
                # 直接增加
                user["reviews"]["total"] += 1
                user["reviews"]["diary_ids"].append(diary_id)
            
            # 最后，手动保存所有更改
            self.spotIo.saveSpots()  # 保存景点数据
            self.userIo.saveUsers()  # 保存用户数据
            
            log.writeLog(f"用户 {user_id} 为景点 {spot_id} 添加日记 {diary_id}，总日记数: {user['reviews']['total']}")
            return diary_id
        
        return -1

    def deleteDiary(self, user_id, diary_id):
        """删除日记"""
        # 检查用户是否存在
        user = self.userIo.getUser(user_id)
        if not user:
            log.writeLog(f"用户 {user_id} 不存在，无法删除日记")
            return False
        
        # 查找日记
        diary_index = -1
        target_diary = None
        for i, diary in enumerate(self.diaries):
            if diary["id"] == diary_id:
                diary_index = i
                target_diary = diary
                break
        
        if diary_index == -1:
            log.writeLog(f"日记 {diary_id} 不存在，无法删除")
            return False
        
        # 检查用户权限
        if target_diary["user_id"] != user_id:
            log.writeLog(f"用户 {user_id} 无权删除日记 {diary_id}")
            return False
        
        # 获取日记关联的景点ID
        spot_id = target_diary["spot_id"]
        
        # 删除图片文件夹
        img_dir = os.path.dirname(self._getDiaryImagePath(diary_id))
        if os.path.exists(img_dir):
            import shutil
            try:
                shutil.rmtree(img_dir)
            except Exception as e:
                log.writeLog(f"删除日记 {diary_id} 的图片文件夹失败: {str(e)}")
        
        # 从列表中删除日记
        self.diaries.pop(diary_index)
        
        # 保存更新
        if not self._saveDiaries():
            log.writeLog(f"保存日记数据失败")
            return False
        
        # 更新用户的评论记录 - 使用新的存储格式
        if "reviews" in user:
            # 直接更新
            if diary_id in user["reviews"]["diary_ids"]:
                user["reviews"]["diary_ids"].remove(diary_id)
                user["reviews"]["total"] -= 1
        
        self.userIo.saveUsers()
        
        # 更新景点的评论数
        spot = self.spotIo.getSpot(spot_id)
        if spot and "reviews" in spot and spot["reviews"] > 0:
            spot["reviews"] -= 1
            self.spotIo.saveSpots()
        
        log.writeLog(f"用户 {user_id} 成功删除日记 {diary_id}，剩余日记数: {user['reviews'].get('total', 0)}")
        return True
    
    def updateScore(self, diary_id, new_score, old_score=0):
        """更新日记评分"""
        for diary in self.diaries:
            if diary["id"] == diary_id:
                # 计算新的评分
                sum_score = float(diary.get("score", 0)) * diary.get("score_count", 0)
                sum_score += new_score - old_score
                
                # 如果是新评分，评分数量加1
                if old_score == 0:
                    if "score_count" not in diary:
                        diary["score_count"] = 0
                    diary["score_count"] += 1
                
                # 计算平均分
                if diary["score_count"] > 0:
                    diary["score"] = round(sum_score / diary["score_count"], 1)
                else:
                    diary["score"] = 0
                
                # 保存更新
                self._saveDiaries()
                return diary["score"]
        
        log.writeLog(f"日记 {diary_id} 不存在，无法更新评分")
        return -1
    
    def diaryVisited(self, diary_id):
        """增加日记访问次数"""
        for diary in self.diaries:
            if diary["id"] == diary_id:
                if "visited_time" not in diary:
                    diary["visited_time"] = 0
                
                diary["visited_time"] += 1
                self._saveDiaries()
                return diary["visited_time"]
        
        log.writeLog(f"日记 {diary_id} 不存在，无法更新访问次数")
        return -1
    
    def getTopRatedDiaries(self, limit=10):
        """获取评分最高的日记"""
        # 过滤掉没有评分的日记
        rated_diaries = [d for d in self.diaries if d.get("score_count", 0) > 0]
        # 按评分降序排序
        sorted_diaries = sorted(rated_diaries, key=lambda x: x.get("score", 0), reverse=True)
        return sorted_diaries[:limit]
    
    def getMostVisitedDiaries(self, limit=10):
        """获取访问量最高的日记"""
        # 按访问量降序排序
        sorted_diaries = sorted(self.diaries, key=lambda x: x.get("visited_time", 0), reverse=True)
        return sorted_diaries[:limit]


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

# 初始化全局实例
userIo = UserIo()
spotIo = SpotIo()
configIo = ConfigIo()
diaryIo = DiaryIo()

