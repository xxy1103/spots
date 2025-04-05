from flask import Blueprint

map = Blueprint('map', __name__)

from . import routes # 导入路由模块
