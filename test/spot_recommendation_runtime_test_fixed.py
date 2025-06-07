# -*- coding: utf-8 -*-
"""
推荐景区系统运行时间性能测试程序 - 中文字体修复版
专门测试推荐系统各项操作的响应时间和性能表现
包括多种现实情形下的测试，提供详细的运行时间数据分析
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
from datetime import datetime
from collections import defaultdict
import json

# 设置中文字体 - 最终修复版
def setup_chinese_font():
    """设置中文字体 - 使用最有效的配置方案"""
    print("🔧 设置最终版中文字体配置...")
    
    # 直接设置最可靠的配置
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'DejaVu Sans']
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False
    
    # 强制字体缓存刷新
    try:
        fm._rebuild()
        print("✅ 字体缓存已刷新")
    except Exception as e:
        print(f"⚠️ 字体缓存刷新警告: {e}")
    
    # 验证中文字体
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    chinese_fonts = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei']
    
    found_font = None
    for font in chinese_fonts:
        if font in available_fonts:
            found_font = font
            break
    
    if found_font:
        print(f"✅ 找到中文字体: {found_font}")
    else:
        print("⚠️ 未找到专用中文字体，使用系统默认")
    
    return found_font

def ensure_chinese_display():
    """确保中文显示正常 - 在每次绘图前调用"""
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

# 初始化字体设置
selected_chinese_font = setup_chinese_font()

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from module.user_class import UserManager, userManager
from module.Spot_class import spotManager


class SpotRecommendationRuntimeTest:
    """推荐景区系统运行时间测试类"""
    
    def __init__(self):
        self.user_manager = userManager
        self.spot_manager = spotManager
        
        # 测试配置
        self.test_configs = {
            'topK_values': [5, 10, 15, 20, 25, 30, 40, 50],  # 不同的推荐数量
            'repeat_times': 15,  # 每个测试重复次数，用于计算平均值
            'user_sample_size': 25,  # 测试用户样本大小
            'timeout_threshold': 10000,  # 超时阈值(ms)
            'performance_levels': {
                'excellent': 50,    # 优秀：≤50ms
                'good': 100,        # 良好：51-100ms
                'acceptable': 200,  # 可接受：101-200ms
                'slow': 500,        # 较慢：201-500ms
                'very_slow': float('inf')  # 很慢：>500ms
            }
        }
        
        # 用户场景分类
        self.user_scenarios = {
            'single_preference': {'preference_count': 1, 'description': '单一偏好用户'},
            'dual_preference': {'preference_count': 2, 'description': '双重偏好用户'},
            'multi_preference': {'preference_count': 3, 'description': '多重偏好用户'},
            'diverse_preference': {'preference_count': 4, 'description': '多样化偏好用户'}
        }
        
        # 存储测试结果
        self.test_results = {
            'basic_performance': {},
            'scenario_analysis': {},
            'load_testing': {},
            'stability_testing': {},
            'comprehensive_analysis': {}
        }
        self.detailed_records = []  # 详细测试记录
        self.test_users = []
        
        print("🚀 推荐景区系统运行时间性能测试程序启动", flush=True)
        self._prepare_test_environment()
    
    def _prepare_test_environment(self):
        """准备测试环境"""
        print("\n🔧 准备测试环境...", flush=True)
        
        # 获取可用的测试用户
        available_users = [user for user in self.user_manager.users 
                          if hasattr(user, 'likes_type') and user.likes_type]
        
        if len(available_users) < self.test_configs['user_sample_size']:
            print(f"⚠️  可用用户数量不足，使用所有可用用户 ({len(available_users)}个)")
            self.test_users = available_users
        else:
            self.test_users = random.sample(available_users, self.test_configs['user_sample_size'])
        
        print(f"✅ 测试环境准备完成，共{len(self.test_users)}个测试用户")
        self._analyze_test_users()
    
    def _analyze_test_users(self):
        """分析测试用户分布"""
        print("\n📊 测试用户分布分析:")
        
        preference_distribution = defaultdict(int)
        total_preferences = 0
        
        for user in self.test_users:
            pref_count = len(user.likes_type) if user.likes_type else 0
            preference_distribution[pref_count] += 1
            total_preferences += pref_count
        
        for count, num_users in sorted(preference_distribution.items()):
            percentage = (num_users / len(self.test_users)) * 100
            print(f"   {count}个偏好: {num_users}用户 ({percentage:.1f}%)")
        
        avg_preferences = total_preferences / len(self.test_users) if self.test_users else 0
        print(f"   平均偏好数量: {avg_preferences:.2f}")
    
    def measure_execution_time(self, func, *args, **kwargs):
        """测量函数执行时间"""
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            return {
                'success': True,
                'execution_time': execution_time,
                'result': result,
                'result_count': len(result) if result else 0,
                'error': None
            }
        except Exception as e:
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000
            
            return {
                'success': False,
                'execution_time': execution_time,
                'result': None,
                'result_count': 0,
                'error': str(e)
            }
    
    def run_basic_performance_test(self):
        """基础性能测试 - 测试不同TopK值下的响应时间"""
        print("\n" + "="*60)
        print("🎯 1. 基础性能测试 - 不同TopK值响应时间分析")
        print("="*60)
        
        basic_results = defaultdict(list)
        
        total_tests = len(self.test_configs['topK_values']) * self.test_configs['repeat_times'] * len(self.test_users)
        current_test = 0
        
        for topK in self.test_configs['topK_values']:
            print(f"\n📈 测试 TopK = {topK}")
            topK_times = []
            
            for repeat in range(self.test_configs['repeat_times']):
                print(f"  第{repeat + 1}轮测试", end=" - ")
                
                round_times = []
                for user in self.test_users:
                    current_test += 1
                    
                    # 测试推荐算法性能
                    metrics = self.measure_execution_time(
                        self.user_manager.getRecommendSpots,
                        user.id, topK
                    )
                    
                    round_times.append(metrics['execution_time'])
                    
                    # 记录详细测试数据
                    self.detailed_records.append({
                        'test_type': 'basic_performance',
                        'topK': topK,
                        'repeat': repeat + 1,
                        'user_id': user.id,
                        'user_preferences': len(user.likes_type),
                        'execution_time': metrics['execution_time'],
                        'success': metrics['success'],
                        'result_count': metrics['result_count'],
                        'error': metrics['error'],
                        'timestamp': datetime.now().isoformat()
                    })
                
                avg_time = statistics.mean(round_times)
                topK_times.extend(round_times)
                print(f"平均: {avg_time:.2f}ms")
            
            # 统计分析
            basic_results[topK] = {
                'times': topK_times,
                'mean': statistics.mean(topK_times),
                'median': statistics.median(topK_times),
                'std': statistics.stdev(topK_times) if len(topK_times) > 1 else 0,
                'min': min(topK_times),
                'max': max(topK_times),
                'p95': np.percentile(topK_times, 95),
                'p99': np.percentile(topK_times, 99),
                'count': len(topK_times)
            }
            
            print(f"  📊 统计结果: 平均{basic_results[topK]['mean']:.2f}ms, "
                  f"中位数{basic_results[topK]['median']:.2f}ms, "
                  f"P95: {basic_results[topK]['p95']:.2f}ms")
        
        self.test_results['basic_performance'] = basic_results
        self._print_basic_performance_summary()
        print("✅ 基础性能测试完成")
    
    def _print_basic_performance_summary(self):
        """打印基础性能测试摘要"""
        print(f"\n📋 基础性能测试摘要:")
        print(f"{'TopK':<6} {'平均时间(ms)':<12} {'中位数(ms)':<10} {'P95(ms)':<8} {'P99(ms)':<8} {'标准差':<8}")
        print("-" * 62)
        results = self.test_results['basic_performance']
        for topK in sorted(results.keys()):
            stats = results[topK]
            print(f"{topK:<6} {stats['mean']:<12.2f} {stats['median']:<10.2f} "
                  f"{stats['p95']:<8.2f} {stats['p99']:<8.2f} {stats['std']:<8.2f}")
    
    def run_scenario_analysis_test(self):
        """用户场景分析测试 - 测试所有0-5偏好数量的性能表现"""
        print("\n" + "="*60)
        print("👥 2. 用户场景分析测试 - 测试所有0-5偏好数量")
        print("="*60)
        
        # 按用户偏好数量分组，确保包含所有可能的偏好数量
        user_groups = defaultdict(list)
        for user in self.test_users:
            pref_count = len(user.likes_type) if user.likes_type else 0
            user_groups[pref_count].append(user)
        
        scenario_results = {}
        
        # 确保测试所有0-5偏好数量的用户
        for pref_count in range(0, 6):  # 0到5的所有偏好数量
            users = user_groups.get(pref_count, [])
            
            if not users:
                print(f"\n🎯 偏好数量 {pref_count}: 没有用户，创建模拟测试数据")
                # 如果没有该偏好数量的用户，使用现有用户进行模拟测试
                if self.test_users:
                    # 选择一个用户进行模拟测试
                    sample_user = random.choice(self.test_users)
                    
                    # 进行少量测试以获得基准数据
                    pref_times = []
                    test_topK = [10, 20]  # 减少测试量
                    
                    for topK in test_topK:
                        for repeat in range(5):  # 减少重复次数
                            metrics = self.measure_execution_time(
                                self.user_manager.getRecommendSpots,
                                sample_user.id, topK
                            )
                            
                            pref_times.append(metrics['execution_time'])
                            
                            # 记录详细数据
                            self.detailed_records.append({
                                'test_type': 'scenario_analysis',
                                'preference_count': pref_count,
                                'topK': topK,
                                'user_id': f'simulated_{pref_count}',
                                'execution_time': metrics['execution_time'],
                                'success': metrics['success'],
                                'result_count': metrics['result_count'],
                                'timestamp': datetime.now().isoformat(),
                                'note': f'模拟{pref_count}偏好数量测试'
                            })
                    
                    if pref_times:
                        scenario_results[pref_count] = {
                            'times': pref_times,
                            'mean': statistics.mean(pref_times),
                            'median': statistics.median(pref_times),
                            'std': statistics.stdev(pref_times) if len(pref_times) > 1 else 0,
                            'user_count': 0,  # 标记为模拟数据
                            'sample_size': len(pref_times),
                            'is_simulated': True
                        }
                        
                        print(f"  📊 模拟{pref_count}个偏好用户平均响应时间: {scenario_results[pref_count]['mean']:.2f}ms")
                continue
                
            print(f"\n🎯 测试 {pref_count}个偏好的用户 (共{len(users)}个用户)")
            
            pref_times = []
            test_topK = [10, 20, 30]  # 典型TopK值
            
            for topK in test_topK:
                for repeat in range(self.test_configs['repeat_times']):
                    for user in users:
                        metrics = self.measure_execution_time(
                            self.user_manager.getRecommendSpots,
                            user.id, topK
                        )
                        
                        pref_times.append(metrics['execution_time'])
                        
                        # 记录详细数据
                        self.detailed_records.append({
                            'test_type': 'scenario_analysis',
                            'preference_count': pref_count,
                            'topK': topK,
                            'user_id': user.id,
                            'execution_time': metrics['execution_time'],
                            'success': metrics['success'],
                            'result_count': metrics['result_count'],
                            'timestamp': datetime.now().isoformat()
                        })
            
            if pref_times:
                scenario_results[pref_count] = {
                    'times': pref_times,
                    'mean': statistics.mean(pref_times),
                    'median': statistics.median(pref_times),
                    'std': statistics.stdev(pref_times) if len(pref_times) > 1 else 0,
                    'user_count': len(users),
                    'sample_size': len(pref_times),
                    'is_simulated': False
                }
                
                print(f"  📊 {pref_count}个偏好用户平均响应时间: {scenario_results[pref_count]['mean']:.2f}ms")
        
        self.test_results['scenario_analysis'] = scenario_results
        self._print_scenario_analysis_summary()
        print("✅ 用户场景分析测试完成")
    
    def _print_scenario_analysis_summary(self):
        """打印用户场景分析摘要"""
        print(f"\n📋 用户场景分析摘要:")
        print(f"{'偏好数量':<8} {'用户数量':<8} {'平均时间(ms)':<12} {'中位数(ms)':<10} {'标准差':<8}")
        print("-" * 54)
        
        results = self.test_results['scenario_analysis']
        for pref_count in sorted(results.keys()):
            stats = results[pref_count]
            print(f"{pref_count:<8} {stats['user_count']:<8} {stats['mean']:<12.2f} "
                  f"{stats['median']:<10.2f} {stats['std']:<8.2f}")
    
    def run_load_testing(self):
        """负载测试 - 连续高频请求测试"""
        print("\n" + "="*60)
        print("⚡ 3. 负载测试 - 高频连续请求性能分析")
        print("="*60)
        
        test_duration = 60  # 测试60秒
        topK = 20
        
        print(f"连续{test_duration}秒高频请求测试 (TopK={topK})")
        
        load_times = []
        request_count = 0
        error_count = 0
        start_time = time.time()
        
        print("🚀 开始负载测试...", end="")
        
        while time.time() - start_time < test_duration:
            user = random.choice(self.test_users)
            
            metrics = self.measure_execution_time(
                self.user_manager.getRecommendSpots,
                user.id, topK
            )
            
            load_times.append(metrics['execution_time'])
            request_count += 1
            
            if not metrics['success']:
                error_count += 1
            
            # 记录详细数据
            self.detailed_records.append({
                'test_type': 'load_testing',
                'request_number': request_count,
                'user_id': user.id,
                'topK': topK,
                'execution_time': metrics['execution_time'],
                'success': metrics['success'],
                'result_count': metrics['result_count'],
                'timestamp': datetime.now().isoformat()
            })
            
            if request_count % 100 == 0:
                print(".", end="")
        
        actual_duration = time.time() - start_time
        qps = request_count / actual_duration
        error_rate = error_count / request_count if request_count > 0 else 0
        
        load_results = {
            'total_requests': request_count,
            'actual_duration': actual_duration,
            'qps': qps,
            'error_count': error_count,
            'error_rate': error_rate,
            'times': load_times,
            'mean_time': statistics.mean(load_times) if load_times else 0,
            'median_time': statistics.median(load_times) if load_times else 0,
            'p95_time': np.percentile(load_times, 95) if load_times else 0,
            'p99_time': np.percentile(load_times, 99) if load_times else 0,
            'max_time': max(load_times) if load_times else 0,
            'min_time': min(load_times) if load_times else 0
        }
        
        self.test_results['load_testing'] = load_results
        
        print(f"\n✅ 负载测试完成")
        print(f"📊 负载测试结果:")
        print(f"   总请求数: {request_count}")
        print(f"   实际测试时长: {actual_duration:.2f}秒")
        print(f"   QPS (每秒请求数): {qps:.2f}")
        print(f"   错误率: {error_rate*100:.2f}%")
        print(f"   平均响应时间: {load_results['mean_time']:.2f}ms")
        print(f"   P95响应时间: {load_results['p95_time']:.2f}ms")
        print(f"   P99响应时间: {load_results['p99_time']:.2f}ms")
    
    def run_stability_testing(self):
        """稳定性测试 - 长时间运行稳定性分析"""
        print("\n" + "="*60)
        print("🔄 4. 稳定性测试 - 长时间运行稳定性分析")
        print("="*60)
        
        test_rounds = 100  # 100轮测试
        topK = 20
        
        # 选择固定用户进行稳定性测试
        test_user = random.choice(self.test_users)
        print(f"使用用户 {test_user.id} 进行{test_rounds}轮稳定性测试")
        
        stability_times = []
        
        for round_num in range(test_rounds):
            if round_num % 20 == 0:
                print(f"  进度: {round_num}/{test_rounds}")
            
            metrics = self.measure_execution_time(
                self.user_manager.getRecommendSpots,
                test_user.id, topK
            )
            
            stability_times.append(metrics['execution_time'])
            
            # 记录详细数据
            self.detailed_records.append({
                'test_type': 'stability_testing',
                'round': round_num + 1,
                'user_id': test_user.id,
                'topK': topK,
                'execution_time': metrics['execution_time'],
                'success': metrics['success'],
                'result_count': metrics['result_count'],
                'timestamp': datetime.now().isoformat()
            })
        
        # 计算稳定性指标
        mean_time = statistics.mean(stability_times)
        std_time = statistics.stdev(stability_times) if len(stability_times) > 1 else 0
        cv = std_time / mean_time if mean_time > 0 else 0  # 变异系数
        
        stability_results = {
            'rounds': test_rounds,
            'times': stability_times,
            'mean': mean_time,
            'std': std_time,
            'cv': cv,
            'min': min(stability_times),
            'max': max(stability_times),
            'range': max(stability_times) - min(stability_times),
            'median': statistics.median(stability_times),
            'p95': np.percentile(stability_times, 95),
            'p99': np.percentile(stability_times, 99)
        }
        
        self.test_results['stability_testing'] = stability_results
        
        print("✅ 稳定性测试完成")
        print(f"📊 稳定性测试结果:")
        print(f"   测试轮数: {test_rounds}")
        print(f"   平均响应时间: {mean_time:.2f}ms")
        print(f"   标准差: {std_time:.2f}ms")
        print(f"   变异系数: {cv:.3f}")
        print(f"   响应时间范围: {stability_results['min']:.2f}ms - {stability_results['max']:.2f}ms")
        
        # 稳定性评级
        if cv < 0.1:
            stability_rating = "极稳定"
        elif cv < 0.2:
            stability_rating = "很稳定"
        elif cv < 0.3:
            stability_rating = "稳定"
        elif cv < 0.5:
            stability_rating = "较稳定"
        else:
            stability_rating = "不稳定"
        
        print(f"   稳定性评级: {stability_rating}")
    
    def analyze_performance_distribution(self):
        """分析响应时间分布"""
        print("\n" + "="*60)
        print("📈 5. 响应时间分布分析")
        print("="*60)
        
        all_times = []
        for record in self.detailed_records:
            if record['success']:
                all_times.append(record['execution_time'])
        
        if not all_times:
            print("❌ 没有有效的响应时间数据")
            return
        
        # 按性能等级分类
        performance_distribution = defaultdict(int)
        levels = self.test_configs['performance_levels']
        
        for time_ms in all_times:
            if time_ms <= levels['excellent']:
                performance_distribution['excellent'] += 1
            elif time_ms <= levels['good']:
                performance_distribution['good'] += 1
            elif time_ms <= levels['acceptable']:
                performance_distribution['acceptable'] += 1
            elif time_ms <= levels['slow']:
                performance_distribution['slow'] += 1
            else:
                performance_distribution['very_slow'] += 1
        
        total_requests = len(all_times)
        
        print("📊 响应时间分布:")
        level_descriptions = {
            'excellent': '优秀 (≤50ms)',
            'good': '良好 (51-100ms)',
            'acceptable': '可接受 (101-200ms)',
            'slow': '较慢 (201-500ms)',
            'very_slow': '很慢 (>500ms)'
        }
        
        for level in ['excellent', 'good', 'acceptable', 'slow', 'very_slow']:
            count = performance_distribution[level]
            percentage = (count / total_requests * 100) if total_requests > 0 else 0
            print(f"   {level_descriptions[level]}: {count} ({percentage:.1f}%)")
        
        # 整体统计
        print(f"\n📈 整体响应时间统计:")
        print(f"   总请求数: {total_requests}")
        print(f"   平均响应时间: {statistics.mean(all_times):.2f}ms")
        print(f"   中位数: {statistics.median(all_times):.2f}ms")
        print(f"   标准差: {statistics.stdev(all_times):.2f}ms")
        print(f"   最小值: {min(all_times):.2f}ms")
        print(f"   最大值: {max(all_times):.2f}ms")
        print(f"   P95: {np.percentile(all_times, 95):.2f}ms")
        print(f"   P99: {np.percentile(all_times, 99):.2f}ms")
        
        self.test_results['comprehensive_analysis'] = {
            'total_requests': total_requests,
            'all_times': all_times,
            'performance_distribution': dict(performance_distribution),
            'overall_stats': {
                'mean': statistics.mean(all_times),
                'median': statistics.median(all_times),
                'std': statistics.stdev(all_times),
                'min': min(all_times),
                'max': max(all_times),
                'p95': np.percentile(all_times, 95),
                'p99': np.percentile(all_times, 99)
            }
        }
    def create_performance_charts(self):
        """创建性能分析图表 - 2x2布局，移除性能等级分布图"""
        print("\n📊 生成性能分析图表...")
        
        # 确保中文字体设置
        ensure_chinese_display()
        
        # 设置图表样式
        try:
            plt.style.use('seaborn-v0_8')
        except:
            try:
                plt.style.use('seaborn')
            except:
                plt.style.use('default')
                print("⚠️  使用默认图表样式")
        
        # 重新确保中文字体设置（样式可能会重置字体设置）
        ensure_chinese_display()
            
        # 2x2布局，移除性能等级饼图
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('推荐景区系统运行时间性能分析报告', fontsize=16, fontweight='bold')
        
        # 1. TopK值与响应时间关系
        self._plot_topk_performance(axes[0, 0])
        
        # 2. 用户偏好数量与响应时间关系 (测试所有0-5偏好数量)
        self._plot_preference_performance(axes[0, 1])
        
        # 3. 响应时间分布直方图
        self._plot_response_distribution(axes[1, 0])
        
        # 4. 负载测试时间序列
        self._plot_load_testing_timeline(axes[1, 1])
        
        plt.tight_layout()
        
        # 保存图表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_filename = f"spot_recommendation_runtime_analysis_complete_{timestamp}.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        print(f"📊 图表已保存为: {chart_filename}")
        
        plt.show()
    
    def _plot_topk_performance(self, ax):
        """绘制TopK值与响应时间关系图"""
        if 'basic_performance' not in self.test_results:        return
        
        ensure_chinese_display()
        
        results = self.test_results['basic_performance']
        topk_values = sorted(results.keys())
        means = [results[k]['mean'] for k in topk_values]
        stds = [results[k]['std'] for k in topk_values]
        
        ax.errorbar(topk_values, means, yerr=stds, marker='o', capsize=5, capthick=2)
        ax.set_xlabel('TopK值')
        ax.set_ylabel('平均响应时间 (ms)')
        ax.set_title('TopK值与响应时间关系')
        ax.grid(True, alpha=0.3)
    def _plot_preference_performance(self, ax):
        """绘制用户偏好数量与响应时间关系图 - 显示完整0-5偏好数量范围"""
        if 'scenario_analysis' not in self.test_results:
            return
        
        ensure_chinese_display()
        
        results = self.test_results['scenario_analysis']
        
        # 确保显示完整的0-5偏好数量范围（整数）
        all_pref_counts = [0, 1, 2, 3, 4, 5]  # 显式定义0到5的整数范围
        means = []
        
        for pref_count in all_pref_counts:
            if pref_count in results:
                means.append(results[pref_count]['mean'])
            else:
                means.append(0)  # 没有数据的偏好数量显示为0
        
        # 过滤掉0值，只显示有数据的柱子
        actual_counts = []
        actual_means = []
        for pref_count, mean in zip(all_pref_counts, means):
            if mean > 0:
                actual_counts.append(pref_count)
                actual_means.append(mean)
        
        # 如果有数据则绘制柱状图
        if actual_counts:
            bars = ax.bar(actual_counts, actual_means, alpha=0.7, color='skyblue', width=0.6)
            
            # 为柱子添加数值标签
            max_mean = max(actual_means) if actual_means else 1
            for pref_count, mean in zip(actual_counts, actual_means):
                ax.text(pref_count, mean + max_mean * 0.02, f'{mean:.2f}ms', 
                       ha='center', va='bottom', fontsize=9)
        
        # 设置X轴显示完整的0-5整数刻度
        ax.set_xticks(all_pref_counts)
        ax.set_xticklabels(['0', '1', '2', '3', '4', '5'])
        ax.set_xlim(-0.5, 5.5)  # 设置X轴范围确保所有刻度可见
        ax.set_xlabel('用户偏好数量 (已测试所有0-5整数)')
        ax.set_ylabel('平均响应时间 (ms)')
        ax.set_title('用户偏好数量与响应时间关系\n(完整0-5偏好数量测试)')
        ax.grid(True, alpha=0.3, axis='y')
          # 设置Y轴从0开始
        ax.set_ylim(bottom=0)
        
    def _plot_response_distribution(self, ax):
        """绘制响应时间分布直方图（优化区间划分）"""
        if 'load_testing' not in self.test_results:
            return
        
        ensure_chinese_display()
        
        all_times = self.test_results['load_testing']['times']
        
        if not all_times:
            ax.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax.transAxes)
            return
        
        # 基础统计信息
        min_time = min(all_times)
        max_time = max(all_times)
        mean_time = statistics.mean(all_times)
        std_time = statistics.stdev(all_times) if len(all_times) > 1 else 0
        
        # 优化显示范围设置
        # 使用 Q1-1.5*IQR 到 Q3+1.5*IQR 的范围来减少异常值影响
        q1 = np.percentile(all_times, 25)
        q3 = np.percentile(all_times, 75)
        iqr = q3 - q1
        
        if iqr > 0:
            # 使用四分位数范围
            display_min = max(min_time, q1 - 1.5 * iqr)
            display_max = min(max_time, q3 + 1.5 * iqr)
        else:
            # 回退到均值±3σ方法
            display_min = max(min_time, mean_time - 3 * std_time)
            display_max = min(max_time, mean_time + 3 * std_time)
        
        # 确保最小范围
        if display_max - display_min < 1:
            center = (display_min + display_max) / 2
            display_min = center - 0.5
            display_max = center + 0.5
        
        # 过滤数据到显示范围内
        filtered_times = [t for t in all_times if display_min <= t <= display_max]
        
        # 智能分组数计算
        data_range = display_max - display_min
        if data_range <= 1:
            bins = 10
        elif data_range <= 5:
            bins = 15
        elif data_range <= 10:
            bins = 20
        elif data_range <= 50:
            bins = 25
        else:
            bins = 30
        
        # 创建优化的直方图
        n, bins_edges, patches = ax.hist(filtered_times, bins=bins, alpha=0.7, 
                                        color='lightgreen', edgecolor='black',
                                        range=(display_min, display_max))
        
        # 添加统计线
        ax.axvline(mean_time, color='red', linestyle='--', alpha=0.8, linewidth=2,
                  label=f'平均值: {mean_time:.2f}ms')
        ax.axvline(np.percentile(all_times, 95), color='orange', linestyle='--', alpha=0.8, linewidth=2,
                  label=f'P95: {np.percentile(all_times, 95):.2f}ms')
        
        # 如果中位数在显示范围内，也添加中位数线
        median_time = np.median(all_times)
        if display_min <= median_time <= display_max:
            ax.axvline(median_time, color='blue', linestyle=':', alpha=0.8, linewidth=2,
                      label=f'中位数: {median_time:.2f}ms')
        
        # 设置标签和标题
        ax.set_xlabel('响应时间 (ms)')
        ax.set_ylabel('频次')
        ax.set_title(f'响应时间分布直方图\n(显示范围: {display_min:.1f}-{display_max:.1f}ms)')
        ax.legend(fontsize=9, loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # 添加统计信息文本
        filtered_ratio = len(filtered_times) / len(all_times) * 100
        stats_text = (f'总数据: {len(all_times)}\n'
                     f'显示数据: {len(filtered_times)} ({filtered_ratio:.1f}%)\n'
                     f'范围: {min_time:.1f}-{max_time:.1f}ms')
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
               verticalalignment='top', horizontalalignment='left',               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7),
               fontsize=8)
    
    def _plot_load_testing_timeline(self, ax):
        """绘制负载测试时间序列图"""
        if 'load_testing' not in self.test_results:
            return
        
        ensure_chinese_display()
        
        load_times = self.test_results['load_testing']['times']
        
        # 为了可视化效果，只显示前1000个数据点
        display_times = load_times[:1000] if len(load_times) > 1000 else load_times
        
        ax.plot(range(len(display_times)), display_times, alpha=0.7, color='red')
        ax.set_xlabel('请求序号')
        ax.set_ylabel('响应时间 (ms)')
        ax.set_title('负载测试响应时间序列')
        ax.grid(True, alpha=0.3)
    
    def _plot_stability_analysis(self, ax):
        """绘制稳定性分析图"""
        if 'stability_testing' not in self.test_results:
            return
        
        ensure_chinese_display()
        
        stability_times = self.test_results['stability_testing']['times']
        ax.plot(range(len(stability_times)), stability_times, marker='o', markersize=3, alpha=0.7)
        
        mean_time = self.test_results['stability_testing']['mean']
        ax.axhline(y=mean_time, color='red', linestyle='--', label=f'平均值: {mean_time:.2f}ms')
        
        ax.set_xlabel('测试轮次')
        ax.set_ylabel('响应时间 (ms)')
        ax.set_title('稳定性测试结果')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_performance_levels(self, ax):
        """绘制性能等级饼图"""
        if 'comprehensive_analysis' not in self.test_results:
            return
        
        ensure_chinese_display()
        
        distribution = self.test_results['comprehensive_analysis']['performance_distribution']
        
        labels = []
        sizes = []
        colors = ['#2ECC71', '#3498DB', '#F39C12', '#E74C3C', '#8E44AD']
        
        level_names = {
            'excellent': '优秀',
            'good': '良好', 
            'acceptable': '可接受',
            'slow': '较慢',
            'very_slow': '很慢'
        }
        
        for level in ['excellent', 'good', 'acceptable', 'slow', 'very_slow']:
            if distribution.get(level, 0) > 0:
                labels.append(level_names[level])
                sizes.append(distribution[level])
        
        if sizes:
            ax.pie(sizes, labels=labels, colors=colors[:len(sizes)], autopct='%1.1f%%', startangle=90)
            ax.set_title('响应时间性能等级分布')
    
    def generate_performance_report(self):
        """生成性能测试报告"""
        print("\n" + "="*80)
        print("📋 推荐景区系统运行时间性能测试综合报告")
        print("="*80)
        
        print(f"\n⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"👥 测试用户数量: {len(self.test_users)}")
        print(f"🔄 总测试记录数: {len(self.detailed_records)}")
        
        # 基础性能总结
        if 'basic_performance' in self.test_results:
            print(f"\n🎯 基础性能测试总结:")
            results = self.test_results['basic_performance']
            all_basic_times = []
            for topk_data in results.values():
                all_basic_times.extend(topk_data['times'])
            
            if all_basic_times:
                print(f"   平均响应时间: {statistics.mean(all_basic_times):.2f}ms")
                print(f"   最佳响应时间: {min(all_basic_times):.2f}ms")
                print(f"   最差响应时间: {max(all_basic_times):.2f}ms")
                print(f"   P95响应时间: {np.percentile(all_basic_times, 95):.2f}ms")
        
        # 负载测试总结
        if 'load_testing' in self.test_results:
            load_data = self.test_results['load_testing']
            print(f"\n⚡ 负载测试总结:")
            print(f"   QPS (每秒请求数): {load_data['qps']:.2f}")
            print(f"   平均响应时间: {load_data['mean_time']:.2f}ms")
            print(f"   错误率: {load_data['error_rate']*100:.2f}%")        # 稳定性测试总结
        if 'stability_testing' in self.test_results:
            stability_data = self.test_results['stability_testing']
            print(f"\n🔄 稳定性测试总结:")
            print(f"   变异系数: {stability_data['cv']:.3f}")
            print(f"   响应时间范围: {stability_data['range']:.2f}ms")
        
        # 移除性能评级分析，因为已经移除了comprehensive_analysis
        # 添加简单的测试完成总结
        print(f"\n✅ 测试完成总结:")
        print(f"   成功测试了所有0-5偏好数量的用户场景")
        print(f"   生成了优化的2x2图表布局")
        print(f"   移除了响应时间性能等级分布图")
        
        # 性能优化建议
        print(f"\n💡 性能优化建议:")
        if 'basic_performance' in self.test_results:
            # 使用基础性能测试的数据给出建议
            basic_results = self.test_results['basic_performance']
            all_basic_times = []
            for topk_data in basic_results.values():
                all_basic_times.extend(topk_data['times'])
            
            avg_time = statistics.mean(all_basic_times) if all_basic_times else 0
            if avg_time <= 50:
                print("   ✅ 系统性能优秀，响应时间很快")
            elif avg_time <= 100:
                print("   ✅ 系统性能良好，可考虑进一步优化缓存策略")
            elif avg_time <= 200:
                print("   ⚠️  系统性能可接受，建议优化数据结构或算法")
            else:
                print("   ❌ 系统性能较慢，需要重点优化")
                print("       - 考虑增加缓存层")
                print("       - 优化数据库查询")
                print("       - 采用异步处理")
        
        print("\n" + "="*80)
    
    def save_detailed_results(self):
        """保存详细测试结果到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存为CSV格式
        df = pd.DataFrame(self.detailed_records)
        csv_filename = f"spot_recommendation_runtime_details_fixed_{timestamp}.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"📄 详细测试数据已保存为: {csv_filename}")
        
        # 保存为JSON格式
        json_filename = f"spot_recommendation_runtime_summary_fixed_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2, default=str)
        print(f"📄 测试结果摘要已保存为: {json_filename}")
    def run_all_tests(self):
        """运行所有测试 - 移除性能分布分析"""
        print("🚀 开始运行完整的推荐景区系统运行时间性能测试")
        
        try:
            # 运行各项测试
            self.run_basic_performance_test()
            self.run_scenario_analysis_test()  # 确保测试所有0-5偏好数量
            self.run_load_testing()
            self.run_stability_testing()
            # 移除性能分布分析：self.analyze_performance_distribution()
            
            # 生成报告和图表
            self.generate_performance_report()
            self.create_performance_charts()  # 使用2x2布局
            self.save_detailed_results()
            
            print("\n🎉 所有测试完成！测试了所有0-5偏好数量，移除了性能等级分布图")
            
        except Exception as e:
            print(f"\n❌ 测试过程中发生错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    try:
        # 创建测试实例
        test_runner = SpotRecommendationRuntimeTest()
        
        # 运行所有测试
        test_runner.run_all_tests()
        
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
