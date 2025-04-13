from flask import Blueprint

api = Blueprint('api', __name__)

from . import routes # 导入路由模块
