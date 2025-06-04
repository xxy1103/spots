# -*- coding: utf-8 -*-
"""
算法复杂度理论对比可视化
"""

import matplotlib.pyplot as plt
import numpy as np

def create_complexity_comparison():
    """创建算法复杂度对比图"""
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 支持中文显示
    plt.rcParams['axes.unicode_minus'] = False    # 支持负号显示
    
    # 创建数据点
    n_values = np.array([10, 50, 100, 500, 1000, 5000, 10000])
    k_values = np.array([2, 5, 10, 20, 50, 100, 200])  # 归并路数
    
    # 计算理论复杂度
    traditional_complexity = n_values * np.log2(k_values)  # O(N log k)
    optimized_complexity = n_values * np.log2(n_values)    # O(N log N)
    
    # 创建图表
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. 复杂度对比图
    ax1.loglog(n_values, traditional_complexity, 'o-', label='传统算法 O(N log k)', 
              color='#FF6B6B', linewidth=3, markersize=8)
    ax1.loglog(n_values, optimized_complexity, 's-', label='优化算法 O(N log N)', 
              color='#4ECDC4', linewidth=3, markersize=8)
    ax1.set_xlabel('数据规模 N', fontsize=12)
    ax1.set_ylabel('操作次数', fontsize=12)
    ax1.set_title('算法时间复杂度理论对比', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # 2. 性能比值图
    ax2.semilogx(n_values, optimized_complexity / traditional_complexity, 'o-', 
                color='#45B7D1', linewidth=3, markersize=8)
    ax2.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='相等线')
    ax2.set_xlabel('数据规模 N', fontsize=12)
    ax2.set_ylabel('优化算法 / 传统算法', fontsize=12)
    ax2.set_title('算法复杂度比值（>1表示传统算法更优）', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # 3. 不同k值下的性能对比
    ax3.clear()
    n_fixed = 1000  # 固定N值
    k_range = np.array([1, 2, 5, 10, 20, 50, 100, 200, 500])
    traditional_k = n_fixed * np.log2(k_range)
    optimized_k = np.full_like(k_range, n_fixed * np.log2(n_fixed), dtype=float)
    
    ax3.plot(k_range, traditional_k, 'o-', label='传统算法 O(N log k)', 
            color='#FF6B6B', linewidth=3, markersize=6)
    ax3.axhline(y=optimized_k[0], color='#4ECDC4', linestyle='-', linewidth=3, 
               label='优化算法 O(N log N)')
    ax3.set_xlabel('归并路数 k', fontsize=12)
    ax3.set_ylabel('操作次数', fontsize=12)
    ax3.set_title(f'固定数据规模(N={n_fixed})下k值对性能的影响', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.set_xscale('log')
    
    # 4. 实际测试场景模拟
    ax4.clear()
    
    # 模拟不同应用场景的数据规模
    scenarios = ['小型系统\n(100个日记)', '中型系统\n(1000个日记)', 
                '大型系统\n(10000个日记)', '超大型系统\n(100000个日记)']
    n_scenarios = np.array([100, 1000, 10000, 100000])
    k_scenarios = np.array([5, 20, 100, 500])  # 对应的归并路数
    
    traditional_scenarios = n_scenarios * np.log2(k_scenarios)
    optimized_scenarios = n_scenarios * np.log2(n_scenarios)
    
    x_pos = np.arange(len(scenarios))
    width = 0.35
    
    bars1 = ax4.bar(x_pos - width/2, traditional_scenarios, width, 
                   label='传统算法', color='#FF6B6B', alpha=0.8)
    bars2 = ax4.bar(x_pos + width/2, optimized_scenarios, width, 
                   label='优化算法', color='#4ECDC4', alpha=0.8)
    
    ax4.set_xlabel('应用场景', fontsize=12)
    ax4.set_ylabel('操作次数', fontsize=12)
    ax4.set_title('不同应用场景下的算法性能对比', fontsize=14, fontweight='bold')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(scenarios)
    ax4.legend(fontsize=12)
    ax4.set_yscale('log')
    ax4.grid(True, alpha=0.3)
    
    # 添加数值标签
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}',
                    ha='center', va='bottom', fontsize=10, rotation=45)
    
    plt.tight_layout()
    plt.savefig('algorithm_complexity_comparison.png', dpi=300, bbox_inches='tight')
    print("算法复杂度对比图已保存为: algorithm_complexity_comparison.png")
    
    return fig

def print_complexity_analysis():
    """打印复杂度分析结果"""
    print("="*80)
    print("日记推荐算法复杂度分析")
    print("="*80)
    
    print("\n📊 理论时间复杂度:")
    print("   传统算法: O(T × S × D + N log k) ≈ O(N log k)")
    print("   优化算法: O(N log N)")
    print("   其中: T=用户兴趣数, S=景点数, D=每景点日记数, N=总日记数, k=归并路数")
    
    print("\n🔍 复杂度对比分析:")
    print("   • 当 k << N 时，传统算法理论上更优")
    print("   • 当 k ≈ N 时，两种算法复杂度相近")
    print("   • 当 k > N 时，优化算法更优（实际上不可能）")
    
    print("\n📈 实际场景分析:")
    scenarios = [
        ("小型系统", 100, 5, "传统算法优势明显"),
        ("中型系统", 1000, 20, "传统算法略优"),
        ("大型系统", 10000, 100, "两种算法相近"),
        ("超大型系统", 100000, 500, "两种算法相近")
    ]
    
    for name, n, k, conclusion in scenarios:
        traditional = n * np.log2(k)
        optimized = n * np.log2(n)
        ratio = optimized / traditional
        print(f"   {name:10} (N={n:6}, k={k:3}): "
              f"传统={traditional:8.0f}, 优化={optimized:8.0f}, "
              f"比值={ratio:.2f} - {conclusion}")
    
    print("\n💡 选择建议:")
    print("   • 小规模数据 (N < 1000): 推荐传统算法")
    print("   • 中等规模数据 (1000 ≤ N < 10000): 根据具体需求选择")
    print("   • 大规模数据 (N ≥ 10000): 两种算法性能相近，优先考虑代码可维护性")
    print("="*80)

def main():
    """主函数"""
    print("日记推荐算法复杂度对比分析")
    
    # 创建复杂度对比图
    fig = create_complexity_comparison()
    
    # 打印分析结果
    print_complexity_analysis()
    
    # 显示图表
    plt.show()

if __name__ == "__main__":
    main()
