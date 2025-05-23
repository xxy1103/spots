from flask import render_template, request, redirect, url_for, jsonify, make_response, session
from . import api
from module.user_class import userManager as user_manager
from module.Spot_class import spotManager as spot_manager
from module.data_structure.quicksort import quicksort
import json
import secrets
from flask import g
from functools import wraps

# 创建User实例



@api.route('/login', methods=['POST'])
def login():
    """
    处理用户登录请求。

    **请求方法:** POST
    **请求类型:** JSON
    **请求参数:**
      - `username` (str): 用户名
      - `password` (str): 密码

    **返回数据格式 (成功 - 200 OK):**
    ```json
    {
        "success": True,
        "message": "登录成功"
    }
    ```
    成功登录后，会在响应中设置一个名为 `user_session` 的HTTPOnly Cookie。

    **返回数据格式 (失败 - 401 Unauthorized):**
    ```json
    {
        "success": False,
        "message": "用户名或密码错误"
    }
    ```
    """
    # 获取JSON数据而非表单数据
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # 调用user_class.py中的loginUser方法验证用户
    user_info = user_manager.loginUser(username, password)
    
    if user_info:
        # 生成会话令牌
        session_token = secrets.token_hex(16)
        
        # 创建响应对象
        response = make_response(jsonify({
            'success': True,
            'message': '登录成功'
        }))
        
        # 设置安全的Cookie，过期时间为30分钟
        # httponly=True 防止JavaScript访问cookie
        # secure=True 仅在HTTPS连接时发送（生产环境开启）
        response.set_cookie(
            'user_session', 
            session_token, 
            max_age=1800,  # 30分钟
            httponly=True,
            # secure=True,  # 在生产环境启用
            samesite='Lax'
        )
        
        # 在服务器端会话中存储用户信息，关联到令牌
        session[session_token] = {
            'user_id': user_info.id,
            'username': user_info.name,
        }
        
        return response
    else:
        # 登录失败
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        }), 401  # 返回401未授权状态码
    
def login_required(f):
    """
    一个装饰器，用于保护需要用户登录才能访问的路由。

    它会检查请求的Cookie中是否存在名为 `user_session` 的有效会话令牌，
    并验证该令牌是否存在于服务器端的会话存储中。

    **行为:**
      - **验证成功:** 将当前用户信息（从服务器会话中获取）存储在 `flask.g.user` 中，
        然后继续执行被装饰的视图函数。
      - **验证失败 (API路由, e.g., /api/...)**: 返回一个JSON响应，状态码为401。
        ```json
        {
            "success": False,
            "message": "请先登录"
        }
        ```
      - **验证失败 (页面路由)**: 重定向到登录页面 (通过 `url_for('login.loginView')`)。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取cookie中的session_token
        session_token = request.cookies.get('user_session')
        
        # 检查token是否在服务器会话中
        if not session_token or session_token not in session:
            # API路由返回JSON响应
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'message': '请先登录'
                }), 401
            # 页面路由重定向到登录页
            else:
                return redirect(url_for('login.loginView'))
        
        # 将用户信息添加到g对象，方便视图函数访问
        g.user = session[session_token]
        return f(*args, **kwargs)
    return decorated_function




@api.route('/check-session', methods=['GET'])
@login_required  # 使用这个装饰器来验证cookie和session
def check_session():
    """
    检查当前是否存在有效的用户会话。
    此路由受 `login_required` 装饰器保护。

    **请求方法:** GET
    **请求参数:** 无 (依赖 `user_session` Cookie 进行验证)

    **返回数据格式 (成功 - 200 OK, 会话有效):**
    ```json
    {
        "success": True,
        "message": "会话有效",
        "user": {
            "username": "current_username"
        }
    }
    ```

    **返回数据格式 (失败 - 401 Unauthorized, 会话无效或未登录):**
    (由 `login_required` 装饰器处理)
    ```json
    {
        "success": False,
        "message": "请先登录"
    }
    ```
    """
    # 如果代码执行到这里，说明login_required验证成功
    # g.user 已经被 login_required 设置
    return jsonify({
        'success': True,
        'message': '会话有效',
        'user': { # 可以选择性返回一些用户信息
            'username': g.user.get('username')
        }
    })

# 注意：login_required 装饰器在验证失败时会自动返回 401 JSON 响应或重定向
# 所以如果会话无效，这个函数体不会执行，前端会收到 401 错误


@api.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    处理用户登出请求。
    清除服务器端的会话信息并删除客户端的会话cookie。

    **请求方法:** GET, POST
    **请求参数:** 无 (依赖 `user_session` Cookie)

    **返回数据格式 (成功 - 200 OK):**
    ```json
    {
        "success": True,
        "message": "已成功登出"
    }
    ```
    成功登出后，会删除名为 `user_session` 的Cookie。
    """
    # 获取cookie中的session_token
    session_token = request.cookies.get('user_session')
    
    # 如果存在token，则从会话中删除
    if session_token and session_token in session:
        session.pop(session_token, None)
    
    # --- 修改这里 ---
    # 创建 JSON 响应
    response = make_response(jsonify({
        'success': True,
        'message': '已成功登出'
    }))
    
    # 删除cookie (确保路径和域匹配设置时的值，如果设置过的话)
    # 如果设置cookie时未指定path/domain，则默认 '/' 和当前域，通常无需指定
    response.delete_cookie('user_session', path='/') # 显式指定 path='/' 通常更安全
    
    return response



