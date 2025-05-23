from flask import render_template, request, redirect, url_for, jsonify, make_response, session
from . import spots
from app.api.routes import login_required # 导入登录验证装饰器
from module.Spot_class import spotManager # 导入景点管理模块


@spots.route('/')
@login_required  # 使用这个装饰器来验证cookie和session
def index():
    return render_template('index.html')

@spots.route('/search')
@login_required  # 使用这个装饰器来验证cookie和session
def search():
    return render_template('spotSearch.html')

@spots.route('/spot_info/<id>')
@login_required  # 使用这个装饰器来验证cookie和session
def spot(id):
    # 获取请求参数 (这里是路径参数 id)
    # 可以选择在这里根据 id 获取景点信息
    try:
        spot_id = int(id) # 尝试将 id 转换为整数
        spotManager.addVisitedTime(spot_id) # 增加访问次数
        spot = spotManager.getSpot(spot_id) # 使用 spotManager 获取景点数据
        if spot is None:
            # 如果找不到景点，可以返回 404 页面或错误信息
            return render_template('404.html'), 404 
        
    except ValueError:
        # 如果 id 不是有效的整数
        return render_template('error.html', message="无效的景点ID格式"), 400
    except Exception as e:
        # 处理其他可能的错误
        print(f"Error fetching spot data: {e}") # 记录错误日志
        return render_template('error.html', message="获取景点信息时出错"), 500

    # 将获取到的景点数据传递给模板
    return render_template('spot_info.html', spot=spot) # 将整个 spot 字典传递过去

