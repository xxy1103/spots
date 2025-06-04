#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
哈夫曼树性能可视化分析
生成性能特征图表
"""

import matplotlib.pyplot as plt
import numpy as np
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_performance_visualization():
    """创建性能分析可视化图表"""
    
    # 测试数据
    char_counts = [50, 100, 200, 500, 1000]
    construction_times = [0.36, 1.09, 0.79, 11.45, 5.67]
    theoretical_times = [k * np.log2(k) * 0.001 for k in char_counts]
    
    text_lengths = [1000, 5000, 10000, 50000, 100000]
    compression_ratios = [54.8, 54.6, 54.7, 54.6, 54.6]
    compression_times = [0.30, 0.71, 1.28, 5.66, 11.53]
    decompression_times = [0.22, 0.98, 1.90, 9.71, 18.46]
    
    # 创建子图
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('哈夫曼树性能分析图表', fontsize=16, fontweight='bold')
    
    # 图1: 构造时间复杂度验证
    ax1.plot(char_counts, construction_times, 'bo-', label='实际时间', linewidth=2, markersize=8)
    ax1.plot(char_counts, theoretical_times, 'r--', label='理论O(k log k)', linewidth=2)
    ax1.set_xlabel('字符种类数 (k)')
    ax1.set_ylabel('构造时间 (ms)')
    ax1.set_title('哈夫曼树构造时间复杂度验证')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    ax1.set_xscale('log')
    
    # 图2: 压缩率与文本长度关系
    ax2.bar(range(len(text_lengths)), compression_ratios, color='lightblue', alpha=0.8)
    ax2.set_xlabel('文本长度')
    ax2.set_ylabel('压缩率 (%)')
    ax2.set_title('压缩率稳定性分析')
    ax2.set_xticks(range(len(text_lengths)))
    ax2.set_xticklabels([f'{length//1000}K' for length in text_lengths])
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(50, 60)
    
    # 添加压缩率数值标注
    for i, ratio in enumerate(compression_ratios):
        ax2.text(i, ratio + 0.5, f'{ratio:.1f}%', ha='center', fontweight='bold')
    
    # 图3: 压缩/解压时间线性关系
    ax3.plot(text_lengths, compression_times, 'g^-', label='压缩时间', linewidth=2, markersize=8)
    ax3.plot(text_lengths, decompression_times, 'ro-', label='解压时间', linewidth=2, markersize=8)
    ax3.set_xlabel('文本长度')
    ax3.set_ylabel('处理时间 (ms)')
    ax3.set_title('压缩/解压时间线性扩展性')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_xscale('log')
    ax3.set_yscale('log')
    
    # 图4: 字符多样性与压缩效果
    diversities = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    compression_by_diversity = [54.5, 54.2, 54.7, 54.9, 32.3, 32.3, 32.3, 32.4, 32.3]
    theoretical_optimal = [55.2, 55.0, 55.5, 55.7, 33.1, 33.1, 33.1, 33.1, 33.1]
    
    x = np.arange(len(diversities))
    width = 0.35
    
    bars1 = ax4.bar(x - width/2, compression_by_diversity, width, label='实际压缩率', color='skyblue')
    bars2 = ax4.bar(x + width/2, theoretical_optimal, width, label='理论最优', color='lightcoral')
    
    ax4.set_xlabel('字符多样性')
    ax4.set_ylabel('压缩率 (%)')
    ax4.set_title('字符多样性对压缩效果的影响')
    ax4.set_xticks(x)
    ax4.set_xticklabels([f'{d:.1f}' for d in diversities])
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 添加数值标注
    for i, (actual, optimal) in enumerate(zip(compression_by_diversity, theoretical_optimal)):
        ax4.text(i - width/2, actual + 1, f'{actual:.1f}', ha='center', fontsize=9)
        ax4.text(i + width/2, optimal + 1, f'{optimal:.1f}', ha='center', fontsize=9)
    
    plt.tight_layout()
    
    # 保存图表
    output_path = "哈夫曼树性能分析图表.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"性能分析图表已保存为: {output_path}")
    
    return fig

def create_complexity_comparison():
    """创建复杂度比较图"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('时间复杂度与空间复杂度分析', fontsize=16, fontweight='bold')
    
    # 时间复杂度比较
    n_values = np.logspace(2, 6, 50)  # 100 到 100万
    
    # 不同操作的时间复杂度
    construction = n_values * np.log2(n_values) / 1000  # O(k log k)
    compression = n_values * 4 / 1000  # O(n × h), 假设h=4
    decompression = n_values * 4 / 1000  # O(n × h)
    
    ax1.loglog(n_values, construction, 'b-', label='构造: O(k log k)', linewidth=2)
    ax1.loglog(n_values, compression, 'g-', label='压缩: O(n × h)', linewidth=2)
    ax1.loglog(n_values, decompression, 'r-', label='解压: O(n × h)', linewidth=2)
    
    ax1.set_xlabel('输入规模 (字符数/种类数)')
    ax1.set_ylabel('相对时间 (ms)')
    ax1.set_title('时间复杂度比较')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 空间复杂度比较
    space_tree = n_values / 1000  # O(k) for tree
    space_codes = n_values * np.log2(n_values) / 8000  # O(k log k) for codes
    space_compression = n_values * 4 / 8000  # O(n × h) for compression buffer
    
    ax2.loglog(n_values, space_tree, 'b-', label='树结构: O(k)', linewidth=2)
    ax2.loglog(n_values, space_codes, 'g-', label='编码表: O(k log k)', linewidth=2)
    ax2.loglog(n_values, space_compression, 'r-', label='压缩缓冲: O(n × h)', linewidth=2)
    
    ax2.set_xlabel('输入规模 (字符数/种类数)')
    ax2.set_ylabel('相对内存使用 (KB)')
    ax2.set_title('空间复杂度比较')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图表
    output_path = "哈夫曼树复杂度分析.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"复杂度分析图表已保存为: {output_path}")
    
    return fig

def main():
    """主函数"""
    print("生成哈夫曼树性能分析图表...")
    
    try:
        # 生成性能分析图表
        fig1 = create_performance_visualization()
        
        # 生成复杂度比较图表
        fig2 = create_complexity_comparison()
        
        print("\n图表生成完成！")
        print("=" * 50)
        print("生成的文件:")
        print("1. 哈夫曼树性能分析图表.png - 实际测试结果可视化")
        print("2. 哈夫曼树复杂度分析.png - 理论复杂度比较")
        print("=" * 50)
        
        # 显示图表（如果在交互环境中）
        plt.show()
        
    except ImportError:
        print("matplotlib未安装，跳过图表生成")
        print("要生成图表，请运行: pip install matplotlib")
    except Exception as e:
        print(f"生成图表时发生错误: {e}")

if __name__ == "__main__":
    main()
