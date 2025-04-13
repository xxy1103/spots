from flask import Flask, redirect, url_for, render_template
from app.map import map
from app.login import login
from app.api import api
from app.spots import spots
import os

app = Flask(__name__)


app.register_blueprint(map, url_prefix='/map')

app.register_blueprint(login,url_prefix="/login")

app.register_blueprint(api,url_prefix="/api")

app.register_blueprint(spots, url_prefix='/spots')

# 设置密钥，在生产环境应使用随机生成的强密钥
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# 配置会话，默认过期时间30分钟
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 单位：秒


@app.errorhandler(404)
def page_not_found(e):
    """处理 404 错误，重定向到登录页面"""
    # 'login.loginView' 指向 login 蓝图中的 loginView 函数
    return redirect(url_for('login.loginView')) 