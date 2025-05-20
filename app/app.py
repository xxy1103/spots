from flask import Flask, redirect, url_for, render_template
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


@app.errorhandler(404)
def page_not_found(e):
    """处理 404 错误，重定向到登录页面"""
    # 'login.loginView' 指向 login 蓝图中的 loginView 函数
    return redirect(url_for('login.loginView'))