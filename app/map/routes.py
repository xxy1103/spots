from flask import render_template, request, redirect, url_for,g,jsonify
from . import map #导入蓝图
from app.api.routes import login_required # 导入登录验证装饰器
from module.Spot_class import spotManager
from module.fileIo import configIo
from module.map import map as map_module # 导入地图模块, 重命名避免与蓝图冲突
from module.data_structure.merge import merge_sort





@map.route('/<int:spot_id>') # 确保 spot_id 是整数
@login_required
def mapView(spot_id):
    """
    显示指定景点的地图页面。

    **请求方法:** GET
    **URL 参数:**
      - `spot_id` (int): 要显示的景点的ID。

    **行为:**
      - 根据 `spot_id` 获取景点信息。
      - 如果景点不存在，返回 404 错误。
      - 如果景点位置信息格式不正确，返回 400 错误。
      - 渲染 `map.html` 模板，并传递景点ID、纬度、经度和景点详细信息。

    **认证:**
      - 需要用户登录 (`@login_required`)。
    """
    # spot_id 已经由 Flask 自动转换为整数
    spot = spotManager.getSpot(spot_id)
    if not spot:
        # 处理景点不存在的情况，例如返回404页面或重定向
        return "Spot not found", 404

    location = spot.location # 使用 .get() 更安全，因为如果键 "location" 不存在，它不会抛出 KeyError，并且可以指定默认值
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
    return render_template('map.html', spot_id=spot_id, lat=lat, lng=lng, spot=spot)


@map.route('/<int:spot_id>/api/scenicSpots') # 确保 spot_id 是整数
@login_required
def scenicSpots(spot_id):
    """
    获取指定景点周边的其他景点数据 (POI - Points of Interest)。

    **请求方法:** GET
    **URL 参数:**
      - `spot_id` (int): 中心景点的ID。

    **返回数据格式 (成功 - 200 OK):**
    ```json
    // 假设 map_module.get_POI_reversal 返回的数据结构
    {
        "pois": [
            {
                "name": "周边景点A",
                "location": "纬度,经度",
                // ...其他POI属性
            },
            // ...更多POI
        ]
    }
    
    ```
    **返回数据格式 (失败):**
      - **404 Not Found:** 如果中心景点不存在或位置信息缺失。
        ```json
        {"error": "Spot not found"}
        // 或
        {"error": "Spot location not found"}
        ```
      - **500 Internal Server Error:** 如果获取POI数据失败。
        ```json
        {"error": "Failed to fetch POI data"}
        ```

    **认证:**
      - 需要用户登录 (`@login_required`)。
    """
    # spot_id 已经由 Flask 自动转换为整数
    spot = spotManager.getSpot(spot_id)
    if not spot:
        return {"error": "Spot not found"}, 404

    location = spot.location # 使用 .get() 更安全
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
    """
    根据指定位置获取所有类型的兴趣点 (POI) 数据，并进行合并排序。

    **请求方法:** GET
    **URL 参数:**
      - `location` (str): 中心位置的坐标，格式通常为 "纬度,经度"。

    **行为:**
      - 从配置文件获取所有POI类型。
      - 对每种POI类型，调用 `map_module.get_POI_reversal` 获取半径500米内的POI列表。
      - 使用 `merge_sort` 合并所有类型的POI列表。
      - 将合并后的列表反转（可能是为了按距离或其他标准降序排列）。

    **返回数据格式 (成功 - 200 OK):**
    ```json
    [
        {
            "name": "POI 名称",
            "distance": "距离", // 或其他排序依据的字段
            // ...其他POI属性
        },
        // ...更多POI对象，已合并排序和反转
    ]
    ```
    如果获取过程中出现问题或没有POI，可能返回空列表 `[]`。
    """
    all_pois = []
    POI_types = configIo.getAllPoiTypes() # 获取所有兴趣点类型
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

@map.route('/api/poi/<location>/<keyword>')
def getPoiByKeyword(location, keyword):
    """
    根据指定位置和关键词（POI类型）获取兴趣点 (POI) 数据。

    **请求方法:** GET
    **URL 参数:**
      - `location` (str): 中心位置的坐标，格式通常为 "纬度,经度"。
      - `keyword` (str): POI的类型或关键词。

    **行为:**
      - 调用 `map_module.get_POI_reversal` 获取指定关键词和位置（半径500米内）的POI列表。
      - 将获取的POI列表反转。

    **返回数据格式 (成功 - 200 OK):**
    ```json
    [
        {
            "name": "POI 名称",
            // ...其他POI属性
        },
        // ...更多POI对象，已反转
    ]
    ```
    如果获取过程中出现问题或没有匹配的POI，可能返回空列表 `[]`。
    """
    poi_list = map_module.get_POI_reversal(keyword, location, 500)

    # 检查返回数据是否为列表
    return jsonify(poi_list[::-1])



