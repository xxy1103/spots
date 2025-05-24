import os
import random
from module.data_structure.heap import MinHeap
from module.data_structure.set import MySet
from typing import List, Tuple, Any, Union, Dict
import osmnx as ox
import webbrowser
try:
    import folium
except ImportError:
    folium = None


class DijkstraRouter:
    """
    使用Dijkstra算法的路由器，用于在地图上计算最短路径
    优化版本：减少代码冗余，提高性能，增加错误处理
    """
    def __init__(self, map_path: str = 'data/map/map.osm', base_speed: float = 5.0):
        """
        初始化路由器，加载OSM地图数据
        
        Args:
            map_path: OSM地图文件路径
            base_speed: 基础行走速度，单位：km/h
        """
        self.map_path = map_path
        self.base_speed = base_speed
        self.graph = None
        self.load_map()
    
    def load_map(self) -> None:
        """从OSM文件加载地图数据并构建图"""
        if not os.path.exists(self.map_path):
            raise FileNotFoundError(f"地图文件不存在: {self.map_path}")
        
        print(f"正在加载地图数据: {self.map_path}")
        try:
            self.graph = ox.graph_from_xml(self.map_path, simplify=True)
        except Exception as e:
            print(f"使用osmnx加载失败: {e}")
            raise
        
        print(f"地图加载完成，节点数: {len(self.graph.nodes)}, 边数: {len(self.graph.edges)}")
        self._initialize_traffic_conditions()
    
    def _initialize_traffic_conditions(self) -> None:
        """为地图中的所有边随机生成拥挤度和速度信息"""
        if self.graph is None:
            return
            
        print("正在初始化道路交通状况...")
        edge_count = 0
        
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            # 生成随机拥挤度 (0.2 到 1.0 之间，避免完全堵塞)
            congestion = random.uniform(0.2, 1.0)
            
            # 根据道路类型设定基础速度
            road_type = data.get('highway', 'unclassified')
            base_speed = self._get_road_base_speed(road_type)
            
            # 实际速度 = 拥挤度 * 基础速度
            actual_speed = congestion * base_speed
            
            # 更新边的属性
            data.update({
                'congestion': congestion,
                'base_speed': base_speed,
                'actual_speed': actual_speed
            })
            
            edge_count += 1
            
        print(f"交通状况初始化完成，处理了 {edge_count} 条道路")
    
    def _get_road_base_speed(self, road_type) -> float:
        """
        根据道路类型获取基础速度 (km/h)
        
        Args:
            road_type: OSM中的道路类型，可能为str或list
        Returns:
            float: 基础速度 km/h
        """
        speed_mapping = {
            'motorway': 80,      # 高速公路
            'trunk': 70,         # 国道
            'primary': 70,       # 主要道路
            'secondary': 50,     # 次要道路
            'tertiary': 30,      # 三级道路
            'residential': 30,   # 住宅区道路
            'service': 15,       # 服务道路
            'footway': 5,        # 人行道
            'path': 5,           # 小径
            'cycleway': 15,      # 自行车道
            'unclassified': 5   # 未分类道路
        }
        
        # 如果是列表，取第一个元素
        if isinstance(road_type, list) and road_type:
            road_type = road_type[0]
        
        # 兜底转为字符串
        if not isinstance(road_type, str):
            road_type = str(road_type)
        
        return speed_mapping.get(road_type, self.base_speed)
    
    def _get_edge_data_candidates(self, node1: Any, node2: Any) -> List[dict]:
        """
        获取两个节点之间的候选边数据
        
        Returns:
            List[dict]: 候选边数据列表
        """
        edge_data_collection = self.graph.get_edge_data(node1, node2)
        if not edge_data_collection:
            return []
        
        if isinstance(edge_data_collection, dict) and edge_data_collection:
            # 检查是否为MultiDiGraph
            if isinstance(next(iter(edge_data_collection.values())), dict):
                return list(edge_data_collection.values())
            else:
                return [edge_data_collection]
        
        return []

    def _calculate_edge_time(self, edge_data: dict, use_vehicle: bool = False) -> float:
        """
        计算边的时间权重
        
        Args:
            edge_data: 边的数据字典
            use_vehicle: 是否使用交通工具
            
        Returns:
            float: 时间权重（秒）
        """
        length = edge_data.get('length', 0)
        if length is None or length < 0:
            return float('inf')
        
        if length == 0:
            return 0.0
        
        # 获取拥挤度和基础速度
        congestion = edge_data.get('congestion', 1.0)
        if use_vehicle:
            road_type = edge_data.get('highway', 'unclassified')
            base_speed_kmh = self._get_road_base_speed(road_type)
        else:
            base_speed_kmh = self.base_speed
        
        # 计算实际速度
        effective_speed_kmh = congestion * base_speed_kmh
        if effective_speed_kmh <= 0:
            return float('inf')
        
        # 转换为m/s并计算时间
        speed_ms = effective_speed_kmh * 1000 / 3600
        return length / speed_ms

    def _get_edge_weight(self, node1: Any, node2: Any, weight_type: str = 'distance', use_vehicle: bool = False) -> float:
        """
        获取两个节点之间边的权重
        
        Args:
            node1: 起始节点
            node2: 目标节点
            weight_type: 权重类型，'distance'表示距离，'time'表示时间
            use_vehicle: 是否使用交通工具（仅在weight_type为'time'时有效）
            
        Returns:
            float: 边的权重值
        """
        candidate_edges = self._get_edge_data_candidates(node1, node2)
        if not candidate_edges:
            return float('inf')
        
        min_weight = float('inf')
        
        for edge_data in candidate_edges:
            if weight_type == 'distance':
                # 距离优化：直接使用长度
                length = edge_data.get('length', 0)
                weight = length if length is not None and length >= 0 else float('inf')
            elif weight_type == 'time':
                # 时间优化：根据长度和速度计算时间
                weight = self._calculate_edge_time(edge_data, use_vehicle)
            else:
                weight = float('inf')
            
            # 选择最小权重
            min_weight = min(min_weight, weight)
        
        return min_weight if min_weight != float('inf') else 1000.0

    def _get_segment_category_speed(self, node1: Any, node2: Any, use_vehicle: bool) -> Union[float, str]:
        """
        确定路段的类别速度，用于分段
        
        Args:
            node1: 起始节点
            node2: 目标节点
            use_vehicle: 是否使用交通工具
            
        Returns:
            Union[float, str]: 速度类别或错误信息
        """
        if not use_vehicle:
            return self.base_speed

        candidate_edges = self._get_edge_data_candidates(node1, node2)
        if not candidate_edges:
            return 'unknown_category_no_edge'

        min_time = float('inf')
        chosen_edge_data = None

        for edge_data in candidate_edges:
            edge_time = self._calculate_edge_time(edge_data, use_vehicle)
            if edge_time < min_time:
                min_time = edge_time
                chosen_edge_data = edge_data
        
        if chosen_edge_data:
            road_type = chosen_edge_data.get('highway', 'unclassified')
            return self._get_road_base_speed(road_type)
        else:
            return 'unknown_category_no_chosen_edge'

    def _segment_path_by_speed(self, flat_path: List[Any], optimize_for: str, use_vehicle: bool) -> List[Dict[str, Any]]:
        """根据速度对路径进行分段"""
        if not flat_path:
            return []

        if len(flat_path) == 1:
            speed_category = self._get_single_point_speed_category(optimize_for, use_vehicle)
            return [{'speed': speed_category, 'nodes': flat_path}]

        if optimize_for == 'distance':
            return [{'speed': 'distance_optimized', 'nodes': flat_path}]

        if not use_vehicle:
            return [{'speed': self.base_speed, 'nodes': flat_path}]

        # optimize_for == 'time' AND use_vehicle == True
        return self._segment_by_vehicle_speed(flat_path, use_vehicle)

    def _get_single_point_speed_category(self, optimize_for: str, use_vehicle: bool) -> str:
        """获取单点的速度类别"""
        if optimize_for == 'time':
            return self.base_speed if not use_vehicle else self._get_road_base_speed('unclassified')
        elif optimize_for == 'distance':
            return 'distance_optimized_point'
        return 'single_point'

    def _segment_by_vehicle_speed(self, flat_path: List[Any], use_vehicle: bool) -> List[Dict[str, Any]]:
        """按车辆速度对路径进行分段"""
        if len(flat_path) < 2:
            return [{'speed': 'error_short_path_unexpected', 'nodes': flat_path}]

        segmented_path = []
        current_category_speed = self._get_segment_category_speed(flat_path[0], flat_path[1], use_vehicle)
        current_nodes = [flat_path[0], flat_path[1]]

        for i in range(1, len(flat_path) - 1):
            node_a = flat_path[i]
            node_b = flat_path[i+1]
            
            next_edge_category_speed = self._get_segment_category_speed(node_a, node_b, use_vehicle)
            
            if self._speeds_match(current_category_speed, next_edge_category_speed):
                current_nodes.append(node_b)
            else:
                segmented_path.append({'speed': current_category_speed, 'nodes': list(current_nodes)})
                current_category_speed = next_edge_category_speed
                current_nodes = [node_a, node_b]
                
        if current_nodes:
            segmented_path.append({'speed': current_category_speed, 'nodes': list(current_nodes)})
            
        return segmented_path

    def _speeds_match(self, speed1: Union[float, str], speed2: Union[float, str]) -> bool:
        """检查两个速度是否匹配"""
        if isinstance(speed1, (int, float)) and isinstance(speed2, (int, float)):
            return abs(speed1 - speed2) < 1e-5
        return speed1 == speed2

    def _flatten_segmented_path(self, segmented_path: List[Dict[str, Any]]) -> List[Any]:
        """将分段路径展平为节点列表"""
        if not segmented_path:
            return []
        
        flat_path = list(segmented_path[0]['nodes'])
        for i in range(1, len(segmented_path)):
            segment_nodes = segmented_path[i]['nodes']
            if segment_nodes and flat_path and segment_nodes[0] == flat_path[-1]:
                flat_path.extend(segment_nodes[1:])
            else:
                flat_path.extend(segment_nodes)
        return flat_path
    
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

    def _validate_nodes(self, start_node: Any, end_node: Any) -> None:
        """验证起始和终止节点是否有效"""
        if self.graph is None:
            raise ValueError("地图数据尚未加载")
            
        if start_node not in self.graph.nodes:
            raise ValueError(f"起点节点 {start_node} 不在地图中")
            
        if end_node not in self.graph.nodes:
            raise ValueError(f"终点节点 {end_node} 不在地图中")

    def _relax_neighbors(self, current_node, distances, predecessors, priority_queue, weight_type='distance', use_vehicle: bool = False):
        """松弛邻居节点"""
        current_distance = distances[current_node]
        
        for neighbor in self.graph.neighbors(current_node):
            weight = self._get_edge_weight(current_node, neighbor, weight_type, use_vehicle=use_vehicle)
            new_distance = current_distance + weight
            
            if new_distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_distance
                predecessors[neighbor] = current_node
                priority_queue.push((new_distance, neighbor))

    def dijkstra(self, start_node: Any, end_node: Any, optimize_for: str = 'distance', use_vehicle: bool = False) -> Tuple[float, List[Dict[str, Any]]]:
        """
        使用Dijkstra算法计算从起点到终点的最短路径

        Args:
            start_node: 起点节点ID
            end_node: 终点节点ID
            optimize_for: 优化目标，'distance'表示最短距离，'time'表示最短时间
            use_vehicle: 是否使用交通工具进行时间估算

        Returns:
            Tuple[float, List[Dict[str, Any]]]: 总成本(距离/时间)和分段路径列表
        """
        self._validate_nodes(start_node, end_node)
        
        if start_node == end_node:
            speed_cat = self._get_single_point_speed_category(optimize_for, use_vehicle)
            return 0.0, [{'speed': speed_cat, 'nodes': [start_node]}]

        distances = {start_node: 0.0}
        predecessors = {}
        priority_queue = MinHeap()
        priority_queue.push((0.0, start_node))
        visited = MySet()
        
        path_found = False
        while not priority_queue.is_empty():
            current_distance, current_node = priority_queue.pop()
            
            if current_node == end_node:
                path_found = True
                break
            
            if visited.contains(current_node) or current_distance > distances.get(current_node, float('inf')):
                continue
            
            visited.add(current_node)
            self._relax_neighbors(current_node, distances, predecessors, priority_queue, optimize_for, use_vehicle=use_vehicle)
        
        if not path_found or end_node not in distances:
            return float('inf'), []
        
        flat_path = self._reconstruct_path(predecessors, start_node, end_node)
        if not flat_path:
            return distances[end_node], []

        segmented_path = self._segment_path_by_speed(flat_path, optimize_for, use_vehicle)
        return distances[end_node], segmented_path

    def dijkstra_shortest_time(self, start_node: Any, end_node: Any, use_vehicle: bool = False) -> Tuple[float, List[Dict[str, Any]]]:
        """计算最短时间路径"""
        return self.dijkstra(start_node, end_node, optimize_for='time', use_vehicle=use_vehicle)

    def _calculate_path_time(self, path: List[Any], use_vehicle: bool = False) -> float:
        """计算路径的总时间"""
        if not path or len(path) < 2:
            return 0.0
        
        total_time = 0.0
        for i in range(len(path) - 1):
            edge_weight = self._get_edge_weight(path[i], path[i+1], 'time', use_vehicle)
            if edge_weight == float('inf'):
                return float('inf')
            total_time += edge_weight
        
        return total_time

    def _calculate_path_distance(self, path: List[Any]) -> float:
        """计算路径的总距离"""
        if not path or len(path) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(path) - 1):
            edge_weight = self._get_edge_weight(path[i], path[i+1], 'distance', False)
            if edge_weight == float('inf'):
                return float('inf')
            total_distance += edge_weight
        
        return total_distance

    def compare_routes(self, start_node: Any, end_node: Any, use_vehicle_for_time: bool = False) -> dict:
        """比较最短距离路径和最短时间路径"""
        # 计算最短距离路径
        distance_cost, distance_segmented_path = self.dijkstra(start_node, end_node, optimize_for='distance', use_vehicle=False)
        
        # 计算最短时间路径
        time_cost, time_segmented_path = self.dijkstra(start_node, end_node, optimize_for='time', use_vehicle=use_vehicle_for_time)
        
        # 展平路径用于计算交叉指标
        distance_flat_path = self._flatten_segmented_path(distance_segmented_path)
        time_flat_path = self._flatten_segmented_path(time_segmented_path)

        distance_path_time = self._calculate_path_time(distance_flat_path, use_vehicle=use_vehicle_for_time) if distance_flat_path else float('inf')
        time_path_distance = self._calculate_path_distance(time_flat_path) if time_flat_path else float('inf')
        
        return {
            'shortest_distance': {
                'path': distance_segmented_path,
                'distance': distance_cost,
                'time': distance_path_time,
                'avg_speed': self._calculate_avg_speed(distance_cost, distance_path_time)
            },
            'shortest_time': {
                'path': time_segmented_path,
                'distance': time_path_distance,
                'time': time_cost,
                'avg_speed': self._calculate_avg_speed(time_path_distance, time_cost)
            }
        }

    def _calculate_avg_speed(self, distance: float, time: float) -> float:
        """计算平均速度"""
        if time > 0 and time != float('inf') and distance != float('inf'):
            return (distance / 1000) / (time / 3600)
        return 0.0

    def get_nearest_node(self, lat: float, lng: float) -> Any:
        """获取最接近给定经纬度的图中节点"""
        try:
            return ox.nearest_nodes(self.graph, lng, lat)
        except:
            # 手动计算最近节点
            min_dist = float('inf')
            nearest_node = None
            
            for node, data in self.graph.nodes(data=True):
                try:
                    node_lat = data.get('y', data.get('lat'))
                    node_lng = data.get('x', data.get('lon'))
                    
                    if node_lat is None or node_lng is None:
                        continue
                    
                    # 使用简单的欧几里得距离作为近似
                    dist = ((node_lat - lat) ** 2 + (node_lng - lng) ** 2) ** 0.5
                    
                    if dist < min_dist:
                        min_dist = dist
                        nearest_node = node
                except Exception:
                    continue
            
            return nearest_node

    def plan_route(self, coordinates: List[Tuple[float, float]], optimize_for: str = 'distance', use_vehicle: bool = False) -> Tuple[float, List[Dict[str, Any]]]:
        """规划经过所有给定坐标点的最短路线"""
        if len(coordinates) < 2:
            raise ValueError("至少需要提供2个坐标点")
        
        # 获取每个坐标对应的最近节点
        nodes = [self.get_nearest_node(lat, lng) for lat, lng in coordinates]
        
        # 检查是否所有节点都有效
        if any(node is None for node in nodes):
            raise ValueError("部分坐标点无法匹配到地图上的节点")
        
        start_node = nodes[0]
        waypoints = nodes[1:]
        
        if len(nodes) == 2:
            return self.dijkstra(nodes[0], nodes[1], optimize_for, use_vehicle=use_vehicle)
        elif len(nodes) == 1:
            speed_cat = self._get_single_point_speed_category(optimize_for, use_vehicle)
            return 0.0, [{'speed': speed_cat, 'nodes': [start_node]}]

        return self._solve_tsp_improved(start_node, waypoints, optimize_for, use_vehicle=use_vehicle)

    def _solve_tsp_improved(self, start_node: Any, waypoints: List[Any], optimize_for: str = 'distance', use_vehicle: bool = False) -> Tuple[float, List[Dict[str, Any]]]:
        """使用改进的贪心算法和2-opt局部优化求解TSP问题"""
        all_nodes = [start_node] + waypoints
        paths_data = {}
        
        # 预计算所有节点对之间的路径
        for i, node_i in enumerate(all_nodes):
            for j, node_j in enumerate(all_nodes):
                if i == j:
                    continue
                cost, segmented_path = self.dijkstra(node_i, node_j, optimize_for, use_vehicle=use_vehicle)
                paths_data[(node_i, node_j)] = (cost, segmented_path)
        
        # 创建距离矩阵用于TSP算法
        distances_for_tsp = {pair: data[0] for pair, data in paths_data.items()}

        tour_nodes = self._nearest_neighbor_tsp(start_node, waypoints, distances_for_tsp)
        improved_tour_nodes = self._two_opt_optimize(tour_nodes, distances_for_tsp)
        
        return self._construct_complete_path(improved_tour_nodes, paths_data, optimize_for, use_vehicle)

    def _nearest_neighbor_tsp(self, start_node: Any, waypoints: List[Any], distances: Dict) -> List[Any]:
        """使用最近邻算法求解TSP问题"""
        unvisited = set(waypoints)
        tour = [start_node]
        current = start_node
        
        while unvisited:
            nearest = min(unvisited, key=lambda node: distances.get((current, node), float('inf')))
            tour.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return tour

    def _two_opt_optimize(self, tour: List[Any], distances: Dict) -> List[Any]:
        """使用2-opt算法优化TSP解"""
        if len(tour) <= 3:
            return tour
        
        improved = True
        while improved:
            improved = False
            for i in range(1, len(tour) - 2):
                for j in range(i + 1, len(tour)):
                    if j == len(tour) - 1:
                        continue
                    
                    # 计算当前边的成本
                    current_cost = (
                        distances.get((tour[i-1], tour[i]), float('inf')) +
                        distances.get((tour[j], tour[j+1]), float('inf'))
                    )
                    
                    # 计算交换后的成本
                    new_cost = (
                        distances.get((tour[i-1], tour[j]), float('inf')) +
                        distances.get((tour[i], tour[j+1]), float('inf'))
                    )
                    
                    if new_cost < current_cost:
                        # 执行2-opt交换
                        tour[i:j+1] = reversed(tour[i:j+1])
                        improved = True
        
        return tour

    def _construct_complete_path(self, tour: List[Any], paths_data: Dict[Tuple[Any,Any], Tuple[float, List[Dict[str,Any]]]], optimize_for: str, use_vehicle: bool) -> Tuple[float, List[Dict[str, Any]]]:
        """基于节点访问顺序构建完整分段路径和计算总成本"""
        complete_segmented_path: List[Dict[str, Any]] = []
        total_calculated_cost = 0.0

        if not tour or len(tour) < 2:
            if tour:
                speed_cat = self._get_single_point_speed_category(optimize_for, use_vehicle)
                return 0.0, [{'speed': speed_cat, 'nodes': tour}]
            return 0.0, []

        for i in range(len(tour) - 1):
            node1 = tour[i]
            node2 = tour[i+1]
            
            segment_cost, segmented_sub_path = paths_data.get((node1, node2), (float('inf'), []))
            
            if not segmented_sub_path:
                total_calculated_cost = float('inf')
                continue

            total_calculated_cost += segment_cost

            if not complete_segmented_path:
                complete_segmented_path.extend(segmented_sub_path)
            else:
                self._merge_segmented_paths(complete_segmented_path, segmented_sub_path)

        return total_calculated_cost, complete_segmented_path

    def _merge_segmented_paths(self, main_path: List[Dict[str, Any]], sub_path: List[Dict[str, Any]]) -> None:
        """合并两个分段路径"""
        if not sub_path:
            return
        
        last_main_segment = main_path[-1]
        first_sub_segment = sub_path[0]
        
        # 检查速度匹配和节点连续性
        speeds_match = self._speeds_match(last_main_segment['speed'], first_sub_segment['speed'])
        nodes_continuous = (last_main_segment['nodes'] and first_sub_segment['nodes'] and 
                           last_main_segment['nodes'][-1] == first_sub_segment['nodes'][0])

        if speeds_match and nodes_continuous:
            last_main_segment['nodes'].extend(first_sub_segment['nodes'][1:])
            if len(sub_path) > 1:
                main_path.extend(sub_path[1:])
        else:
            main_path.extend(sub_path)

    def get_route_coordinates(self, path: List[Any]) -> List[dict]:
        """获取路径上所有节点的经纬度坐标"""
        path_coords = []
        for item in path:
            route_coords = []
            for node_id in item.get('nodes', []):
                try:
                    node = self.graph.nodes[node_id] 
                    lat = node.get('y', node.get('lat'))
                    lng = node.get('x', node.get('lon'))
                    
                    if lat is not None and lng is not None:
                        route_coords.append([lat, lng])
                except:
                    pass

            path_segments = {
                "speed": item.get('speed', 'unknown'),
                "nodes": route_coords
            }
            path_coords.append(path_segments)

        return path_coords

    def calculate_distances_to_points(self, start_coordinate: str, target_points: List[dict], optimize_for: str = 'distance') -> List[dict]:
        """使用一次Dijkstra算法计算从起点到多个目标点的距离或时间"""
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
            
            # 使用多目标Dijkstra算法
            distances = self._dijkstra_multi_target(start_node, target_nodes, optimize_for)
            
            # 将结果写入目标点列表
            for i, point in enumerate(target_points):
                if target_nodes[i] is not None:
                    point["value1"] = distances.get(target_nodes[i], float('inf'))
                else:
                    point["value1"] = float('inf')
            
            return target_points
            
        except Exception as e:
            print(f"计算距离/时间失败: {e}")
            for point in target_points:
                point["value1"] = float('inf')
            return target_points

    def _dijkstra_multi_target(self, start_node: Any, target_nodes: List[Any], optimize_for: str = 'distance') -> dict:
        """单源多目标的Dijkstra算法"""
        if not target_nodes:
            return {}
            
        valid_targets = set(target for target in target_nodes 
                          if target is not None and target in self.graph)
        
        if not valid_targets:
            return {}
        
        distances = {start_node: 0.0}
        priority_queue = MinHeap()
        priority_queue.push((0.0, start_node))
        visited = MySet()
        target_distances = {}
        
        while not priority_queue.is_empty() and len(target_distances) < len(valid_targets):
            current_distance, current_node = priority_queue.pop()
            
            if visited.contains(current_node):
                continue
            
            if current_distance > distances.get(current_node, float('inf')):
                continue
            
            visited.add(current_node)
            
            if current_node in valid_targets:
                target_distances[current_node] = current_distance
            
            if len(target_distances) == len(valid_targets):
                break
            
            # 松弛邻居
            for neighbor in self.graph.neighbors(current_node):
                weight = self._get_edge_weight(current_node, neighbor, optimize_for)
                new_distance = current_distance + weight
                
                if new_distance < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_distance
                    priority_queue.push((new_distance, neighbor))
        
        return target_distances

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """计算两点之间的哈弗辛距离（球面距离）"""
        from math import radians, sin, cos, sqrt, atan2
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        r = 6371  # 地球半径，单位为公里
        
        return r * c

    def plot_route_interactive(self, path: List[Any], original_coordinates: List[Tuple[float, float]] = None, save_path=None):
        """使用Folium创建交互式地图"""
        try:
            if folium is None:
                print("请安装必要的库: pip install folium")
                return None
                
            route_coords = self.get_route_coordinates(path)
            
            if not route_coords:
                print("无法获取路径坐标")
                return None
            
            # 提取所有坐标点
            all_coords = []
            for segment in route_coords:
                all_coords.extend(segment['nodes'])
            
            if len(all_coords) < 2:
                print("路径点数量不足")
                return None
            
            # 计算中心点和缩放级别
            lats = [lat for lat, _ in all_coords]
            lngs = [lng for _, lng in all_coords]
            center_lat = sum(lats) / len(lats)
            center_lng = sum(lngs) / len(lngs)
            
            lat_range = max(lats) - min(lats)
            lng_range = max(lngs) - min(lngs)
            zoom_start = 14
            
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
            
            # 添加路径线
            folium.PolyLine(
                locations=all_coords,
                color='blue',
                weight=5,
                opacity=0.7,
                tooltip='路线'
            ).add_to(m)
            
            # 添加起点和终点标记
            if all_coords:
                start_lat, start_lng = all_coords[0]
                end_lat, end_lng = all_coords[-1]
                
                folium.Marker([start_lat, start_lng], popup='<b>起点</b>', 
                             icon=folium.Icon(color='green')).add_to(m)
                folium.Marker([end_lat, end_lng], popup='<b>终点</b>', 
                             icon=folium.Icon(color='red')).add_to(m)
            
            # 保存地图
            if not save_path:
                save_path = 'route_map.html'
            
            m.save(save_path)
            print(f"交互式地图已保存至: {save_path}")
            
            try:
                webbrowser.open('file://' + os.path.abspath(save_path))
            except Exception as e:
                print(f"自动打开地图失败: {e}")
                
            return save_path
        except Exception as e:
            print(f"创建交互式地图失败: {e}")
            return None


# 使用示例
if __name__ == "__main__":
    try:
        router = DijkstraRouter()
        
        coordinates = [
            (39.92094, 116.36924),
            (39.93428, 116.38447),
        ]
        
        total_distance, path = router.plan_route(coordinates)
        route_coords = router.get_route_coordinates(path)
        
        print(f"总距离: {total_distance:.2f} 米")
        print(f"途径节点数: {len(path)}")
        
        html_path = router.plot_route_interactive(path, coordinates)
        print(f"地图已保存至: {html_path}")
        
    except Exception as e:
        print(f"程序执行失败: {e}")
