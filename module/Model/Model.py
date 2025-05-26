import datetime
from module.data_structure.rb_tree import RedBlackTree
from module.data_structure.HuffmanTree import huffman_decoding,huffman_encoding
import os
class Diary:
    def __init__(self, diary_id: int, user_name: str, user_id: int, spot_id: int, content: str, title: str, 
                 images: list = None, videos: list = None, scoreToSpot: float = None, 
                 time: str = None, score: float = 0, score_count: int = 0, 
                 visited_time: int = 0, compressed: bool = False):
        """
        初始化日记对象。
        """
        self.id = diary_id
        self.user_name = user_name  # 用户名
        self.user_id = user_id
        self.spot_id = spot_id
        self.content = content
        self.title = title
        self.time = time if time else datetime.datetime.now().strftime("%Y-%m-%d")
        self.score = score
        self.score_count = score_count
        self.visited_time = visited_time
        self.img_list = images if images is not None else []
        self.video_path = videos if videos is not None else []  # 视频路径字段
        self.compressed = compressed
        self.scoreToSpot = scoreToSpot  # 对景点的评分

    def compress(self,codes):
        """
        对日记内容进行压缩。
        """
        # 检查内容中是否存在不在编码表中的字符，因为不更新哈夫曼树，所以是直接终止压缩
        for char in self.content:
            if char not in codes:
                return False
            
        if not self.compressed:
            self.content = huffman_encoding(self.content,None,codes)
            self.compressed = True
        # 写入压缩后的内容
        diary_content_dir = f"data/scenic_spots/spot_{self.spot_id}/diary_content"
        os.makedirs(diary_content_dir, exist_ok=True)
        compressed_filename = f"compressed_content_{self.id}.bin"
        full_path = os.path.join(diary_content_dir, compressed_filename)
        with open(full_path, "wb") as f:
            f.write(self.content)

        self.content = f"data/scenic_spots/spot_{self.spot_id}/diary_content/{compressed_filename}"  # 更新内容路径
        self.compressed = True
        return True

    def getContent(self,huffman_tree):
        """
        获取日记内容。
        """
        if self.compressed:
            content_path = self.content
            # 检查文件是否存在
            if not os.path.exists(content_path):
                return None
            with open(content_path, "rb") as f:
                compressed_content = f.read()
            # 解码内容
            decoded_content = huffman_decoding(compressed_content, huffman_tree)
            return decoded_content
        else:
            # 如果没有压缩，直接返回内容
            return self.content
        
    def to_dict(self) -> dict:
        """
        将日记对象转换为字典。
        """
        # 对日记的内容进行压缩存储


        return {
            "id": self.id,
            "user_name": self.user_name,
            "user_id": self.user_id,
            "spot_id": self.spot_id,
            "content": self.content,
            "title": self.title,
            "time": self.time,
            "score": self.score,
            "score_count": self.score_count,
            "visited_time": self.visited_time,
            "img_list": self.img_list,
            "video_path": self.video_path,
            "compressed": self.compressed,
            "scoreToSpot": self.scoreToSpot,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        从字典创建日记对象。
        """
        return cls(
            diary_id=data.get("id"),
            user_name=data.get("user_name", ""),
            user_id=data.get("user_id"),
            spot_id=data.get("spot_id"),
            content=data.get("content"),
            title=data.get("title"),
            time=data.get("time"),
            score=data.get("score", 0),
            score_count=data.get("score_count", 0),
            visited_time=data.get("visited_time", 0),
            images=data.get("img_list", []),
            videos=data.get("video_path", []),
            compressed=data.get("compressed", False),
            scoreToSpot=data.get("scoreToSpot")
        )
    def updateScore(self,newscore,oldscore):
        sum_score = self.score * self.score_count
        sum_score += newscore - oldscore

        if oldscore == 0:
            self.score_count += 1

        # 计算平均分
        if self.score_count > 0:
            self.score = round(sum_score / self.score_count, 1)
        else:
            self.score = 0

        return self.score

    def visited(self):
        """
        访问次数+1
        """
        self.visited_time += 1
    def delete(self):
        """
        删除日记
        """
        # 删除日记内容文件
        if self.compressed:
            content_path = self.content
            # 检查文件是否存在
            if os.path.exists(content_path):
                os.remove(content_path)
        # 删除图片文件：
        for img_path in self.img_list:
            if os.path.exists(img_path):
                os.remove(img_path)
        # 删除视频文件：
        for video_path in self.video_path:
            if os.path.exists(video_path):
                os.remove(video_path)
        # 删除日记对象
        del self


class Reviews:
    def __init__(self, total: int = 0, diary_ids: list = None):
        """
        初始化评论对象。
        """
        self.total = total
        self.diary_id_tree = RedBlackTree()  # 使用红黑树存储评论ID
        if diary_ids:  # 确保 diary_ids 不是 None 才进行迭代
            for diary_id in diary_ids:
                self.diary_id_tree.insert(diary_id, diary_id)

    def to_dict(self) -> dict:
        """
        将评论对象转换为字典。
        """
        return {
            "total": self.total,
            "diary_ids": self.diary_id_tree.get_all_keys()  # 获取所有评论ID
        }
    @classmethod
    def from_dict(cls, data: dict):
        """
        从字典创建评论对象。
        """
        # __init__ 方法将根据 diary_ids 列表处理 RedBlackTree 的创建和填充
        return cls(
            total=data.get("total", 0),
            diary_ids=data.get("diary_ids", [])  # 传递 diary_ids 列表
        )
    def getDiaryIds(self):
        """
        获取所有日记ID
        """
        return self.diary_id_tree.get_all_keys()
    def addOne(self, diary_id: int):
        """
        添加一篇日记
        """
        self.diary_id_tree.insert(diary_id, diary_id)
        self.total += 1
    def deleteOne(self, diary_id: int):
        """
        删除一篇日记
        """
        self.diary_id_tree.delete(diary_id)
        self.total -= 1

class User:
    def __init__(self, user_id: int, name: str, password: str, likes_type: list = None, 
                 reviews: Reviews = None, spot_marking: list = None, review_marking: list = None):
        """
        初始化用户对象。
        """
        self.id = user_id
        self.name = name
        self.password = password  # 存储哈希后的密码
        self.likes_type = likes_type if likes_type is not None else []
        self.reviews = reviews if reviews is not None else Reviews()
        self.spot_marking = spot_marking if spot_marking is not None else []
        self.review_marking = review_marking if review_marking is not None else RedBlackTree()

    def to_dict(self) -> dict:
        """
        将用户对象转换为字典。
        """
        reviews_marking_json = []
        lists =  self.review_marking.get_all_keys()
        for i in lists:
            item = {"id":i,"score":self.review_marking.search(i).value}
            reviews_marking_json.append(item)
        return {
            "id": self.id,
            "name": self.name,
            "password": self.password,
            "likes_type": self.likes_type,
            "reviews": self.reviews.to_dict(),
            "spot_marking": self.spot_marking,
            "review_marking": reviews_marking_json,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        从字典创建用户对象。
        """
        reviews_marking = RedBlackTree()
        for i in data["review_marking"]:
            reviews_marking.insert(i["id"], i["score"])
        return cls(
            user_id=data.get("id"),
            name=data.get("name"),
            password=data.get("password"),
            likes_type=data.get("likes_type", []),
            reviews=Reviews.from_dict(data.get("reviews", {})),
            spot_marking=data.get("spot_marking", []),
            review_marking=reviews_marking
        )
    
    def addDiary(self,diary):
        """
        用户增加一篇日记
        """
        self.reviews.addOne(diary.id)

    def deleteDiary(self,diary): 
        """
        用户删除一篇日记
        """
        
        self.reviews.deleteOne(diary.id)

    def diaryMarking(self,diary,score):
        oldscore = self.review_marking.search(diary.id)
        self.review_marking.insert(diary.id,score)
        return oldscore #通过返回旧分数来判断是否是第一次评分
    
    def getDiaryScore(self,diary_id):
        """
        获取用户对某篇日记的评分
        """
        if self.review_marking.search(diary_id) is not None:
            return self.review_marking.search(diary_id).value
        return 0

    def getDiaryList(self):
        """
        获取用户的日记列表
        """
        return self.reviews.getDiaryIds()


class Spot:
    def __init__(self, spot_id: int, name: str, score: float, spot_type: str, 
                 reviews: Reviews = None, url: str = None, img: str = None, 
                 info: list = None, introduce: dict = None, 
                 visited_time: int = 0, location: str = None):
        """
        初始化景点对象。
        """
        self.id = spot_id
        self.name = name
        self.score = score
        self.type = spot_type
        self.reviews = reviews if reviews is not None else Reviews()
        self.url = url
        self.img = img
        self.info = info if info is not None else []
        self.introduce = introduce if introduce is not None else {}
        self.visited_time = visited_time
        self.location = location

    def to_dict(self) -> dict:
        """
        将景点对象转换为字典。
        """
        return {
            "id": self.id,
            "name": self.name,
            "score": self.score,
            "type": self.type,
            "reviews": self.reviews.to_dict(),
            "url": self.url,
            "img": self.img,
            "info": self.info,
            "introduce": self.introduce,
            "visited_time": self.visited_time,
            "location": self.location,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        从字典创建景点对象。
        """
        return cls(
            spot_id=data.get("id"),
            name=data.get("name"),
            score=data.get("score", 0.0),
            spot_type=data.get("type"),
            reviews=Reviews.from_dict(data.get("reviews", {})),
            url=data.get("url"),
            img=data.get("img"),
            info=data.get("info", []),
            introduce=data.get("introduce", {}),
            visited_time=data.get("visited_time", 0),
            location=data.get("location")
        )
    
    def updateScore(self,newscore,oldscore):
        sum_score = self.score * self.reviews.total
        sum_score += newscore - oldscore

        if oldscore == 0:
            self.reviews.total += 1

        # 计算平均分
        if self.reviews.total > 0:
            self.score = round(sum_score / self.reviews.total, 1)
        else:
            self.score = 0

        return self.score

    def visited(self):
        """
        访问次数+1
        """
        self.visited_time += 1
        
    def addDiary(self,diary):
        """
        增加一篇日记
        """
        sum_score = self.score * self.reviews.total
        sum_score += diary.scoreToSpot - 0

        self.score = round(sum_score / (self.reviews.total + 1), 1)
        self.reviews.addOne(diary.id)
        return self.score

    def deleteDiary(self,diary):
        """
        删除一篇日记
        """
        sum_score = self.score * self.reviews.total
        sum_score -= diary.scoreToSpot
        self.score = round(sum_score / (self.reviews.total - 1), 1)
        self.reviews.deleteOne(diary.id)
        return self.score
    def getDiaryList(self):
        """
        景区的日记列表
        """
        return self.reviews.getDiaryIds()
