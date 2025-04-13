from flask import render_template, request, redirect, url_for,g
from . import map #导入蓝图
from app.api.routes import login_required # 导入登录验证装饰器

@map.route('/')
@login_required
def mapView():
    """显示地图页面"""
    return render_template('map.html')


@map.route('/api/scenic_spots')
def scenicSpots():
    """获取景点数据"""
    


@map.route('/api/poi')
def getPoi():
    """获取兴趣点数据"""
    
