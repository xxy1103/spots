from flask import render_template,jsonify, request, redirect, url_for,g
from . import diary  # 导入蓝图
from app.api.routes import login_required # 导入登录验证装饰器
import os
from werkzeug.utils import secure_filename
import time
from module.user_class import userManager as user_manager
from module.diary_class import diaryManager as diary_manager
from module.Spot_class import spotManager as spot_manager
import module.printLog as log
from module.data_structure.quicksort import quicksort



@diary.route('/user/<int:user_id>', methods=['GET']) 
@login_required
# 获取用户的日记列表
def get_user_diaries(user_id):
    """
    获取用户的日记列表
    """
    user = user_manager.getUser(user_id)
    if not user:
        return render_template('error.html', message="用户不存在")
      # diaries_id = user["reviews"]["diary_ids"]
    diaries_id = user.reviews.getDiaryIds()
    diaries = []
    for diary_id in diaries_id:
        diary = diary_manager.getDiary(diary_id)
        diary_json = diary.to_dict()
        diary_json["content"] = diary_manager.getDiaryContent(diary_id)
        if diary:
            diaries.append(diary_json)

    # 判断是否为当前登录用户
    is_current_user = g.user and g.user["user_id"] == user_id

    return render_template('user_diaries.html', diaries=diaries, user=user, is_current_user=is_current_user)
    #return jsonify(diaries)

@diary.route('/spot/<int:spot_id>', methods=['GET'])
@login_required
# 获取景点的日记列表
def get_spot_diaries(spot_id):
    """
    获取景点的日记列表
    """

    

    spot = spot_manager.getSpot(spot_id)
    if not spot:
        return render_template('error.html', message="景点不存在")

    diaries_id = spot_manager.spotDiaryHeapArray[spot_id - 1].getTopK(100)  # 确保堆中的数据是最新的
    diaries = []
    for diary_id in diaries_id:
        diary = diary_manager.getDiary(diary_id["id"])
        if diary:
            diary_json = diary.to_dict()
            diary_json["content"] = diary_manager.getDiaryContent(diary_id["id"])
            diary_json["spot_name"] = spot.name
            diaries.append(diary_json)
    return jsonify(diaries)


@diary.route('<int:diary_id>', methods=['GET'])
@login_required
# 获取日记的详细信息
def get_diary(diary_id):
    """
    获取日记的详细信息
    """
    diary = diary_manager.getDiary(diary_id)
    
    if not diary:
        return render_template('error.html', message="日记不存在")
    # 获取作者信息
    diary_manager.visitDiary(diary_id)
    user = user_manager.getUser(diary.user_id)
    if not user:
        return render_template('error.html', message="用户不存在")

    diary_json = diary.to_dict()
    diary_json["content"] = diary_manager.getDiaryContent(diary_id)
    diary_json["spot_name"] = spot_manager.getSpot(diary.spot_id).name

    log.writeLog(diary.video_path)

    return render_template('diary_detail.html', diary=diary_json, user=user)


# 以上改完
@diary.route('/<int:diary_id>', methods=['DELETE', 'POST']) # 支持 DELETE 和 POST 请求
@login_required
def delete_diary(diary_id):
    """
    删除日记
    """
    # 如果是 POST 请求，检查是否是模拟的 DELETE 请求
    if request.method == 'POST' and request.form.get('_method') == 'DELETE':
        # 继续处理为 DELETE 请求
        pass
        
    user_id = g.user["user_id"]
    diary = diary_manager.getDiary(diary_id)
    score = diary.scoreToSpot
    spot_id = diary.spot_id
    spot = spot_manager.getSpot(spot_id)
    user = user_manager.getUser(user_id)
    if not diary:
        return render_template('error.html', message="日记不存在")

    if diary.user_id != user_id:
        return render_template('error.html', message="无权限删除该日记")
    # 删除日记
    diary_manager.deleteDiary(user_id,diary_id)
    newscore = spot.deleteDiary(diary)
    spot_manager.updateScore(spot_id, newscore)
    user.deleteDiary(diary)

    return redirect(url_for('diary.get_user_diaries', user_id=user_id))


@diary.route('/recommend/user/<int:user_id>', methods=['GET'])
@login_required
def get_recommendations(user_id):
    """
    获取用户的推荐内容
    """
    topK = request.args.get('topK', default=10, type=int)
    recommendations = user_manager.getRecommendDiaries(user_id,topK=topK)
    if recommendations is None:
        return render_template('error.html', message="用户不存在或推荐内容为空")
    if not recommendations:
        return render_template('error.html', message="未找到推荐内容")
    
    # 将推荐内容转换为字典列表
    recommendations = [diary.to_dict() for diary in recommendations]
    # 获取每个日记的内容
    for diary in recommendations:
        diary["content"] = diary_manager.getDiaryContent(diary["id"])
        diary["spot_name"] = spot_manager.getSpot(diary["spot_id"]).name

    return jsonify(recommendations)


