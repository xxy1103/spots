# 本类用于获取data中的数组，所用输入可以调用此类，统一方法

import os
import json
import datetime
import module.printLog as log
from module.data_structure.stack import Stack
from module.data_structure.HuffmanTree import huffman_decoding, encode_to_binary

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

    def userDiaryAdd(self, userId:int, diaryId:int):
        """
        当用户添加新日记时，增加用户的评论数量
        :param userId: 用户id
        :param diaryId: 日记id
        """
        try:
            user = self.getUser(userId)
            if not user:
                log.writeLog(f"用户 {userId} 不存在，无法更新评论数")
                return False

            if "reviews" not in user:
                user["reviews"] = {
                    "total": 0,
                    "diary_ids": []
                }

            user["reviews"]["total"] += 1
            user["reviews"]["diary_ids"].append(diaryId)
            #self.saveUsers()
            log.writeLog(f"用户 {userId} 的评论数更新为 {user['reviews']}")
            return True
        except Exception as e:
            log.writeLog(f"更新用户 {userId} 评论数失败: {str(e)}")
            return False
    def userDiaryDecrease(self, userId:int, diaryId:int):
        """
        当用户删除日记时，减少用户的评论数量
        :param userId: 用户id
        :param diaryId: 日记id
        """
        try:
            user = self.getUser(userId)
            if not user:
                log.writeLog(f"用户 {userId} 不存在，无法更新评论数")
                return False

            if "reviews" not in user:
                user["reviews"] = {
                    "total": 0,
                    "diary_ids": []
                }
                log.writeLog(f"用户 {userId} 没有评论字段，已初始化")
                return True

            # 确保评论数不会小于0
            if user["reviews"]["total"] > 0:
                user["reviews"]["total"] -= 1
                if diaryId in user["reviews"]["diary_ids"]:
                    user["reviews"]["diary_ids"].remove(diaryId)
            #self.saveUsers()
            log.writeLog(f"用户 {userId} 的评论数更新为 {user['reviews']}")
            return True
        except Exception as e:
            log.writeLog(f"更新用户 {userId} 评论数失败: {str(e)}")
            return False
    def userUpdateSpotMark(self, userId:int, spotId:int, score:float):
        """
        当用户给景点评分时，增加用户的评分数量
        """
        try:
            user = self.getUser(userId)
            if not user:
                log.writeLog(f"用户 {userId} 不存在，无法更新评分数")
                return -1
            if "spot_marking" not in user:
                spot_marking = []
                user["spot_marking"] = spot_marking
            # 检查是否已经评分
            for item in user["spot_marking"]:   #改 最好修改为查找算法
                if item["spot_id"] == spotId:
                    # 如果已经评分，更新评分
                    oldScore = item["score"]
                    item["score"] = score
                    log.writeLog(f"用户 {userId} 更新景点 {spotId} 的评分为 {score}")
                    return oldScore
            # 如果没有评分，添加新的评分
            item = {"spot_id": spotId, "score": score}
            user["spot_marking"].append(item)
            log.writeLog(f"用户 {userId} 的评分数更新为 {user['spot_marking']}")
            return 0
        except Exception as e:
            log.writeLog(f"更新用户 {userId} 评分数失败: {str(e)}")
            return -1
    def userUpdateDiaryMark(self, userId:int, diaryId:int, score:float):
        """
        当用户给日记评分时，增加用户的评分数量
        """
        try:
            user = self.getUser(userId)
            if not user:
                log.writeLog(f"用户 {userId} 不存在，无法更新评分数")
                return -1
            if "review_marking" not in user:
                review_marking = []
                user["review_marking"] = review_marking
            # 检查是否已经评分
            for item in user["review_marking"]:   #改 最好修改为查找算法
                if item["diary_id"] == diaryId:
                    # 如果已经评分，更新评分
                    oldScore = item["score"]
                    item["score"] = score
                    log.writeLog(f"用户 {userId} 更新日记 {diaryId} 的评分为 {score}")
                    return oldScore
            # 如果没有评分，添加新的评分
            item = {"diary_id": diaryId, "score": score}
            user["review_marking"].append(item)
            log.writeLog(f"用户 {userId} 的评分数更新为 {user['review_marking']}")
            return 0
        except Exception as e:
            log.writeLog(f"更新用户 {userId} 评分数失败: {str(e)}")
            return -1
            

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
    def spotReviewsAdd(self, spotId:int,diary_id:int, save_immediately=False)->bool:
        """
        当景区添加新日记时，增加景点的评论数量
    
        Args:
            spotId: 景点ID
            diary_id: 日记ID
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
                spot["reviews"] = {
                    "total": 0,
                    "diary_ids": []
                }

            spot["reviews"]["total"] += 1
            spot["reviews"]["diary_ids"].append(diary_id)
            
            # 只在需要时保存
            if save_immediately:
                self.saveSpots()
                
            log.writeLog(f"景点 {spotId} 的评论数更新为 {spot['reviews']}")
            return True
        except Exception as e:
            log.writeLog(f"更新景点 {spotId} 评论数失败: {str(e)}")
            return False

    def spotReviewsDecrease(self, spotId:int, diary_id:int, save_immediately=False)->bool:
        """
        当景区删除日记时，减少景点的评论数量
    
        Args:
            spotId: 景点ID
            diary_id: 日记ID
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
                spot["reviews"] = {
                    "total": 0,
                    "diary_ids": []
                }
                log.writeLog(f"景点 {spotId} 没有评论字段，已初始化")
                return True

            # 确保评论数不会小于0
            if spot["reviews"]["total"] > 0:
                spot["reviews"]["total"] -= 1
                if diary_id in spot["reviews"]["diary_ids"]:
                    spot["reviews"]["diary_ids"].remove(diary_id)
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
            return self.holes.pop(), self.holes.getlist()
        self.currentId += 1
        return self.currentId, self.holes.getlist()

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

        # 加载哈夫曼树
        self.huffman_tree = None
        self.codes = None
        
        if self.load_global_huffman_tree():
            log.writeLog("全局哈夫曼树加载成功")
        else:
            log.writeLog("全局哈夫曼树加载失败，无法进行压缩搜索")

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

    def getDiaryImagePath(self, spot_id:int, diary_id:int): #改完 修改为图片实际存储路径
        """获取日记图片存储路径"""
        return os.path.join(self.reviews_base_path, f"spot_{spot_id}", f"review_{diary_id}","images")

    def getAllDiaries(self):
        """获取所有日记"""
        return self.diaries     # 建议遍历使用时再增加判断条件 diary != None，避免空值的影响
                                # 或者使用self.holes[] 获取None的下标
    def getDiary(self, diary_id:int):
        """获取单个日记"""
        if diary_id <= self.currentId and diary_id >= 0:
            return self.diaries[diary_id]
        else:
            return None

    def get_diary_with_content(self, diary_id:int): # 在要直接显示日记内容时使用这个方法
        """
        获取已压缩的日记并解压内容
        
        Args:
            diary_id: 日记ID
            
        Returns:
            dict: 包含解压内容的日记对象
        """
        diary = self.getDiary(diary_id)
        if not diary:
            return None
            
        # 确认已压缩，解压
        if diary.get("compressed", True):
            decompressed_diary = self.decompress_diary_content(diary_id)
            if decompressed_diary:
                # 解压缩的方法我都用了副本，本意是因为我们并不保存原始数据，希望这样能防止解压缩的过程中对本地数据或者用户输入的新数据产生什么影响
                return decompressed_diary
                
        # 未压缩或解压失败，返回原始对象
        return diary

    def getSpotDiaries(self, spot_id:int): #无用方法，仅在测试使用，实际使用时从spotIo中获取
        """获取指定景点的所有日记"""
        diarys = [diary for diary in self.diaries if diary != None and diary["spot_id"] == spot_id]
        return diarys
        #return [diary for diary in self.diaries if diary["spot_id"] == spot_id]

    def getUserDiaries(self, user_id:int): #无用方法，仅在测试使用，实际使用时从userIo中获取
        """获取指定用户的所有日记"""
        diarys = [diary for diary in self.diaries if diary != None and diary["user_id"] == user_id]
        return diarys
        #return [diary for diary in self.diaries if diary["user_id"] == user_id]

    def searchDiaries(self, search_term, max_results=10):
        """根据搜索词搜索日记

        args:
            search_term：搜索词
            max_results: 返回结果的最大数量，默认为10
        
        return:
            result：包含搜索词的日记对象list
        """
        # 1. 加载全局哈夫曼树，用于压缩内容搜索
        if not self.huffman_tree or not self.codes:
            log.writeLog("无法加载全局哈夫曼树，只能搜索未压缩日记")
            # 如果无法加载树，仍然可以搜索未压缩日记
            compressed_search = False # 用于标记将要执行的搜索是那种类型，just一种用于处理搜索词编码异常情况的保险
        else:
            # 2. 将搜索词编码 - 只用于压缩内容搜索
            try:
                search_encoded = ''
                for char in search_term:
                    #此处的编码是使用编码表直接进行编码，因此理论上不含填充位
                    if char not in self.codes:
                        log.writeLog(f"搜索词包含编码表中不存在的字符: {char}")
                        compressed_search = False
                        break
                    search_encoded += self.codes[char]
                compressed_search = True
            except Exception as e:
                log.writeLog(f"编码搜索词时出错: {e}")
                compressed_search = False
                
        # 3. 开始搜索日记
        candidates = [] # 匹配的日记id列表
        
        for diary in self.getAllDiaries():
            if not diary:
                print("\n日记为空\n")
                continue  # 跳过已删除的日记
                
            diary_id = diary.get("id")
            
            # 有些日记可能已经解压了，根据不同的情况进行搜索
            if diary.get("compressed", False) and compressed_search:
                # 3.1 压缩日记: 在二进制数据中搜索编码后的搜索词
                content_path = diary.get("content", "")
                # print(f"正在搜索日记 {diary_id} 的内容: {content_path}")
                if not content_path:
                    print(f"日记 {diary_id} 的内容文件不存在: {content_path}")
                    continue
                    
                try:
                    # 读取压缩文件
                    with open(content_path, 'rb') as f:
                        binary_data = f.read()
                        
                    # 获取填充信息
                    padding_info = binary_data[0]
                    
                    # 将二进制数据转换为位字符串
                    # 使用列表然后再join，而不是连续拼接字符串
                    bits_list = [format(byte, '08b') for byte in binary_data[1:]]
                    bit_string = ''.join(bits_list)
                        
                    # 移除末尾填充位，确保正确的位流
                    if padding_info > 0:
                        bit_string = bit_string[:-padding_info]
                    
                    # if diary_id == 0:
                    #     print(f"日记 {diary_id} 的位字符串: {bit_string}")
                    #     print(f"搜索词的编码: {search_encoded}")

                    # 在位级别搜索编码后的搜索词
                    if search_encoded in bit_string:
                        candidates.append(diary_id)
                        
                except Exception as e:
                    log.writeLog(f"搜索压缩日记 {diary_id} 失败: {str(e)}")
                    continue
                    
            else:  
                # 3.2 未压缩日记: 直接在原文本中搜索
                content = diary.get("content", "")
                
                # 在标题和内容中搜索，逻辑上或许与searchByTitle重复了，这里为了验证搜索功能先保留
                title = diary.get("title", "")
                if search_term in content or search_term in title:
                    candidates.append(diary_id)
                    
            # 如果候选列表足够大，提前结束搜索
            if len(candidates) >= max_results * 2:
                print(f"候选列表已达到最大值: {len(candidates)}")
                break
        
        # 4. 验证候选结果 (对于压缩过的内容，需要解压验证；对于未压缩内容，二次确认)
        results = []
        for diary_id in candidates:
            diary = self.getDiary(diary_id)
            
            if diary.get("compressed", False):
                # 压缩日记需要解压验证
                decompressed = self.decompress_diary_content(diary_id)
                if decompressed:
                    # 在解压后的内容中搜索
                    if search_term in decompressed.get("content", ""):
                        results.append(diary)
                        if len(results) >= max_results:
                            break
            else:
                # 未压缩日记已经在上面确认过匹配，直接添加
                results.append(diary)
                if len(results) >= max_results:
                    break
        
        log.writeLog(f"搜索结果: 找到 {len(results)}/{max_results} 条匹配的日记")
        return results

    def addDiary(self, user_id:int, spot_id:int, title:str, content:str, images:list=None, videos:list=None): #添加视频支持
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
        diary_id,self.holes = self.diariesIdGenerator.getId()
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
            "img_list": images,
            "video_path": videos,  # 添加视频路径字段
            "compressed": False
        }
        
        print(f"新日记: {new_diary}")
        # 添加到日记列表
        if diary_id <= self.currentId:
            self.diaries[new_diary["id"]] = new_diary
        else:
            self.diaries.append(new_diary)
            self.currentId = diary_id
        self.diary_count += 1
        
        # 更新景点评论数，不立即保存
        self.spotIo.spotReviewsAdd(spot_id, diary_id, save_immediately=False)

        self.userIo.userDiaryAdd(user_id, diary_id)  # 更新用户评论数
            
        log.writeLog(f"用户 {user_id} 为景点 {spot_id} 添加日记 {diary_id}，总日记数: {user['reviews']['total']}")
        return diary_id

    def deleteDiary(self, user_id:int, diary_id:int): #改完 删除一条日记后，id与下标的关系被打乱

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
        target_diary = None

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

        
        # 更新用户的评论记录 - 使用新的存储格式
        self.userIo.userDiaryDecrease(user_id, diary_id)  # 更新用户评论数

        # self.userIo.saveUsers()

        # 更新景点的评论数
        self.spotIo.spotReviewsDecrease(spot_id, diary_id, save_immediately=False)

        log.writeLog(f"用户 {user_id} 成功删除日记 {diary_id}，剩余日记数: {user['reviews'].get('total', 0)}")
        return True

    def updateScore(self, diary_id:int, new_score:float, old_score:float=0): #改完
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

    def diaryVisited(self, diary_id:int): #改完
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

    def load_global_huffman_tree(self):
        """
        加载全局哈夫曼树
        
        Returns:
            tuple: (root, codes) 树根节点和编码表，加载失败时两个参数都返回None
        """
        try:
            import pickle
            from module.data_structure.HuffmanTree import generate_huffman_codes
            
            huffman_tree_path = os.path.join(dataPath, "diaries", "global_huffman_tree.pkl")
            
            if not os.path.exists(huffman_tree_path):
                log.writeLog(f"全局哈夫曼树文件不存在: {huffman_tree_path}")
                return None, None
                
            with open(huffman_tree_path, 'rb') as f:
                huffman_data = pickle.load(f)
            
            # 全局哈夫曼树.pkl文件中储存的是树根节点，如要使用请注意，因为程序无法判断里面的内容
            self.huffman_tree = huffman_data
            self.codes = generate_huffman_codes(self.huffman_tree)
            log.writeLog(f"从树根自动生成编码表")

            if not self.huffman_tree:
                log.writeLog(f"加载的哈夫曼树无效")
                return None, None

            log.writeLog(f"成功加载全局哈夫曼树，包含 {len(self.codes)} 个字符编码")
            return True
        except Exception as e:
            log.writeLog(f"加载全局哈夫曼树失败: {str(e)}")
            return False

    def decompress_diary_content(self, diary_id:int):
        """
        解压缩日记内容并更新content字段
        
        Args:
            diary_id: 日记ID
            
        Returns:
            dict: 更新后的日记对象，失败返回None
        """
        # 获取日记对象
        diary = self.getDiary(diary_id)
        if not diary:
            log.writeLog(f"日记 {diary_id} 不存在")
            return None
            
        # 检查日记是否已压缩
        if not diary.get("compressed", False):
            log.writeLog(f"日记 {diary_id} 未被压缩，无需解压")
            return diary
            
       
        if not self.huffman_tree:
            return None
            
        try:
            # 获取压缩文件路径
            content_path = diary.get("content", "")
            if not content_path:
                log.writeLog(f"日记 {diary_id} 没有内容路径")
                return None
            # 检查文件是否存在
            if not os.path.exists(content_path):
                log.writeLog(f"压缩文件不存在: {content_path}")
                return None
                
            # 读取压缩文件
            with open(content_path, 'rb') as f:
                binary_data = f.read()
                
            # 解码内容
            decoded_content = huffman_decoding(binary_data, self.huffman_tree)
            
            # 更新日记对象
            diary_copy = diary.copy()  # 创建副本避免修改原始对象
            diary_copy["content"] = decoded_content  # 保存解码后的内容
            
            log.writeLog(f"日记 {diary_id} 内容解压成功，长度: {len(decoded_content)}")
            return diary_copy
        except Exception as e:
            log.writeLog(f"解压日记 {diary_id} 内容失败: {str(e)}")
            return None

    def compress_diary(self, diary):
        """
        使用全局哈夫曼树压缩日记内容并保存
        
        Args:
            diary: 日记对象
            
        Returns:
            dict: 更新后的日记对象，失败返回None
        """
        if not diary:
            log.writeLog("没有提供要压缩的日记对象")
            return None
            
        diary_id = diary.get("id")
        if diary_id is None:
            log.writeLog("日记对象没有ID字段")
            return None
            
        # 检查是否已经压缩过
        if diary.get("compressed", False):
            log.writeLog(f"日记 {diary_id} 已经压缩过")
            return diary
            
        # 获取内容
        content = diary.get("content", "")
        if not content:
            log.writeLog(f"日记 {diary_id} 没有内容可压缩")
            return diary
            
        
        if not self.codes:
            return None
            
        try:
            # 检查内容中是否存在不在编码表中的字符，因为不更新哈夫曼树，所以是直接终止压缩
            for char in content:
                if char not in self.codes:
                    log.writeLog(f"日记 {diary_id} 包含未在全局哈夫曼树中的字符: {char}")
                    return None
                    
            # 压缩内容
            compressed_data = encode_to_binary(content, self.codes)
            
            # 获取相关信息
            spot_id = diary.get("spot_id")
            if not spot_id:
                log.writeLog(f"日记 {diary_id} 没有关联的景点ID")
                return None
                
            # 创建保存目录
            diary_content_dir = os.path.join(dataPath, "scenic_spots", f"spot_{spot_id}", "diary_content")
            os.makedirs(diary_content_dir, exist_ok=True)
            
            # 构建压缩文件路径
            compressed_filename = f"compressed_content_{diary_id}.bin"
            full_compressed_path = os.path.join(diary_content_dir, compressed_filename)
            
            # 保存压缩文件
            # with open(full_compressed_path, 'wb') as f:
            #     f.write(compressed_data)
                
            # 更新日记对象
            diary_copy = diary.copy()  # 创建副本
            diary_copy["content"] = f"scenic_spots/spot_{spot_id}/diary_content/{compressed_filename}"  # 更新内容路径
            diary_copy["compressed"] = True
            
            log.writeLog(f"日记 {diary_id} 压缩成功，保存到: {full_compressed_path}")
            return diary_copy
        except Exception as e:
            log.writeLog(f"压缩日记 {diary_id} 失败: {str(e)}")
            return None



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

    # 测试解压日记内容
    print("\n测试decompress_diary_content方法:")
    # 找一个已压缩的日记
    # compressed_diary = diary_io.getDiary(5)
    for diary in diary_io.getAllDiaries():
        if diary and diary.get("compressed", False):
            compressed_diary = diary
            break

    if compressed_diary:
        diary_id = compressed_diary["id"]
        print(f"找到已压缩日记 ID: {diary_id}, 标题: {compressed_diary.get('title', '无标题')}")
        decompressed = diary_io.decompress_diary_content(diary_id)
        if decompressed and "content" in decompressed:
            content_preview = decompressed["content"]
            print(f"日记解压成功，内容预览: {content_preview}")
        else:
            print(f"日记 {diary_id} 解压失败")
    else:
        print("没有找到已压缩的日记，跳过解压测试")

    # 测试日记压缩
    print("\n测试compress_diary方法:")
    # 创建一个测试日记进行压缩
    test_diary = {
        "id": new_diary_id if new_diary_id > 0 else 9999,
        "name": "测试用户",
        "user_id": 1,
        "spot_id": 1,
        "content": "这是一条测试日记内容，用于测试哈夫曼压缩功能。包含一些中文和符号：！@#￥%……&*（）。",
        "title": "压缩测试日记",
        "time": datetime.datetime.now().strftime("%Y-%m-%d"),
        "score": 0,
        "score_count": 0,
        "visited_time": 0,
        "img_list": [],
        "compressed": False
    }

    try:
        compressed_diary = diary_io.compress_diary(test_diary)
        if compressed_diary and compressed_diary.get("compressed", False):
            print(f"日记压缩成功!")
            print(f"压缩前内容路径: {test_diary['content']}")
            print(f"压缩后内容路径: {compressed_diary['content']}")
            
            # 创建测试日记的副本但不保存到数据库
            # diary_io.diaries.append(compressed_diary)
            # diary_io.diary_count += 1
            # diary_io.saveDiaries()
        else:
            print("日记压缩失败或未压缩")
    except Exception as e:
        print(f"压缩过程中发生错误: {str(e)}")

    # 测试获取带解压内容的日记
    print("\n测试get_diary_with_content方法:")
    # 找一个已压缩的日记
    if all_diaries:
        # 找第一个已压缩的日记
        for d in all_diaries:
            if d and d.get("compressed", False):
                diary_id = d["id"] +2
                print(f"使用已存在的压缩日记 ID: {diary_id} 测试")
                break
        else:
            print("没有找到已压缩的日记，跳过测试")
            diary_id = None
    else:
        diary_id = None
        print("没有可用的压缩日记进行测试")

    if diary_id is not None:
        diary_with_content = diary_io.get_diary_with_content(diary_id)
        if diary_with_content:
            # 如果是字符串内容，显示前100个字符
            content = diary_with_content.get("content", "")
            if isinstance(content, str) and len(content) > 0:
                if len(content) > 100:
                    content_preview = content[:100] + "..."
                else:
                    content_preview = content
                print(f"成功获取带解压内容的日记: {diary_with_content['title']}")
                print(f"内容预览: {content_preview}")
            else:
                print(f"日记内容可能不是文本或为空: {type(content)}")
        else:
            print(f"获取日记 {diary_id} 失败")

    print("\n===== 测试搜索功能 =====")
    import time

    def display_search_results(results, start_idx=0, limit=10):
        """显示搜索结果"""
        if not results:
            print("未找到匹配的日记")
            return 0
            
        end_idx = min(start_idx + limit, len(results))
        print(f"\n显示结果 {start_idx+1} 到 {end_idx}，共 {len(results)} 条：")
        
        for i in range(start_idx, end_idx):
            diary = results[i]
            diary_id = diary.get("id", "未知")
            title = diary.get("title", "无标题")
            
            # 获取日记内容预览
            try:
                decompressed = diary_io.decompress_diary_content(diary_id)
                if decompressed and "content" in decompressed:
                    content = decompressed.get("content", "")
                    preview = content[:100] + "..." if len(content) > 100 else content
                else:
                    preview = diary.get("content", "")[:100] + "..."
            except:
                preview = "无法获取内容预览"
                
            print(f"ID: {diary_id} | 标题: {title}")
            print(f"内容预览: {preview}")
            print("-" * 80)
            
        return end_idx

    while True:
        search_term = input("\n请输入搜索词(输入'q'退出搜索测试): ")
        if search_term.lower() == 'q':
            break
            
        # 初始化搜索参数
        current_page = 1
        batch_size = 10
        total_fetched = 0
        all_results = []
        
        # 执行初次搜索
        start_time = time.time()
        initial_results = diary_io.searchDiaries(search_term, batch_size)
        search_time = time.time() - start_time
        
        # 保存所有结果
        all_results.extend(initial_results)
        
        print(f"\n搜索完成! 耗时: {search_time:.4f} 秒, 找到 {len(initial_results)} 条匹配结果")
        
        if not initial_results:
            print("未找到匹配的日记，请尝试其他搜索词")
            continue
            
        # 显示初始结果
        total_fetched = display_search_results(initial_results, 0, batch_size)
        
        # 提供选项
        while True:
            if total_fetched >= len(all_results):
                # 已显示所有已获取的结果，可以尝试获取更多
                choice = input("\n已显示所有当前结果。输入 'f' 获取更多结果，'n' 进行新搜索，其他任意键返回主菜单: ")
                if choice.lower() == 'f':
                    # 获取下一批结果
                    print(f"\n正在搜索下一批结果...")
                    start_time = time.time()
                    current_page += 1
                    # 获取更多结果 - 因为现有searchDiaries不支持分页，所以这里我们增加批量大小
                    new_batch_size = current_page * batch_size
                    more_results = diary_io.searchDiaries(search_term, new_batch_size)
                    search_time = time.time() - start_time
                    
                    # 只保留新的结果
                    if len(more_results) > len(all_results):
                        all_results = more_results
                        print(f"找到额外的 {len(all_results) - total_fetched} 条结果，总计: {len(all_results)} 条")
                        # 显示新结果
                        total_fetched = display_search_results(all_results, total_fetched, batch_size)
                    else:
                        print("没有更多匹配的结果了")
                elif choice.lower() == 'n':
                    break  # 进行新搜索
                else:
                    return  # 返回主菜单
            else:
                # 还有更多已获取结果可以显示
                choice = input("\n输入 'm' 显示更多当前结果，'n' 进行新搜索，其他任意键返回主菜单: ")
                if choice.lower() == 'm':
                    # 显示下一批已获取结果
                    total_fetched = display_search_results(all_results, total_fetched, batch_size)
                elif choice.lower() == 'n':
                    break  # 进行新搜索
                else:
                    return  # 返回主菜单

    print("\n===== 搜索功能测试完成 =====")

    # 保存所有修改
    # 注释：在实际使用中，DiaryIo类的方法会自动保存修改
    # 但在测试中，我们可能需要手动保存
    # print("\n保存所有测试修改:")
    # diary_io.saveDiaries()
    # diary_io.spotIo.saveSpots()
    # diary_io.userIo.saveUsers()
    
    print("\n===== DiaryIo类测试完成 =====")

# 初始化全局实例
userIo = UserIo()
spotIo = SpotIo()
configIo = ConfigIo()
diaryIo = DiaryIo()



