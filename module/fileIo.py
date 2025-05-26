# 本类用于获取data中的数组，所用输入可以调用此类，统一方法
import module.printLog as log
import datetime
import pickle
import json
import os



dataPath = r"data/"

class UserIo:

    @staticmethod
    def load_users():
        """
        从文件加载用户信息
        """
        usersPath = os.path.join(dataPath, r"users/users.json")
        with open(usersPath, "r", encoding="utf-8") as f:
            usersData = json.load(f)
        return usersData

    @staticmethod
    def save_users(data:dict):
        """
        保存数据
        """
        usersPath = dataPath + r"users/users.json"
        with open(usersPath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

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
        
    @staticmethod
    def load_spots():
        """
        从文件加载景点信息
        """
        spotsPath = os.path.join(dataPath,r"scenic_spots/spots.json")
        with open(spotsPath, "r", encoding="utf-8") as f:
            spotsData = json.load(f)
        return spotsData
    @staticmethod
    def save_spots(data:dict):
        """
        保存数据
        """
        spotsPath = os.path.join(dataPath,r"scenic_spots/spots.json")
        with open(spotsPath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)





class DiaryIo:
    @staticmethod
    def load_Diaries():
        """
        从文件加载日记信息
        """
        diaries_path = os.path.join(dataPath, "diaries", "diaries.json")
        with open(diaries_path, "r", encoding="utf-8") as f:
            diariesData = json.load(f)
        return diariesData
    
    @staticmethod
    def load_global_huffman_tree():
        """
        加载全局哈夫曼树
        
        Returns:
            tuple: (root, codes) 树根节点和编码表，加载失败时两个参数都返回None
        """
        try:
            huffman_tree_path = os.path.join(dataPath, "diaries", "global_huffman_tree.pkl")
            
            if not os.path.exists(huffman_tree_path):
                log.writeLog(f"全局哈夫曼树文件不存在: {huffman_tree_path}")
                return None
                
            with open(huffman_tree_path, 'rb') as f:
                huffman_data = pickle.load(f)
            huffman_tree = huffman_data

            return huffman_tree
        except Exception as e:
            log.writeLog(f"加载全局哈夫曼树失败: {str(e)}")
            return None
        
    @staticmethod
    def save_diaries(data:dict):
        """
        保存日记信息到文件
        """
        diaries_path = os.path.join(dataPath, "diaries", "diaries.json")
        with open(diaries_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    








  

# 初始化全局实例
userIo = UserIo()
spotIo = SpotIo()
configIo = ConfigIo()
diaryIo = DiaryIo()



