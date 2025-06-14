from flask import Flask, redirect, url_for, render_template, send_from_directory
from app.map import map
from app.login import login
from app.api import api
from app.spots import spots
from app.diary import diary
import os

app = Flask(__name__)

# 移除文件上传大小限制
app.config['MAX_CONTENT_LENGTH'] = None  # 不限制上传文件大小
app.config['MAX_CONTENT_PATH'] = None    # 不限制上传路径长度

# 注册蓝图
app.register_blueprint(map, url_prefix='/map')

app.register_blueprint(login,url_prefix="/login")

app.register_blueprint(api,url_prefix="/api")

app.register_blueprint(spots, url_prefix='/spots')

app.register_blueprint(diary, url_prefix='/diary')

# 旅游日记的蓝图注册
# app.register_blueprint(diary,url_prefix='/diary')

# 设置密钥，在生产环境应使用随机生成的强密钥
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# 配置会话，默认过期时间30分钟
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 单位：秒

# 提供外部静态资源的路由
@app.route('/<path:filename>')
def external_static(filename):
    # 指定外部静态资源的根目录，例如指向data目录
    external_static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    return send_from_directory(external_static_folder, filename)

@app.errorhandler(404)
def page_not_found(e):
    """处理 404 错误，重定向到登录页面"""
    # 'login.loginView' 指向 login 蓝图中的 loginView 函数
    return redirect(url_for('login.loginView'))

if __name__ == '__main__':
    print("Flask应用启动中...")
    print(f"访问地址: http://localhost:5000")
    print("日记搜索页面: http://localhost:5000/diary/search")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)