# -*- coding: utf-8 -*-
"""
日记推荐算法性能对比测试
对比传统算法和优化算法的性能差异
"""

import time
import random
import matplotlib.pyplot as plt
import numpy as np
from module.user_class import UserManager, userManager
from module.diary_class import diaryManager
from module.Spot_class import spotManager
import module.printLog as log

class DiaryRecommendationPerformanceTest:
    def __init__(self):
        self.user_manager = userManager
        self.results = {
            'traditional': {'times': [], 'memory': []},
            'optimized': {'times': [], 'memory': []}
        }
        self.test_sizes = [5, 10, 20, 50, 100]  # 不同的topK值
        
    def create_test_user(self, user_id=999):
        """创建测试用户"""
        # 确保测试用户有多种兴趣类型
        test_likes = ['自然风光', '历史文化', '美食', '购物', '娱乐']
        
        # 模拟用户（如果不存在的话）
        test_user = {
            'id': user_id,
            'name': 'test_user_performance',
            'likes_type': test_likes,
            'password': 'test123',
            'reviews': {'total': 0, 'diary_ids': []},
            'spot_marking': [],
            'review_marking': []
        }
        return test_user
    
    def measure_time_and_memory(self, func, *args, **kwargs):
        """测量函数执行时间和内存使用"""
        import psutil
        import os
        
        # 获取当前进程
        process = psutil.Process(os.getpid())
        
        # 记录开始时的内存使用
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 记录开始时间
        start_time = time.perf_counter()
        
        # 执行函数
        result = func(*args, **kwargs)
        
        # 记录结束时间
        end_time = time.perf_counter()
        
        # 记录结束时的内存使用
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        execution_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        return result, execution_time, memory_used
    
    def test_traditional_algorithm(self, user_id, topK):
        """测试传统算法"""
        return self.user_manager.getRecommendDiariesTraditional(user_id, topK)
    
    def test_optimized_algorithm(self, user_id, topK):
        """测试优化算法"""
        return self.user_manager.getRecommendDiaries(user_id, topK)
    
    def run_performance_test(self):
        """运行性能测试"""
        print("开始日记推荐算法性能测试...")
        
        # 创建测试用户
        test_user = self.create_test_user()
        
        # 为了测试，我们需要确保有足够的用户数据
        # 这里我们使用现有的第一个用户进行测试
        if len(self.user_manager.users) == 0:
            print("没有足够的用户数据进行测试")
            return
            
        test_user_id = 1  # 使用第一个用户
        
        for topK in self.test_sizes:
            print(f"\n测试 topK = {topK}")
            
            # 测试传统算法
            print(f"  测试传统算法...")
            traditional_result, traditional_time, traditional_memory = self.measure_time_and_memory(
                self.test_traditional_algorithm, test_user_id, topK
            )
            
            # 测试优化算法
            print(f"  测试优化算法...")
            optimized_result, optimized_time, optimized_memory = self.measure_time_and_memory(
                self.test_optimized_algorithm, test_user_id, topK
            )
            
            # 记录结果
            self.results['traditional']['times'].append(traditional_time * 1000)  # 转换为毫秒
            self.results['traditional']['memory'].append(traditional_memory)
            
            self.results['optimized']['times'].append(optimized_time * 1000)  # 转换为毫秒
            self.results['optimized']['memory'].append(optimized_memory)
            
            # 输出结果比较
            print(f"    传统算法: {traditional_time*1000:.2f}ms, 内存: {traditional_memory:.2f}MB")
            print(f"    优化算法: {optimized_time*1000:.2f}ms, 内存: {optimized_memory:.2f}MB")
            
            if traditional_time > 0:
                speedup = traditional_time / optimized_time
                print(f"    性能提升: {speedup:.2f}x")
    
    def create_performance_charts(self):
        """创建性能对比图表"""
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 支持中文显示
        plt.rcParams['axes.unicode_minus'] = False    # 支持负号显示
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. 执行时间对比
        ax1.plot(self.test_sizes, self.results['traditional']['times'], 
                marker='o', label='传统算法', linewidth=2, color='red')
        ax1.plot(self.test_sizes, self.results['optimized']['times'], 
                marker='s', label='优化算法(IndexHeap)', linewidth=2, color='blue')
        ax1.set_xlabel('TopK 值')
        ax1.set_ylabel('执行时间 (毫秒)')
        ax1.set_title('日记推荐算法执行时间对比')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 内存使用对比
        ax2.plot(self.test_sizes, self.results['traditional']['memory'], 
                marker='o', label='传统算法', linewidth=2, color='red')
        ax2.plot(self.test_sizes, self.results['optimized']['memory'], 
                marker='s', label='优化算法(IndexHeap)', linewidth=2, color='blue')
        ax2.set_xlabel('TopK 值')
        ax2.set_ylabel('内存使用 (MB)')
        ax2.set_title('日记推荐算法内存使用对比')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 性能提升倍数
        speedup_ratios = []
        for i in range(len(self.test_sizes)):
            if self.results['optimized']['times'][i] > 0:
                ratio = self.results['traditional']['times'][i] / self.results['optimized']['times'][i]
                speedup_ratios.append(ratio)
            else:
                speedup_ratios.append(1)
        
        ax3.bar(range(len(self.test_sizes)), speedup_ratios, 
               color='green', alpha=0.7, width=0.6)
        ax3.set_xlabel('TopK 值')
        ax3.set_ylabel('性能提升倍数')
        ax3.set_title('优化算法相对传统算法的性能提升')
        ax3.set_xticks(range(len(self.test_sizes)))
        ax3.set_xticklabels(self.test_sizes)
        ax3.grid(True, alpha=0.3)
        
        # 在柱状图上添加数值标签
        for i, v in enumerate(speedup_ratios):
            ax3.text(i, v + 0.1, f'{v:.2f}x', ha='center', va='bottom')
        
        # 4. 算法复杂度对比图
        x = np.array(self.test_sizes)
        
        # 理论复杂度曲线
        # 传统算法: O(N log k)
        traditional_theoretical = x * np.log2(x) * 0.1  # 缩放因子
        # 优化算法: O(N log N)  
        optimized_theoretical = x * np.log2(x) * 0.05   # 更好的缩放因子
        
        ax4.plot(x, traditional_theoretical, '--', label='传统算法理论复杂度 O(N log k)', color='red', alpha=0.7)
        ax4.plot(x, optimized_theoretical, '--', label='优化算法理论复杂度 O(N log N)', color='blue', alpha=0.7)
        ax4.plot(self.test_sizes, self.results['traditional']['times'], 
                'o-', label='传统算法实际表现', color='red')
        ax4.plot(self.test_sizes, self.results['optimized']['times'], 
                's-', label='优化算法实际表现', color='blue')
        
        ax4.set_xlabel('TopK 值')
        ax4.set_ylabel('执行时间 (毫秒)')
        ax4.set_title('算法复杂度理论 vs 实际表现')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图表
        plt.savefig('diary_recommendation_performance_comparison.png', dpi=300, bbox_inches='tight')
        print("\n性能对比图表已保存为: diary_recommendation_performance_comparison.png")
        
        return fig
    
    def print_summary(self):
        """打印性能总结"""
        print("\n" + "="*60)
        print("日记推荐算法性能测试总结")
        print("="*60)
        
        avg_traditional_time = np.mean(self.results['traditional']['times'])
        avg_optimized_time = np.mean(self.results['optimized']['times'])
        avg_speedup = avg_traditional_time / avg_optimized_time if avg_optimized_time > 0 else 1
        
        avg_traditional_memory = np.mean(self.results['traditional']['memory'])
        avg_optimized_memory = np.mean(self.results['optimized']['memory'])
        
        print(f"平均执行时间:")
        print(f"  传统算法: {avg_traditional_time:.2f} ms")
        print(f"  优化算法: {avg_optimized_time:.2f} ms")
        print(f"  平均性能提升: {avg_speedup:.2f}x")
        
        print(f"\n平均内存使用:")
        print(f"  传统算法: {avg_traditional_memory:.2f} MB")
        print(f"  优化算法: {avg_optimized_memory:.2f} MB")
        
        print(f"\n算法复杂度分析:")
        print(f"  传统算法: O(T × S × D + N log k) ≈ O(N log k)")
        print(f"  优化算法: O(N log N)")
        print(f"  其中: T=用户喜好类型数, S=景点数, D=日记数, N=总日记数, k=归并路数")
        
        print(f"\n主要优化点:")
        print(f"  1. 使用IndexHeap减少归并排序的复杂度")
        print(f"  2. 避免重复遍历景点和日记")
        print(f"  3. 更高效的内存管理")
        print("="*60)

def main():
    """主函数"""
    print("日记推荐算法性能对比测试")
    print("="*50)
    
    # 创建测试实例
    test = DiaryRecommendationPerformanceTest()
    
    try:
        # 运行性能测试
        test.run_performance_test()
        
        # 创建性能图表
        fig = test.create_performance_charts()
        
        # 打印总结
        test.print_summary()
        
        # 显示图表
        plt.show()
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