@api.route('/register', methods=['POST'])
def register():
    """
    处理用户注册请求。
    接收用户名、密码和兴趣标签，创建新用户。

    **请求方法:** POST
    **请求类型:** JSON
    **请求参数:**
      - `username` (str): 用户希望注册的用户名。
      - `password` (str): 用户设置的密码。
      - `selectedTags` (list of str): 用户选择的兴趣标签列表。

    **返回数据格式 (成功 - 200 OK):**
    ```json
    {
        "success": True,
        "message": "注册成功"
    }
    ```

    **返回数据格式 (失败 - 400 Bad Request, 无效输入):**
    ```json
    {
        "success": False,
        "message": "无效的请求数据" 
    }
    ```
    或
    ```json
    {
        "success": False,
        "message": "缺少必要的注册信息"
    }
    ```
    或
    ```json
    {
        "success": False,
        "message": "兴趣标签格式错误"
    }
    ```

    **返回数据格式 (失败 - 409 Conflict, 用户名已存在):**
    ```json
    {
        "success": False,
        "message": "注册失败，用户名可能已存在"
    }
    ```
    """
    # --- 修改这里：从 request.json 获取数据 ---
    data = request.get_json() 
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400

    username = data.get("username")
    password = data.get("password")
    liketype = data.get("selectedTags") # 前端发送的是数组

    # --- 基本验证 ---
    if not username or not password or not liketype:
         return jsonify({'success': False, 'message': '缺少必要的注册信息'}), 400
    if not isinstance(liketype, list): # 确保 liketype 是列表
         return jsonify({'success': False, 'message': '兴趣标签格式错误'}), 400
    # --- 验证结束 ---

    # 调用user_class.py中的addUser方法添加用户
    # 假设 addUser 现在接收一个列表作为 liketype
    if user_manager.addUser(username, password, liketype): 
        return jsonify({
            'success': True,
            'message': '注册成功'
        }) # 成功时默认返回 200 OK
    else:
        return jsonify({
            'success': False,
            'message': '注册失败，用户名可能已存在' # 更具体的错误信息可能来自 addUser 方法
        }), 409 # 409 Conflict 更适合表示资源已存在

@api.route('/recommended-spots', methods=['GET'])
@login_required  # 确保用户已登录
def recommended_spots():
    """
    获取推荐的旅游景点。
    根据当前登录用户的兴趣标签返回推荐的景点列表。
    此路由受 `login_required` 装饰器保护。

    **请求方法:** GET
    **请求参数:** 无 (依赖 `user_session` Cookie 进行用户识别)

    **返回数据格式 (成功 - 200 OK):**
    ```json
    {
        "success": True,
        "spots": [
            {
                "name": "景点名称",
                "id": "景点ID",
                "score": 4.5, // 评分
                "type": "景点类型",
                "visited_time": 100, // 游览次数/热度
                "img": "image_url.jpg" // 图片链接
                // ... 其他景点相关字段
            },
            // ...更多景点对象
        ]
    }
    ```
    如果用户没有对应的推荐或推荐列表为空，`spots` 数组可能为空。

    **返回数据格式 (失败 - 401 Unauthorized, 未登录):**
    (由 `login_required` 装饰器处理)
    ```json
    {
        "success": False,
        "message": "请先登录"
    }
    ```
    """
    user = g.user
    user_id = user['user_id']
    
    # 1. 获取原始推荐景点数据
    # 假设 getRecommendSpots 返回一个列表，其中每个元素是包含景点信息的字典或对象
    raw_recommended_spots = user_manager.getRecommendSpots(user_id,10) 

    # 2. 处理数据，只选择需要的字段 (例如 'name' 和 'description')
    filtered_spots = []
    if raw_recommended_spots: # 确保列表不为空
        for spot in raw_recommended_spots:
            # 假设 spot 是一个对象
            spot = spot_manager.getSpot(spot['id'])  
            filtered_spot = {
                'name': spot.name,  # 假设原始数据是字典
                'id': spot.id,  # 假设原始数据是字典
                'score': spot.score,  # 假设原始数据是字典
                'type': spot.type,  # 假设原始数据是字典
                'visited_time': spot.visited_time,  # 假设原始数据是字典
                'img': spot.img,  # 假设原始数据是字典
                # 添加其他你需要的字段
            }
            filtered_spots.append(filtered_spot)

    # 3. 返回处理后的数据
    # 遵循前端期望的格式 {'success': True, 'spots': [...]}
    return jsonify({
        'success': True, 
        'spots': filtered_spots
    })



