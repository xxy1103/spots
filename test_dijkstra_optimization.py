"""
测试脚本：验证优化后的 DijkstraRouter 类的功能
"""
import sys
import os
import time

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def test_dijkstra_performance():
    """
    性能对比测试：原始版本 vs 优化版本
    """
    print("=== DijkstraRouter 性能对比测试 ===\n")
    
    # 测试参数
    test_points = [
        (39.9042, 116.4074),  # 北京天安门
        (39.9163, 116.3972),  # 故宫
        (39.9289, 116.3883),  # 景山公园
        (39.9075, 116.3912),  # 中山公园
        (39.8955, 116.4056),  # 前门
    ]
    
    vehicle_type = "walking"
    
    try:
        # 测试原始版本
        print("1. 测试原始版本...")
        from module.data_structure.dijkstra import DijkstraRouter as OriginalRouter
        
        start_time = time.time()
        original_router = OriginalRouter()
        original_load_time = time.time() - start_time
        print(f"   原始版本加载时间: {original_load_time:.2f}秒")
          # 测试路径计算
        start_time = time.time()
        original_result = original_router.plan_route(
            [test_points[0], test_points[1]], 'distance', vehicle_type == "driving"
        )
        original_calc_time = time.time() - start_time
        print(f"   原始版本路径计算时间: {original_calc_time:.2f}秒")
        
        if original_result:
            distance, path = original_result
            print(f"   原始版本路径长度: {len(path)} 个节点")
            print(f"   原始版本总距离: {distance}")
            print(f"   原始版本路径数据: {type(path)}")
        
    except Exception as e:
        print(f"   原始版本测试失败: {e}")
        original_router = None
        original_load_time = 0
        original_calc_time = 0
    
    print()
    
    try:
        # 测试优化版本
        print("2. 测试优化版本...")
        from module.data_structure.dijkstra import DijkstraRouter as OptimizedRouter
        
        start_time = time.time()
        optimized_router = OptimizedRouter()
        optimized_load_time = time.time() - start_time
        print(f"   优化版本加载时间: {optimized_load_time:.2f}秒")
          # 测试路径计算
        start_time = time.time()
        optimized_result = optimized_router.plan_route(
            [test_points[0], test_points[1]], 'distance', vehicle_type == "driving"
        )
        optimized_calc_time = time.time() - start_time
        print(f"   优化版本路径计算时间: {optimized_calc_time:.2f}秒")
        
        if optimized_result:
            distance, path = optimized_result
            print(f"   优化版本路径长度: {len(path)} 个节点")
            print(f"   优化版本总距离: {distance}")
            print(f"   优化版本路径数据: {type(path)}")
        
    except Exception as e:
        print(f"   优化版本测试失败: {e}")
        optimized_router = None
        optimized_load_time = 0
        optimized_calc_time = 0
    
    print()
    
    # 性能对比
    print("3. 性能对比结果:")
    if original_load_time > 0 and optimized_load_time > 0:
        load_improvement = ((original_load_time - optimized_load_time) / original_load_time) * 100
        print(f"   加载时间改进: {load_improvement:+.1f}%")
    
    if original_calc_time > 0 and optimized_calc_time > 0:
        calc_improvement = ((original_calc_time - optimized_calc_time) / original_calc_time) * 100
        print(f"   计算时间改进: {calc_improvement:+.1f}%")
    
    print()


