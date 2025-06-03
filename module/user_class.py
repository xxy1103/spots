# -*- coding: utf-8 -*-
from module.data_structure.btree import BTree
from module.fileIo import userIo
from module.diary_class import diaryManager
from module.Spot_class import spotManager
from module.Model.Model import User
import module.data_structure.kwaymerge as kwaymerge

import module.printLog as log
import base64
import hashlib
import os


def hashPassword(password, salt=None):
    """
    对密码进行加盐哈希
    
    Args:
        password (str): 要哈希的密码
        salt (bytes, optional): 盐值，如果不提供则生成新盐
        
    Returns:
        tuple: (哈希后的密码字符串, 盐值字符串)
    """
    # 如果没有提供盐值，生成一个16字节的随机盐
    if salt is None:
        salt = os.urandom(16)
    elif isinstance(salt, str):
        # 如果盐是字符串形式，转换回bytes
        salt = base64.b64decode(salt)
    
    # 使用SHA-256算法对密码和盐进行哈希
    hash_obj = hashlib.sha256()
    hash_obj.update(salt)
    hash_obj.update(password.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    
    # 将盐转换为字符串以便存储
    salt_str = base64.b64encode(salt).decode('utf-8')
    
    # 返回"盐:哈希"格式的字符串
    return f"{salt_str}:{password_hash}"

def verifyPassword(password, stored_hash):
    """
    验证密码是否匹配已存储的哈希值
    
    Args:
        password (str): 要验证的密码
        stored_hash (str): 存储的哈希字符串(格式为"盐:哈希")
        
    Returns:
        bool: 如果密码匹配返回True，否则返回False
    """
    # 分离存储的盐和哈希值
    stored_salt, stored_pw_hash = stored_hash.split(':', 1)
    
    # 使用相同的盐和算法重新计算哈希
    hash_to_check = hashPassword(password, stored_salt)
    
    # 比较计算出的哈希与存储的哈希
    return hash_to_check == stored_hash
    
class PasswordManager:
    """密码管理工具类"""
    
    @staticmethod
    def hash_password(raw_password):
        """对密码进行加盐哈希加密"""
        return hashPassword(raw_password)
    
    @staticmethod
    def verify_password(raw_password, stored_hash):
        """验证密码是否正确"""
        return verifyPassword(raw_password, stored_hash)




class UserManager:
    def __init__(self, users=None, counts=0):

        self.users = users if users is not None else []
        self.counts = counts if counts > 0 else len(users)
        self.btree = BTree(t=3)
        for user in self.users:
            self.btree.insert({"id":user.id, "name":user.name})
        log.writeLog("用户数据加载完成")

    @classmethod
    def from_dict(cls,data:dict):
        """
        从字典创建对象
        """
        users_json = data["users"]
        count_json = data["counts"]
        users = []
        for user_json in users_json:
            user = User.from_dict(user_json)
            users.append(user)
        return cls(
            users=users,
            counts=count_json
        )
    
    def to_dict(self):
        """
        将对象转换为字典
        """
        users_json = [user.to_dict() for user in self.users]
        return {
            "counts": self.counts,
            "users": users_json
        }

    def getUser(self, userId):
        """
        获取用户信息
        """
        return self.users[userId-1]

    def addUser(self, username, password, liketype):
        existing_user_node = self.btree.search(username) 
        if existing_user_node is not None:
            # --- 修改这里：日志记录也使用 username ---
            log.writeLog(f"用户 {username} 已存在") 
            return False
        
        # 现在可以安全地创建新的 user 字典
        user = {
            "name": username,
            "id": self.counts + 1, 
            "password": password, # 密码将在下面哈希
            "likes_type": liketype,
            "reviews": {
                "total": 0, # 总日记数
                "diary_ids": [], # 日记ID列表
            },
            "spot_marking": [],
            "review_marking": []
        }
        # 对密码进行哈希处理
        user["password"] = hashPassword(user["password"])
        
        user = User.from_dict(user)
        self.users.append(user)
        self.counts = self.counts + 1

        # 使用返回的 ID 更新 B 树
        self.btree.insert({"id": user.id, "name": user.name})
        log.writeLog(f"添加用户 {username} (ID: {user.id}) 成功")
        return True # 返回 True 表示成功
    
    def searchUser(self, name):
        user = self.btree.search(name)
        if user is None:
            log.writeLog(f"用户{name}不存在")
            return None
        log.writeLog(f"找到用户{user['name']}")
        return user
    
    
    def loginUser(self, userName, userPassword):
        user = self.searchUser(userName)
        if user is None:
            log.writeLog(f"用户{userName}不存在")
            return None
            
        # 获取完整用户信息
        full_user_info = self.getUser(user["id"]) # b树中返回的对象是字典{"id":,"name":}
          # 验证密码
        if not verifyPassword(userPassword, full_user_info.password):
            log.writeLog(f"用户{userName}密码错误")
            return None
            
        log.writeLog(f"用户{userName}登录成功")
        return full_user_info
    

    def getRecommendSpots(self, userId, topK=10):
        """
        获取用户推荐的景点 - 使用堆优化的推荐算法
        """
        user = self.getUser(userId)
        if user is None:
            log.writeLog(f"用户{userId}不存在")
            return None
        
        user_likes = user.likes_type
        
        # 使用优化的堆算法进行推荐
        return self._getRecommendSpotsOptimized(user_likes, topK)
    
    def _getRecommendSpotsOptimized(self, user_likes, topK=10):
        """
        使用堆优化的推荐算法
        时间复杂度: O((M + topK) × log M)，其中M是用户喜好类型数
        """
        from module.data_structure.heap import RecommendationHeap, create_spot_iterator
        
        # 使用最小堆来维护全局最高评分景点
        iterators_heap = RecommendationHeap()
        seen_spots = set()  # 去重
        
        # 为每个类型创建迭代器并初始化堆
        for spot_type in user_likes:
            spots_iter = create_spot_iterator(spot_type, spotManager)
            try:
                first_spot = next(spots_iter)
                # 堆中存储 (-score, spot_id, iterator, spot_data)
                # 使用负分数实现最大堆效果
                iterators_heap.push((-first_spot['score'], first_spot['id'], spots_iter, first_spot))
            except StopIteration:
                # 该类型没有景点，跳过
                continue
        
        result = []
        
        # 从堆中依次取出最高分的景点
        while not iterators_heap.is_empty() and len(result) < topK:
            try:
                neg_score, spot_id, spots_iter, spot_data = iterators_heap.pop()
                
                # 避免重复推荐
                if spot_id not in seen_spots:
                    result.append(spot_data)
                    seen_spots.add(spot_id)
                
                # 从同一个迭代器获取下一个景点
                try:
                    next_spot = next(spots_iter)
                    iterators_heap.push((-next_spot['score'], next_spot['id'], spots_iter, next_spot))
                except StopIteration:
                    # 该迭代器已耗尽，继续处理其他迭代器
                    continue
                    
            except IndexError:
                # 堆为空，结束循环
                break
        
        if not result:
            log.writeLog(f"未能根据用户喜好找到任何景点")
            return []
        
        log.writeLog(f"使用堆优化算法成功获取{len(result)}个推荐景点")
        return result

    def getRecommendSpotsTraditional(self, userId, topK=10):
        """
        传统的推荐算法（保留用于对比）
        获取用户推荐的景点
        """
        user = self.getUser(userId)
        if user is None:
            log.writeLog(f"用户{userId}不存在")
            return None
        
        # 获取用户的兴趣标签
        user_likes = user.likes_type

        # --- 初始化空的已排序推荐列表 ---
        sorted_recommended_spots = []

        # --- 迭代用户喜欢的类型，逐步合并排序 ---
        for spot_type in user_likes:
            # 使用 k=topK 获取该类型所有排序后的景点
            spots_of_type = spotManager.getTopKByType(spot_type, k=topK)    #只获取前 topK 个
            if spots_of_type: # 确保列表非空
                # 将新获取的有序列表与当前已合并的列表进行归并排序
                sorted_recommended_spots.append(spots_of_type)
        
        merged_list = kwaymerge.k_way_merge_descending(sorted_recommended_spots)

        if not merged_list:
             log.writeLog(f"未能根据用户{userId}的喜好找到任何景点")
             return []

        # 返回排序并去重后的前 topK 个景点
        return merged_list[:topK]

    def getRecommendDiaries(self, userId, topK=10):
        """
        获取用户推荐的日记
        """
        user = self.getUser(userId)
        if user is None:
            log.writeLog(f"用户{userId}不存在")
            return None
        
        # 获取用户的兴趣标签
        user_likes = user.likes_type

        # --- 初始化空的已排序推荐列表 ---

        recommended_diaries = []

        for spot_type in user_likes:
            spots_of_type = spotManager.getTopKByType(spot_type, k=-1)  #需要获取所有景点的日记
            if spots_of_type: # 确保列表非空
                # 迭代每个景点，获取其日记
                for spot in spots_of_type:
                    spot_id = spot["id"]
                    diarys = spotManager.spotDiaryHeapArray[spot_id-1].getTopK(topK)
                    if diarys: # 确保列表非空
                        # 将新获取的有序列表与当前已合并的列表进行归并排序
                        recommended_diaries.append(diarys)
        # 使用 k-way merge 对推荐的日记进行排序
        recommended_diaries = kwaymerge.k_way_merge_descending(recommended_diaries)
        
        if not recommended_diaries:
            log.writeLog(f"未能根据用户{userId}的喜好找到任何日记")
            return []
        diarys = []
        for i in range(topK):
            diarys.append(diaryManager.getDiary(recommended_diaries[i]["id"]))

        return diarys  # 返回对象列表

    def addDiary(self, userId, diaryId):
        """
        增加日记
        """
        user = self.getUser(userId)
        user.addDiary(diaryId)
        

    def markingReview(self, userId, diary_id, score):
        """
        用户对日记进行评分
        """
        # 获取日记信息
        user = self.getUser(userId)
        diary = diaryManager.getDiary(diary_id)
        oldscore = user.diaryMarking(diary, score)
        return oldscore


userManager = UserManager.from_dict(userIo.load_users())



