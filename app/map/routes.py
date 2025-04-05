from flask import render_template, request, redirect, url_for
from . import map #导入蓝图


@map.route('/')
def mapView():
    """显示地图页面"""
    return render_template('map.html')


@map.route('/api/scenic_spots')
def scenicSpots():
    """获取景点数据"""
    


@map.route('/api/poi')
def getPoi():
    """获取兴趣点数据"""
    
