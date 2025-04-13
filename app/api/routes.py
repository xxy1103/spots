from flask import render_template, request, redirect, url_for, jsonify, make_response, session
from . import api
from module.user_class import User
from module.fileIo import UserIo
import json
import secrets

# 创建User实例
userIo = UserIo()
user_manager = User(userIo=userIo)

@api.route('/login', methods=['POST'])
def login():
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
            'user_id': user_info['id'],
            'username': user_info['name']
        }
        
        return response
    else:
        # 登录失败
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        }), 401  # 返回401未授权状态码
    


from functools import wraps

def login_required(f):
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

# filepath: d:\windows\desktop\数据结构课设\个性化旅游系统\app\api\routes.py
# ... (import statements and existing code) ...
from flask import g # 确保导入 g

# ... (existing routes like /login, login_required, /user-profile, /logout) ...

@api.route('/check-session', methods=['GET'])
@login_required  # 使用这个装饰器来验证cookie和session
def check_session():
    """
    检查当前是否存在有效的用户会话。
    如果 login_required 验证通过，说明用户已登录。
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
    # 获取cookie中的session_token
    session_token = request.cookies.get('user_session')
    
    # 如果存在token，则从会话中删除
    if session_token and session_token in session:
        session.pop(session_token, None)
    
    # 创建响应
    response = make_response(redirect(url_for('login.login_page')))
    
    # 删除cookie
    response.delete_cookie('user_session')
    
    return response

# ... (imports and other routes) ...

@api.route('/register', methods=['POST'])
def register():
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

