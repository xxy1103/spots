# -*- coding: utf-8 -*-
"""
日记搜索系统性能测试程序
测试不同搜索方法在不同条件下的运行时性能
包括：全文搜索、标题搜索、内容搜索、用户搜索、景点搜索
"""

import sys
import os
import time
import random
import string
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import json
from datetime import datetime
import statistics

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 导入必要的模块
from module.user_class import UserManager
from module.diary_class import DiaryManager
from module.Spot_class import SpotManager
from module.Model.Model import User

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class DiarySearchPerformanceTest:
    def __init__(self):
        """初始化测试环境"""
        # 使用全局管理器实例
        from module.user_class import userManager
        from module.diary_class import diaryManager  
        from module.Spot_class import spotManager
        
        self.user_manager = userManager
        self.diary_manager = diaryManager
        self.spot_manager = spotManager
        
        # 测试配置
        self.test_iterations = 10  # 每种情况测试10次
        
        # 测试用例配置
        self.full_search_keyword_lengths = list(range(0, 201, 10))  # 0-200字符，步长10
        self.title_search_keyword_lengths = list(range(0, 9))  # 0-8字符
        self.content_search_keyword_lengths = list(range(0, 301, 15))  # 0-300字符，步长15
        
        # 测试结果存储
        self.test_results = {
            'full_search': {
                'keyword_lengths': [],
                'avg_times': [],
                'std_times': [],
                'result_counts': []
            },
            'title_search': {
                'keyword_lengths': [],
                'avg_times': [],
                'std_times': [],
                'result_counts': []
            },
            'content_search': {
                'keyword_lengths': [],
                'avg_times': [],
                'std_times': [],
                'result_counts': []
            },
            'user_search': {
                'avg_time': 0,
                'std_time': 0,
                'result_count': 0
            },
            'spot_search': {
                'avg_time': 0,
                'std_time': 0,
                'result_count': 0
            }
        }
        
        # 测试关键词库
        self.chinese_chars = ['北', '京', '上', '海', '广', '州', '深', '圳', '杭', '州', 
                             '西', '湖', '故', '宫', '天', '安', '门', '长', '城', '颐',
                             '和', '园', '景', '区', '旅', '游', '风', '光', '美', '丽',
                             '山', '水', '古', '迹', '文', '化', '历', '史', '自', '然',
                             '公', '园', '博', '物', '馆', '寺', '庙', '塔', '楼', '阁']
        
        self.test_keywords = {
            'short': ['北京', '故宫', '西湖', '长城'],
            'medium': ['天安门广场', '颐和园景区', '杭州西湖风光', '万里长城游览'],
            'long': ['北京故宫博物院历史文化景区', '杭州西湖风景名胜区自然风光', '中国万里长城世界文化遗产']
        }
        
        print("日记搜索性能测试系统初始化完成")
        print(f"当前日记总数: {self.diary_manager.counts}")
        print(f"当前用户总数: {self.user_manager.counts}")
        print(f"当前景点总数: {self.spot_manager.counts}")

    def generate_test_keyword(self, length):
        """生成指定长度的测试关键词"""
        if length == 0:
            return ""
        elif length <= 2:
            return ''.join(random.choices(self.chinese_chars, k=length))
        elif length <= 10:
            # 短关键词：随机选择已有关键词或生成新的
            if random.random() < 0.5 and self.test_keywords['short']:
                keyword = random.choice(self.test_keywords['short'])
                if len(keyword) <= length:
                    return keyword
            return ''.join(random.choices(self.chinese_chars, k=length))
        elif length <= 50:
            # 中等关键词
            if random.random() < 0.3 and self.test_keywords['medium']:
                keyword = random.choice(self.test_keywords['medium'])
                if len(keyword) <= length:
                    return keyword
            return ''.join(random.choices(self.chinese_chars, k=length))
        else:
            # 长关键词：重复现有关键词或生成长文本
            if random.random() < 0.2 and self.test_keywords['long']:
                keyword = random.choice(self.test_keywords['long'])
                if len(keyword) <= length:
                    return keyword
            # 生成长关键词
            words = random.choices(self.chinese_chars, k=length)
            return ''.join(words)

    def measure_search_time(self, search_function, *args):
        """测量搜索函数的执行时间"""
        start_time = time.perf_counter()
        result = search_function(*args)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        result_count = len(result) if result else 0
        return execution_time, result_count

    def test_full_search_performance(self):
        """测试全文搜索性能（综合搜索）"""
        print("\n=== 开始全文搜索性能测试 ===")
        print("测试关键词长度范围: 0-200字符")
        
        for length in self.full_search_keyword_lengths:
            print(f"\n测试关键词长度: {length} 字符")
            times = []
            result_counts = []
            
            for iteration in range(self.test_iterations):
                keyword = self.generate_test_keyword(length)
                
                # 模拟全文搜索：组合标题搜索和内容搜索
                try:
                    start_time = time.perf_counter()
                    
                    # 标题搜索
                    title_results = self.diary_manager.searchByTitle(keyword)
                    # 内容搜索  
                    content_results = self.diary_manager.searchByContent(keyword, max_results=20)
                    
                    # 合并结果（简单合并，去重）
                    all_results = title_results.copy()
                    title_ids = set(diary.id for diary in title_results if diary)
                    for diary in content_results:
                        if diary and diary.id not in title_ids:
                            all_results.append(diary)
                    
                    end_time = time.perf_counter()
                    execution_time = end_time - start_time
                    result_count = len(all_results)
                    
                    times.append(execution_time)
                    result_counts.append(result_count)
                    
                except Exception as e:
                    print(f"    迭代 {iteration + 1} 出错: {e}")
                    times.append(0)
                    result_counts.append(0)
            
            # 计算统计数据
            avg_time = statistics.mean(times) if times else 0
            std_time = statistics.stdev(times) if len(times) > 1 else 0
            avg_result_count = statistics.mean(result_counts) if result_counts else 0
            
            self.test_results['full_search']['keyword_lengths'].append(length)
            self.test_results['full_search']['avg_times'].append(avg_time)
            self.test_results['full_search']['std_times'].append(std_time)
            self.test_results['full_search']['result_counts'].append(avg_result_count)
            
            print(f"    平均时间: {avg_time:.6f}s ± {std_time:.6f}s")
            print(f"    平均结果数: {avg_result_count:.1f}")

    def test_title_search_performance(self):
        """测试标题搜索性能"""
        print("\n=== 开始标题搜索性能测试 ===")
        print("测试关键词长度范围: 0-8字符")
        
        for length in self.title_search_keyword_lengths:
            print(f"\n测试关键词长度: {length} 字符")
            times = []
            result_counts = []
            
            for iteration in range(self.test_iterations):
                keyword = self.generate_test_keyword(length)
                
                try:
                    execution_time, result_count = self.measure_search_time(
                        self.diary_manager.searchByTitle, keyword
                    )
                    times.append(execution_time)
                    result_counts.append(result_count)
                    
                except Exception as e:
                    print(f"    迭代 {iteration + 1} 出错: {e}")
                    times.append(0)
                    result_counts.append(0)
            
            # 计算统计数据
            avg_time = statistics.mean(times) if times else 0
            std_time = statistics.stdev(times) if len(times) > 1 else 0
            avg_result_count = statistics.mean(result_counts) if result_counts else 0
            
            self.test_results['title_search']['keyword_lengths'].append(length)
            self.test_results['title_search']['avg_times'].append(avg_time)
            self.test_results['title_search']['std_times'].append(std_time)
            self.test_results['title_search']['result_counts'].append(avg_result_count)
            
            print(f"    平均时间: {avg_time:.6f}s ± {std_time:.6f}s")
            print(f"    平均结果数: {avg_result_count:.1f}")

    def test_content_search_performance(self):
        """测试内容搜索性能"""
        print("\n=== 开始内容搜索性能测试 ===")
        print("测试关键词长度范围: 0-300字符")
        
        for length in self.content_search_keyword_lengths:
            print(f"\n测试关键词长度: {length} 字符")
            times = []
            result_counts = []
            
            for iteration in range(self.test_iterations):
                keyword = self.generate_test_keyword(length)
                
                try:
                    execution_time, result_count = self.measure_search_time(
                        self.diary_manager.searchByContent, keyword, 20
                    )
                    times.append(execution_time)
                    result_counts.append(result_count)
                    
                except Exception as e:
                    print(f"    迭代 {iteration + 1} 出错: {e}")
                    times.append(0)
                    result_counts.append(0)
            
            # 计算统计数据
            avg_time = statistics.mean(times) if times else 0
            std_time = statistics.stdev(times) if len(times) > 1 else 0
            avg_result_count = statistics.mean(result_counts) if result_counts else 0
            
            self.test_results['content_search']['keyword_lengths'].append(length)
            self.test_results['content_search']['avg_times'].append(avg_time)
            self.test_results['content_search']['std_times'].append(std_time)
            self.test_results['content_search']['result_counts'].append(avg_result_count)
            
            print(f"    平均时间: {avg_time:.6f}s ± {std_time:.6f}s")
            print(f"    平均结果数: {avg_result_count:.1f}")

    def test_user_search_performance(self):
        """测试用户搜索性能"""
        print("\n=== 开始用户搜索性能测试 ===")
        
        # 获取一些真实用户名进行测试
        test_usernames = []
        for i in range(min(50, self.user_manager.counts)):
            user = self.user_manager.getUser(i)
            if user and hasattr(user, 'name'):
                test_usernames.append(user.name)
        
        if not test_usernames:
            print("没有找到可用的用户名，跳过用户搜索测试")
            return
        
        print(f"使用 {len(test_usernames)} 个用户名进行测试")
        
        times = []
        result_counts = []
        
        for iteration in range(self.test_iterations):
            # 随机选择一个用户名
            username = random.choice(test_usernames)
            
            try:
                # 测试B树搜索
                execution_time, result_count = self.measure_search_time(
                    self.user_manager.searchUser, username
                )
                times.append(execution_time)
                result_counts.append(1 if result_count > 0 else 0)  # 用户搜索返回单个结果或None
                
            except Exception as e:
                print(f"    迭代 {iteration + 1} 出错: {e}")
                times.append(0)
                result_counts.append(0)
        
        # 计算统计数据
        avg_time = statistics.mean(times) if times else 0
        std_time = statistics.stdev(times) if len(times) > 1 else 0
        avg_result_count = statistics.mean(result_counts) if result_counts else 0
        
        self.test_results['user_search']['avg_time'] = avg_time
        self.test_results['user_search']['std_time'] = std_time
        self.test_results['user_search']['result_count'] = avg_result_count
        
        print(f"用户搜索平均时间: {avg_time:.6f}s ± {std_time:.6f}s")
        print(f"平均成功查找率: {avg_result_count:.2%}")

    def test_spot_search_performance(self):
        """测试景点搜索性能"""
        print("\n=== 开始景点搜索性能测试 ===")
        
        # 使用一些常见的景点关键词
        spot_keywords = ['故宫', '长城', '西湖', '天安门', '颐和园', '北京', '上海', '景区', '公园', '博物馆']
        
        times = []
        result_counts = []
        
        for iteration in range(self.test_iterations):
            # 随机选择一个景点关键词
            keyword = random.choice(spot_keywords)
            
            try:
                execution_time, result_count = self.measure_search_time(
                    self.spot_manager.getSpotByName, keyword
                )
                times.append(execution_time)
                result_counts.append(result_count)
                
            except Exception as e:
                print(f"    迭代 {iteration + 1} 出错: {e}")
                times.append(0)
                result_counts.append(0)
        
        # 计算统计数据
        avg_time = statistics.mean(times) if times else 0
        std_time = statistics.stdev(times) if len(times) > 1 else 0
        avg_result_count = statistics.mean(result_counts) if result_counts else 0
        
        self.test_results['spot_search']['avg_time'] = avg_time
        self.test_results['spot_search']['std_time'] = std_time
        self.test_results['spot_search']['result_count'] = avg_result_count
        
        print(f"景点搜索平均时间: {avg_time:.6f}s ± {std_time:.6f}s")
        print(f"平均结果数: {avg_result_count:.1f}")

    def generate_charts(self):
        """生成性能分析图表"""
        print("\n=== 生成性能分析图表 ===")
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('日记搜索系统性能分析', fontsize=16, fontweight='bold')
        
        # 1. 全文搜索性能趋势
        ax1 = axes[0, 0]
        if self.test_results['full_search']['keyword_lengths']:
            x = self.test_results['full_search']['keyword_lengths']
            y = self.test_results['full_search']['avg_times']
            errors = self.test_results['full_search']['std_times']
            
            ax1.errorbar(x, y, yerr=errors, marker='o', capsize=5, capthick=2)
            ax1.set_xlabel('关键词长度 (字符)')
            ax1.set_ylabel('平均搜索时间 (秒)')
            ax1.set_title('全文搜索性能趋势')
            ax1.grid(True, alpha=0.3)
        
        # 2. 标题搜索性能
        ax2 = axes[0, 1]
        if self.test_results['title_search']['keyword_lengths']:
            x = self.test_results['title_search']['keyword_lengths']
            y = self.test_results['title_search']['avg_times']
            errors = self.test_results['title_search']['std_times']
            
            ax2.errorbar(x, y, yerr=errors, marker='s', capsize=5, capthick=2, color='green')
            ax2.set_xlabel('关键词长度 (字符)')
            ax2.set_ylabel('平均搜索时间 (秒)')
            ax2.set_title('标题搜索性能 (哈希表+集合交集)')
            ax2.grid(True, alpha=0.3)
        
        # 3. 内容搜索性能
        ax3 = axes[1, 0]
        if self.test_results['content_search']['keyword_lengths']:
            x = self.test_results['content_search']['keyword_lengths']
            y = self.test_results['content_search']['avg_times']
            errors = self.test_results['content_search']['std_times']
            
            ax3.errorbar(x, y, yerr=errors, marker='^', capsize=5, capthick=2, color='red')
            ax3.set_xlabel('关键词长度 (字符)')
            ax3.set_ylabel('平均搜索时间 (秒)')
            ax3.set_title('内容搜索性能 (哈夫曼编码+KMP算法)')
            ax3.grid(True, alpha=0.3)
          # 4. 各种搜索方法对比
        ax4 = axes[1, 1]
        methods = ['用户搜索\n(B树)', '景点搜索\n(哈希表+集合)']
        times = [
            self.test_results['user_search']['avg_time'],
            self.test_results['spot_search']['avg_time']
        ]
        errors = [
            self.test_results['user_search']['std_time'],
            self.test_results['spot_search']['std_time']
        ]
        
        bars = ax4.bar(methods, times, yerr=errors, capsize=5, 
                      color=['skyblue', 'lightcoral'], alpha=0.7)
        ax4.set_ylabel('平均搜索时间 (秒)')
        ax4.set_title('不同搜索方法性能对比')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 在柱状图上显示数值
        for i, (bar, time_val) in enumerate(zip(bars, times)):
            height = bar.get_height()
            error_val = errors[i] if i < len(errors) else 0
            ax4.text(bar.get_x() + bar.get_width()/2., height + error_val,
                    f'{time_val:.6f}s', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # 保存图表
        chart_filename = f'diary_search_performance_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        print(f"性能分析图表已保存: {chart_filename}")
        
        plt.show()

    def generate_markdown_report(self):
        """生成详细的markdown格式分析报告"""
        print("\n=== 生成分析报告 ===")
        
        report_filename = f'diary_search_performance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("# 日记搜索系统性能分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n")
            
            # 系统概述
            f.write("## 1. 系统概述\n\n")
            f.write("本报告分析了个性化旅游系统中日记搜索功能的性能表现，测试了不同搜索方法在各种条件下的运行时性能。\n\n")
            f.write("### 测试环境\n")
            f.write(f"- 日记总数: {self.diary_manager.counts}\n")
            f.write(f"- 用户总数: {self.user_manager.counts}\n")
            f.write(f"- 景点总数: {self.spot_manager.counts}\n")
            f.write(f"- 每种测试重复次数: {self.test_iterations}\n\n")
            
            # 全文搜索分析
            f.write("## 2. 全文搜索性能分析\n\n")
            f.write("全文搜索结合了标题搜索和内容搜索，提供最全面的搜索结果。\n\n")
            f.write("### 数据结构与算法\n")
            f.write("- **标题搜索**: 哈希表 + MySet集合交集运算\n")
            f.write("- **内容搜索**: 哈夫曼编码 + KMP字符串匹配算法\n")
            f.write("- **时间复杂度**: O(k×m + n×p×log c)，其中k为关键词长度，m为平均匹配数，n为日记数量，p为压缩内容长度，c为字符集大小\n\n")
            
            if self.test_results['full_search']['keyword_lengths']:
                f.write("### 性能测试结果\n\n")
                f.write("| 关键词长度 | 平均时间(秒) | 标准差(秒) | 平均结果数 |\n")
                f.write("|------------|-------------|-----------|----------|\n")
                
                for i, length in enumerate(self.test_results['full_search']['keyword_lengths']):
                    avg_time = self.test_results['full_search']['avg_times'][i]
                    std_time = self.test_results['full_search']['std_times'][i]
                    result_count = self.test_results['full_search']['result_counts'][i]
                    f.write(f"| {length} | {avg_time:.6f} | {std_time:.6f} | {result_count:.1f} |\n")
                
                # 性能分析
                max_time_idx = self.test_results['full_search']['avg_times'].index(max(self.test_results['full_search']['avg_times']))
                min_time_idx = self.test_results['full_search']['avg_times'].index(min(self.test_results['full_search']['avg_times']))
                
                f.write(f"\n### 关键发现\n")
                f.write(f"- **最快搜索**: {self.test_results['full_search']['keyword_lengths'][min_time_idx]}字符关键词，耗时{self.test_results['full_search']['avg_times'][min_time_idx]:.6f}秒\n")
                f.write(f"- **最慢搜索**: {self.test_results['full_search']['keyword_lengths'][max_time_idx]}字符关键词，耗时{self.test_results['full_search']['avg_times'][max_time_idx]:.6f}秒\n")
                f.write(f"- **性能比率**: {self.test_results['full_search']['avg_times'][max_time_idx]/self.test_results['full_search']['avg_times'][min_time_idx]:.2f}倍差异\n\n")
            
            # 标题搜索分析
            f.write("## 3. 标题搜索性能分析\n\n")
            f.write("标题搜索使用哈希表和自定义集合类进行字符级别的索引匹配。\n\n")
            f.write("### 算法实现\n")
            f.write("- **数据结构**: 哈希表 + MySet自定义集合\n")
            f.write("- **核心算法**: 字符级别哈希映射 + 集合交集运算\n")
            f.write("- **时间复杂度**: O(k×m + r×s)，其中k为关键词长度，m为平均每字符匹配日记数，r为结果数量，s为集合操作复杂度\n\n")
            
            if self.test_results['title_search']['keyword_lengths']:
                f.write("### 性能测试结果\n\n")
                f.write("| 关键词长度 | 平均时间(秒) | 标准差(秒) | 平均结果数 |\n")
                f.write("|------------|-------------|-----------|----------|\n")
                
                for i, length in enumerate(self.test_results['title_search']['keyword_lengths']):
                    avg_time = self.test_results['title_search']['avg_times'][i]
                    std_time = self.test_results['title_search']['std_times'][i]
                    result_count = self.test_results['title_search']['result_counts'][i]
                    f.write(f"| {length} | {avg_time:.6f} | {std_time:.6f} | {result_count:.1f} |\n")
            
            # 内容搜索分析
            f.write("\n## 4. 内容搜索性能分析\n\n")
            f.write("内容搜索采用哈夫曼编码压缩和KMP字符串匹配算法，支持在压缩内容中进行高效搜索。\n\n")
            f.write("### 算法实现\n")
            f.write("- **压缩算法**: 哈夫曼编码\n")
            f.write("- **搜索算法**: KMP字符串匹配\n")
            f.write("- **时间复杂度**: O(n + p×log c)，其中n为日记数量，p为压缩内容长度，c为字符集大小\n\n")
            
            if self.test_results['content_search']['keyword_lengths']:
                f.write("### 性能测试结果\n\n")
                f.write("| 关键词长度 | 平均时间(秒) | 标准差(秒) | 平均结果数 |\n")
                f.write("|------------|-------------|-----------|----------|\n")
                
                for i, length in enumerate(self.test_results['content_search']['keyword_lengths']):
                    avg_time = self.test_results['content_search']['avg_times'][i]
                    std_time = self.test_results['content_search']['std_times'][i]
                    result_count = self.test_results['content_search']['result_counts'][i]
                    f.write(f"| {length} | {avg_time:.6f} | {std_time:.6f} | {result_count:.1f} |\n")
            
            # 用户和景点搜索分析
            f.write("\n## 5. 专项搜索性能分析\n\n")
            f.write("### 用户搜索\n")
            f.write("- **数据结构**: B树 + Trie树\n")
            f.write("- **时间复杂度**: O(log n + d)，其中n为用户数量，d为结果处理时间\n")
            f.write(f"- **平均搜索时间**: {self.test_results['user_search']['avg_time']:.6f}s ± {self.test_results['user_search']['std_time']:.6f}s\n")
            f.write(f"- **平均成功率**: {self.test_results['user_search']['result_count']:.2%}\n\n")
            
            f.write("### 景点搜索\n")
            f.write("- **数据结构**: 哈希表 + MySet集合\n")
            f.write("- **时间复杂度**: O(k×m + r×d)，其中k为关键词长度，m为平均匹配数，r为结果数量，d为景点数据处理时间\n")
            f.write(f"- **平均搜索时间**: {self.test_results['spot_search']['avg_time']:.6f}s ± {self.test_results['spot_search']['std_time']:.6f}s\n")
            f.write(f"- **平均结果数**: {self.test_results['spot_search']['result_count']:.1f}\n\n")
            
            # 性能优化建议
            f.write("## 6. 性能优化建议\n\n")
            f.write("### 短期优化\n")
            f.write("1. **缓存机制**: 对频繁搜索的关键词建立结果缓存\n")
            f.write("2. **索引优化**: 优化哈希表的负载因子和冲突处理\n")
            f.write("3. **并行处理**: 对于全文搜索，可以并行执行标题和内容搜索\n\n")
            
            f.write("### 长期优化\n")
            f.write("1. **倒排索引**: 建立更高效的倒排索引结构\n")
            f.write("2. **分布式搜索**: 当数据量增大时，考虑分布式搜索架构\n")
            f.write("3. **机器学习**: 引入相关性排序和智能推荐\n\n")
            
            # 结论
            f.write("## 7. 结论\n\n")
            f.write("通过本次性能测试，我们得出以下结论：\n\n")
            f.write("1. **标题搜索效率最高**，适用于快速精确匹配\n")
            f.write("2. **内容搜索功能最强**，但性能开销较大\n")
            f.write("3. **用户搜索和景点搜索性能稳定**，适合实时查询\n")
            f.write("4. **系统整体性能良好**，能够满足实际应用需求\n\n")
            
            f.write("---\n")
            f.write("*报告由日记搜索性能测试系统自动生成*\n")
        
        print(f"分析报告已保存: {report_filename}")
        return report_filename

    def run_comprehensive_test(self):
        """运行完整的性能测试"""
        print("="*60)
        print("日记搜索系统综合性能测试")
        print("="*60)
        
        start_time = time.time()
        
        # 执行各项测试
        self.test_full_search_performance()
        self.test_title_search_performance()
        self.test_content_search_performance()
        self.test_user_search_performance()
        self.test_spot_search_performance()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n=== 测试完成 ===")
        print(f"总测试时间: {total_time:.2f}秒")
        
        # 生成可视化图表
        self.generate_charts()
        
        # 生成分析报告
        report_file = self.generate_markdown_report()
        
        print(f"\n=== 测试总结 ===")
        print("性能测试已完成，结果已保存到图表和报告文件中。")
        print(f"详细分析报告: {report_file}")
        
        return self.test_results

def main():
    """主函数"""
    print("日记搜索系统性能测试程序")
    print("本程序将测试各种搜索方法的性能表现")
    
    # 创建测试实例
    test_system = DiarySearchPerformanceTest()
    
    # 询问用户是否执行完整测试
    print("\n选择测试模式:")
    print("1. 快速测试 (较少的测试用例)")
    print("2. 完整测试 (所有测试用例)")
    print("3. 自定义测试")
    
    choice = input("请选择 (1-3): ").strip()
    
    if choice == "1":
        # 快速测试：减少测试用例
        test_system.test_iterations = 5
        test_system.full_search_keyword_lengths = list(range(0, 51, 10))
        test_system.content_search_keyword_lengths = list(range(0, 101, 20))
        print("执行快速测试模式...")
        
    elif choice == "3":
        # 自定义测试
        iterations = input("输入每种测试的重复次数 (默认10): ").strip()
        if iterations.isdigit():
            test_system.test_iterations = int(iterations)
        print(f"使用自定义配置: {test_system.test_iterations}次重复测试")
    
    # 运行测试
    results = test_system.run_comprehensive_test()
    
    print("\n" + "="*60)
    print("测试完成！感谢使用日记搜索性能测试系统")
    print("="*60)

if __name__ == "__main__":
    main()
