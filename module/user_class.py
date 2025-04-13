from module.data_structure.btree import BTree
from module.fileIo import userIo
from module.Spot_class import spotManager
from module.data_structure.merge import merge_sort
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




class User:
    def __init__(self):
        self.userIo = userIo
        self.users = userIo.getAlluser()
        self.userCount = userIo.getCount()
        self.btree = BTree(t=3)
        for user in self.users:
            self.btree.insert({"id":user["id"], "name":user["name"]})
        log.writeLog("用户数据加载完成")

    def addUser(self, username, password, liketype):
        # --- 修改这里：使用传入的 username 进行搜索 ---
        existing_user_node = self.btree.search(username) 
        if existing_user_node is not None:
            # --- 修改这里：日志记录也使用 username ---
            log.writeLog(f"用户 {username} 已存在") 
            return False
        
        # 现在可以安全地创建新的 user 字典
        user = {
            "name": username,
            "id": None, # id 应该由 userIo.addUser 分配
            "password": password, # 密码将在下面哈希
            "likes_type": liketype,
            "reviews": []
        }
        # 对密码进行哈希处理
        user["password"] = hashPassword(user["password"])
        
        # 调用 userIo 添加用户，这应该会设置 user['id']
        new_user_id = self.userIo.addUser(user) 
        if new_user_id is None: # 假设 addUser 失败返回 None
             log.writeLog(f"通过 userIo 添加用户 {username} 失败")
             return False

        # 使用返回的 ID 更新 B 树
        self.btree.insert({"id": new_user_id, "name": username}) 
        log.writeLog(f"添加用户 {username} (ID: {new_user_id}) 成功")
        return True # 返回 True 表示成功
    
    def searchUser(self, name):
        user = self.btree.search(name)
        if user is None:
            log.writeLog(f"用户{name}不存在")
            return None
        log.writeLog(f"找到用户{user['name']}")
        return user
    
    def loginUser(self, userName, userPassword):
        user = self.btree.search(userName)
        if user is None:
            log.writeLog(f"用户{userName}不存在")
            return None
            
        # 获取完整用户信息
        full_user_info = self.userIo.getUser(user["id"])
        
        # 验证密码
        if not verifyPassword(userPassword, full_user_info["password"]):
            log.writeLog(f"用户{userName}密码错误")
            return None
            
        log.writeLog(f"用户{userName}登录成功")
        return full_user_info
    
    def deleteUser(self, name):
        user = self.btree.search(name)
        if user is None:
            log.writeLog(f"用户{name}不存在")
            return False
        
        self.userIo.deleteUser(user["id"])
        log.writeLog(f"删除用户{user['name']}成功")
        return True   

    def getRecommendSpots(self, userId, topK=10):
        """
        获取用户推荐的景点
        """
        user = self.userIo.getUser(userId)
        if user is None:
            log.writeLog(f"用户{userId}不存在")
            return None
        
        # 获取用户的兴趣标签
        user_likes = user["likes_type"]
        
        # --- 获取用户喜欢类型的所有景点 ---
        preferred_spots = []
        if not user_likes: # 如果用户没有喜欢的类型，可以返回全局热门或空列表
            log.writeLog(f"用户{userId}没有设置喜欢的景点类型")
            # 方案1：返回全局热门 (需要 spotManager 支持)
            return spotManager.getAllSpotsSorted()[:topK] 
            # 方案2：返回空列表
            # return []

        for spot_type in user_likes:
            # 使用 k=-1 获取该类型所有排序后的景点
            spots_of_type = spotManager.getTopKByType(spot_type, k=-1) 
            if spots_of_type: # 确保列表非空
                preferred_spots.extend(spots_of_type)
        
        if not preferred_spots:
             log.writeLog(f"未能根据用户{userId}的喜好找到任何景点")
             return []

        # --- 使用归并排序对收集到的景点进行总排序 ---
        # 注意：getTopKByType(k=-1) 已经返回排序好的列表，
        # 但这里我们需要对 *所有* 喜欢类型的景点进行 *合并排序*
        # 如果 getTopKByType(k=-1) 返回的是未排序列表，则必须排序
        # 即使返回的是已排序列表，合并后也需要重新排序以获得总排名
        
        # 移除可能的重复景点（如果一个景点属于多个用户喜欢的类型）
        # 使用字典去重，保留ID唯一的景点
        unique_spots_dict = {spot['id']: spot for spot in preferred_spots}
        unique_preferred_spots = list(unique_spots_dict.values())

        # 对去重后的列表进行归并排序
        sorted_recommended_spots = merge_sort(unique_preferred_spots)
        
        log.writeLog(f"为用户{userId}生成推荐景点列表，共{len(sorted_recommended_spots)}个，返回前{topK}个")
        
        # 返回排序后的前 topK 个景点
        return sorted_recommended_spots[:topK]

        
        
        


userManager = User()