@api.route('/search-spots', methods=['GET'])
@login_required  # 确保用户已登录
def search_spots():
    """
    根据用户输入的关键词、景点类型和排序方式搜索景点。
    返回符合条件的景点列表。
    此路由受 `login_required` 装饰器保护。

    **请求方法:** GET
    **请求参数 (Query Parameters):**
      - `keyword` (str, 可选): 用于搜索景点名称的关键词。
      - `type` (str, 可选): 用于筛选特定类型的景点。
      - `exclude_type` (str, 可选): 用于排除特定类型的景点。
      - `min_score` (float, 可选): 最低评分。
      - `max_score` (float, 可选): 最高评分。
      - `user_preference` (bool, 可选): 是否使用用户偏好推荐。
      - `sort_by` (str, 可选, 默认值: 'default'): 排序依据。
        可选值: 'default' (默认排序), 'popularity_desc' (按热度降序)。

    **返回数据格式 (成功 - 200 OK):**
    ```json
    {
        "success": True,
        "spots": [
            {
                "name": "景点名称",
                "id": "景点ID",
                "score": 4.5,
                "type": "景点类型",
                "visited_time": 120,
                "img": "image_url.jpg"
                // ... 其他景点相关字段
            },
            // ...更多景点对象
        ]
    }
    ```
    如果未找到匹配的景点，`spots` 数组可能为空。

    **返回数据格式 (失败 - 401 Unauthorized, 未登录):**
    (由 `login_required` 装饰器处理)
    ```json
    {
        "success": False,
        "message": "请先登录"
    }
    ```
    """
    # 获取所有查询参数
    keyword = request.args.get('keyword')
    spot_type = request.args.get('type')
    exclude_type = request.args.get('exclude_type')
    min_score = request.args.get('min_score')
    max_score = request.args.get('max_score')
    user_preference = request.args.get('user_preference', 'false').lower() == 'true'
    sort_by = request.args.get('sort_by', default='default')

    # 1. 获取景点列表的初始数据集
    if keyword:
        spots = spot_manager.getSpotByName(keyword)
        spots = quicksort(spots, sort_key="value1")  # 按评分排序
    elif user_preference:
        # 基于用户偏好推荐景点
        user = g.user
        user_id = user['user_id']
        spots = user_manager.getRecommendSpots(user_id)
    elif spot_type:
        # 直接使用Spot类的方法获取特定类型的景点
        spots = spot_manager.getTopKByType(spot_type, k=-1)  # 获取所有景点
    else:
        # 获取所有景点
        spots = spot_manager.getAllSpotsSorted()
    
    # 2. 应用过滤条件
    # 初始化一个空列表存储经过完整处理的景点
    processed_spots = []
    if spots:
        for spot_id in spots:
            # 获取完整的景点信息
            spot = spot_manager.getSpot(spot_id['id'])
            
            # 应用过滤条件
            # 2.1 排除特定类型
            if exclude_type and spot.type == exclude_type:
                continue
                
            # 2.2 根据类型过滤
            if spot_type and spot.type != spot_type:
                continue
                
            # 2.3 根据评分范围过滤
            spot_score = float(spot.score)
            if min_score and spot_score < float(min_score):
                continue
            if max_score and spot_score > float(max_score):
                continue
                
            # 添加通过过滤的景点到结果中
            processed_spots.append({
                'name': spot.name,
                'id': spot.id,
                'value1': spot.score,
                'type': spot.type,
                'value2': spot.visited_time,
                'img': spot.img,
                'info': spot.info
            })
    
    # 3. 排序
    if sort_by == 'popularity_desc':
        processed_spots = quicksort(processed_spots, sort_key="value2")

    # 4. 返回结果
    return jsonify({
        'success': True, 
        'spots': processed_spots
    })


