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

    return render_template('user_diaries.html', diaries=diaries, user=user)
    #return jsonify(diaries)


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

