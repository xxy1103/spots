"""
简化的测试脚本：验证优化后的 DijkstraRouter 类
"""
import sys
import os
import time

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def test_basic_functionality():
    """基础功能测试"""
    print("=== 基础功能测试 ===\n")
    
    try:
        from module.data_structure.dijkstra import DijkstraRouter
        
        print("1. 初始化路由器...")
        router = DijkstraRouter()
        print("   ✓ 优化版本初始化成功")
        
        # 测试路径规划
        print("\n2. 测试路径规划...")
        start_point = (39.9042, 116.4074)  # 北京天安门
        end_point = (39.9163, 116.3972)    # 故宫
        
        result = router.plan_route([start_point, end_point], 'distance', False)
        if result:
            distance, path = result
            print("   ✓ 路径规划成功")
            print(f"   路径长度: {len(path)} 个节点")
            print(f"   总距离: {distance:.2f} 米")
        else:
            print("   ✗ 路径规划失败")
            
    except Exception as e:
        print(f"优化版本测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_code_quality():
    """代码质量对比"""
    print("=== 代码质量对比 ===\n")
    
    try:
        # 检查文件大小
        original_size = os.path.getsize("module/data_structure/dijkstra.py")
        optimized_size = os.path.getsize("module/data_structure/dijkstra_optimized.py")
        
        print(f"1. 文件大小对比:")
        print(f"   原始版本: {original_size:,} 字节")
        print(f"   优化版本: {optimized_size:,} 字节")
        reduction = ((original_size - optimized_size) / original_size) * 100
        print(f"   减少: {reduction:.1f}%")
        
        # 检查行数
        with open("module/data_structure/dijkstra.py", 'r', encoding='utf-8') as f:
            original_lines = len(f.readlines())
        
        with open("module/data_structure/dijkstra_optimized.py", 'r', encoding='utf-8') as f:
            optimized_lines = len(f.readlines())
        
        print(f"\n2. 代码行数对比:")
        print(f"   原始版本: {original_lines:,} 行")
        print(f"   优化版本: {optimized_lines:,} 行")
        line_reduction = ((original_lines - optimized_lines) / original_lines) * 100
        print(f"   减少: {line_reduction:.1f}%")
        
    except Exception as e:
        print(f"代码质量检查失败: {e}")

def test_performance():
    """性能测试"""
    print("=== 性能测试 ===\n")
    
    test_points = [
        (39.9042, 116.4074),  # 北京天安门
        (39.9163, 116.3972),  # 故宫
    ]
    
    try:
        print("1. 测试优化版本性能...")
        from module.data_structure.dijkstra import DijkstraRouter as OptimizedRouter
        
        start_time = time.time()
        optimized_router = OptimizedRouter()
        load_time = time.time() - start_time
        print(f"   加载时间: {load_time:.2f}秒")
        
        start_time = time.time()
        result = optimized_router.plan_route(test_points, 'distance', False)
        calc_time = time.time() - start_time
        print(f"   计算时间: {calc_time:.2f}秒")
        
        if result:
            distance, path = result
            print(f"   路径节点: {len(path)}")
            print(f"   总距离: {distance:.2f} 米")
        
    except Exception as e:
        print(f"性能测试失败: {e}")

if __name__ == "__main__":
    print("开始测试优化后的 DijkstraRouter 类...\n")
    
    test_code_quality()
    print("\n" + "="*50 + "\n")
    
    test_basic_functionality()
    print("\n" + "="*50 + "\n")
    
    test_performance()
    
    print("\n测试完成！")