@diary.route("/add", methods=["POST"])
@login_required
# 添加新的日记
def add_diary():
    """
    添加新的日记
    """
    user_id = g.user["user_id"]
    spot_id = request.form.get("spot_id", type=int)
    spot_marking = request.form.get("spot_marking", default=0, type=float)
    # 确保评分在合理范围内
    if spot_marking is None or spot_marking < 0:
        spot_marking = 0
    elif spot_marking > 5:
        spot_marking = 5
    
    title = request.form.get("title")
    content = request.form.get("content")
    
    if not spot_id or not title or not content:
        return render_template('error.html', message="请填写完整信息")

    spot = spot_manager.getSpot(spot_id)


    
    # 处理图片文件
    images = request.files.getlist("images")
    image_paths = []
    
    if images and images[0].filename != '':
        # 确保目录存在
        image_dir = f"data/scenic_spots/spot_{spot_id}/images"
        os.makedirs(image_dir, exist_ok=True)
        
        for image in images:
            if image and image.filename:
                # 生成唯一文件名，避免冲突
                timestamp = int(time.time() * 1000)
                filename = f"{timestamp}_{secure_filename(image.filename)}"
                file_path = image_dir + "/" + filename
                image.save(file_path)
                image_paths.append(file_path)
    
    # 处理视频文件（支持多个视频）
    videos = request.files.getlist("videos")
    video_paths = []

    if videos and videos[0].filename != '':
        # 确保目录存在
        video_dir = f"data/scenic_spots/spot_{spot_id}/videos"
        os.makedirs(video_dir, exist_ok=True)

        for video in videos:
            if video and video.filename:
                # 生成唯一文件名，避免冲突
                timestamp = int(time.time() * 1000)
                filename = f"{timestamp}_{secure_filename(video.filename)}"
                file_path = video_dir + "/" + filename
                video.save(file_path)
                video_paths.append(file_path)
    # 添加日记
    user = user_manager.getUser(user_id)
    spot = spot_manager.getSpot(spot_id)
    diary = diary_manager.addDiary(user, spot, title, content, images=image_paths, videos=video_paths, scoreToSpot=spot_marking)

    user.addDiary(diary)
    newscore = spot.addDiary(diary)
    # 更新景点评分
    spot_manager.updateScore(spot_id, newscore)
    if diary is None:
        return render_template('error.html', message="添加日记失败")
    
    # 打印调试
    spot = spot_manager.getSpot(spot_id)
    log.writeLog(spot.to_dict())
    # 用户
    user = user_manager.getUser(user_id)
    log.writeLog(user.to_dict())

    # 重定向到日记详情页
    return redirect(url_for('diary.get_diary', diary_id=diary.id))

@diary.route("/<int:diary_id>/user_marking", methods=["GET"])
@login_required
def get_diary_marking(diary_id):
    """
    获取日记的评分信息
    """
    user = user_manager.getUser(g.user["user_id"])
    return jsonify({
        "score": user.getDiaryScore(diary_id) 
    })

@diary.route("/add", methods=["GET"])
@login_required
def add_diary_page():
    """
    显示添加日记的页面
    """
    from module.Spot_class import spotManager
    
    # 获取所有景点信息用于选择
    spots = spotManager.spots
    
    return render_template('diary_add.html', spots=spots)


@diary.route("/<int:diary_id>/marking", methods=["POST"])
@login_required
def add_diary_marking(diary_id):
    """
    添加日记的评分
    """

    score = request.form.get("score", default=0, type=float)

    # 确保评分在合理范围内
    if score <= 0 or score > 5:
        return render_template('error.html', message="评分必须大于0小于等于5")
    user_id = g.user["user_id"]
    # 在用户的评分中添加评分，同时查询是否有旧评分
    oldscore = user_manager.markingReview(user_id, diary_id, score)

    # 跟新索引和日记类中的评分
    diary_manager.rateDiary(diary_id, score, oldscore)

    return redirect(url_for('diary.get_diary', diary_id=diary_id))