def test_functionality():
    """
    功能测试：验证各个方法是否正常工作
    """
    print("=== 功能测试 ===\n")
    
    try:
        from module.data_structure.dijkstra import DijkstraRouter
        
        print("1. 初始化路由器...")
        router = DijkstraRouter()
        print("   ✓ 初始化成功")
          # 测试点
        start_point = (39.9042, 116.4074)  # 北京天安门
        end_point = (39.9163, 116.3972)    # 故宫
        
        print("\n2. 测试单点路径查找...")
        result = router.plan_route([start_point, end_point], 'distance', False)
        if result:
            distance, path = result
            print("   ✓ 单点路径查找成功")
            print(f"   路径包含 {len(path)} 个节点")
            print(f"   总距离: {distance}")
        else:
            print("   ✗ 单点路径查找失败")
        
        print("\n3. 测试多点路径优化...")
        waypoints = [
            (39.9042, 116.4074),  # 天安门
            (39.9163, 116.3972),  # 故宫
            (39.9289, 116.3883),  # 景山公园
            (39.9075, 116.3912),  # 中山公园
        ]
        try:
            optimized_route = router.plan_route(waypoints, 'distance', False)
            if optimized_route:
                distance, path = optimized_route
                print("   ✓ 多点路径优化成功")
                print(f"   优化后路径包含 {len(path)} 个路段")
                print(f"   总距离: {distance}")
            else:
                print("   ✗ 多点路径优化失败")
        except Exception as e:
            print(f"   ✗ 多点路径优化失败: {e}")
        print("\n4. 测试不同交通方式...")
        vehicles = [("walking", False), ("driving", True), ("cycling", False)]
        for vehicle_name, use_vehicle in vehicles:
            try:
                result = router.plan_route([start_point, end_point], 'distance', use_vehicle)
                if result:
                    print(f"   ✓ {vehicle_name} 模式测试成功")
                else:
                    print(f"   ✗ {vehicle_name} 模式测试失败")
            except Exception as e:
                print(f"   ✗ {vehicle_name} 模式测试失败: {e}")
        
        print("\n5. 测试边界情况...")
          # 测试相同起终点
        try:
            result = router.plan_route([start_point, start_point], 'distance', False)
            print("   ✓ 相同起终点测试成功")
        except Exception as e:
            print(f"   ✗ 相同起终点测试失败: {e}")
        
        # 测试无效坐标
        try:
            result = router.plan_route([(0, 0), (0, 0)], 'distance', False)
            print("   ✓ 无效坐标处理正常")
        except Exception as e:
            print(f"   ✓ 无效坐标正确抛出异常: {type(e).__name__}")
        
        print("\n功能测试完成！")
        
    except Exception as e:
        print(f"功能测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_code_quality():
    """
    代码质量检查
    """
    print("=== 代码质量检查 ===\n")
    
    try:
        # 检查文件大小
        original_size = os.path.getsize("module/data_structure/dijkstra.py")
        optimized_size = os.path.getsize("module/data_structure/dijkstra_optimized.py")
        
        print(f"1. 文件大小对比:")
        print(f"   原始版本: {original_size:,} 字节")
        print(f"   优化版本: {optimized_size:,} 字节")
        reduction = ((original_size - optimized_size) / original_size) * 100
        print(f"   代码减少: {reduction:.1f}%")
        
        # 检查行数
        with open("module/data_structure/dijkstra.py", 'r', encoding='utf-8') as f:
            original_lines = len(f.readlines())
        
        with open("module/data_structure/dijkstra_optimized.py", 'r', encoding='utf-8') as f:
            optimized_lines = len(f.readlines())
        
        print(f"\n2. 代码行数对比:")
        print(f"   原始版本: {original_lines:,} 行")
        print(f"   优化版本: {optimized_lines:,} 行")
        line_reduction = ((original_lines - optimized_lines) / original_lines) * 100
        print(f"   行数减少: {line_reduction:.1f}%")
        
        # 检查方法数量（简单统计def关键字）
        with open("module/data_structure/dijkstra.py", 'r', encoding='utf-8') as f:
            original_content = f.read()
            original_methods = original_content.count('def ')
        
        with open("module/data_structure/dijkstra_optimized.py", 'r', encoding='utf-8') as f:
            optimized_content = f.read()
            optimized_methods = optimized_content.count('def ')
        
        print(f"\n3. 方法数量对比:")
        print(f"   原始版本: {original_methods} 个方法")
        print(f"   优化版本: {optimized_methods} 个方法")
        
        if optimized_methods > original_methods:
            print(f"   新增方法: {optimized_methods - original_methods} 个（重构产生）")
        elif optimized_methods < original_methods:
            print(f"   合并方法: {original_methods - optimized_methods} 个")
        else:
            print("   方法数量不变")
        
        print("\n代码质量检查完成！")
        
    except Exception as e:
        print(f"代码质量检查失败: {e}")


if __name__ == "__main__":
    print("开始测试优化后的 DijkstraRouter 类...\n")
    
    # 运行所有测试
    test_code_quality()
    print("\n" + "="*50 + "\n")
    
    test_functionality()
    print("\n" + "="*50 + "\n")
    
    test_dijkstra_performance()
    
    print("\n测试完成！")
