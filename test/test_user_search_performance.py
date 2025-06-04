# -*- coding: utf-8 -*-
"""
用户名查找性能测试程序
比较B树和Trie树在用户名查找操作中的性能差异
"""

import time
import random
import string
import statistics
import matplotlib.pyplot as plt
import matplotlib
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from module.data_structure.btree import BTree
from module.data_structure.trie import UsernameTrie
from module.Model.Model import User

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

class UserSearchPerformanceTest:
    """用户查找性能测试类"""
    
    def __init__(self):
        self.btree = BTree(t=3)
        self.trie = UsernameTrie()
        self.test_usernames = []
        self.test_results = {
            'btree_insert': [],
            'trie_insert': [],
            'btree_search': [],
            'trie_search': [],
            'prefix_search': []
        }
    
    def generate_test_data(self, num_users):
        """
        生成测试用户数据
        
        Args:
            num_users (int): 用户数量
        """
        print(f"生成 {num_users} 个测试用户...")
        self.test_usernames = []
        
        # 生成随机用户名
        for i in range(num_users):
            # 生成长度为5-15的随机用户名
            length = random.randint(5, 15)
            username = ''.join(random.choices(string.ascii_lowercase, k=length))
            # 添加数字后缀确保唯一性
            username += str(i)
            self.test_usernames.append(username)
        
        print(f"生成完成，共 {len(self.test_usernames)} 个用户名")
    
    def test_insertion_performance(self):
        """测试插入操作性能"""
        print("\n=== 测试插入操作性能 ===")
        
        # 测试B树插入
        print("测试B树插入...")
        start_time = time.perf_counter()
        for i, username in enumerate(self.test_usernames):
            self.btree.insert({"id": i+1, "name": username})
        btree_insert_time = time.perf_counter() - start_time
        self.test_results['btree_insert'].append(btree_insert_time)
        
        # 测试Trie树插入
        print("测试Trie树插入...")
        start_time = time.perf_counter()
        for i, username in enumerate(self.test_usernames):
            self.trie.insert_user(i+1, username)
        trie_insert_time = time.perf_counter() - start_time
        self.test_results['trie_insert'].append(trie_insert_time)
        
        print(f"B树插入时间: {btree_insert_time:.6f} 秒")
        print(f"Trie树插入时间: {trie_insert_time:.6f} 秒")
        print(f"Trie树比B树快: {(btree_insert_time/trie_insert_time):.2f} 倍" if trie_insert_time < btree_insert_time else f"B树比Trie树快: {(trie_insert_time/btree_insert_time):.2f} 倍")
    
    def test_search_performance(self, search_count=1000):
        """
        测试查找操作性能
        
        Args:
            search_count (int): 查找次数
        """
        print(f"\n=== 测试查找操作性能 (查找{search_count}次) ===")
        
        # 随机选择要查找的用户名
        search_usernames = random.sample(self.test_usernames, min(search_count, len(self.test_usernames)))
        
        # 测试B树查找
        print("测试B树查找...")
        start_time = time.perf_counter()
        btree_found_count = 0
        for username in search_usernames:
            result = self.btree.search(username)
            if result is not None:
                btree_found_count += 1
        btree_search_time = time.perf_counter() - start_time
        self.test_results['btree_search'].append(btree_search_time)
        
        # 测试Trie树查找
        print("测试Trie树查找...")
        start_time = time.perf_counter()
        trie_found_count = 0
        for username in search_usernames:
            result = self.trie.search_by_username(username)
            if result is not None:
                trie_found_count += 1
        trie_search_time = time.perf_counter() - start_time
        self.test_results['trie_search'].append(trie_search_time)
        
        print(f"B树查找时间: {btree_search_time:.6f} 秒 (找到 {btree_found_count} 个)")
        print(f"Trie树查找时间: {trie_search_time:.6f} 秒 (找到 {trie_found_count} 个)")
        print(f"Trie树比B树快: {(btree_search_time/trie_search_time):.2f} 倍" if trie_search_time < btree_search_time else f"B树比Trie树快: {(trie_search_time/btree_search_time):.2f} 倍")
        
        return btree_search_time, trie_search_time
    
    def test_prefix_search_performance(self, prefix_count=100):
        """
        测试前缀查找性能（Trie树独有功能）
        
        Args:
            prefix_count (int): 前缀查找次数
        """
        print(f"\n=== 测试前缀查找性能 (查找{prefix_count}次) ===")
        
        # 生成随机前缀
        prefixes = []
        for _ in range(prefix_count):
            # 随机选择一个用户名的前缀
            username = random.choice(self.test_usernames)
            prefix_length = random.randint(2, min(5, len(username)))
            prefix = username[:prefix_length]
            prefixes.append(prefix)
        
        # 测试Trie树前缀查找
        print("测试Trie树前缀查找...")
        start_time = time.perf_counter()
        total_matches = 0
        for prefix in prefixes:
            results = self.trie.find_users_by_prefix(prefix)
            total_matches += len(results)
        prefix_search_time = time.perf_counter() - start_time
        self.test_results['prefix_search'].append(prefix_search_time)
        
        print(f"前缀查找时间: {prefix_search_time:.6f} 秒")
        print(f"平均每次查找找到: {total_matches/prefix_count:.2f} 个匹配用户")
        
        return prefix_search_time
    
    def run_comprehensive_test(self, user_counts=[100, 500, 1000, 2000, 5000]):
        """
        运行综合性能测试
        
        Args:
            user_counts (list): 要测试的用户数量列表
        """
        print("开始综合性能测试...")
        
        results = {
            'user_counts': [],
            'btree_insert_times': [],
            'trie_insert_times': [],
            'btree_search_times': [],
            'trie_search_times': [],
            'prefix_search_times': []
        }
        
        for count in user_counts:
            print(f"\n{'='*50}")
            print(f"测试用户数量: {count}")
            print(f"{'='*50}")
            
            # 重置数据结构
            self.btree = BTree(t=3)
            self.trie = UsernameTrie()
            
            # 生成测试数据
            self.generate_test_data(count)
            
            # 测试插入性能
            self.test_insertion_performance()
            
            # 测试查找性能
            search_count = min(1000, count)  # 查找次数不超过用户总数
            btree_time, trie_time = self.test_search_performance(search_count)
            
            # 测试前缀查找性能
            prefix_time = self.test_prefix_search_performance(100)
            
            # 记录结果
            results['user_counts'].append(count)
            results['btree_insert_times'].append(self.test_results['btree_insert'][-1])
            results['trie_insert_times'].append(self.test_results['trie_insert'][-1])
            results['btree_search_times'].append(btree_time)
            results['trie_search_times'].append(trie_time)
            results['prefix_search_times'].append(prefix_time)
        
        return results
    
    def generate_performance_report(self, results):
        """
        生成性能测试报告
        
        Args:
            results (dict): 测试结果数据
        """
        print(f"\n{'='*60}")
        print("性能测试报告")
        print(f"{'='*60}")
        
        print("\n1. 插入操作性能对比:")
        print("-" * 40)
        for i, count in enumerate(results['user_counts']):
            btree_time = results['btree_insert_times'][i]
            trie_time = results['trie_insert_times'][i]
            speedup = btree_time / trie_time if trie_time < btree_time else -(trie_time / btree_time)
            print(f"用户数: {count:5d} | B树: {btree_time:.6f}s | Trie树: {trie_time:.6f}s | 倍数: {speedup:+.2f}")
        
        print("\n2. 查找操作性能对比:")
        print("-" * 40)
        for i, count in enumerate(results['user_counts']):
            btree_time = results['btree_search_times'][i]
            trie_time = results['trie_search_times'][i]
            speedup = btree_time / trie_time if trie_time < btree_time else -(trie_time / btree_time)
            print(f"用户数: {count:5d} | B树: {btree_time:.6f}s | Trie树: {trie_time:.6f}s | 倍数: {speedup:+.2f}")
        
        print("\n3. 前缀查找性能 (Trie树独有):")
        print("-" * 40)
        for i, count in enumerate(results['user_counts']):
            prefix_time = results['prefix_search_times'][i]
            print(f"用户数: {count:5d} | 前缀查找: {prefix_time:.6f}s")
        
        # 计算平均性能提升
        insert_speedups = []
        search_speedups = []
        for i in range(len(results['user_counts'])):
            if results['trie_insert_times'][i] < results['btree_insert_times'][i]:
                insert_speedups.append(results['btree_insert_times'][i] / results['trie_insert_times'][i])
            if results['trie_search_times'][i] < results['btree_search_times'][i]:
                search_speedups.append(results['btree_search_times'][i] / results['trie_search_times'][i])
        
        print(f"\n4. 性能总结:")
        print("-" * 40)
        if insert_speedups:
            avg_insert_speedup = statistics.mean(insert_speedups)
            print(f"插入操作平均加速比: {avg_insert_speedup:.2f}x (Trie树比B树快)")
        if search_speedups:
            avg_search_speedup = statistics.mean(search_speedups)
            print(f"查找操作平均加速比: {avg_search_speedup:.2f}x (Trie树比B树快)")
        
        print(f"Trie树独有功能: 支持前缀查找，平均查找时间: {statistics.mean(results['prefix_search_times']):.6f}s")
    
    def plot_performance_charts(self, results):
        """
        绘制性能对比图表
        
        Args:
            results (dict): 测试结果数据
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        user_counts = results['user_counts']
        
        # 1. 插入性能对比
        ax1.plot(user_counts, results['btree_insert_times'], 'b-o', label='B树', linewidth=2, markersize=6)
        ax1.plot(user_counts, results['trie_insert_times'], 'r-s', label='Trie树', linewidth=2, markersize=6)
        ax1.set_xlabel('用户数量')
        ax1.set_ylabel('插入时间 (秒)')
        ax1.set_title('插入操作性能对比')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 查找性能对比
        ax2.plot(user_counts, results['btree_search_times'], 'b-o', label='B树', linewidth=2, markersize=6)
        ax2.plot(user_counts, results['trie_search_times'], 'r-s', label='Trie树', linewidth=2, markersize=6)
        ax2.set_xlabel('用户数量')
        ax2.set_ylabel('查找时间 (秒)')
        ax2.set_title('查找操作性能对比')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 性能提升比例
        insert_ratios = [b/t for b, t in zip(results['btree_insert_times'], results['trie_insert_times'])]
        search_ratios = [b/t for b, t in zip(results['btree_search_times'], results['trie_search_times'])]
        
        ax3.plot(user_counts, insert_ratios, 'g-^', label='插入操作', linewidth=2, markersize=6)
        ax3.plot(user_counts, search_ratios, 'm-v', label='查找操作', linewidth=2, markersize=6)
        ax3.axhline(y=1, color='k', linestyle='--', alpha=0.5, label='性能相等线')
        ax3.set_xlabel('用户数量')
        ax3.set_ylabel('性能比率 (B树时间/Trie树时间)')
        ax3.set_title('Trie树相对于B树的性能提升')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 前缀查找性能
        ax4.plot(user_counts, results['prefix_search_times'], 'c-d', label='前缀查找', linewidth=2, markersize=6)
        ax4.set_xlabel('用户数量')
        ax4.set_ylabel('前缀查找时间 (秒)')
        ax4.set_title('前缀查找性能 (Trie树独有功能)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('用户名trie树与B树对比.png', dpi=300, bbox_inches='tight')
        print(f"\n性能对比图表已保存为: 用户名trie树与B树对比.png")
        plt.show()


def main():
    """主函数"""
    print("用户名查找性能测试程序")
    print("比较B树和Trie树在用户名查找操作中的性能差异")
    
    # 创建测试实例
    test = UserSearchPerformanceTest()
    
    # 运行综合测试
    user_counts = [100, 500, 1000, 2000, 5000]
    results = test.run_comprehensive_test(user_counts)
    
    # 生成报告
    test.generate_performance_report(results)
    
    # 绘制图表
    try:
        test.plot_performance_charts(results)
    except Exception as e:
        print(f"绘制图表时出现错误: {e}")
        print("这可能是因为缺少matplotlib库，但测试结果仍然有效")
    
    print(f"\n{'='*60}")
    print("测试完成！")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
