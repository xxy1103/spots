from module.fileIo import diaryIo
# userManager导入了DiaryManager，则diary_class中不能再导入user,否则报错
from module.data_structure.hashtable import HashTable
from module.data_structure.indexHeap import TopKHeap
from module.data_structure.quicksort import quicksort
from module.data_structure.merge import merge_sort
from module.data_structure.set import MySet
from module.printLog import writeLog
import datetime #日期使用
import re #正则表达式使用

class DiaryManager:
    """日记管理类，实现日记的搜索、排序和推荐功能"""
    
    def __init__(self):
        """初始化日记管理器"""
        # 获取所有日记
        self.diaryIo = diaryIo
        self.diaries = self.diaryIo.getAllDiaries()
        
        # 构建索引结构
        self._buildIndexes()
        
        writeLog("日记管理系统初始化完成")
    
    def _buildIndexes(self):
        """构建各种索引结构以提高查询效率"""
        # 哈希表用于快速检索
        hash_table_size = max(1000, len(self.diaries) * 2)
        self.titleHashTable = HashTable(hash_table_size)  # 标题索引
        
        # 索引堆用于快速获取TopK
        self.visitedHeap = TopKHeap()  # 按浏览量排序
        self.scoreHeap = TopKHeap()    # 按评分排序
        
        # 分类索引
        self.spotDiaries = {}  # 按景点分类
        self.userDiaries = {}  # 按用户分类
        
        # 构建所有索引
        for diary in self.diaries:
            diary_id = diary.get("id")
            
            
            # 添加到索引堆
            score = diary.get("score", 0)
            visited_time = diary.get("visited_time", 0)
            self.scoreHeap.insert(diary_id, score, visited_time)
            self.visitedHeap.insert(diary_id, visited_time, score)
            
            
            title = diary.get("title", "")
            if title:
                # self._indexText(title, diary_id, self.titleHashTable)
                self.titleHashTable.insert({"id": diary_id, "name": title})
            
        
        writeLog("日记索引构建完成")
    
    def getDiary(self, diary_id:int):
        """获取单个日记"""
        return self.diaryIo.getDiary(diary_id)
    
    def getAllDiaries(self):# 对完不用这个方法
        """获取所有日记"""
        return self.diaries

    def addDiary(self, user_id:int, spot_id:int, title, content, images=None, videos=None):
        """添加新日记"""
        diary_id = self.diaryIo.addDiary(user_id, spot_id, title, content, images, videos)

        if diary_id >= 0:
            # 重新构建索引
            self.titleHashTable.insert({"id": diary_id, "name": title})
            writeLog(f"用户 {user_id} 添加日记 {diary_id} 成功，索引已更新")
            return diary_id
        
        return -1
    
    def deleteDiary(self, user_id:int, diary_id:int):
        """删除日记"""
        success = self.diaryIo.deleteDiary(user_id, diary_id)
        if success:
            self.titleHashTable.delete(diary_id)
        
        return success
    
    def visitDiary(self, diary_id:int):
        """浏览日记，增加浏览量"""
        visited_time = self.diaryIo.diaryVisited(diary_id)
        
        if visited_time > 0:
            # 更新索引堆中的浏览次数
            self.visitedHeap.updateVisitedTime(diary_id, visited_time)
        return visited_time

    def rateDiary(self, diary_id:int, newScore:float, oldScore:float):
        """为日记评分"""
        # 更新日记评分
        new_score = self.diaryIo.updateScore(diary_id, newScore, oldScore)


        if new_score >= 0:
            # 更新索引堆中的评分
            self.scoreHeap.updateScore(diary_id, new_score)
            
            return new_score
        
        return -1
    
    def getTopKByVisited(self, k=10):
        """获取浏览量最高的K条日记"""
        top_ids = self.visitedHeap.getTopK(k)
        result = []
        
        for item in top_ids:
            diary_id = item["id"]
            diary = self.getDiary(diary_id)
            if diary:
                result.append(diary)
        
        return result
    
    def getTopKByScore(self, k=10):
        """获取评分最高的K条日记"""
        top_ids = self.scoreHeap.getTopK(k)
        result = []
        
        for item in top_ids:
            diary_id = item["id"]
            diary = self.getDiary(diary_id)
            if diary:
                result.append(diary)
        
        return result
    
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
        result_list = [self.diaries[diary_id] for diary_id in result_ids if 0 <= diary_id <= self.diaryIo.currentId]

        return result_list
    
    # 根据发布日期排序
    def getLatestDiaries(self, k=10): #改 或删
        """获取最新发布的日记"""
        # 为日记添加日期对象以便排序
        dated_diaries = []
        
        for diary in self.diaries:
            diary_copy = diary.copy()
            diary_copy["date_obj"] = diary.get("time", "1970-01-01")
            dated_diaries.append(diary_copy)
        
        # 按日期降序排序
        sorted_diaries = merge_sort(dated_diaries, sort_key="date_obj", reverse=True)
        
        # 清理辅助字段
        for diary in sorted_diaries:
            if "date_obj" in diary:
                del diary["date_obj"]
        
        # 返回前K条
        return sorted_diaries[:k] 
    
    def getDiariesWithContent(self,diary_id:int):
        """获取日记的内容"""
        return self.diaryIo.decompress_diary_content(diary_id)

# 创建全局实例
diaryManager = DiaryManager()