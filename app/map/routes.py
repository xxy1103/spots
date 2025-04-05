from flask import render_template, request, redirect, url_for
from . import map #导入蓝图


@map.route('/')
def map_view():
    """显示地图页面"""
    return render_template('map.html')


