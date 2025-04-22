from flask import render_template, request, redirect, url_for,g,jsonify
from . import map #导入蓝图
from app.api.routes import login_required # 导入登录验证装饰器
from module.Spot_class import spotManager
from module.map import map as map_module # 导入地图模块, 重命名避免与蓝图冲突
from module.data_structure.merge import merge_sort


POI_types = ["餐厅","超市","酒店","加油站","停车场","医院","银行","奶茶店","图书馆","厕所"] # 预定义的POI类型列表


@map.route('/<int:spot_id>') # 确保 spot_id 是整数
@login_required
def mapView(spot_id):
    """显示地图页面"""
    # spot_id 已经由 Flask 自动转换为整数
    spot = spotManager.getSpot(spot_id)
    if not spot:
        # 处理景点不存在的情况，例如返回404页面或重定向
        return "Spot not found", 404

    location = spot.get("location") # 使用 .get() 更安全，因为如果键 "location" 不存在，它不会抛出 KeyError，并且可以指定默认值
    #获取经纬度从"纬度,经度"格式转换为列表
    if location:
        try:
            # 使用列表推导式和 strip() 来去除空白字符
            parts = [part.strip() for part in location.split(",")]
            if len(parts) == 2:
                lat = float(parts[0])
                lng = float(parts[1])
            else:
                # 处理分割后部分数量不为2的情况
                raise ValueError("Location string does not contain exactly one comma.")
        except ValueError:
            # 处理位置格式错误的情况，例如返回400错误
            # 可以考虑记录下无效的 location 值以供调试
            # import logging
            # logging.error(f"Invalid location format encountered: {location}")
            return "Invalid location format", 400

    # 将 spot_id 传递给模板
    return render_template('map.html', spot_id=spot_id, lat=lat, lng=lng)


@map.route('/<int:spot_id>/api/scenicSpots') # 确保 spot_id 是整数
@login_required
def scenicSpots(spot_id):
    """获取景点数据"""
    # spot_id 已经由 Flask 自动转换为整数
    spot = spotManager.getSpot(spot_id)
    if not spot:
        return {"error": "Spot not found"}, 404

    location = spot.get("location") # 使用 .get() 更安全
    if not location:
        return {"error": "Spot location not found"}, 404

    # 假设 map_module.get_POI 返回的是包含 poi 列表的 JSON
    # 例如: {"pois": [{"name": "景点A", "location": "经度,纬度"}, ...]}
    poi_data = map_module.get_POI_reversal("景点", location, 2000)
    if poi_data:
        return jsonify(poi_data), 200
    else:
        return {"error": "Failed to fetch POI data"}, 500


@map.route('/api/poi/<location>')
def getPoi(location):
    """获取兴趣点数据，合并所有类型并排序"""
    all_pois = []
    for poi_type in POI_types:
        # 调用 map_module.get_POI 获取数据
        # 假设直接返回 POI 列表，例如: [{'name': '...', 'distance': ...}, ...]
        poi_list = map_module.get_POI_reversal(poi_type, location, 500)
        # 检查返回数据是否为列表
        if isinstance(poi_list, list):
            # 使用 merge_sort 合并当前类型的 POI 列表和已有的 all_pois 列表
            # 假设 poi_list 和 all_pois 都已按 merge_sort 的标准排序
            # （或者 map_module.get_POI 返回的是按此标准排序的列表）
            all_pois = merge_sort(all_pois, poi_list)

    # 循环结束后，all_pois 包含了所有类型、按指定标准合并排序后的 POI
    # 反转
    all_pois = all_pois[::-1]
    return jsonify(all_pois)









