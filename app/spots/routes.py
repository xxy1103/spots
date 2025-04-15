from flask import render_template, request, redirect, url_for, jsonify, make_response, session
from . import spots
from app.api.routes import login_required # 导入登录验证装饰器


@spots.route('/')
@login_required  # 使用这个装饰器来验证cookie和session
def index():
    return render_template('index.html')

@spots.route('/search')
@login_required  # 使用这个装饰器来验证cookie和session
def search():
    return render_template('spotSearch.html')