@diary.route("/search", methods=["GET"])
@login_required
def search_diary():
    """
    搜索日记 - 优化版本，支持分页和性能优化
    """
    keyword = request.args.get("keyword", default="", type=str)
    user_id = g.user["user_id"]
    search_type = request.args.get("type", default="title", type=str)
    sort_by = request.args.get("sort_by", default="value1", type=str) # value1表示默认排序，value2表示按热度排序
    
    # 添加分页参数
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)  # 每页显示20个日记
    is_ajax = request.args.get("ajax", default="", type=str) == "1"  # 判断是否为AJAX请求    # 获取搜索结果
    if keyword != "":
        match search_type:
            case "title":
                diaries = diary_manager.searchByTitle(keyword)
            case "content":
                diaries = diary_manager.searchByContent(keyword, 100)  # 增加搜索数量限制
            case "user":
                user = user_manager.searchUser(keyword) # 只支持精确查找
                if user is None:
                    diaries = []
                else:
                    user = user_manager.getUser(user["id"])
                    diaries_id = user.getDiaryList()
                    diaries = [diary_manager.getDiary(diary_id) for diary_id in diaries_id]
            case "spot":
                spots = spot_manager.getSpotByName(keyword)
                if len(spots) == 0:
                    diaries = []
                else:
                    diaries = []
                    for i in spots:
                        spot = spot_manager.getSpot(i["id"])
                        diaries_id = spot.getDiaryList()
                        for diary_id in diaries_id:
                            diaries.append(diary_manager.getDiary(diary_id))
            case _: # 上面的搜索方法全部搜索一遍
                diaries = []
                diaries.extend(diary_manager.searchByTitle(keyword))
                diaries.extend(diary_manager.searchByContent(keyword))
                user = user_manager.searchUser(keyword)
                if user is not None:
                    user = user_manager.getUser(user["id"])
                    diaries_id = user.getDiaryList()
                    for diary_id in diaries_id:
                        diaries.append(diary_manager.getDiary(diary_id))
                spots = spot_manager.getSpotByName(keyword)
                if len(spots) != 0:
                    for i in spots:
                        spot = spot_manager.getSpot(i["id"])
                        diaries_id = spot.getDiaryList()
                        for diary_id in diaries_id:
                            diaries.append(diary_manager.getDiary(diary_id))
                            
        # 转换为字典格式并去重
        diaries_dict = {}
        for diary in diaries:
            if diary and diary.id not in diaries_dict:
                diaries_dict[diary.id] = {
                    "title": diary.title,
                    "content": diary_manager.getDiaryContent(diary.id)[:200] + "..." if len(diary_manager.getDiaryContent(diary.id)) > 200 else diary_manager.getDiaryContent(diary.id),  # 限制内容长度
                    "user": diary.user_id,
                    "spot": diary.spot_id,
                    "value1": diary.score,
                    "value2": diary.visited_time,
                    "id": diary.id,
                    "img_list": diary.img_list[:3] if diary.img_list else [],  # 只加载前3张图片
                    "video_list": diary.video_path[:2] if diary.video_path else [],  # 只加载前2个视频
                    "scoreToSpot": diary.scoreToSpot,
                    "time": diary.time,
                }
        diaries_json = list(diaries_dict.values())
        
    else:
        # 如果没有搜索关键词，只获取前100个日记进行初始显示
        all_diaries = diary_manager.getAllDiaries()
        diaries_dict = {}
        for diary in all_diaries[:100]:  # 限制初始加载数量
            if diary:
                diaries_dict[diary.id] = {
                    "title": diary.title,
                    "content": diary_manager.getDiaryContent(diary.id)[:200] + "..." if len(diary_manager.getDiaryContent(diary.id)) > 200 else diary_manager.getDiaryContent(diary.id),
                    "user": diary.user_id,
                    "spot": diary.spot_id,
                    "value1": diary.score,
                    "value2": diary.visited_time,
                    "id": diary.id,
                    "img_list": diary.img_list[:3] if diary.img_list else [],
                    "video_list": diary.video_path[:2] if diary.video_path else [],
                    "scoreToSpot": diary.scoreToSpot,
                    "time": diary.time,
                }
        diaries_json = list(diaries_dict.values())

    # 排序
    sorted_diaries = quicksort(diaries_json, sort_by)
    
    # 计算分页信息
    total_count = len(sorted_diaries)
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    page_diaries = sorted_diaries[start_index:end_index]
    
    # 构造分页信息
    pagination_info = {
        'page': page,
        'per_page': per_page,
        'total': total_count,
        'pages': (total_count + per_page - 1) // per_page,
        'has_prev': page > 1,
        'has_next': end_index < total_count,
        'prev_num': page - 1 if page > 1 else None,
        'next_num': page + 1 if end_index < total_count else None
    }
    
    # 如果是AJAX请求，只返回JSON数据
    if is_ajax:
        return jsonify({
            'success': True,
            'diaries': page_diaries,
            'pagination': pagination_info
        })
    
    # 返回搜索结果
    return render_template('diary_search.html', 
                         diaries=page_diaries, 
                         keyword=keyword, 
                         user_id=user_id,
                         pagination=pagination_info,
                         total_count=total_count)