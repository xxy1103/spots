import os
import heapq
from typing import List, Tuple, Dict, Any, Optional
import math

import osmnx as ox
import networkx as nx


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
    
    def dijkstra(self, start_node: Any, end_node: Any) -> Tuple[float, List[Any]]:
        """
        使用Dijkstra算法计算从起点到终点的最短路径
        
        Args:
            start_node: 起点节点ID
            end_node: 终点节点ID
            
        Returns:
            Tuple[float, List[Any]]: 总距离和路径节点列表
        """
        # 检查节点是否存在于图中
        if start_node not in self.graph or end_node not in self.graph:
            return float('inf'), []
        
        # 初始化距离字典和前驱节点字典
        distances = {node: float('inf') for node in self.graph.nodes}
        distances[start_node] = 0
        predecessors = {node: None for node in self.graph.nodes}
        
        # 使用优先队列实现Dijkstra算法
        priority_queue = [(0, start_node)]
        visited = set()
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            # 如果已经找到目标节点的最短路径，退出循环
            if current_node == end_node:
                break
            
            # 如果已经访问过该节点，跳过
            if current_node in visited:
                continue
            
            # 标记为已访问
            visited.add(current_node)
            
            # 检查所有邻居节点
            for neighbor in self.graph.neighbors(current_node):
                # 获取边的权重（距离）
                try:
                    edge_data = self.graph.get_edge_data(current_node, neighbor)
                    # 处理可能有多条边的情况
                    if isinstance(edge_data, dict):
                        if len(edge_data) == 1:
                            # 单边情况
                            weight = list(edge_data.values())[0].get('length', 1.0)
                        else:
                            # 多边情况，选择最短的
                            weight = min(
                                [data.get('length', float('inf')) for data in edge_data.values()]
                            )
                    else:
                        weight = edge_data.get('length', 1.0)
                except (AttributeError, KeyError):
                    # 如果没有length属性，使用默认值1.0
                    weight = 1.0
                
                # 计算到邻居的新距离
                distance = current_distance + weight
                
                # 如果找到更短的路径，更新距离和前驱节点
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    predecessors[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor))
        
        # 如果没有找到路径
        if distances[end_node] == float('inf'):
            return float('inf'), []
        
        # 构建路径
        path = []
        current = end_node
        while current is not None:
            path.append(current)
            current = predecessors[current]
        path.reverse()
        
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
        
        # 计算所有点对之间的最短路径
        distances = {}
        paths = {}
        for i, node_i in enumerate([start_node] + waypoints):
            for j, node_j in enumerate(waypoints):
                if i != j + 1:  # 避免计算自身到自身的距离
                    dist, path = self.dijkstra(node_i, node_j)
                    distances[(node_i, node_j)] = dist
                    paths[(node_i, node_j)] = path
        
        # 使用贪心算法处理多途径点路径规划
        current_node = start_node
        remaining_points = set(waypoints)
        total_distance = 0
        complete_path = [current_node]
        
        # 贪心算法：每次选择距离最近的未访问点
        while remaining_points:
            # 找到距离当前点最近的未访问点
            next_node = min(
                remaining_points,
                key=lambda node: distances.get((current_node, node), float('inf'))
            )
            
            # 获取从当前点到下一点的路径
            segment_distance = distances.get((current_node, next_node), float('inf'))
            segment_path = paths.get((current_node, next_node), [])
            
            # 如果无法找到路径，报错
            if segment_distance == float('inf') or not segment_path:
                raise ValueError(f"无法找到从 {current_node} 到 {next_node} 的路径")
            
            # 将路径添加到完整路径中（排除起点以避免重复）
            complete_path.extend(segment_path[1:])
            
            # 更新总距离
            total_distance += segment_distance
            
            # 更新当前点并移除已访问点
            current_node = next_node
            remaining_points.remove(next_node)
        
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
                    route_coords.append((lat, lng))
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
        """
        try:
            import folium
            
            # 获取路径坐标
            route_coords = self.get_route_coordinates(path)
            
            if not route_coords:
                raise ValueError("无法获取路径坐标")
            
            # 创建地图，以路径中心点为中心
            center_lat = sum(lat for lat, _ in route_coords) / len(route_coords)
            center_lng = sum(lng for _, lng in route_coords) / len(route_coords)
            
            m = folium.Map(location=[center_lat, center_lng], zoom_start=14)
            
            # 添加路径线
            folium.PolyLine(
                locations=[(lat, lng) for lat, lng in route_coords],
                color='blue',
                weight=4,
                opacity=0.7
            ).add_to(m)
            
            # 添加起点和终点标记
            start_lat, start_lng = route_coords[0]
            end_lat, end_lng = route_coords[-1]
            
            folium.Marker(
                [start_lat, start_lng],
                popup='起点',
                icon=folium.Icon(color='green')
            ).add_to(m)
            
            folium.Marker(
                [end_lat, end_lng],
                popup='终点',
                icon=folium.Icon(color='red')
            ).add_to(m)
            
            # 添加原始途径点标记
            if original_coordinates and len(original_coordinates) > 1:
                for i, (lat, lng) in enumerate(original_coordinates[1:], 1):
                    folium.Marker(
                        [lat, lng],
                        popup=f'途径点 {i}',
                        icon=folium.Icon(color='orange', icon='info-sign')
                    ).add_to(m)
            
            # 添加中间路径节点标记
            for i, (lat, lng) in enumerate(route_coords[1:-1], 1):
                folium.CircleMarker(
                    [lat, lng],
                    radius=3,
                    color='blue',
                    fill=True,
                    fill_opacity=0.6
                ).add_to(m)
            
            # 保存为HTML文件
            if not save_path:
                save_path = 'route_map.html'
            
            m.save(save_path)
            print(f"交互式地图已保存至: {save_path}")
            
            return save_path
        except ImportError:
            print("请安装必要的库: pip install folium")
        except Exception as e:
            print(f"创建交互式地图失败: {e}")




# 使用示例
if __name__ == "__main__":
    # 创建路由器实例
    router = DijkstraRouter()
    
    # 示例坐标 (纬度, 经度)
    coordinates = [
        (39.92094, 116.36924),  # 北京某地点1
        (39.91198, 116.40554),  # 北京某地点2
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
            import webbrowser
            webbrowser.open(html_path)
        except:
            pass
        
    except Exception as e:
        print(f"路线规划失败: {e}")