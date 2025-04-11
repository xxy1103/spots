from data_structure.btree import BTree
from fileIo import UserIo
import printLog as log
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
    def __init__(self,userIo):
        self.userIo = userIo
        self.users = userIo.getAlluser()
        self.userCount = userIo.getCount()
        self.btree = BTree(t=3)
        for user in self.users:
            self.btree.insert({"id":user["id"], "name":user["name"]})
        log.writeLog("用户数据加载完成")

    def addUser(self, user):
        if self.btree.search(user["name"]) is not None:
            log.writeLog(f"用户{user['name']}已存在")
            return False
        
        # 对密码进行哈希处理
        user["password"] = hashPassword(user["password"])
        
        self.userIo.addUser(user)
        self.btree.insert({"id":user["id"], "name":user["name"]})
        log.writeLog(f"添加用户{user['name']}成功")
        return True
    
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




