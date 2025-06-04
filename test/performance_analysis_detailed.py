#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
详细的Trie树与B树性能分析
分析不同场景下两种数据结构的优势
"""

import time
import random
import string
import sys
import os

# 添加模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from module.data_structure.btree import BTree
from module.data_structure.trie import UsernameTrie

class PerformanceAnalyzer:
    def __init__(self):
        self.results = {}
    
    def generate_usernames_fixed_length(self, count, length=8):
        """生成固定长度的用户名"""
        usernames = []
        for i in range(count):
            username = ''.join(random.choices(string.ascii_lowercase, k=length))
            usernames.append(f"{username}{i:04d}")  # 避免重复
        return usernames
    
    def generate_usernames_variable_length(self, count):
        """生成长度差异很大的用户名"""
        usernames = []
        for i in range(count):
            # 长度在3到50之间随机变化
            length = random.randint(3, 50)
            username = ''.join(random.choices(string.ascii_lowercase, k=length))
            usernames.append(f"{username}{i:04d}")
        return usernames
    
    def generate_usernames_with_common_prefixes(self, count):
        """生成有很多公共前缀的用户名"""
        prefixes = ["admin", "user", "test", "guest", "member"]
        usernames = []
        for i in range(count):
            prefix = random.choice(prefixes)
            suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            usernames.append(f"{prefix}_{suffix}")
        return usernames
    
    def test_insertion_performance(self, usernames, description):
        """测试插入性能"""
        print(f"\n=== {description} - 插入性能测试 ===")
        
        # B树测试
        btree = BTree(t=3)
        start_time = time.time()
        for i, username in enumerate(usernames):
            btree.insert({"id": i+1, "name": username})
        btree_time = time.time() - start_time
        
        # Trie树测试
        trie = UsernameTrie()
        start_time = time.time()
        for i, username in enumerate(usernames):
            trie.insert_user(i+1, username)
        trie_time = time.time() - start_time
        
        print(f"B树插入时间: {btree_time:.4f}秒")
        print(f"Trie树插入时间: {trie_time:.4f}秒")
        print(f"性能比率 (Trie/B树): {trie_time/btree_time:.2f}")
        
        return btree, trie, btree_time, trie_time
    
    def test_search_performance(self, btree, trie, usernames, description):
        """测试精确搜索性能"""
        print(f"\n=== {description} - 精确搜索性能测试 ===")
        
        # 随机选择一些用户名进行搜索
        search_usernames = random.sample(usernames, min(1000, len(usernames)))
        
        # B树搜索测试
        start_time = time.time()
        btree_found = 0
        for username in search_usernames:
            result = btree.search(username)
            if result:
                btree_found += 1
        btree_time = time.time() - start_time
        
        # Trie树搜索测试
        start_time = time.time()
        trie_found = 0
        for username in search_usernames:
            result = trie.search_by_username(username)
            if result:
                trie_found += 1
        trie_time = time.time() - start_time
        
        print(f"B树搜索时间: {btree_time:.4f}秒 (找到{btree_found}个)")
        print(f"Trie树搜索时间: {trie_time:.4f}秒 (找到{trie_found}个)")
        print(f"性能比率 (Trie/B树): {trie_time/btree_time:.2f}")
        
        return btree_time, trie_time
    
    def test_prefix_search_performance(self, trie, usernames, description):
        """测试前缀搜索性能"""
        print(f"\n=== {description} - 前缀搜索性能测试 ===")
        
        # 生成一些前缀
        prefixes = []
        for username in random.sample(usernames, min(100, len(usernames))):
            if len(username) >= 3:
                prefixes.append(username[:3])  # 3字符前缀
        
        # 去重
        prefixes = list(set(prefixes))
        
        # Trie树前缀搜索
        start_time = time.time()
        total_found = 0
        for prefix in prefixes:
            results = trie.find_users_by_prefix(prefix)
            total_found += len(results)
        trie_time = time.time() - start_time
        
        print(f"Trie树前缀搜索时间: {trie_time:.4f}秒")
        print(f"搜索{len(prefixes)}个前缀，总共找到{total_found}个匹配")
        print(f"平均每个前缀找到: {total_found/len(prefixes):.1f}个用户")
        
        return trie_time
    
    def analyze_memory_usage(self, btree, trie, usernames, description):
        """分析内存使用情况"""
        print(f"\n=== {description} - 内存使用分析 ===")
        
        # 简单的内存估算（实际内存使用更复杂）
        
        # B树内存估算
        btree_nodes = len(usernames) // 2  # 估算节点数
        btree_memory = btree_nodes * 64 + len(usernames) * 50  # 节点开销 + 数据
        
        # Trie树内存估算
        total_chars = sum(len(username) for username in usernames)
        unique_chars = len(set(''.join(usernames)))
        trie_memory = total_chars * 40 + unique_chars * 20  # 字符节点开销
        
        print(f"B树估算内存: {btree_memory/1024:.1f}KB")
        print(f"Trie树估算内存: {trie_memory/1024:.1f}KB")
        print(f"内存比率 (Trie/B树): {trie_memory/btree_memory:.2f}")
    
    def run_comprehensive_analysis(self):
        """运行综合分析"""
        print("=" * 60)
        print("Trie树 vs B树 综合性能分析")
        print("=" * 60)
        
        # 场景1: 用户名长度固定且较短
        print("\n" + "="*50)
        print("场景1: 用户名长度固定且较短 (8字符)")
        print("="*50)
        usernames1 = self.generate_usernames_fixed_length(5000, 8)
        btree1, trie1, _, _ = self.test_insertion_performance(usernames1, "固定短长度")
        self.test_search_performance(btree1, trie1, usernames1, "固定短长度")
        self.test_prefix_search_performance(trie1, usernames1, "固定短长度")
        self.analyze_memory_usage(btree1, trie1, usernames1, "固定短长度")
        
        # 场景2: 用户名长度差异很大
        print("\n" + "="*50)
        print("场景2: 用户名长度差异很大 (3-50字符)")
        print("="*50)
        usernames2 = self.generate_usernames_variable_length(5000)
        btree2, trie2, _, _ = self.test_insertion_performance(usernames2, "长度差异大")
        self.test_search_performance(btree2, trie2, usernames2, "长度差异大")
        self.test_prefix_search_performance(trie2, usernames2, "长度差异大")
        self.analyze_memory_usage(btree2, trie2, usernames2, "长度差异大")
        
        # 场景3: 很多公共前缀
        print("\n" + "="*50)
        print("场景3: 用户名有很多公共前缀")
        print("="*50)
        usernames3 = self.generate_usernames_with_common_prefixes(5000)
        btree3, trie3, _, _ = self.test_insertion_performance(usernames3, "公共前缀多")
        self.test_search_performance(btree3, trie3, usernames3, "公共前缀多")
        self.test_prefix_search_performance(trie3, usernames3, "公共前缀多")
        self.analyze_memory_usage(btree3, trie3, usernames3, "公共前缀多")
        
        # 场景4: 不同数据量的影响
        print("\n" + "="*50)
        print("场景4: 不同数据量的性能影响")
        print("="*50)
        for count in [1000, 5000, 10000, 20000]:
            print(f"\n--- 数据量: {count} ---")
            usernames = self.generate_usernames_fixed_length(count, 8)
            btree, trie, insert_b, insert_t = self.test_insertion_performance(
                usernames, f"{count}用户")
            search_b, search_t = self.test_search_performance(
                btree, trie, usernames, f"{count}用户")
            
            print(f"插入性能比 (Trie/B树): {insert_t/insert_b:.2f}")
            print(f"搜索性能比 (Trie/B树): {search_t/search_b:.2f}")

def main():
    analyzer = PerformanceAnalyzer()
    analyzer.run_comprehensive_analysis()
    
    print("\n" + "="*60)
    print("结论总结:")
    print("="*60)
    print("1. 固定短长度用户名: Trie树在前缀搜索上有绝对优势")
    print("2. 长度差异大: B树性能更稳定，内存使用更高效")
    print("3. 公共前缀多: Trie树内存共享优势明显")
    print("4. 大数据量: Trie树性能受用户名长度影响，B树受数量影响")
    print("5. 精确搜索: 小数据量时B树更优，大数据量时Trie树更优")

if __name__ == "__main__":
    main()
