# 本类用于获取data中的数组，所用输入可以调用此类，统一方法
from module.data_structure.HuffmanTree import huffman_decoding, encode_to_binary
from module.data_structure.HuffmanTree import generate_huffman_codes
from module.Model.Model import Diary, User, Reviews, Spot
from module.data_structure.rb_tree import RedBlackTree
from module.data_structure.stack import Stack
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
        usersPath = dataPath + r"/users/users.json"
        with open(usersPath, "r", encoding="utf-8") as f:
            usersData = json.load(f)
        return usersData

    @staticmethod
    def save_users(data:dict):
        """
        保存数据
        """
        usersPath = dataPath + r"/users/users.json"
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
    def save_Diaries(data:dict):
        """
        保存日记信息到文件
        """
        diaries_path = os.path.join(dataPath, "diaries", "diaries.json")
        with open(diaries_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
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








  

# 初始化全局实例
userIo = UserIo()
spotIo = SpotIo()
configIo = ConfigIo()
diaryIo = DiaryIo()



