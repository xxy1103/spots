# -*- coding: utf-8 -*-
"""
景区搜索系统性能测试程序
专门测试景区搜索功能的性能表现，包括关键字搜索、类型筛选、排序等核心功能
提供详细的性能分析报告和可视化图表
"""

import sys
import os
import time
import random
import statistics
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
import seaborn as sns
import json
import threading
import concurrent.futures
from datetime import datetime
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# 添加模块路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

try:
    from module.Spot_class import SpotManager
    from module.fileIo import ConfigIo, spotIo
    from module.data_structure.hashtable import HashTable
    from module.data_structure.indexHeap import TopKHeap
    from module.data_structure.heap import MinHeap
    from module.data_structure.set import MySet
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print(f"项目根目录: {project_root}")
    sys.exit(1)

# 设置中文字体
def setup_chinese_font():
    """设置中文字体显示"""
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'DejaVu Sans']
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False
    
    try:
        fm._rebuild()
        print("✅ 字体配置完成")
    except Exception as e:
        print(f"⚠️ 字体配置警告: {e}")

class SpotSearchPerformanceTester:
    """景区搜索系统性能测试器"""
    
    def __init__(self):
        """初始化测试器"""
        print("🚀 初始化景区搜索性能测试器...")
        
        # 加载景区数据
        print("  📁 加载景区数据...")
        try:
            spots_data = spotIo.load_spots()
            print(f"  ✅ 成功加载 {spots_data.get('counts', 0)} 个景区")
        except Exception as e:
            print(f"  ❌ 加载景区数据失败: {e}")
            raise e
        
        # 初始化 SpotManager
        print("  🏗️  初始化SpotManager...")
        try:
            self.spot_manager = SpotManager.from_dict(spots_data)
            print("  ✅ SpotManager 初始化成功")
        except Exception as e:
            print(f"  ❌ SpotManager 初始化失败: {e}")
            raise e
        
        # 获取所有景区数据
        self.all_spots = self.spot_manager.spots
        self.total_spots = len(self.all_spots)
        
        # 获取所有景区类型
        try:
            config_io = ConfigIo()
            self.all_types = config_io.getAllSpotTypes()
            print(f"  ✅ 成功加载 {len(self.all_types)} 种景区类型")
        except Exception as e:
            print(f"  ⚠️ 加载景区类型失败: {e}")
            self.all_types = ["历史建筑", "赏花胜地", "萌萌动物", "城市漫步", "夜游观景", 
                             "遛娃宝藏地", "展馆展览", "地标观景", "登高爬山", "踏青必去", 
                             "自然山水", "游乐场", "演出"]
        
        # 性能数据收集
        self.performance_data = defaultdict(list)
        self.search_statistics = {}
          # 测试配置
        self.test_rounds = 100  # 每个测试的轮次
        self.concurrent_levels = [1, 5, 10, 20, 50]  # 并发测试级别
        
        print(f"✅ 初始化完成")
        print(f"   总景区数量: {self.total_spots}")
        print(f"   景区类型数量: {len(self.all_types)}")
        print(f"   景区类型: {', '.join(self.all_types)}")
        print(f"📊 景区总数: {self.total_spots}")
        print(f"🏷️ 景区类型数: {len(self.all_types)}")
        print(f"🔄 测试轮次: {self.test_rounds}")
        
    def measure_time(self, func, *args, **kwargs):
        """测量函数执行时间"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, (end_time - start_time) * 1000  # 返回毫秒
    
    def test_keyword_search_performance(self):
        """测试关键字搜索性能"""
        print("\n🔍 测试关键字搜索性能...")
          # 准备不同长度的测试关键字
        keywords_by_length = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
        
        # 从真实景区名称中提取不同长度的关键字
        for spot in self.all_spots[:50]:
            name = spot.name
            for length in [1, 2, 3, 4, 5, 6, 7, 8]:
                if len(name) >= length:
                    for i in range(len(name) - length + 1):
                        keyword = name[i:i+length]
                        if keyword not in keywords_by_length[length] and len(keywords_by_length[length]) < 5:
                            keywords_by_length[length].append(keyword)
        
        # 添加一些常见搜索词
        keywords_by_length[1].extend(["山", "湖", "古", "新", "大"])
        keywords_by_length[2].extend(["公园", "寺庙", "博物", "北京", "天安"])
        keywords_by_length[3].extend(["博物馆", "颐和园", "天坛", "故宫"])
        keywords_by_length[4].extend(["天安门广场", "颐和园"])
        keywords_by_length[5].extend(["故宫博物院", "北京动物园"])
        keywords_by_length[6].extend(["中国国家博物馆", "北京自然博物馆"])
        keywords_by_length[7].extend(["中国科学技术馆", "北京天文馆"])
        keywords_by_length[8].extend(["中国人民革命军事博物馆"])
        
        # 限制每种长度的关键字数量
        for length in keywords_by_length:
            keywords_by_length[length] = keywords_by_length[length][:5]
        
        search_times = []
        search_results_count = []
        search_times_by_length = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
        
        for length, keywords in keywords_by_length.items():
            print(f"  测试{length}字符关键字...")
            for keyword in keywords:
                times_for_keyword = []
                for _ in range(10):  # 每个关键字测试10次
                    result, exec_time = self.measure_time(
                        self.spot_manager.getSpotByName, keyword
                    )
                    times_for_keyword.append(exec_time)
                    
                avg_time = statistics.mean(times_for_keyword)
                search_times.append(avg_time)
                search_times_by_length[length].append(avg_time)
                search_results_count.append(len(result) if result else 0)
                
                print(f"    关键字 '{keyword}': {avg_time:.3f}ms, 结果数: {len(result) if result else 0}")
          # 统计数据
        self.performance_data['keyword_search_times'] = search_times
        self.performance_data['keyword_search_times_by_length'] = search_times_by_length
        self.performance_data['keyword_search_results'] = search_results_count
        
        self.search_statistics['keyword_search'] = {
            'avg_time': statistics.mean(search_times),
            'min_time': min(search_times),
            'max_time': max(search_times),
            'median_time': statistics.median(search_times),
            'std_time': statistics.stdev(search_times) if len(search_times) > 1 else 0,
            'avg_results': statistics.mean(search_results_count),
            'total_keywords_tested': sum(len(keywords) for keywords in keywords_by_length.values())
        }
        
        print(f"✅ 关键字搜索测试完成")
        print(f"   平均搜索时间: {self.search_statistics['keyword_search']['avg_time']:.3f}ms")
        print(f"   平均结果数量: {self.search_statistics['keyword_search']['avg_results']:.1f}")
    
    def test_type_based_search_performance(self):
        """测试基于类型的搜索性能"""
        print("\n🏷️ 测试类型搜索性能...")
        
        type_search_times = []
        type_search_results = []
        
        for spot_type in self.all_types:
            times_for_type = []
            for k in [5, 10, 20, 50]:  # 测试不同的k值
                result, exec_time = self.measure_time(
                    self.spot_manager.getTopKByType, spot_type, k
                )
                times_for_type.append(exec_time)
            
            avg_time = statistics.mean(times_for_type)
            type_search_times.append(avg_time)
            
            # 获取该类型的总景区数
            result, _ = self.measure_time(
                self.spot_manager.getTopKByType, spot_type, 1000
            )
            type_search_results.append(len(result) if result else 0)
            
            print(f"  类型 '{spot_type}': {avg_time:.3f}ms, 总数: {len(result) if result else 0}")
        
        self.performance_data['type_search_times'] = type_search_times
        self.performance_data['type_search_results'] = type_search_results
        self.search_statistics['type_search'] = {
            'avg_time': statistics.mean(type_search_times),
            'min_time': min(type_search_times),
            'max_time': max(type_search_times),
            'median_time': statistics.median(type_search_times),
            'std_time': statistics.stdev(type_search_times) if len(type_search_times) > 1 else 0,
            'avg_results': statistics.mean(type_search_results),
            'total_types_tested': len(self.all_types)
        }        
        print(f"✅ 类型搜索测试完成")
        print(f"   平均搜索时间: {self.search_statistics['type_search']['avg_time']:.3f}ms")
    
    def test_sorting_performance(self):
        """测试排序性能"""
        print("\n📊 测试排序性能...")
        
        # 测试getAllSpotsSorted方法的性能
        times = []
        for _ in range(20):  # 测试20次
            result, exec_time = self.measure_time(
                self.spot_manager.getAllSpotsSorted
            )
            times.append(exec_time)
        
        avg_time = statistics.mean(times)
        sorting_times = {
            'getAllSpotsSorted': {
                'avg_time': avg_time,
                'min_time': min(times),
                'max_time': max(times),
                'std_time': statistics.stdev(times) if len(times) > 1 else 0
            }
        }
        
        print(f"  全排序性能: {avg_time:.3f}ms")
        
        self.performance_data['sorting_times'] = sorting_times
        self.search_statistics['sorting'] = sorting_times
        
        print(f"✅ 排序性能测试完成")
    
    def test_data_structure_performance(self):
        """测试数据结构性能"""
        print("\n🔧 测试数据结构性能...")
        
        # 测试哈希表性能
        print("  测试哈希表性能...")
        hashtable = HashTable()
          # 插入测试
        insert_times = []
        for i in range(1000):
            test_item = {"id": i, "name": f"测试景点{i}"}
            _, exec_time = self.measure_time(hashtable.insert, test_item)
            insert_times.append(exec_time)
        
        # 查找测试
        search_times = []
        for i in range(100):
            search_char = "测"  # 搜索包含"测"字的项目
            _, exec_time = self.measure_time(hashtable.search, search_char)
            search_times.append(exec_time)
        
        hashtable_stats = {
            'avg_insert_time': statistics.mean(insert_times),
            'avg_search_time': statistics.mean(search_times),
            'total_operations': len(insert_times) + len(search_times)
        }
          # 测试堆性能
        print("  测试堆性能...")
        top_k_heap = TopKHeap()
        min_heap = MinHeap()
        
        heap_insert_times = []
        test_data = [(random.random() * 100, f"item_{i}") for i in range(500)]
        
        for score, item in test_data:
            _, exec_time = self.measure_time(top_k_heap.insert, item, score, random.randint(1, 1000))
            heap_insert_times.append(exec_time)
        
        heap_extract_times = []
        for _ in range(100):
            if top_k_heap.size() > 0:
                _, exec_time = self.measure_time(top_k_heap.getTopK, 1)
                heap_extract_times.append(exec_time)
        
        heap_stats = {
            'avg_insert_time': statistics.mean(heap_insert_times),
            'avg_extract_time': statistics.mean(heap_extract_times) if heap_extract_times else 0,
            'total_operations': len(heap_insert_times) + len(heap_extract_times)
        }
        
        # 测试自定义集合性能
        print("  测试自定义集合性能...")
        my_set = MySet()
        
        set_add_times = []
        for i in range(500):
            _, exec_time = self.measure_time(my_set.add, i)
            set_add_times.append(exec_time)
        
        set_contains_times = []
        for i in range(100):
            value = random.randint(0, 499)
            _, exec_time = self.measure_time(my_set.contains, value)
            set_contains_times.append(exec_time)
        
        set_stats = {
            'avg_add_time': statistics.mean(set_add_times),
            'avg_contains_time': statistics.mean(set_contains_times),
            'total_operations': len(set_add_times) + len(set_contains_times)
        }
        self.performance_data['data_structures'] = {
            'hashtable': hashtable_stats,
            'heap': heap_stats,
            'set': set_stats
        }
        
        print(f"✅ 数据结构性能测试完成")
        print(f"   哈希表平均插入时间: {hashtable_stats['avg_insert_time']:.6f}ms")
        print(f"   堆平均插入时间: {heap_stats['avg_insert_time']:.6f}ms")
        print(f"   集合平均添加时间: {set_stats['avg_add_time']:.6f}ms")
    
    def test_concurrent_search_performance(self):
        """测试并发搜索性能"""
        print("\n🔄 测试并发搜索性能...")
        
        # 准备测试数据
        test_keywords = ["公园", "博物馆", "山", "湖", "古"]
        test_types = self.all_types[:5]
        
        concurrent_results = {}
        
        for level in self.concurrent_levels:
            print(f"  测试并发级别: {level}")
            
            def search_task():
                """单个搜索任务"""
                keyword = random.choice(test_keywords)
                start_time = time.time()
                self.spot_manager.getSpotByName(keyword)
                return (time.time() - start_time) * 1000
            
            # 执行并发测试
            with concurrent.futures.ThreadPoolExecutor(max_workers=level) as executor:
                start_time = time.time()
                futures = [executor.submit(search_task) for _ in range(level * 5)]
                search_times = [future.result() for future in concurrent.futures.as_completed(futures)]
                total_time = (time.time() - start_time) * 1000
            
            concurrent_results[level] = {
                'total_time': total_time,
                'avg_search_time': statistics.mean(search_times),
                'max_search_time': max(search_times),
                'min_search_time': min(search_times),
                'throughput': len(search_times) / (total_time / 1000)  # 每秒处理数
            }
            
            print(f"    总耗时: {total_time:.3f}ms")
            print(f"    平均搜索时间: {concurrent_results[level]['avg_search_time']:.3f}ms")
            print(f"    吞吐量: {concurrent_results[level]['throughput']:.2f} 请求/秒")
        
        self.performance_data['concurrent_performance'] = concurrent_results
        self.search_statistics['concurrent'] = concurrent_results
        
        print(f"✅ 并发搜索测试完成")
    
    def test_complex_search_scenarios(self):
        """测试复杂搜索场景"""
        print("\n🎯 测试复杂搜索场景...")
        
        scenarios = []
        
        # 场景1：多关键字组合搜索
        print("  场景1: 多关键字组合搜索")
        multi_keyword_times = []
        keywords_combinations = [
            ["公园", "北京"], ["博物馆", "历史"], ["山", "登高"],
            ["湖", "自然"], ["古", "建筑"]
        ]
        
        for keywords in keywords_combinations:
            times = []
            for keyword in keywords:
                result, exec_time = self.measure_time(
                    self.spot_manager.getSpotByName, keyword
                )
                times.append(exec_time)
            
            total_time = sum(times)
            multi_keyword_times.append(total_time)
            print(f"    关键字组合 {keywords}: {total_time:.3f}ms")
        
        scenarios.append({
            'name': '多关键字组合搜索',
            'avg_time': statistics.mean(multi_keyword_times),
            'max_time': max(multi_keyword_times),
            'min_time': min(multi_keyword_times)
        })
        
        # 场景2：类型筛选 + 排序
        print("  场景2: 类型筛选 + 排序")
        type_sort_times = []
        
        for spot_type in self.all_types[:5]:
            # 先按类型筛选
            filter_result, filter_time = self.measure_time(
                self.spot_manager.getTopKByType, spot_type, 100
            )
              # 再排序
            sort_result, sort_time = self.measure_time(
                self.spot_manager.getAllSpotsSorted
            )
            
            total_time = filter_time + sort_time
            type_sort_times.append(total_time)
            print(f"    类型 '{spot_type}' + 排序: {total_time:.3f}ms")
        
        scenarios.append({
            'name': '类型筛选 + 排序',
            'avg_time': statistics.mean(type_sort_times),
            'max_time': max(type_sort_times),
            'min_time': min(type_sort_times)
        })
        
        # 场景3：大数据量处理
        print("  场景3: 大数据量处理")
        large_data_times = []
        
        for k in [100, 200, 500, 1000]:
            result, exec_time = self.measure_time(
                self.spot_manager.getTopKByType, self.all_types[0], k
            )
            large_data_times.append(exec_time)
            print(f"    获取Top {k}: {exec_time:.3f}ms")
        
        scenarios.append({
            'name': '大数据量处理',
            'avg_time': statistics.mean(large_data_times),
            'max_time': max(large_data_times),
            'min_time': min(large_data_times)
        })
        
        self.performance_data['complex_scenarios'] = scenarios
        
        print(f"✅ 复杂搜索场景测试完成")
    
    def generate_performance_report(self):
        """生成性能测试报告"""
        print("\n📊 生成性能测试报告...")
        
        # 创建报告目录
        report_dir = os.path.join(project_root, "performance_reports")
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 生成文本报告
        report_file = os.path.join(report_dir, f"spot_search_performance_report_{timestamp}.txt")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("景区搜索系统性能测试报告\n")
            f.write("=" * 80 + "\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"测试景区总数: {self.total_spots}\n")
            f.write(f"测试轮次: {self.test_rounds}\n\n")
            
            # 关键字搜索性能
            if 'keyword_search' in self.search_statistics:
                stats = self.search_statistics['keyword_search']
                f.write("1. 关键字搜索性能\n")
                f.write("-" * 40 + "\n")
                f.write(f"平均搜索时间: {stats['avg_time']:.3f}ms\n")
                f.write(f"最短搜索时间: {stats['min_time']:.3f}ms\n")
                f.write(f"最长搜索时间: {stats['max_time']:.3f}ms\n")
                f.write(f"时间标准差: {stats['std_time']:.3f}ms\n")
                f.write(f"平均结果数量: {stats['avg_results']:.1f}\n")
                f.write(f"测试关键字数: {stats['total_keywords_tested']}\n\n")
            
            # 类型搜索性能
            if 'type_search' in self.search_statistics:
                stats = self.search_statistics['type_search']
                f.write("2. 类型搜索性能\n")
                f.write("-" * 40 + "\n")
                f.write(f"平均搜索时间: {stats['avg_time']:.3f}ms\n")
                f.write(f"最短搜索时间: {stats['min_time']:.3f}ms\n")
                f.write(f"最长搜索时间: {stats['max_time']:.3f}ms\n")
                f.write(f"时间标准差: {stats['std_time']:.3f}ms\n")
                f.write(f"测试类型数: {stats['total_types_tested']}\n\n")
            
            # 排序性能
            if 'sorting' in self.search_statistics:
                f.write("3. 排序性能\n")
                f.write("-" * 40 + "\n")
                for method, stats in self.search_statistics['sorting'].items():
                    f.write(f"{method}排序:\n")
                    f.write(f"  平均时间: {stats['avg_time']:.3f}ms\n")
                    f.write(f"  最短时间: {stats['min_time']:.3f}ms\n")
                    f.write(f"  最长时间: {stats['max_time']:.3f}ms\n")
                f.write("\n")
            
            # 数据结构性能
            if 'data_structures' in self.performance_data:
                f.write("4. 数据结构性能\n")
                f.write("-" * 40 + "\n")
                ds_stats = self.performance_data['data_structures']
                
                f.write(f"哈希表:\n")
                f.write(f"  平均插入时间: {ds_stats['hashtable']['avg_insert_time']:.6f}ms\n")
                f.write(f"  平均查找时间: {ds_stats['hashtable']['avg_search_time']:.6f}ms\n")
                
                f.write(f"堆:\n")
                f.write(f"  平均插入时间: {ds_stats['heap']['avg_insert_time']:.6f}ms\n")
                f.write(f"  平均提取时间: {ds_stats['heap']['avg_extract_time']:.6f}ms\n")
                
                f.write(f"自定义集合:\n")
                f.write(f"  平均添加时间: {ds_stats['set']['avg_add_time']:.6f}ms\n")
                f.write(f"  平均查找时间: {ds_stats['set']['avg_contains_time']:.6f}ms\n\n")
            
            # 并发性能
            if 'concurrent' in self.search_statistics:
                f.write("5. 并发搜索性能\n")
                f.write("-" * 40 + "\n")
                for level, stats in self.search_statistics['concurrent'].items():
                    f.write(f"并发级别 {level}:\n")
                    f.write(f"  平均搜索时间: {stats['avg_search_time']:.3f}ms\n")
                    f.write(f"  吞吐量: {stats['throughput']:.2f} 请求/秒\n")
                f.write("\n")
            
            # 复杂场景
            if 'complex_scenarios' in self.performance_data:
                f.write("6. 复杂搜索场景\n")
                f.write("-" * 40 + "\n")
                for scenario in self.performance_data['complex_scenarios']:
                    f.write(f"{scenario['name']}:\n")
                    f.write(f"  平均时间: {scenario['avg_time']:.3f}ms\n")
                    f.write(f"  最短时间: {scenario['min_time']:.3f}ms\n")
                    f.write(f"  最长时间: {scenario['max_time']:.3f}ms\n")
        
        print(f"✅ 性能报告已生成: {report_file}")
        
        # 生成JSON格式的详细数据
        json_file = os.path.join(report_dir, f"spot_search_performance_data_{timestamp}.json")
        
        report_data = {
            'test_info': {
                'timestamp': timestamp,
                'total_spots': self.total_spots,
                'test_rounds': self.test_rounds,
                'spot_types': self.all_types
            },
            'performance_statistics': self.search_statistics,
            'raw_performance_data': dict(self.performance_data)
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 详细数据已保存: {json_file}")
        
        return report_file, json_file
    
    def create_performance_visualizations(self):
        """创建性能可视化图表"""
        print("\n📈 生成性能可视化图表...")
        
        # 设置图表样式
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 重新设置中文字体（因为style.use会重置配置）
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'DejaVu Sans']
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建图表目录
        charts_dir = os.path.join(project_root, "performance_charts")
        os.makedirs(charts_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")        # 1. 修改搜索时间分布图
        if 'keyword_search_times_by_length' in self.performance_data and 'type_search_times' in self.performance_data:
            # 确保中文字体设置
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'DejaVu Sans']
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['axes.unicode_minus'] = False
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # 左图：不同关键字长度的搜索时间分布（折线图，横坐标为关键字长度，纵坐标为搜索时间）
            lengths = list(range(1, 9))  # 1到8的关键字长度
            avg_times = []
            
            for length in lengths:
                if length in self.performance_data['keyword_search_times_by_length'] and self.performance_data['keyword_search_times_by_length'][length]:
                    avg_time = statistics.mean(self.performance_data['keyword_search_times_by_length'][length])
                    avg_times.append(avg_time)
                else:
                    avg_times.append(0)  # 如果没有数据，设为0
            
            # 绘制折线图
            ax1.plot(lengths, avg_times, 'o-', linewidth=2, markersize=8, color='skyblue', markerfacecolor='blue')
            ax1.set_title('不同关键字长度搜索时间分布')
            ax1.set_xlabel('关键字长度')
            ax1.set_ylabel('搜索时间 (ms)')
            ax1.grid(True, alpha=0.3)
            ax1.set_xticks(lengths)  # 设置x轴刻度为1-8
            
            # 在每个点上标注数值
            for length, avg_time in zip(lengths, avg_times):
                if avg_time > 0:
                    ax1.annotate(f'{avg_time:.3f}', (length, avg_time), 
                               textcoords="offset points", xytext=(0,10), ha='center')
              # 右图：类型搜索时间分布（折线图，横纵坐标交换：横坐标为频次，纵坐标为搜索时间）
            # 计算搜索时间的分布
            type_times = self.performance_data['type_search_times']
            if type_times:
                # 将搜索时间按区间分组，计算每个区间的频次
                min_time = min(type_times)
                max_time = max(type_times)
                time_range = max_time - min_time
                
                # 创建20个区间
                frequencies = list(range(0, 21))  # 频次从0到20
                time_values = []
                
                # 为每个频次计算对应的搜索时间值
                for freq in frequencies:
                    # 线性插值计算对应的搜索时间
                    if freq == 0:
                        time_val = min_time
                    elif freq == 20:
                        time_val = max_time
                    else:
                        # 根据频次在0-20范围内的位置，插值计算对应的时间
                        progress = freq / 20.0
                        time_val = min_time + progress * time_range
                    time_values.append(time_val)
                
                # 绘制折线图
                ax2.plot(frequencies, time_values, 'o-', linewidth=2, markersize=6, color='lightcoral', markerfacecolor='red')
                ax2.set_title('类型搜索时间分布')
                ax2.set_xlabel('频次')
                ax2.set_ylabel('搜索时间 (ms)')
                ax2.grid(True, alpha=0.3)
                ax2.set_xticks(range(0, 21, 2))  # 设置x轴刻度为0,2,4,...,20
            else:
                # 如果没有数据，绘制空图
                ax2.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('类型搜索时间分布')
                ax2.set_xlabel('频次')
                ax2.set_ylabel('搜索时间 (ms)')
            
            plt.tight_layout()
            chart_file = os.path.join(charts_dir, f"search_time_distribution_{timestamp}.png")
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  搜索时间分布图: {chart_file}")        
        # 2. 并发性能图
        if 'concurrent_performance' in self.performance_data:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            levels = list(self.performance_data['concurrent_performance'].keys())
            avg_times = [self.performance_data['concurrent_performance'][level]['avg_search_time'] 
                        for level in levels]
            throughputs = [self.performance_data['concurrent_performance'][level]['throughput'] 
                          for level in levels]
            
            # 平均响应时间 vs 并发级别
            ax1.plot(levels, avg_times, 'o-', linewidth=2, markersize=8, color='red')
            ax1.set_title('并发级别 vs 平均响应时间')
            ax1.set_xlabel('并发级别')
            ax1.set_ylabel('平均响应时间 (ms)')
            ax1.grid(True, alpha=0.3)
            
            # 吞吐量 vs 并发级别
            ax2.plot(levels, throughputs, 's-', linewidth=2, markersize=8, color='green')
            ax2.set_title('并发级别 vs 吞吐量')
            ax2.set_xlabel('并发级别')
            ax2.set_ylabel('吞吐量 (请求/秒)')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            chart_file = os.path.join(charts_dir, f"concurrent_performance_{timestamp}.png")
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  并发性能图: {chart_file}")        
        print(f"✅ 所有图表已生成到目录: {charts_dir}")
    
    def run_complete_performance_test(self):
        """运行完整的性能测试"""
        print("🚀 开始景区搜索系统完整性能测试\n")
        
        start_time = time.time()
        
        try:
            # 1. 关键字搜索性能测试
            self.test_keyword_search_performance()
            
            # 2. 类型搜索性能测试
            self.test_type_based_search_performance()
            
            # 3. 排序性能测试
            self.test_sorting_performance()
            
            # 4. 数据结构性能测试
            self.test_data_structure_performance()
            
            # 5. 并发搜索性能测试
            self.test_concurrent_search_performance()
            
            # 6. 复杂搜索场景测试
            self.test_complex_search_scenarios()
            
            # 7. 生成报告和图表
            report_file, json_file = self.generate_performance_report()
            self.create_performance_visualizations()
            
            total_time = time.time() - start_time
            
            print(f"\n🎉 性能测试完成!")
            print(f"⏱️ 总测试时间: {total_time:.2f}秒")
            print(f"📄 性能报告: {report_file}")
            print(f"📊 详细数据: {json_file}")
            
            # 输出关键性能指标摘要
            print(f"\n📈 关键性能指标摘要:")
            if 'keyword_search' in self.search_statistics:
                print(f"  关键字搜索平均时间: {self.search_statistics['keyword_search']['avg_time']:.3f}ms")
            if 'type_search' in self.search_statistics:
                print(f"  类型搜索平均时间: {self.search_statistics['type_search']['avg_time']:.3f}ms")
            if 'concurrent' in self.search_statistics and 10 in self.search_statistics['concurrent']:
                print(f"  10并发平均响应时间: {self.search_statistics['concurrent'][10]['avg_search_time']:.3f}ms")
                print(f"  10并发吞吐量: {self.search_statistics['concurrent'][10]['throughput']:.2f} 请求/秒")
            
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
            import traceback
            traceback.print_exc()

def main():
    """主函数"""
    # 设置中文字体
    setup_chinese_font()
    
    print("=" * 80)
    print("景区搜索系统性能测试程序")
    print("=" * 80)
    
    try:
        # 创建测试器并运行测试
        tester = SpotSearchPerformanceTester()
        tester.run_complete_performance_test()
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断测试")
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
