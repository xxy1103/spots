from module.data_structure.dijkstra import dijkstraRouter
from module.data_structure.POiSearch import POISearch
from module.data_structure.quicksort import quicksort



class Map:
    def __init__(self):
        self.router = dijkstraRouter
        self.poi_search = POISearch()

    def plan_route(self, coordinates, method="distance", use_vehicle=False):
        """
        规划路线
        :param coordinates: 经纬度坐标列表
        :param method: 路线规划方式 ("distance" 或 "time")
        :param use_vehicle: 是否使用车辆 (仅在 method="time" 时有效)
        :return: 路线总距离/时间和分段路径节点
        """
        total_cost, segmented_path = self.router.plan_route(coordinates, method, use_vehicle)
        route_segments = self.router.get_route_coordinates(segmented_path)
        return total_cost, route_segments
    
    def get_POI_reversal(self, query, location, radius=500, page_num=0, page_size=20, output="json"):
        """
        获取周边POI点
        :param query: 搜索关键词
        :param location: 位置坐标，格式为"纬度,经度"
        :param radius: 搜索半径，单位为米
        :param page_num: 页码
        :param page_size: 每页返回的POI数量
        :param output: 返回格式
        :return: POI搜索结果
        """
        result,type = self.poi_search.search(query, location, radius, page_num, page_size, output)
        if result.get("status") == 0:
            pois = self.poi_search.get_poi_details(result, location,type)
            if pois:
                pois = quicksort(pois)
            return pois
        return None
    

map = Map()


if __name__ == "__main__":
    map_instance = Map()
    pois = map_instance.get_POI_reversal("餐厅", "39.915,116.404",2000)
    if pois:
        for poi in pois:
            print(f"名称: {poi['name']}, 地址: {poi['address']}, 距离: {poi['score']}米")
    else:
        print("未找到相关POI")


    
    
    