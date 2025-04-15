from flask import render_template, request, redirect, url_for
from . import login #导入蓝图



@login.route('/')
def loginView():
    """显示登录页面"""
    return render_template('login.html')

@login.route('/register')
def registerView():
    """显示注册页面"""
    return render_template('register.html')

