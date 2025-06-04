# -*- coding: utf-8 -*-
"""
简化版用户查找性能测试
专门针对UserManager类的B树和Trie树查找性能对比
"""

import time
import random
import string
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from module.user_class import UserManager
from module.Model.Model import User

class SimpleUserSearchTest:
    """简化的用户查找性能测试"""
    
    def __init__(self):
        self.user_manager = UserManager()
        self.test_usernames = []
    
    def generate_test_users(self, num_users):
        """
        生成测试用户并添加到UserManager中
        
        Args:
            num_users (int): 用户数量
        """
        print(f"生成并添加 {num_users} 个测试用户...")
        self.test_usernames = []
        
        for i in range(num_users):
            # 生成随机用户名
            length = random.randint(5, 10)
            username = ''.join(random.choices(string.ascii_lowercase, k=length))
            username += str(i)  # 确保唯一性
            
            # 添加用户
            success = self.user_manager.addUser(
                username=username,
                password="test123",
                liketype=["文化", "自然"]
            )
            
            if success:
                self.test_usernames.append(username)
        
        print(f"成功添加 {len(self.test_usernames)} 个用户")
    
    def test_search_performance(self, search_count=1000):
        """
        测试B树和Trie树的查找性能
        
        Args:
            search_count (int): 查找次数
        """
        if not self.test_usernames:
            print("没有测试用户，请先生成测试数据")
            return
        
        # 随机选择要查找的用户名
        search_usernames = random.choices(self.test_usernames, k=min(search_count, len(self.test_usernames)))
        
        print(f"\n开始性能测试 (查找 {len(search_usernames)} 次)...")
        
        # 测试B树查找性能
        print("测试B树查找...")
        start_time = time.perf_counter()
        btree_found_count = 0
        for username in search_usernames:
            result = self.user_manager.searchUser(username)
            if result is not None:
                btree_found_count += 1
        btree_search_time = time.perf_counter() - start_time
        
        # 测试Trie树查找性能
        print("测试Trie树查找...")
        start_time = time.perf_counter()
        trie_found_count = 0
        for username in search_usernames:
            result = self.user_manager.searchUserWithTrie(username)
            if result is not None:
                trie_found_count += 1
        trie_search_time = time.perf_counter() - start_time
        
        # 输出结果
        print(f"\n=== 查找性能对比结果 ===")
        print(f"B树查找:")
        print(f"  - 总时间: {btree_search_time:.6f} 秒")
        print(f"  - 平均每次: {(btree_search_time/len(search_usernames)*1000):.4f} 毫秒")
        print(f"  - 找到用户: {btree_found_count} 个")
        
        print(f"Trie树查找:")
        print(f"  - 总时间: {trie_search_time:.6f} 秒")
        print(f"  - 平均每次: {(trie_search_time/len(search_usernames)*1000):.4f} 毫秒")
        print(f"  - 找到用户: {trie_found_count} 个")
        
        if trie_search_time < btree_search_time:
            speedup = btree_search_time / trie_search_time
            print(f"\nTrie树比B树快 {speedup:.2f} 倍")
        else:
            slowdown = trie_search_time / btree_search_time
            print(f"\nB树比Trie树快 {slowdown:.2f} 倍")
        
        return btree_search_time, trie_search_time
    
    def test_prefix_search(self, prefix_count=50):
        """
        测试前缀查找功能（Trie树独有）
        
        Args:
            prefix_count (int): 前缀查找次数
        """
        if not self.test_usernames:
            print("没有测试用户，请先生成测试数据")
            return
        
        print(f"\n测试前缀查找功能 (Trie树独有, {prefix_count} 次)...")
        
        # 生成随机前缀
        prefixes = []
        for _ in range(prefix_count):
            username = random.choice(self.test_usernames)
            prefix_length = random.randint(2, min(4, len(username)))
            prefix = username[:prefix_length]
            prefixes.append(prefix)
        
        start_time = time.perf_counter()
        total_matches = 0
        for prefix in prefixes:
            results = self.user_manager.searchUserByPrefix(prefix)
            total_matches += len(results)
        prefix_search_time = time.perf_counter() - start_time
        
        print(f"前缀查找结果:")
        print(f"  - 总时间: {prefix_search_time:.6f} 秒")
        print(f"  - 平均每次: {(prefix_search_time/prefix_count*1000):.4f} 毫秒")
        print(f"  - 平均每次找到: {total_matches/prefix_count:.2f} 个匹配用户")
        
        # 展示几个前缀查找的例子
        print(f"\n前缀查找示例:")
        for i, prefix in enumerate(prefixes[:5]):
            results = self.user_manager.searchUserByPrefix(prefix)
            usernames = [user['name'] for user in results[:3]]  # 只显示前3个
            print(f"  '{prefix}' -> {len(results)} 个匹配: {usernames}{'...' if len(results) > 3 else ''}")
    
    def run_comprehensive_test(self, user_counts=[100, 500, 1000]):
        """
        运行综合性能测试
        
        Args:
            user_counts (list): 要测试的用户数量列表
        """
        print("=" * 60)
        print("用户查找性能综合测试")
        print("=" * 60)
        
        results = []
        
        for count in user_counts:
            print(f"\n{'-' * 40}")
            print(f"测试用户数量: {count}")
            print(f"{'-' * 40}")
            
            # 重新初始化UserManager
            self.user_manager = UserManager()
            
            # 生成测试用户
            self.generate_test_users(count)
            
            # 测试查找性能
            search_count = min(500, count)
            btree_time, trie_time = self.test_search_performance(search_count)
            
            # 测试前缀查找
            self.test_prefix_search(50)
            
            results.append({
                'user_count': count,
                'btree_time': btree_time,
                'trie_time': trie_time,
                'speedup': btree_time / trie_time if trie_time < btree_time else -(trie_time / btree_time)
            })
        
        # 打印总结
        print(f"\n{'=' * 60}")
        print("测试总结")
        print(f"{'=' * 60}")
        print(f"{'用户数':>8} {'B树时间(s)':>12} {'Trie时间(s)':>12} {'性能比率':>10}")
        print(f"{'-' * 50}")
        
        for result in results:
            print(f"{result['user_count']:>8} {result['btree_time']:>12.6f} {result['trie_time']:>12.6f} {result['speedup']:>+10.2f}")
        
        return results


def main():
    """主函数"""
    print("用户查找性能测试程序")
    print("测试UserManager中B树和Trie树的查找性能")
    
    # 创建测试实例
    test = SimpleUserSearchTest()
    
    # 运行小规模快速测试
    print("\n进行快速测试...")
    test.generate_test_users(200)
    test.test_search_performance(300)
    test.test_prefix_search(20)
    
    # 询问是否进行综合测试
    response = input("\n是否进行更全面的性能测试？(y/n): ").lower().strip()
    if response == 'y' or response == 'yes':
        test.run_comprehensive_test([100, 500, 1000, 2000])
    
    print(f"\n{'=' * 60}")
    print("测试完成！")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
