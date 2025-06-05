# encoding:utf-8
import requests
import json
from dotenv import load_dotenv
load_dotenv() # 加载 .env 文件中的环境变量
try:
    from module.data_structure.coordTransform_utils import gcj02_to_wgs84, wgs84_to_gcj02
    from module.data_structure.dijkstra import dijkstraRouter
except:
    from coordTransform_utils import gcj02_to_wgs84, wgs84_to_gcj02
    from dijkstra import DijkstraRouter


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
        self.dijkstra_router = dijkstraRouter
        
    def _get_dijkstra_router(self):
        """
        获取Dijkstra路由器实例（延迟初始化）
        """
        if self.dijkstra_router is None:
            try:
                self.dijkstra_router = DijkstraRouter()
                print("Dijkstra路由器初始化成功")
            except Exception as e:
                print(f"Dijkstra路由器初始化失败: {e}")
                self.dijkstra_router = False  # 标记为失败，避免重复尝试
        return self.dijkstra_router if self.dijkstra_router is not False else None
        
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

        lat, lng = map(float,location.split(","))
        result  = wgs84_to_gcj02(lng, lat)  # 将WGS84坐标转换为GCJ02坐标
        
        location = f"{result[1]},{result[0]}"  # 转换后的坐标格式为"纬度,经度"        
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
    
    def get_poi_details(self, result, location=None, type=None, use_dijkstra=True):
        """
        从搜索结果中提取POI详情
        
        参数:
            result: search方法返回的结果
            location: 参考位置的经纬度（可选），格式为"纬度,经度"字符串，例如"39.915,116.404"
                如果提供则计算距离
            type: POI类型
            use_dijkstra: 是否使用Dijkstra算法计算距离，默认为True
                
        返回:
            POI详情列表，每个POI包含名称、地址、经纬度等信息
        """

        if result.get("status") != 0 or "results" not in result:
            return []

        pois = []
        
        # 预处理POI数据
        for poi in result["results"]:
            # 获取POI的位置信息
            poi_location = poi.get("location", {})
            poi_lat = poi_location.get("lat")
            poi_lng = poi_location.get("lng")
            
            if poi_lat is None or poi_lng is None:
                continue
                
            # 将GCJ02坐标转换为WGS84坐标
            poi_result = gcj02_to_wgs84(poi_lng, poi_lat)
            poi_location["lat"] = poi_result[1]  # 纬度
            poi_location["lng"] = poi_result[0]  # 经度

            poi_info = {
                "name": poi.get("name", ""),
                "type": type,
                "address": poi.get("address", ""),
                "province": poi.get("province", ""),
                "city": poi.get("city", ""),
                "area": poi.get("area", ""),
                "telephone": poi.get("telephone", ""),
                "location": poi_location,
                "value1": None,  # 距离字段，稍后填充
                "value2": 0
            }
            pois.append(poi_info)
        
        # 如果没有提供参考位置或POI列表为空，直接返回
        if not location or not pois:
            return pois
            
        # 使用Dijkstra算法计算距离
        if use_dijkstra:
            router = self._get_dijkstra_router()
            if router is not None:
                try:
                    # 使用Dijkstra算法的多目标距离计算功能
                    pois_with_dijkstra_distance = router.calculate_distances_to_points(
                        start_coordinate=location,
                        target_points=pois,
                        optimize_for='distance'
                    )
                    print(f"使用Dijkstra算法成功计算了{len(pois_with_dijkstra_distance)}个POI的距离")
                    return pois_with_dijkstra_distance
                except Exception as e:
                    print(f"Dijkstra距离计算失败，回退到直线距离计算: {e}")
                    # 如果Dijkstra计算失败，回退到Haversine公式
                    use_dijkstra = False
            else:
                print("Dijkstra路由器不可用，使用直线距离计算")
                use_dijkstra = False
        
        return pois

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