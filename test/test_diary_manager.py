import unittest
from module.diary_class import diaryManager
import random
import datetime

class TestDiaryManager(unittest.TestCase):
    """测试DiaryManager类的各个功能"""
    
    def setUp(self):
        """每个测试用例执行前的设置"""
        self.manager = diaryManager
        # 保存一些初始状态，以便在测试后可以恢复
        self.original_diaries = self.manager.getAllDiaries()
        self.test_diary_ids = []  # 存储测试过程中创建的日记ID，用于后续清理
    
    def tearDown(self):
        """每个测试用例执行后的清理工作"""
        # 删除测试过程中创建的日记
        for diary_id in self.test_diary_ids:
            self.manager.deleteDiary(1, diary_id)
    
    def test_get_diary(self):
        """测试获取单个日记的功能"""
        # 首先确保有日记可以获取
        all_diaries = self.manager.getAllDiaries()
        if all_diaries:
            # 获取第一个日记的ID
            diary_id = all_diaries[0]["id"]
            # 获取这个日记
            diary = self.manager.getDiary(diary_id)
            # 验证获取的日记是否正确
            self.assertIsNotNone(diary, "应当能获取到存在的日记")
            self.assertEqual(diary["id"], diary_id, "获取的日记ID应当与请求的ID一致")
        else:
            # 如果没有日记，测试获取不存在的日记ID
            self.assertIsNone(self.manager.getDiary(-1), "获取不存在的日记应当返回None")
    
    def test_get_all_diaries(self):
        """测试获取所有日记的功能"""
        all_diaries = self.manager.getAllDiaries()
        # 验证返回的是列表
        self.assertIsInstance(all_diaries, list, "获取所有日记应当返回列表")
        # 如果有日记，验证每个日记有id属性
        for diary in all_diaries:
            if diary:
                self.assertIn("id", diary, "每个日记应当有id属性")
    
    def test_add_diary(self):
        """测试添加日记的功能"""
        # 创建一个测试用户和测试日记
        user_id = 1
        spot_id = 1  # 假设spot_id为1的景点存在
        title = "测试日记标题 " + str(random.randint(1000, 9999))
        content = "这是一篇测试日记内容 " + str(random.randint(1000, 9999))
        
        # 添加日记
        diary_id = self.manager.addDiary(user_id, spot_id, title, content)
        
        # 验证添加是否成功
        self.assertGreaterEqual(diary_id, 0, "添加日记应当返回有效的diary_id")
        
        # 记录创建的日记ID，以便后续清理
        self.test_diary_ids.append(diary_id)
        
        # 验证是否能通过ID获取到这个日记
        added_diary = self.manager.getDiary(diary_id)
        self.assertIsNotNone(added_diary, "应当能获取到刚添加的日记")
        self.assertEqual(added_diary["title"], title, "添加的日记标题应当正确")
        self.assertEqual(added_diary["content"], content, "添加的日记内容应当正确")
        self.assertEqual(added_diary["user_id"], user_id, "添加的日记用户ID应当正确")
    
    def test_delete_diary(self):
        """测试删除日记的功能"""
        # 先添加一篇测试日记
        user_id = 1
        spot_id = 1
        title = "要删除的测试日记 " + str(random.randint(1000, 9999))
        content = "这篇日记将被删除 " + str(random.randint(1000, 9999))
        
        # 添加日记
        diary_id = self.manager.addDiary(user_id, spot_id, title, content)
        self.assertGreaterEqual(diary_id, 0, "添加日记应当返回有效的diary_id")
        
        # 删除日记
        deleted = self.manager.deleteDiary(user_id, diary_id)
        self.assertTrue(deleted, "删除日记应当成功")
        
        # 验证日记已被删除
        deleted_diary = self.manager.getDiary(diary_id)
        self.assertIsNone(deleted_diary, "删除的日记应当无法获取")
    
    def test_visit_diary(self):
        """测试浏览日记，增加浏览量的功能"""
        # 先添加一篇测试日记
        user_id = 1
        spot_id = 1
        title = "浏览测试日记 " + str(random.randint(1000, 9999))
        content = "这篇日记将被浏览 " + str(random.randint(1000, 9999))
        
        # 添加日记
        diary_id = self.manager.addDiary(user_id, spot_id, title, content)
        self.assertGreaterEqual(diary_id, 0, "添加日记应当返回有效的diary_id")
        self.test_diary_ids.append(diary_id)
        
        # 获取初始浏览量
        diary = self.manager.getDiary(diary_id)
        initial_visited = diary.get("visited_time", 0)
        
        # 浏览日记
        new_visited = self.manager.visitDiary(diary_id)
        
        # 验证浏览量是否增加
        self.assertGreater(new_visited, initial_visited, "浏览日记后浏览量应当增加")
        
        # 再次获取日记，验证浏览量是否更新
        updated_diary = self.manager.getDiary(diary_id)
        self.assertEqual(updated_diary["visited_time"], new_visited, "日记对象中的浏览量应当被更新")
    
    def test_rate_diary(self):
        """测试为日记评分的功能"""
        # 先添加一篇测试日记
        user_id = 1
        spot_id = 1
        title = "评分测试日记 " + str(random.randint(1000, 9999))
        content = "这篇日记将被评分 " + str(random.randint(1000, 9999))
        print(self.manager.diaryIo.currentId)
        print(self.manager.diaryIo.diary_count)
        # 添加日记
        diary_id = self.manager.addDiary(user_id, spot_id, title, content)
        self.assertGreaterEqual(diary_id, 0, "添加日记应当返回有效的diary_id")
        self.test_diary_ids.append(diary_id)
        
        # 为日记评分
        new_score = 4.5
        old_score = 0  # 假设初始评分为0
        updated_score = self.manager.rateDiary(diary_id, new_score, old_score)
        
        # 验证评分是否更新
        self.assertGreaterEqual(updated_score, 0, "评分应当成功")
        
        # 再次获取日记，验证评分是否更新
        updated_diary = self.manager.getDiary(diary_id)
        self.assertEqual(updated_diary["score"], updated_score, "日记对象中的评分应当被更新")
    
    def test_get_top_k_by_visited(self):
        """测试获取浏览量最高的K条日记"""
        # 设置获取前3条
        top_k = 3
        top_diaries = self.manager.getTopKByVisited(top_k)
        
        # 验证返回的数量
        self.assertLessEqual(len(top_diaries), top_k, "返回的日记数量应当不超过指定的K值")
        
        # 验证排序是否正确
        if len(top_diaries) > 1:
            for i in range(len(top_diaries) - 1):
                self.assertGreaterEqual(
                    top_diaries[i].get("visited_time", 0),
                    top_diaries[i+1].get("visited_time", 0),
                    "日记应当按浏览量降序排序"
                )
    
    def test_get_top_k_by_score(self):
        """测试获取评分最高的K条日记"""
        # 设置获取前3条
        top_k = 3
        top_diaries = self.manager.getTopKByScore(top_k)
        
        # 验证返回的数量
        self.assertLessEqual(len(top_diaries), top_k, "返回的日记数量应当不超过指定的K值")
        
        # 验证排序是否正确
        if len(top_diaries) > 1:
            for i in range(len(top_diaries) - 1):
                self.assertGreaterEqual(
                    top_diaries[i].get("score", 0),
                    top_diaries[i+1].get("score", 0),
                    "日记应当按评分降序排序"
                )
    
    def test_search_by_title(self):
        """测试搜索日记内容和标题的功能"""
        # 先添加一篇包含特定关键词的测试日记
        user_id = 1
        spot_id = 1
        keyword = "独特关键词" + str(random.randint(1000, 9999))
        title = f"搜索测试日记 {keyword}"
        content = f"这篇日记包含{keyword}作为关键词"
        
        # 添加日记
        diary_id = self.manager.addDiary(user_id, spot_id, title, content)
        self.assertGreaterEqual(diary_id, 0, "添加日记应当返回有效的diary_id")
        self.test_diary_ids.append(diary_id)
        
        # 搜索包含关键词的日记
        results = self.manager.searchByTitle(keyword)
        
        # 验证搜索结果
        self.assertGreater(len(results), 0, "应当能搜索到包含关键词的日记")
        
        # 验证结果中包含我们添加的日记
        found = False
        for diary in results:
            if diary["id"] == diary_id:
                found = True
                break
        self.assertTrue(found, "搜索结果中应当包含刚添加的包含关键词的日记")
        
        # 搜索一个不可能存在的关键词
        impossible_keyword = "不可能存在的关键词" + str(random.randint(10000, 99999))
        no_results = self.manager.searchByTitle(impossible_keyword)
        self.assertEqual(len(no_results), 0, "搜索不存在的关键词应当返回空列表")
    
    # def test_get_latest_diaries(self):
    #     """测试获取最新发布的日记的功能"""
    #     # 添加一篇带有当前时间的测试日记
    #     user_id = 1
    #     spot_id = 1
    #     current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     title = f"最新测试日记 {random.randint(1000, 9999)}"
    #     content = f"这是一篇发布于{current_time}的测试日记"
        
    #     # 添加日记
    #     diary_id = self.manager.addDiary(user_id, spot_id, title, content)
    #     self.assertGreaterEqual(diary_id, 0, "添加日记应当返回有效的diary_id")
    #     self.test_diary_ids.append(diary_id)
        
    #     # 获取最新日记
    #     latest_diaries = self.manager.getLatestDiaries(5)
        
    #     # 验证返回的结果
    #     self.assertGreater(len(latest_diaries), 0, "应当能获取到最新日记")
        
    #     # 验证我们添加的日记是否在结果中
    #     found = False
    #     for diary in latest_diaries:
    #         if diary["id"] == diary_id:
    #             found = True
    #             break
    #     self.assertTrue(found, "最新日记中应当包含刚添加的日记")
        
    #     # 验证日记是按日期降序排序的
    #     if len(latest_diaries) > 1:
    #         for i in range(len(latest_diaries) - 1):
    #             self.assertGreaterEqual(
    #                 latest_diaries[i].get("time", ""),
    #                 latest_diaries[i+1].get("time", ""),
    #                 "日记应当按日期降序排序"
    #             )
    
    def test_entry_exclusivity(self):
        """测试日记条目的独特性 - 确保哈希表搜索返回正确的结果"""
        # 添加两篇包含不同关键词的日记
        user_id = 1
        spot_id = 1
        
        # 第一篇日记 - 包含独特关键词A
        keyword_a = "独特关键词A" + str(random.randint(1000, 9999))
        title_a = f"测试日记A {keyword_a}"
        content_a = f"这篇日记包含{keyword_a}"
        diary_id_a = self.manager.addDiary(user_id, spot_id, title_a, content_a)
        self.test_diary_ids.append(diary_id_a)
        
        # 第二篇日记 - 包含独特关键词B
        keyword_b = "独特关键词B" + str(random.randint(1000, 9999))
        title_b = f"测试日记B {keyword_b}"
        content_b = f"这篇日记包含{keyword_b}"
        diary_id_b = self.manager.addDiary(user_id, spot_id, title_b, content_b)
        self.test_diary_ids.append(diary_id_b)
        
        # 搜索关键词A
        results_a = self.manager.searchByTitle(keyword_a)
        
        # 验证只包含关键词A的日记
        found_a = False
        found_b = False
        for diary in results_a:
            if diary["id"] == diary_id_a:
                found_a = True
            if diary["id"] == diary_id_b:
                found_b = True
                
        self.assertTrue(found_a, "搜索关键词A应当返回包含A的日记")
        self.assertFalse(found_b, "搜索关键词A不应当返回包含B的日记")
        
        # 搜索关键词B
        results_b = self.manager.searchByTitle(keyword_b)
        
        # 验证只包含关键词B的日记
        found_a = False
        found_b = False
        for diary in results_b:
            if diary["id"] == diary_id_a:
                found_a = True
            if diary["id"] == diary_id_b:
                found_b = True
                
        self.assertFalse(found_a, "搜索关键词B不应当返回包含A的日记")
        self.assertTrue(found_b, "搜索关键词B应当返回包含B的日记")

    def test_edge_cases(self):
        """测试边缘情况"""
        # 测试搜索空字符串
        empty_results = self.manager.searchByTitle("")
        self.assertEqual(len(empty_results), 0, "搜索空字符串应当返回空列表")
        
        # 测试获取不存在的日记
        self.assertIsNone(self.manager.getDiary(-9999), "获取不存在的日记ID应当返回None")
        
        # 测试传入非法参数给getTopKByVisited和getTopKByScore
        self.assertEqual(len(self.manager.getTopKByVisited(0)), 0, "K=0应当返回空列表")
        self.assertEqual(len(self.manager.getTopKByScore(0)), 0, "K=0应当返回空列表")
        
        # 测试删除不存在的日记
        self.assertFalse(self.manager.deleteDiary(1, -9999), "删除不存在的日记应当返回False")


if __name__ == "__main__":
    unittest.main()
