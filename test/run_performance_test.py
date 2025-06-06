#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
提供多种测试选项
"""

import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='景点推荐算法性能测试')
    parser.add_argument('--mode', choices=['quick', 'full'], default='quick',
                        help='测试模式: quick=快速测试, full=全面测试')
    parser.add_argument('--users', type=int, default=30,
                        help='测试用户数量 (仅全面测试模式)')
    parser.add_argument('--iterations', type=int, default=3,
                        help='每个场景重复测试次数 (仅全面测试模式)')
    parser.add_argument('--topk', nargs='+', type=int, default=[5, 10, 20, 50],
                        help='TopK值列表')
    
    args = parser.parse_args()
    
    print("🔬 景点推荐算法性能测试")
    print("=" * 50)
    print(f"测试模式: {args.mode}")
    
    if args.mode == 'quick':
        print("运行快速测试...")
        try:
            from test.spot_recommed_compare_quickly import quick_performance_test
            quick_performance_test()
        except Exception as e:
            print(f"快速测试失败: {e}")
            return 1
    
    elif args.mode == 'full':
        print(f"运行全面测试...")
        print(f"  用户数量: {args.users}")
        print(f"  重复次数: {args.iterations}")
        print(f"  TopK值: {args.topk}")
        
        try:
            from test_ultra_optimized_performance import RecommendationPerformanceTester
            
            tester = RecommendationPerformanceTester()
            tester.create_test_users(num_users=args.users)
            tester.run_comprehensive_test(topK_values=args.topk, iterations=args.iterations)
            tester.visualize_results()
            tester.generate_detailed_report()
            tester.save_raw_data()
            
        except Exception as e:
            print(f"全面测试失败: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    print("\n✅ 测试完成！")
    return 0

if __name__ == "__main__":
    sys.exit(main())
