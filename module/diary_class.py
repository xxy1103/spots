from module.fileIo import diaryIo
# userManager导入了DiaryManager，则diary_class中不能再导入user,否则报错
from module.data_structure.hashtable import HashTable
from module.data_structure.stack import Stack
from module.data_structure.set import MySet
from module.printLog import writeLog
from module.data_structure.HuffmanTree import generate_huffman_codes
from module.data_structure.KMP import kmp_search
from module.Model.Model import Diary, User, Spot
import module.printLog as log
import datetime #日期使用


            
class IdGenerator:      
    def __init__(self, currentId, holes=[]):
        self.holes = Stack(holes)
        self.currentId = currentId

    def getId(self):
        if not self.holes.is_empty():
            return self.holes.pop()
        self.currentId += 1
        return self.currentId

    def releaseId(self, id):
        if id <= self.currentId:
            self.holes.push(id)
        return self.holes.getlist()
    
    def getHolesList(self):
        return self.holes.getlist()
    
    def getCurrentId(self):
        return self.currentId

class DiaryManager:
    """日记管理类，实现日记的搜索、排序和推荐功能"""

    def __init__(self,diaries,counts,titleHashTable=None,idGenerator=None,huffman_tree=None,codes=None):
        """初始化日记管理器"""
        # 获取所有日记
        self.diaries = diaries
        self.titleHashTable = titleHashTable

        self.idGenerator = idGenerator
        self.counts = counts
        self.huffman_tree = huffman_tree
        self.codes = codes
        writeLog("日记管理系统初始化完成")

    @classmethod
    def from_dict(cls, data: dict,huffman_tree):
        """
        从字典创建日记管理器
        """
        # 解析数据
        diarys_json = data.get("diaries", [])
        diaries = []
        for diary in diarys_json:
            diaries.append(Diary.from_dict(diary))
        # id生成器
        id_generator = IdGenerator(data.get("currentId", 0), data.get("holes", []))
        counts = data.get("counts", 0)
        # 创建title查找哈希表
        hash_table_size = max(1000, counts * 3)
        titleHashTable = HashTable(hash_table_size)
        for diary in diaries:
            titleHashTable.insert({"id": diary.id, "name": diary.title})


        # 加载哈夫曼树
        codes = generate_huffman_codes(huffman_tree)
        log.writeLog(f"成功加载全局哈夫曼树，包含 {len(codes)} 个字符编码")
        # 创建对象
        return cls(diaries,counts, titleHashTable, id_generator,huffman_tree, codes)
    def to_dict(self):
        """
        将日记管理器转换为字典
        """
        diaries_json = [diary.to_dict() if diary is not None else None for diary in self.diaries]
        return {
            "counts": self.counts,
            "currentId": self.idGenerator.currentId,
            "holes": self.idGenerator.getHolesList(),
            "diaries": diaries_json
        }
    
    def getDiary(self, diary_id:int):
        """获取单个日记"""
        return self.diaries[diary_id] if 0 <= diary_id <= self.idGenerator.getCurrentId() else None
    def getAllDiaries(self):
        """获取所有日记的列表的一个拷贝"""
        return self.diaries.copy() if self.diaries else []
        

    def addDiary(self, user:User, spot:Spot, title, content, images=None, videos=None, scoreToSpot:float=0):
        """添加新日记"""

        """添加新日记"""
        if images is None:
            images = []
        
        if videos is None:
            videos = []

        current_id = self.idGenerator.getCurrentId()

        new_diary_json = {
            "id": self.idGenerator.getId(),
            "user_name": user.name,
            "user_id": user.id,
            "spot_id": spot.id,
            "content": content,
            "title": title,
            "time": datetime.datetime.now().strftime("%Y-%m-%d"),
            "score": 0,
            "score_count": 0,
            "visited_time": 0,
            "img_list": images,
            "video_path": videos,  # 添加视频路径字段
            "compressed": False,
            "scoreToSpot": scoreToSpot,  # 添加评分到景点的字段
        }

        # 创建日记对象
        new_diary = Diary.from_dict(new_diary_json)
        # 压缩日记内容
        new_diary.compress(self.codes)
        # 添加到日记列表
        if new_diary.id <= current_id:
            self.diaries[new_diary.id] = new_diary
        else:
            self.diaries.append(new_diary)
        # 日记总数+1
        self.counts += 1    

        # 将新名称添加到哈希表
        self.titleHashTable.insert({"id": new_diary.id, "name": title})
        return new_diary # 返回新创建的对象


    def deleteDiary(self, user_id:int, diary_id:int):
        """删除日记"""
        # success = self.diaryIo.deleteDiary(user_id, diary_id)
        # if success:
        #     self.titleHashTable.delete(diary_id)
        
        # return success
        diary = self.getDiary(diary_id)
        if not diary:
            log.writeLog(f"日记 {diary_id} 不存在，无法删除")
            return False
        # 检查用户是否有权限删除日记
        if diary.user_id != user_id:
            log.writeLog(f"用户 {user_id} 无权限删除日记 {diary_id}")
            return False
        # 删除日记
        diary.delete()
        # 删除日记对象
        self.diaries[diary_id] = None
        self.idGenerator.releaseId(diary_id)
        self.counts -= 1
        # 从哈希表中删除日记
        self.titleHashTable.delete(diary_id)
        # 从索引堆中删除日记
        self.visitedHeap.delete(diary_id)   


    def visitDiary(self, diary_id:int):
        """浏览日记，增加浏览量"""
        
        diary = self.getDiary(diary_id)
        if diary is not None:
            diary.visited()
        
        return diary.visited_time


    def rateDiary(self, diary_id:int, newScore:float, oldScore:float):
        """为日记评分"""
        # 更新日记评分
        diary = self.getDiary(diary_id)
        new_score = diary.updateScore(newScore, oldScore)


        return new_score
 
    # 日记的全文搜索
    # 通过关键字的出现位置和次数增加权重分数，最后根据分数排序
    def searchByTitle(self, keys):
        """搜索日记标题"""
        if not keys:
            return []

        # 获取第一个字符匹配的日记
        first_char_diaries = self.titleHashTable.search(keys[0])
        if not first_char_diaries:
            # 如果第一个字符就没有匹配项，则不可能有交集
            return []

        # 使用第一个字符的结果初始化结果 ID 集合 (使用 MySet)
        result_ids = MySet(diary['id'] for diary in first_char_diaries)

        # 遍历关键词中的剩余字符
        for char in keys[1:]:
            # 获取包含当前字符的所有日记
            current_char_diaries = self.titleHashTable.search(char)
            if not current_char_diaries:
                # 如果任何一个后续字符没有匹配项，则交集为空
                return []

            # 创建当前字符的日记 ID 集合 (使用 MySet)
            current_ids = MySet(diary['id'] for diary in current_char_diaries)

            # 计算与当前结果集的交集 (使用 MySet 的 intersection_update)
            result_ids.intersection_update(current_ids)

            # 如果交集为空，提前结束 (使用 is_empty 方法)
            if result_ids.is_empty():
                return []

        # 根据最终的 ID 集合获取日记对象列表
        # 使用 self.diaries 列表直接访问，假设 ID 是从 1 开始且连续的
        # 迭代 MySet
        result_list = []
        for diary_id in result_ids:
            diary = self.getDiary(diary_id)
            result_list.append(diary)

        return result_list  # 返回包含指定字符串中每个字符的所有日记对象列表
    def getDiaryContent(self,diary_id:int):
        """获取日记的内容"""
        diary = self.getDiary(diary_id)
        if diary is None:
            log.writeLog(f"日记 {diary_id} 不存在")
            return None
        # 获取日记内容
        content = diary.getContent(self.huffman_tree)
        if content is None:
            log.writeLog(f"日记 {diary_id} 内容获取失败，可能是压缩文件损坏或不存在")
            # 返回空字符串而不是 None，避免模板错误
            return ""
        return content
    def searchByContent(self, search_term, max_results=10):
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
        
        for i in range(self.idGenerator.currentId):
            diary = self.getDiary(i)
            if not diary:
                continue  # 跳过已删除的日记
            diary_id = diary.id

            # 有些日记可能已经解压了，根据不同的情况进行搜索
            if diary.compressed and compressed_search:
                # 3.1 压缩日记: 在二进制数据中搜索编码后的搜索词
                content_path = diary.content
                # print(f"正在搜索日记 {diary_id} 的内容: {content_path}")
                if not content_path:
                    log.writeLog(f"日记 {diary_id} 的内容文件不存在: {content_path}")
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
                    if kmp_search(bit_string, search_encoded):
                        candidates.append(diary_id)
                        
                except Exception as e:
                    log.writeLog(f"搜索压缩日记 {diary_id} 失败: {str(e)}")
                    continue
                    
            else:  
                # 3.2 未压缩日记: 直接在原文本中搜索
                content = diary.content
                
                # 在标题和内容中搜索，逻辑上或许与searchByTitle重复了，这里为了验证搜索功能先保留
                title = diary.title
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
            if diary.compressed:
                # 压缩日记需要解压验证
                
                decompressed = diary.getContent(self.huffman_tree)
                if decompressed:
                    # 在解压后的内容中搜索
                    if kmp_search(decompressed, search_term):
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


# 创建全局实例

# 加载数据和哈夫曼树
diary_data = diaryIo.load_Diaries()
huffman_tree = diaryIo.load_global_huffman_tree()

# 使用from_dict方法初始化DiaryManager
diaryManager = DiaryManager.from_dict(diary_data, huffman_tree)