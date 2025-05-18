# 本类用于获取data中的数组，所用输入可以调用此类，统一方法

import os
import json
import datetime
import module.printLog as log
from module.data_structure.stack import Stack

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

class IdGenerator:      
    def __init__(self, currentId, holes=[]):
        self.holes = Stack(holes)
        self.currentId = currentId

    def getId(self):
        if not self.holes.is_empty():
            return self.holes.pop(), self.currentId,self.holes.getlist()
        self.currentId += 1
        return self.currentId, self.currentId,self.holes.getlist()

    def releaseId(self, id):
        if id <= self.currentId:
            self.holes.push(id)
        return self.holes.getlist()

class DiaryIo:
    def __init__(self):
        """初始化日记IO类"""
        global userIo, spotIo
        self.spotIo = spotIo 
        self.userIo = userIo 
        # 集中存储路径
        self.diaries_path = os.path.join(dataPath, "diaries", "diaries.json")
        self.reviews_base_path = os.path.join(dataPath, "scenic_spots") # 改完 路径改为"scenic_spots"下

        # 确保目录存在
        os.makedirs(os.path.dirname(self.diaries_path), exist_ok=True)
        os.makedirs(self.reviews_base_path, exist_ok=True)

        # 加载日记数据
        self.diaries = []
        self.diary_count = 0
        self.currentId = 0
        self.holes = []
        self._loadDiaries()

        log.writeLog("日记IO系统初始化完成")
    
    def _loadDiaries(self): #Checked
        """从diaries.json加载所有日记数据"""
        if os.path.exists(self.diaries_path):
            try:
                with open(self.diaries_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.diaries = data.get("diaries", [])
                    self.diary_count = data.get("counts", len(self.diaries))
                    self.currentId = data.get("currentId", 0)
                    self.holes = data.get("holes", [])
                    self.diariesIdGenerator = IdGenerator(self.currentId, self.holes)
                log.writeLog(f"已加载 {self.diary_count} 条日记")
            except Exception as e:
                log.writeLog(f"加载日记文件失败: {str(e)}")
                self.diaries = []
                self.diary_count = 0
        else:
            # 文件不存在，创建空数据
            self.diaries = []
            self.diary_count = 0
            self.saveDiaries()
            log.writeLog("已创建新的日记数据文件")
    
    def saveDiaries(self): #Checked
        """保存日记数据到文件"""
        try:
            data = {
                "counts": self.diary_count,
                "currentId": self.currentId,
                "holes": self.holes,
                "diaries": self.diaries
            }
            with open(self.diaries_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            log.writeLog(f"已保存 {self.diary_count} 条日记到文件")
            return True
        except Exception as e:
            log.writeLog(f"保存日记文件失败: {str(e)}")
            return False

    def getDiaryImagePath(self, spot_id, diary_id): #改完 修改为图片实际存储路径
        """获取日记图片存储路径"""
        return os.path.join(self.reviews_base_path, f"spot_{spot_id}", f"review_{diary_id}","images")

    def getAllDiaries(self): #Checked
        """获取所有日记"""
        return self.diaries
    
    def getDiary(self, diary_id): #改完 直接获取对应id的日记
        """获取单个日记"""
        if diary_id < self.diary_count:
            return self.diaries[diary_id]
        else:
            log.writeLog(f"日记 {diary_id} 不存在")
        return None     # 返回None表示对应日记不存在
    
    def getSpotDiaries(self, spot_id): #改 使用合适的数据结构优化
        """获取指定景点的所有日记"""
        diarys = [diary for diary in self.diaries if diary != None and diary["spot_id"] == spot_id]
        return diarys
        #return [diary for diary in self.diaries if diary["spot_id"] == spot_id]
    
    def getUserDiaries(self, user_id): #改 使用合适的数据结构优化
        """获取指定用户的所有日记"""
        diarys = [diary for diary in self.diaries if diary != None and diary["user_id"] == user_id]
        return diarys
        #return [diary for diary in self.diaries if diary["user_id"] == user_id]
    
    def addDiary(self, user_id, spot_id, title, content, images=None): #改完
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
        diary_id,self.currentId,self.holes = self.diariesIdGenerator.getId()
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
            img_dir = self.getDiaryImagePath(spot_id, diary_id)
            os.makedirs(img_dir, exist_ok=True)
            
            # 保存图片路径
            for i, img_data in enumerate(images):
                img_path = os.path.join(img_dir, f"{diary_id}_{i}.jpg")
                new_diary["img_list"].append(img_path)
                # 实际的图片保存由前端处理
                with open(img_path, "wb") as img_file:
                    img_file.write(img_data)
                
        # 添加到日记列表
        self.diaries.append(new_diary)
        self.diary_count += 1
        
        # 更新景点评论数，不立即保存
        self.spotIo.spotReviewsAdd(spot_id, save_immediately=False) #待改 修改Spot后改
            
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
            
        # 暂时不需要保存
        # # 最后，手动保存所有更改
        # self.spotIo.saveSpots()  # 保存景点数据
        # self.userIo.saveUsers()  # 保存用户数据
            
        log.writeLog(f"用户 {user_id} 为景点 {spot_id} 添加日记 {diary_id}，总日记数: {user['reviews']['total']}")
        return diary_id

    def deleteDiary(self, user_id, diary_id): #改完 删除一条日记后，id与下标的关系被打乱
        
        """
        删除日记
        user_id:执行操作的用户id
        diary_id:被删除的日记id
        """
        # 检查用户是否存在
        user = self.userIo.getUser(user_id)
        if not user:
            log.writeLog(f"用户 {user_id} 不存在，无法删除日记")
            return False
        
        # 查找日记
        diary_index = -1
        target_diary = None
        # for i, diary in enumerate(self.diaries):
        #     if diary["id"] == diary_id:
        #         diary_index = i
        #         target_diary = diary
        #         break
        target_diary = self.getDiary(diary_id)

        if target_diary is None:
            log.writeLog(f"日记 {diary_id} 不存在，无法删除")
            return False
        
        # 检查用户权限
        if target_diary["user_id"] != user_id:
            log.writeLog(f"用户 {user_id} 无权删除日记 {diary_id}")
            return False
        
        # 获取日记关联的景点ID
        spot_id = target_diary["spot_id"]
        
        # 删除图片文件夹 #改 暂未实现
        img_dir = os.path.dirname(self.getDiaryImagePath(spot_id, diary_id))
        if os.path.exists(img_dir):
            import shutil
            try:
                shutil.rmtree(img_dir)
            except Exception as e:
                log.writeLog(f"删除日记 {diary_id} 的图片文件夹失败: {str(e)}")
        
        # 从列表中删除日记
        self.diaries[diary_id] = None
        self.holes = self.diariesIdGenerator.releaseId(diary_id)  # 释放ID
        self.diary_count -= 1

        # 暂时不保存数据
        # # 保存更新
        # if not self._saveDiaries():
        #     log.writeLog(f"保存日记数据失败")
        #     return False
        
        # 更新用户的评论记录 - 使用新的存储格式
        if "reviews" in user:   #思考 是否可以替换更加高效的数据结构
            # 直接更新
            if diary_id in user["reviews"]["diary_ids"]:
                user["reviews"]["diary_ids"].remove(diary_id)
                user["reviews"]["total"] -= 1

        # self.userIo.saveUsers()

        # 更新景点的评论数
        spot = self.spotIo.getSpot(spot_id)
        if spot and "reviews" in spot and spot["reviews"] > 0:
            spot["reviews"] -= 1
            # self.spotIo.saveSpots()

        log.writeLog(f"用户 {user_id} 成功删除日记 {diary_id}，剩余日记数: {user['reviews'].get('total', 0)}")
        return True
    
    def updateScore(self, diary_id, new_score, old_score=0): #改完
        """
        更新日记评分
        old_score为0时，表示新评分
        """
        diary = self.getDiary(diary_id)
        if diary is not None:
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
                #self.saveDiaries()
                return diary["score"]
        
        log.writeLog(f"日记 {diary_id} 不存在，无法更新评分")
        return -1
    
    def diaryVisited(self, diary_id): #改完
        """增加日记访问次数"""
        diary = self.getDiary(diary_id)
        if diary is not None:
            if diary["id"] == diary_id:
                if "visited_time" not in diary:
                    diary["visited_time"] = 0
                
                diary["visited_time"] += 1
                # self._saveDiaries()
                return diary["visited_time"]
        
        log.writeLog(f"日记 {diary_id} 不存在，无法更新访问次数")
        return -1
    # 这种与文件无关的操作，应该放在diaryClass中
    # def getTopRatedDiaries(self, limit=10):
    #     """获取评分最高的日记"""
    #     # 过滤掉没有评分的日记
    #     rated_diaries = [d for d in self.diaries if d.get("score_count", 0) > 0]
    #     # 按评分降序排序
    #     sorted_diaries = sorted(rated_diaries, key=lambda x: x.get("score", 0), reverse=True)
    #     return sorted_diaries[:limit]
    
    # def getMostVisitedDiaries(self, limit=10):
    #     """获取访问量最高的日记"""
    #     # 按访问量降序排序
    #     sorted_diaries = sorted(self.diaries, key=lambda x: x.get("visited_time", 0), reverse=True)
    #     return sorted_diaries[:limit]


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

def testDiaryIo():
    """
    全面测试DiaryIo类的各个方法
    """
    print("\n===== 开始测试DiaryIo类 =====")
    
    # 获取已初始化的DiaryIo实例
    diary_io = diaryIo
    
    diary_io.deleteDiary(61,1)
    # 测试获取所有日记
    print("\n测试getAllDiaries方法:")
    all_diaries = diary_io.getAllDiaries()
    print(f"总日记数量: {len(all_diaries)}")
    
    # 测试获取单个日记
    print("\n测试getDiary方法:")
    if len(all_diaries) > 0:
        diary_id = all_diaries[0]["id"]
        print(f"获取日记ID {diary_id} 的详细信息:")
        diary = diary_io.getDiary(diary_id)
        if diary:
            print(f"日记标题: {diary['title']}")
            print(f"日记内容: {diary['content'][:30]}...")  # 只显示内容的前30个字符
        else:
            print(f"日记 {diary_id} 不存在")
    else:
        print("没有可用的日记进行测试")
    
    # 测试获取指定景点的所有日记
    print("\n测试getSpotDiaries方法:")
    spot_id = 1  # 假设使用ID为1的景点进行测试
    spot_diaries = diary_io.getSpotDiaries(spot_id)
    print(f"景点 {spot_id} 的日记数量: {len(spot_diaries)}")
    if spot_diaries:
        print(f"第一条日记标题: {spot_diaries[0]['title']}")
    
    # 测试获取指定用户的所有日记
    print("\n测试getUserDiaries方法:")
    user_id = 1  # 假设使用ID为1的用户进行测试
    user_diaries = diary_io.getUserDiaries(user_id)
    print(f"用户 {user_id} 的日记数量: {len(user_diaries)}")
    if user_diaries:
        print(f"第一条日记标题: {user_diaries[0]['title']}")
    
    # 测试添加新日记
    print("\n测试addDiary方法:")
    try:
        user_id = 1  # 假设使用ID为1的用户
        spot_id = 1  # 假设使用ID为1的景点
        title = "测试日记标题"
        content = "这是一条测试日记的内容，用于测试DiaryIo类的addDiary方法。"
        new_diary_id = diary_io.addDiary(user_id, spot_id, title, content)
        print(f"添加新日记成功，ID: {new_diary_id}")
        
        # 验证新日记是否添加成功
        if new_diary_id > 0:
            new_diary = diary_io.getDiary(new_diary_id)
            if new_diary:
                print(f"验证新日记: 标题={new_diary['title']}, 内容={new_diary['content'][:30]}...")
            else:
                print("无法获取新添加的日记")
    except Exception as e:
        print(f"添加日记失败: {str(e)}")
    
    # 测试更新日记评分
    print("\n测试updateScore方法:")
    if new_diary_id > 0:
        new_score = 4.5
        updated_score = diary_io.updateScore(new_diary_id, new_score)
        print(f"日记 {new_diary_id} 的评分已更新为: {updated_score}")
    
    # 测试增加日记访问次数
    print("\n测试diaryVisited方法:")
    if new_diary_id > 0:
        visits = diary_io.diaryVisited(new_diary_id)
        print(f"日记 {new_diary_id} 的访问次数已更新为: {visits}")
    
    # 测试删除日记
    print("\n测试deleteDiary方法:")
    if new_diary_id > 0:
        delete_success = diary_io.deleteDiary(user_id, new_diary_id)
        if delete_success:
            print(f"日记 {new_diary_id} 已成功删除")
            # 验证删除结果
            deleted_diary = diary_io.getDiary(new_diary_id)
            if deleted_diary is None:
                print("验证成功: 日记已被删除")
            else:
                print("警告: 日记似乎没有被完全删除")
        else:
            print(f"删除日记 {new_diary_id} 失败")
    
    print(diary_io.holes)

    # 保存所有修改
    # 注释：在实际使用中，DiaryIo类的方法会自动保存修改
    # 但在测试中，我们可能需要手动保存
    print("\n保存所有测试修改:")
    diary_io.saveDiaries()
    diary_io.spotIo.saveSpots()
    diary_io.userIo.saveUsers()
    
    print("\n===== DiaryIo类测试完成 =====")

# 初始化全局实例
userIo = UserIo()
spotIo = SpotIo()
configIo = ConfigIo()
diaryIo = DiaryIo()