@map.route('/api/navigation', methods=['POST'])
def navigation():
    """
    获取两点或多点之间的导航路线规划数据。

    **请求方法:** POST
    **请求类型:** JSON
    **请求体参数:**
    ```json
    {
        "points": [
            {"lat": 纬度1, "lng": 经度1}, // 起点
            {"lat": 纬度2, "lng": 经度2}, // 终点或途径点
            // ...更多途径点
        ]
    }
    ```

    **返回数据格式 (成功 - 200 OK):**
    ```json
    {
        "success": True,
        "route": [
            [纬度A, 经度A], // 路径点1
            [纬度B, 经度B], // 路径点2
            // ...更多路径点坐标
        ],
        "distance": 总距离, // 单位：米
        "duration": null // 预计时间（秒），当前版本可能未实现或固定为null
    }
    ```

    **返回数据格式 (失败):**
      - **400 Bad Request:** 如果输入数据无效（如缺少 `points`，坐标点少于2个，或坐标点格式错误）。
        ```json
        {"success": False, "message": "无效的输入数据"}
        // 或
        {"success": False, "message": "无效的坐标点数据，至少需要两个点"}
        // 或
        {"success": False, "message": "坐标点格式错误，应为 {lat: number, lng: number}"}
        ```
      - **500 Internal Server Error:** 如果路线规划过程中发生内部错误（如地图模块规划失败）。
        ```json
        {"success": False, "message": "路线规划失败: <具体错误信息>"}
        ```
    """
    data = request.get_json()
    # 校验输入数据
    if not data or 'points' not in data: # 前端发送的是 'points'
        return jsonify({"success": False, "message": "无效的输入数据"}), 400

    coordinates = data['points'] # 获取坐标点列表
    # 校验坐标点格式
    if not isinstance(coordinates, list) or len(coordinates) < 2:
        return jsonify({"success": False, "message": "无效的坐标点数据，至少需要两个点"}), 400
    
    # 进一步校验每个坐标点的格式（例如，确保它们是包含 lat 和 lng 的字典）
    valid_coordinates = []
    for point in coordinates:
        if isinstance(point, dict) and 'lat' in point and 'lng' in point:
             # 修改这里：将坐标点转换为元组 (lat, lng)
             valid_coordinates.append((point['lat'], point['lng'])) 
        else:
             return jsonify({"success": False, "message": "坐标点格式错误，应为 {lat: number, lng: number}"}), 400


    try:
        # 调用地图模块的规划路线方法
        # 注意：假设 map_module.plan_route 返回 (总距离, 路径点列表, 预计时间)
        # 如果只返回距离和路径，需要相应调整
        # result = map_module.plan_route(valid_coordinates) 
        
        # 假设 map_module.plan_route 返回 (total_distance, path_points)
        print(f"传递给 plan_route 的坐标: {valid_coordinates}") # 调试输出，确认格式为 [(lat, lng), ...]
        total_distance, path_points = map_module.plan_route(valid_coordinates) 
        # 检查规划结果 - 确保 path_points 是一个非空列表或元组
        # 使用 'not path_points' 来检查 None 或空列表/元组 []/()
        if total_distance is None or not path_points: 
             raise ValueError("地图模块未能成功规划路线或返回空路径") 

        # 假设没有返回预计时间，duration 设为 None 或不包含在响应中
        duration = None # 如果 map_module.plan_route 返回时间，则替换这里


        return jsonify({
            "success": True,
            "route": path_points, # 确保返回给前端的是 [[lat1, lng1], ...]
            "distance": total_distance, # 总距离（米）
            "duration": duration # 预计时间（秒），如果可用
        })

    except Exception as e:
        # 处理地图模块可能抛出的异常或其他错误
        print(f"路线规划出错: {e}") # 记录错误日志
        return jsonify({"success": False, "message": f"路线规划失败: {e}"}), 500
