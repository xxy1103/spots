import os
from module.data_structure.heap import MinHeap
from module.data_structure.set import MySet
from typing import List, Tuple, Any
import osmnx as ox
import webbrowser
try:
    import folium
except ImportError:
    folium = None
# 导入自定义 Set 类



class DijkstraRouter:
    """
    使用Dijkstra算法的路由器，用于在地图上计算最短路径
    """
    
    def __init__(self, map_path: str = 'data/map/map.osm'):
        """
        初始化路由器，加载OSM地图数据
        
        Args:
            map_path: OSM地图文件路径
        """
        self.map_path = map_path
        self.graph = None
        self.load_map()
    
    def load_map(self) -> None:
        """
        从OSM文件加载地图数据并构建图
        """
        # 检查文件是否存在
        if not os.path.exists(self.map_path):
            raise FileNotFoundError(f"地图文件不存在: {self.map_path}")
        
        # 加载OSM数据到NetworkX图
        print(f"正在加载地图数据: {self.map_path}")
        try:
            # 尝试使用osmnx直接加载OSM数据
            self.graph = ox.graph_from_xml(self.map_path, simplify=True)
        except Exception as e:
            print(f"使用osmnx加载失败: {e}")
        print(f"地图加载完成，节点数: {len(self.graph.nodes)}, 边数: {len(self.graph.edges)}")
    
    def _validate_nodes(self, start_node: Any, end_node: Any) -> None:
        """验证节点是否有效"""
        if self.graph is None:
            raise ValueError("地图数据未加载")
        
        if start_node not in self.graph:
            raise ValueError(f"起点节点 {start_node} 不存在于地图中")
        
        if end_node not in self.graph:
            raise ValueError(f"终点节点 {end_node} 不存在于地图中")
    
    def _get_edge_weight(self, current_node: Any, neighbor: Any) -> float:
        """
        获取边的权重，统一处理多边情况
        """
        try:
            edge_data = self.graph.get_edge_data(current_node, neighbor)
            
            if edge_data is None:
                return float('inf')
            
            # 处理多边情况：选择最短边
            if isinstance(edge_data, dict) and len(edge_data) > 1:
                weights = []
                for edge_key, data in edge_data.items():
                    weight = data.get('length', data.get('weight', 1.0))
                    if isinstance(weight, (int, float)) and weight >= 0:
                        weights.append(weight)
                return min(weights) if weights else 1.0
            
            # 单边情况
            if isinstance(edge_data, dict):
                first_edge = next(iter(edge_data.values()))
                weight = first_edge.get('length', first_edge.get('weight', 1.0))
            else:
                weight = edge_data.get('length', edge_data.get('weight', 1.0))
            
            # 验证权重有效性
            if not isinstance(weight, (int, float)) or weight < 0:
                return 1.0
            
            return weight
            
        except Exception:
            return 1.0
    
    def _reconstruct_path(self, predecessors: dict, start_node: Any, end_node: Any) -> List[Any]:
        """重构路径，添加循环检测"""
        if end_node not in predecessors and end_node != start_node:
            return []
        
        path = []
        current = end_node
        visited_in_path = set()
        
        while current is not None:
            # 检测循环
            if current in visited_in_path:
                raise ValueError("路径重构中检测到循环")
            
            path.append(current)
            visited_in_path.add(current)
            current = predecessors.get(current)
            
            # 防止无限循环
            if len(path) > len(self.graph.nodes):
                raise ValueError("路径重构超出节点数量限制")
        
        path.reverse()
        return path
    
    def _relax_neighbors(self, current_node, distances, predecessors, priority_queue):
        """松弛邻居节点"""
        current_distance = distances[current_node]
        
        for neighbor in self.graph.neighbors(current_node):
            weight = self._get_edge_weight(current_node, neighbor)
            new_distance = current_distance + weight
            
            if new_distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_distance
                predecessors[neighbor] = current_node
                priority_queue.push((new_distance, neighbor))

    def dijkstra(self, start_node: Any, end_node: Any) -> Tuple[float, List[Any]]:
        """
        使用Dijkstra算法计算从起点到终点的最短路径

        Args:
            start_node: 起点节点ID
            end_node: 终点节点ID

        Returns:
            Tuple[float, List[Any]]: 总距离和路径节点列表
        """
        # 验证输入
        self._validate_nodes(start_node, end_node)
        
        # 如果起点和终点相同，直接返回
        if start_node == end_node:
            return 0.0, [start_node]

        # 初始化距离字典和前驱节点字典
        distances = {start_node: 0.0}
        predecessors = {}
        
        # 使用最小堆作为优先队列
        priority_queue = MinHeap()
        priority_queue.push((0.0, start_node))
        
        # 使用自定义Set记录已访问节点
        visited = MySet()
        
        while not priority_queue.is_empty():
            current_distance, current_node = priority_queue.pop()
            
            # 找到目标节点，提前退出
            if current_node == end_node:
                break
            
            # 如果已访问过该节点，跳过
            if visited.contains(current_node):
                continue
            
            # 过滤过期的队列项
            if current_distance > distances.get(current_node, float('inf')):
                continue
            
            # 标记当前节点为已访问
            visited.add(current_node)
            
            # 松弛邻居节点
            self._relax_neighbors(current_node, distances, predecessors, priority_queue)
        
        # 如果终点不可达
        if end_node not in distances:
            return float('inf'), []
          # 重构路径
        path = self._reconstruct_path(predecessors, start_node, end_node)
        
        return distances[end_node], path
    
    def get_nearest_node(self, lat: float, lng: float) -> Any:
        """
        获取最接近给定经纬度的图中节点
        
        Args:
            lat: 纬度
            lng: 经度
            
        Returns:
            节点ID
        """
        try:
            # 使用osmnx的函数查找最近节点
            return ox.nearest_nodes(self.graph, lng, lat)
        except:
            # 如果ox.nearest_nodes不可用，手动计算最近节点
            min_dist = float('inf')
            nearest_node = None
            
            for node, data in self.graph.nodes(data=True):
                try:
                    node_lat = data.get('y', data.get('lat'))
                    node_lng = data.get('x', data.get('lon'))
                    
                    if node_lat is None or node_lng is None:
                        continue
                    
                    # 计算距离（使用简单的欧几里得距离作为近似）
                    dist = ((node_lat - lat) ** 2 + (node_lng - lng) ** 2) ** 0.5
                    
                    if dist < min_dist:
                        min_dist = dist
                        nearest_node = node
                except Exception:
                    continue
            
            return nearest_node
    def plan_route(self, coordinates: List[Tuple[float, float]]) -> Tuple[float, List[Any]]:
        """
        规划经过所有给定坐标点的最短路线
        
        Args:
            coordinates: 经纬度坐标列表，第一个是起点，其余为途径点
                         每个坐标是一个(纬度,经度)的元组
        
        Returns:
            Tuple[float, List[Any]]: 总距离和完整路径节点列表
        """
        if len(coordinates) < 2:
            raise ValueError("至少需要提供2个坐标点")
        
        # 获取每个坐标对应的最近节点
        nodes = [self.get_nearest_node(lat, lng) for lat, lng in coordinates]
        
        # 检查是否所有节点都有效
        if any(node is None for node in nodes):
            raise ValueError("部分坐标点无法匹配到地图上的节点")
        
        start_node = nodes[0]
        waypoints = nodes[1:]
        
        # 如果只有一个途径点，直接计算从起点到终点的路径
        if len(waypoints) == 1:
            return self.dijkstra(start_node, waypoints[0])
            
        # 使用改进的贪心算法和2-opt局部优化
        return self._solve_tsp_improved(start_node, waypoints)
    
    def _solve_tsp_improved(self, start_node: Any, waypoints: List[Any]) -> Tuple[float, List[Any]]:
        """
        使用改进的贪心算法和2-opt局部优化求解TSP问题
        
        Args:
            start_node: 起点节点
            waypoints: 途径点列表
            
        Returns:
            Tuple[float, List[Any]]: 总距离和完整路径节点列表
        """
        # 计算所有点对之间的最短路径
        all_nodes = [start_node] + waypoints
        distances = {}
        paths = {}
        
        # 预计算所有点对之间的距离和路径
        for i, node_i in enumerate(all_nodes):
            for j, node_j in enumerate(all_nodes):
                if i != j:  # 避免计算自身到自身的距离
                    dist, path = self.dijkstra(node_i, node_j)
                    distances[(node_i, node_j)] = dist
                    paths[(node_i, node_j)] = path
        
        # 步骤1：贪心算法构造初始解
        tour = self._nearest_neighbor_tsp(start_node, waypoints, distances)
        
        # 步骤2：使用2-opt进行局部优化
        improved_tour = self._two_opt_optimize(tour, distances)
        
        # 步骤3：构建完整路径
        return self._construct_complete_path(improved_tour, paths)
    
    def _nearest_neighbor_tsp(self, start_node: Any, waypoints: List[Any], distances: dict) -> List[Any]:
        """
        使用最近邻算法构造TSP初始解
        
        Args:
            start_node: 起点节点
            waypoints: 途径点列表
            distances: 点对之间的距离字典
            
        Returns:
            List[Any]: 访问顺序的节点列表
        """
        current = start_node
        unvisited = set(waypoints)
        tour = [current]
        
        while unvisited:
            # 找到距离当前点最近的未访问点
            next_node = min(
                unvisited,
                key=lambda node: distances.get((current, node), float('inf'))
            )
            
            tour.append(next_node)
            current = next_node
            unvisited.remove(next_node)
            
        return tour
    
    def _two_opt_optimize(self, tour: List[Any], distances: dict) -> List[Any]:
        """
        使用2-opt算法对路径进行局部优化
        
        Args:
            tour: 初始路径
            distances: 点对之间的距离字典
            
        Returns:
            List[Any]: 优化后的路径
        """
        improved = True
        best_distance = self._calculate_tour_distance(tour, distances)
        
        while improved:
            improved = False
            
            for i in range(1, len(tour) - 1):
                for j in range(i + 1, len(tour)):
                    if j - i == 1:
                        continue  # 相邻边不交换
                    
                    # 计算2-opt交换后的新路径距离
                    new_tour = tour[:i] + tour[i:j+1][::-1] + tour[j+1:]
                    new_distance = self._calculate_tour_distance(new_tour, distances)
                    
                    # 如果新路径更短，则接受交换
                    if new_distance < best_distance:
                        tour = new_tour
                        best_distance = new_distance
                        improved = True
                        break
                
                if improved:
                    break
            
        return tour
    
    def _calculate_tour_distance(self, tour: List[Any], distances: dict) -> float:
        """
        计算给定路径的总距离
        
        Args:
            tour: 访问顺序的节点列表
            distances: 点对之间的距离字典
            
        Returns:
            float: 路径总距离
        """
        total = 0
        for i in range(len(tour) - 1):
            dist = distances.get((tour[i], tour[i+1]), float('inf'))
            if dist == float('inf'):
                return float('inf')
            total += dist
        return total
    
    def _construct_complete_path(self, tour: List[Any], paths: dict) -> Tuple[float, List[Any]]:
        """
        基于节点访问顺序构建完整路径
        
        Args:
            tour: 访问顺序的节点列表
            paths: 点对之间的路径字典
            
        Returns:
            Tuple[float, List[Any]]: 总距离和完整路径节点列表
        """
        total_distance = 0
        complete_path = [tour[0]]  # 起始点
        
        for i in range(len(tour) - 1):
            current_node = tour[i]
            next_node = tour[i + 1]
            
            # 获取这两点之间的路径
            segment_path = paths.get((current_node, next_node), [])
            segment_distance = len(segment_path) - 1  # 简单估计距离
            
            if not segment_path:
                raise ValueError(f"无法找到从 {current_node} 到 {next_node} 的路径")
            
            # 添加除起点外的路径点（避免重复）
            complete_path.extend(segment_path[1:])
            total_distance += segment_distance
            
        return total_distance, complete_path
    
    def get_route_coordinates(self, path: List[Any]) -> List[Tuple[float, float]]:
        """
        获取路径上所有节点的经纬度坐标
        
        Args:
            path: 路径节点ID列表
            
        Returns:
            List[Tuple[float, float]]: 路径上点的(纬度,经度)坐标列表
        """
        route_coords = []
        for node_id in path:
            try:
                node = self.graph.nodes[node_id]
                # 尝试不同的属性名称获取坐标
                lat = node.get('y', node.get('lat'))
                lng = node.get('x', node.get('lon'))
                
                if lat is not None and lng is not None:
                    route_coords.append([lat, lng])
            except:
                pass  # 忽略错误节点
        
        return route_coords
    def plot_route_interactive(self, path: List[Any], original_coordinates: List[Tuple[float, float]] = None, save_path=None):
        """
        使用Folium创建交互式地图
        
        Args:
            path: 路径节点ID列表
            original_coordinates: 原始输入的坐标点列表，包括起点和途径点
            save_path: 保存HTML文件的路径，如果为None则自动生成
            
        Returns:
            str: 生成的HTML文件路径
        """
        try:
            if folium is None:
                print("请安装必要的库: pip install folium")
                return None
                
            # 获取路径坐标
            route_coords = self.get_route_coordinates(path)
            
            if not route_coords or len(route_coords) < 2:
                print("无法获取路径坐标或路径点数量不足")
                return None
            
            # 计算中心点和缩放级别
            lats = [lat for lat, _ in route_coords]
            lngs = [lng for _, lng in route_coords]
            center_lat = sum(lats) / len(lats)
            center_lng = sum(lngs) / len(lngs)
            
            # 动态计算缩放级别
            lat_range = max(lats) - min(lats)
            lng_range = max(lngs) - min(lngs)
            zoom_start = 14  # 默认缩放级别
            
            # 根据路径覆盖范围调整缩放级别
            if max(lat_range, lng_range) > 0.1:
                zoom_start = 10
            elif max(lat_range, lng_range) < 0.01:
                zoom_start = 16
            
            # 创建地图
            m = folium.Map(
                location=[center_lat, center_lng], 
                zoom_start=zoom_start,
                tiles='OpenStreetMap'
            )
            
            # 添加多种底图切换控件
            folium.TileLayer('CartoDB positron', name='浅色地图').add_to(m)
            folium.TileLayer('CartoDB dark_matter', name='深色地图').add_to(m)
            folium.TileLayer('Stamen Terrain', name='地形图').add_to(m)
            folium.LayerControl().add_to(m)
            
            # 添加路径线
            folium.PolyLine(
                locations=[(lat, lng) for lat, lng in route_coords],
                color='blue',
                weight=5,
                opacity=0.7,
                tooltip='路线',
                dash_array='5, 10'  # 虚线效果
            ).add_to(m)
            
            # 添加起点和终点标记
            start_lat, start_lng = route_coords[0]
            end_lat, end_lng = route_coords[-1]
            
            # 使用更美观的图标
            try:
                # 起点标记
                folium.Marker(
                    [start_lat, start_lng],
                    popup='<b>起点</b>',
                    icon=folium.Icon(color='green', icon='play', prefix='fa')
                ).add_to(m)
                
                # 终点标记
                folium.Marker(
                    [end_lat, end_lng],
                    popup='<b>终点</b>',
                    icon=folium.Icon(color='red', icon='flag-checkered', prefix='fa')
                ).add_to(m)
            except:
                # 降级使用默认图标
                folium.Marker([start_lat, start_lng], popup='<b>起点</b>', icon=folium.Icon(color='green')).add_to(m)
                folium.Marker([end_lat, end_lng], popup='<b>终点</b>', icon=folium.Icon(color='red')).add_to(m)
            
            # 添加原始途径点标记
            if original_coordinates and len(original_coordinates) > 1:
                for i, (lat, lng) in enumerate(original_coordinates[1:-1], 1):
                    try:
                        folium.Marker(
                            [lat, lng],
                            popup=f'<b>途径点 {i}</b>',
                            icon=folium.Icon(color='orange', icon='map-pin', prefix='fa')
                        ).add_to(m)
                    except:
                        folium.Marker([lat, lng], popup=f'途径点 {i}', icon=folium.Icon(color='orange')).add_to(m)
            
            # 添加路径里程信息
            path_length = 0
            for i in range(len(route_coords) - 1):
                # 计算路段距离
                lat1, lng1 = route_coords[i]
                lat2, lng2 = route_coords[i+1]
                segment_length = self._haversine_distance(lat1, lng1, lat2, lng2)
                path_length += segment_length
                
                # 在路径上添加间隔标记
                if i > 0 and i % max(1, len(route_coords) // 10) == 0:
                    folium.CircleMarker(
                        route_coords[i],
                        radius=4,
                        color='blue',
                        fill=True,
                        fill_opacity=0.8,
                        popup=f'约 {path_length:.2f} km'
                    ).add_to(m)
            
            # 在地图上添加总距离信息
            try:
                folium.Marker(
                    [center_lat, center_lng],
                    icon=folium.DivIcon(
                        icon_size=(150, 36),
                        icon_anchor=(75, 18),
                        html=f'<div style="font-size: 12pt; background-color: rgba(255,255,255,0.7); \
                            padding: 5px; border-radius: 5px; text-align: center;"><b>总距离: {path_length:.2f} km</b></div>'
                    )
                ).add_to(m)
            except Exception as e:
                print(f"添加距离信息时出错: {e}")
            
            # 保存为HTML文件并自动打开
            if not save_path:
                save_path = 'route_map.html'
            
            m.save(save_path)
            print(f"交互式地图已保存至: {save_path}")
            
            try:
                # 尝试自动在浏览器中打开地图
                webbrowser.open('file://' + os.path.abspath(save_path))
            except Exception as e:
                print(f"自动打开地图失败: {e}")
                
            return save_path
        except Exception as e:
            print(f"创建交互式地图失败: {e}")
            return None
            
    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        计算两点之间的哈弗辛距离（球面距离）
        
        Args:
            lat1, lon1: 第一个点的纬度和经度
            lat2, lon2: 第二个点的纬度和经度
            
        Returns:
            float: 两点之间的距离，单位为公里
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # 将纬度和经度转换为弧度
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # 哈弗辛公式
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        r = 6371  # 地球半径，单位为公里
        
        return r * c

    def calculate_distances_to_points(self, start_coordinate: str, target_points: List[dict]) -> List[dict]:
        """
        使用一次Dijkstra算法计算从起点到多个目标点的距离
        
        Args:
            start_coordinate: 起点坐标，格式为"纬度,经度"
            target_points: 目标点列表，每个元素为字典，包含location信息
                          可通过["location"]["lat"]和["location"]["lng"]获取坐标
        
        Returns:
            List[dict]: 更新后的目标点列表，每个点的["value1"]字段包含到起点的距离
        """
        try:
            # 解析起点坐标
            lat_str, lng_str = start_coordinate.split(',')
            start_lat = float(lat_str.strip())
            start_lng = float(lng_str.strip())
            
            # 获取起点的最近节点
            start_node = self.get_nearest_node(start_lat, start_lng)
            if start_node is None:
                raise ValueError("无法找到起点对应的地图节点")
            
            # 获取所有目标点的最近节点
            target_nodes = []
            for point in target_points:
                try:
                    target_lat = point["location"]["lat"]
                    target_lng = point["location"]["lng"]
                    target_node = self.get_nearest_node(target_lat, target_lng)
                    target_nodes.append(target_node)
                except (KeyError, TypeError) as e:
                    print(f"解析目标点坐标失败: {e}")
                    target_nodes.append(None)
            
            # 使用修改后的Dijkstra算法一次性计算到所有目标点的距离
            distances = self._dijkstra_multi_target(start_node, target_nodes)
            
            # 将距离结果写入目标点列表
            for i, point in enumerate(target_points):
                if target_nodes[i] is not None:
                    point["value1"] = distances.get(target_nodes[i], float('inf'))
                else:
                    point["value1"] = float('inf')
            
            return target_points
            
        except Exception as e:
            print(f"计算距离失败: {e}")
            # 如果计算失败，将所有距离设为无穷大
            for point in target_points:
                point["value1"] = float('inf')
            return target_points

    # 多目标Dijkstra算法，修正缩进
    def _dijkstra_multi_target(self, start_node: Any, target_nodes: List[Any]) -> dict:
        """
        单源多目标的Dijkstra算法，从一个起点计算到多个目标点的最短路径
        
        Args:
            start_node: 起点节点
            target_nodes: 目标节点列表
            
        Returns:
            dict: 从起点到每个目标点的距离字典
        """
        if not target_nodes:
            return {}
            
        valid_targets = set(target for target in target_nodes 
                          if target is not None and target in self.graph)
        
        if not valid_targets:
            return {}
        
        # 初始化
        distances = {start_node: 0.0}
        priority_queue = MinHeap()
        priority_queue.push((0.0, start_node))
        visited = MySet()
        target_distances = {}
        
        while not priority_queue.is_empty() and len(target_distances) < len(valid_targets):
            current_distance, current_node = priority_queue.pop()
            
            if visited.contains(current_node):
                continue
            
            # 过滤过期的队列项
            if current_distance > distances.get(current_node, float('inf')):
                continue
            
            visited.add(current_node)
            
            # 检查是否为目标节点
            if current_node in valid_targets:
                target_distances[current_node] = current_distance
            
            # 如果找到所有目标，提前退出
            if len(target_distances) == len(valid_targets):
                break
            
            # 松弛邻居
            for neighbor in self.graph.neighbors(current_node):
                weight = self._get_edge_weight(current_node, neighbor)
                new_distance = current_distance + weight
                
                if new_distance < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_distance
                    priority_queue.push((new_distance, neighbor))
        
        return target_distances

# 使用示例
if __name__ == "__main__":
    # 创建路由器实例
    router = DijkstraRouter()
    
    # 示例坐标 (纬度, 经度)
    coordinates = [
        (39.92094, 116.36924),  # 北京某地点1
        (39.93428, 116.38447),  # 北京某地点3
    ]
    
    # 规划路线
    try:
        total_distance, path = router.plan_route(coordinates)
        
        # 获取路径坐标
        route_coords = router.get_route_coordinates(path)
        
        print(f"总距离: {total_distance:.2f} 米")
        print(f"途径节点数: {len(path)}")
        print("路径经纬度坐标示例:")
        for lat, lng in route_coords[:5]:
            print(f"  ({lat}, {lng})")
        if len(route_coords) > 5:
            print("  ...")
        
        # # 可视化路径 - 静态图
        # print("\n生成静态路径图...")
        # router.plot_route_static(path)
        
        # 可视化路径 - 交互式地图，传入原始坐标
        print("\n生成交互式地图...")
        html_path = router.plot_route_interactive(path, coordinates)
        print(f"请在浏览器中打开 {html_path} 查看交互式地图")
        
        # 自动打开浏览器显示地图
        try:
            webbrowser.open(html_path)
        except:
            pass
        
    except Exception as e:
        print(f"路线规划失败: {e}")
    
    # 新增方法的使用示例
    print("\n=== 测试新增的距离计算方法 ===")
    
    # 起点坐标（字符串格式）
    start_point = "39.92094,116.36924"
    
    # 目标点列表
    target_points = [
        {
            "name": "目标点1",
            "location": {"lat": 39.93428, "lng": 116.38447}
        },
        {
            "name": "目标点2", 
            "location": {"lat": 39.91523, "lng": 116.37156}
        },
        {
            "name": "目标点3",
            "location": {"lat": 39.94234, "lng": 116.39567}
        }
    ]
    
    try:
        # 计算距离
        result_points = router.calculate_distances_to_points(start_point, target_points)
        
        print(f"起点坐标: {start_point}")
        print("到各目标点的距离:")
        for point in result_points:
            name = point.get("name", "未知点")
            distance = point.get("value1", float('inf'))
            lat = point["location"]["lat"]
            lng = point["location"]["lng"]
            
            if distance == float('inf'):
                print(f"  {name} ({lat}, {lng}): 无法到达")
            else:
                print(f"  {name} ({lat}, {lng}): {distance:.2f} 米")
                
    except Exception as e:
        print(f"距离计算失败: {e}")