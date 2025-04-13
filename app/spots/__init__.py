from flask import Blueprint

spots = Blueprint('spots', __name__)

from . import routes # 导入路由模块
