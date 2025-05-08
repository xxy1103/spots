from module.fileIo import diaryIo
from module.Spot_class import spotManager
from module.user_class import userManager
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
        self.contentHashTable = HashTable(hash_table_size)  # 内容索引
        self.titleHashTable = HashTable(hash_table_size)  # 标题索引
        self.userHashTable = HashTable(hash_table_size)  # 用户ID索引
        self.spotHashTable = HashTable(hash_table_size)  # 景点ID索引
        
        # 索引堆用于快速获取TopK
        self.visitedHeap = TopKHeap()  # 按浏览量排序
        self.scoreHeap = TopKHeap()    # 按评分排序
        
        # 分类索引
        self.spotDiaries = {}  # 按景点分类
        self.userDiaries = {}  # 按用户分类
        
        # 构建所有索引
        for diary in self.diaries:
            diary_id = diary.get("id")
            
            # 添加到按景点分类的字典
            spot_id = diary.get("spot_id")
            if spot_id not in self.spotDiaries:
                self.spotDiaries[spot_id] = []
            self.spotDiaries[spot_id].append(diary)
            
            # 添加到按用户分类的字典
            user_id = diary.get("user_id")
            if user_id not in self.userDiaries:
                self.userDiaries[user_id] = []
            self.userDiaries[user_id].append(diary)
            
            # 添加到索引堆
            score = diary.get("score", 0)
            visited_time = diary.get("visited_time", 0)
            self.scoreHeap.insert(diary_id, score, visited_time)
            self.visitedHeap.insert(diary_id, visited_time, score)
            
            # 为内容、标题、用户ID和景点ID建立索引
            content = diary.get("content", "")
            if content:
                self._indexText(content, diary_id, self.contentHashTable)
            
            title = diary.get("title", "")
            if title:
                self._indexText(title, diary_id, self.titleHashTable)
            
            self._indexNumber(user_id, diary_id, self.userHashTable)
            self._indexNumber(spot_id, diary_id, self.spotHashTable)
        
        writeLog("日记索引构建完成")
    
    def _indexText(self, text, diary_id, hash_table):
        """为文本内容建立字符级索引"""
        if not text:
            return
            
        # 按字符索引
        for char in text:
            entry = hash_table.search(char)
            
            if not entry:
                # 创建新条目
                hash_table.insert({"key": char, "diaries": [diary_id]})
            else:
                # 添加到现有条目
                if diary_id not in entry["diaries"]:
                    entry["diaries"].append(diary_id)
    
    def _indexNumber(self, number, diary_id, hash_table):
        """为数字字段建立索引"""
        if number is None:
            return
            
        key = str(number)
        entry = hash_table.search(key)
        
        if not entry:
            hash_table.insert({"key": key, "diaries": [diary_id]})
        else:
            if diary_id not in entry["diaries"]:
                entry["diaries"].append(diary_id)
    
    def _rebuildIndexes(self):
        """重建所有索引"""
        # 重新从磁盘加载日记
        self.diaries = self.diaryIo.getAllDiaries()
        
        # 清空所有索引
        hash_table_size = max(1000, len(self.diaries) * 2)
        self.contentHashTable = HashTable(hash_table_size)
        self.titleHashTable = HashTable(hash_table_size)
        self.userHashTable = HashTable(hash_table_size)
        self.spotHashTable = HashTable(hash_table_size)
        self.visitedHeap = TopKHeap()
        self.scoreHeap = TopKHeap()
        self.spotDiaries = {}
        self.userDiaries = {}
        
        # 重新构建索引
        self._buildIndexes()
        
        writeLog("日记索引已重新构建")
    
    def getDiary(self, diary_id):
        """获取单个日记"""
        return self.diaryIo.getDiary(diary_id)
    
    def getAllDiaries(self):
        """获取所有日记"""
        return self.diaries
    
    def getSpotDiaries(self, spot_id):
        """获取指定景点的所有日记"""
        return self.spotDiaries.get(spot_id, [])
    
    def getUserDiaries(self, user_id):
        """获取指定用户的所有日记"""
        return self.userDiaries.get(user_id, [])
    
    def addDiary(self, user_id, spot_id, title, content, images=None):
        """添加新日记"""
        diary_id = self.diaryIo.addDiary(user_id, spot_id, title, content, images)
        
        if diary_id >= 0:
            # 重新构建索引
            self._rebuildIndexes()
            writeLog(f"用户 {user_id} 添加日记 {diary_id} 成功，索引已更新")
            return diary_id
        
        return -1
    
    def deleteDiary(self, user_id, diary_id):
        """删除日记"""
        success = self.diaryIo.deleteDiary(user_id, diary_id)
        
        if success:
            # 重新构建索引
            self._rebuildIndexes()
            writeLog(f"用户 {user_id} 删除日记 {diary_id} 成功，索引已更新")
        
        return success
    
    def visitDiary(self, diary_id):
        """浏览日记，增加浏览量"""
        visited_time = self.diaryIo.diaryVisited(diary_id)
        
        if visited_time > 0:
            # 更新索引堆中的浏览次数
            self.visitedHeap.updateVisitedTime(diary_id, visited_time)
            
            # 更新内存中的日记对象
            for diary in self.diaries:
                if diary["id"] == diary_id:
                    diary["visited_time"] = visited_time
                    break
        
        return visited_time
    
    def rateDiary(self, user_id, diary_id, score):
        """为日记评分"""
        # 获取用户信息
        user = userManager.userIo.getUser(user_id)
        if not user:
            writeLog(f"用户 {user_id} 不存在，无法评分")
            return False
        
        # 检查用户是否已经评分过
        old_score = 0
        if "diary_rating" not in user:
            user["diary_rating"] = []
        else:
            for rating in user["diary_rating"]:
                if rating["diary_id"] == diary_id:
                    old_score = rating["score"]
                    rating["score"] = score
                    break
            else:
                # 添加新评分记录
                user["diary_rating"].append({
                    "diary_id": diary_id,
                    "score": score
                })
        
        # 更新日记评分
        new_score = self.diaryIo.updateScore(diary_id, score, old_score)
        
        # 保存用户数据
        userManager.userIo.saveUsers()
        
        if new_score >= 0:
            # 更新索引堆中的评分
            self.scoreHeap.updateScore(diary_id, new_score)
            
            # 更新内存中的日记对象
            for diary in self.diaries:
                if diary["id"] == diary_id:
                    diary["score"] = new_score
                    break
            
            writeLog(f"用户 {user_id} 为日记 {diary_id} 评分 {score}，新平均分为 {new_score}")
            return True
        
        return False
    
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
    def searchByContent(self, keyword):
        """搜索日记内容和标题"""
        if not keyword or len(keyword) < 1:
            return []
        
        # 在内容中搜索
        content_results = self._searchWithHash(keyword, self.contentHashTable)
        # 在标题中搜索
        title_results = self._searchWithHash(keyword, self.titleHashTable)
        
        # 合并结果（去重）
        result_ids = set(content_results).union(set(title_results))
        
        # 获取完整的日记对象并计算相关度
        results = []
        for diary_id in result_ids:
            diary = self.getDiary(diary_id)
            if diary:
                # 计算相关度分数
                relevance = 0
                
                content = diary.get("content", "")
                title = diary.get("title", "")
                
                # 标题匹配分数（标题匹配权重更高）
                if keyword in title:
                    relevance += 10
                    relevance += title.count(keyword) * 2
                
                # 内容匹配分数
                if keyword in content:
                    relevance += 5
                    relevance += content.count(keyword)
                
                # 其他权重因素（评分、浏览量）
                relevance += min(diary.get("score", 0), 5)
                relevance += min(diary.get("visited_time", 0) / 100, 5)
                
                # 添加相关度得分
                diary_copy = diary.copy()
                diary_copy["relevance"] = relevance
                results.append(diary_copy)
        
        # 按相关度排序
        sorted_results = quicksort(results, sort_key="relevance", reverse=True)
        return sorted_results
    
    def _searchWithHash(self, keyword, hash_table):
        """使用哈希表进行搜索，返回匹配的日记ID列表"""
        matching_ids = set()
        first_char = True
        
        for char in keyword:
            # 查找包含这个字符的所有日记ID
            entry = hash_table.search(char)
            if not entry:
                continue
                
            diary_ids = set(entry.get("diaries", []))
            
            if first_char:
                matching_ids = diary_ids
                first_char = False
            else:
                # 取交集，确保所有字符都匹配
                matching_ids = matching_ids.intersection(diary_ids)
            
            # 如果已经没有匹配项，提前结束
            if not matching_ids:
                break
        
        return list(matching_ids)
    
    def searchBySpot(self, spot_id):
        """按景点ID搜索日记"""
        # 直接从分类索引中获取
        return self.getSpotDiaries(spot_id)
    
    def searchByUser(self, user_id):
        """按用户ID搜索日记"""
        # 直接从分类索引中获取
        return self.getUserDiaries(user_id)
    
    # 根据发布日期排序
    def getLatestDiaries(self, k=10):
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
    
    def getRecommendedDiaries(self, user_id, k=10):
        """根据用户兴趣推荐日记"""
        # 获取用户信息
        user = userManager.userIo.getUser(user_id)
        if not user:
            # 用户不存在，返回热门日记
            return self.getTopKByVisited(k)
        
        # 获取用户兴趣标签
        user_likes = user.get("likes_type", [])
        if isinstance(user_likes, str):
            user_likes = [user_likes]
        
        # 计算每篇日记的推荐分数
        scored_diaries = []
        
        for diary in self.diaries:
            # 跳过用户自己的日记
            if diary.get("user_id") == user_id:
                continue
                
            # 初始推荐分数 = 评分*2 + 浏览量/100
            score = diary.get("score", 0) * 2 + diary.get("visited_time", 0) / 100
            
            # 景点类型匹配加分
            spot_id = diary.get("spot_id")
            spot = spotManager.getSpot(spot_id)
            
            if spot and any(like in spot.get("type", "") for like in user_likes):
                score += 5
            
            # 用户已经评价过的日记降低分数
            if "diary_rating" in user:
                for rating in user["diary_rating"]:
                    if rating["diary_id"] == diary["id"]:
                        score -= 2
                        break
            
            # 添加推荐分数
            diary_copy = diary.copy()
            diary_copy["recommend_score"] = score
            scored_diaries.append(diary_copy)
        
        # 按推荐分数降序排序
        sorted_diaries = quicksort(scored_diaries, sort_key="recommend_score", reverse=True)
        
        # 返回前K条
        return sorted_diaries[:k]

# 创建全局实例
diaryManager = DiaryManager()