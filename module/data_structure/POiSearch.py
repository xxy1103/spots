# encoding:utf-8
import requests
import json
from dotenv import load_dotenv
load_dotenv() # 加载 .env 文件中的环境变量


import os
api_key = os.environ.get("BAIDU_MAP_AK")

class POISearch:
    """
    百度地图POI搜索类，用于查询周边的POI点
    """
    
    def __init__(self, ak=api_key):
        """
        初始化POI搜索类
        
        参数:
            ak: 百度地图API的访问密钥
        """
        self.host = "https://api.map.baidu.com"
        self.uri = "/place/v2/search"
        self.ak = ak
        
    def search(self, query, location, radius=500, page_num=0, page_size=20, output="json"):
        """
        搜索周边POI点
        
        参数:
            query: 搜索关键词
            location: 位置坐标，格式为"纬度,经度"，例如"39.915,116.404"
            radius: 搜索半径，单位为米，默认500米
            page_num: 页码，默认为0
            page_size: 每页返回的POI数量，默认为20
            output: 返回格式，默认为json
            coord_type: 坐标类型，1表示wgs84ll
            
        返回:
            查询结果字典
        """
        params = {
            "query": query,
            "location": location,
            "radius": radius,
            "page_num": page_num,
            "page_size": page_size,
            "output": output,
            "ak": self.ak,
            "coord_type": 2,  # 百度地图坐标类型，1表示wgs84ll，2表示gcj02ll
            "ret_coordtype": "gcj02ll"  # 返回坐标类型
        }
        
        try:
            response = requests.get(url=self.host + self.uri, params=params)
            if response.status_code == 200:
                return response.json(),query
            else:
                return {"status": response.status_code, "message": "请求失败"}
        except Exception as e:
            return {"status": -1, "message": f"发生异常: {str(e)}"}
    
    
    def get_poi_details(self, result, location=None, type=None):
        """
        从搜索结果中提取POI详情
        
        参数:
            result: search方法返回的结果
            location: 参考位置的经纬度（可选），格式为"纬度,经度"字符串，例如"39.915,116.404"
                如果提供则计算距离
                
        返回:
            POI详情列表，每个POI包含名称、地址、经纬度等信息
        """
        from math import radians, sin, cos, asin, sqrt # 移到函数开头，避免在循环中重复导入

        ref_lat = None
        ref_lng = None
        
        # 解析location字符串为经纬度
        if location:
            try:
                lat_str, lng_str = location.split(',')
                ref_lat = float(lat_str)
                ref_lng = float(lng_str)
            except (ValueError, AttributeError):
                # 如果解析失败，保持ref_lat和ref_lng为None
                pass
        
        if result.get("status") == 0 and "results" in result:
            pois = []
            for poi in result["results"]:
                # 获取POI的位置信息
                poi_location = poi.get("location", {})
                poi_lat = poi_location.get("lat")
                poi_lng = poi_location.get("lng")
                
                # 计算距离（如果提供了参考位置）
                distance = None
                if ref_lat is not None and ref_lng is not None and poi_lat is not None and poi_lng is not None:
                    # 使用 Haversine 公式计算距离
                    # 将经纬度从度数转换为弧度
                    lat1, lon1, lat2, lon2 = map(radians, [ref_lat, ref_lng, poi_lat, poi_lng])

                    # Haversine 公式
                    dlon = lon2 - lon1 
                    dlat = lat2 - lat1 
                    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                    c = 2 * asin(sqrt(a)) 
                    r = 6371 # 地球平均半径（单位：公里）
                    distance_km = c * r
                    distance = round(distance_km * 1000) # 转换为米并四舍五入
                
                poi_info = {
                    "name": poi.get("name", ""),
                    "type": type,
                    "address": poi.get("address", ""),
                    "province": poi.get("province", ""),
                    "city": poi.get("city", ""),
                    "area": poi.get("area", ""),
                    "telephone": poi.get("telephone", ""),
                    "location": poi_location,
                    "score": distance,
                    "visited_time":  0
                }
                pois.append(poi_info)
            return pois
        return []

# 使用示例
if __name__ == "__main__":
    poi_search = POISearch()
    # 搜索北京天安门附近2公里内的银行
    location = "39.915,116.404"  # 定义位置坐标
    result,qurry = poi_search.search("景点", location, 500)
    
    if result.get("status") == 0:
        print(f"总共找到 {result.get('total')} 个结果")
        
        # 获取POI详情，传递位置参数以便计算距离
        pois = poi_search.get_poi_details(result, location)
        
        # 打印前5个POI信息
        for i, poi in enumerate(pois[:5], 1):
            print(f"\n{i}. {poi['name']}")
            print(f"   地址: {poi['address']}")
            print(f"   距离: {poi['score']}米") if poi['score'] is not None else print(f"   距离: 未知")
            print(f"   坐标: 纬度 {poi['location'].get('lat')}, 经度 {poi['location'].get('lng')}")
    else:
        print(f"搜索失败: {result}")