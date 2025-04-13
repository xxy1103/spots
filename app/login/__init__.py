from flask import Blueprint

login = Blueprint('login', __name__)

from . import routes # 导入路由模块