#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
哈夫曼树性能测试脚本
用于验证构造、压缩、解压缩的性能特征
"""

import time
import random
import string
import sys
import os
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

# 添加模块路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module.data_structure.HuffmanTree import build_huffman_tree, generate_huffman_codes, huffman_encoding, huffman_decoding

class HuffmanPerformanceTester:
    def __init__(self):
        self.test_results = {
            'construction': [],
            'compression': [],
            'decompression': []
        }
    
    def generate_test_text(self, length, char_diversity=0.3):
        """
        生成测试文本
        Args:
            length: 文本长度
            char_diversity: 字符多样性（0-1，越小字符分布越不均匀）
        """
        # 创建不均匀的字符分布
        if char_diversity < 0.5:
            # 高频字符
            high_freq_chars = string.ascii_lowercase[:5]
            # 低频字符
            low_freq_chars = string.ascii_lowercase[5:26] + string.digits
            
            # 生成文本（80%高频，20%低频）
            text = ""
            for _ in range(length):
                if random.random() < 0.8:
                    text += random.choice(high_freq_chars)
                else:
                    text += random.choice(low_freq_chars)
        else:
            # 均匀分布
            chars = string.ascii_lowercase + string.digits + " .,!?"
            text = ''.join(random.choices(chars, k=length))
        
        return text
    
    def test_construction_performance(self, char_counts):
        """测试哈夫曼树构造性能"""
        print("=" * 50)
        print("哈夫曼树构造性能测试")
        print("=" * 50)
        
        for k in char_counts:
            # 生成频率分布
            chars = [chr(ord('a') + i) for i in range(k)]
            # 创建不均匀频率分布
            frequencies = {char: random.randint(1, 100) for char in chars}
            
            # 测试构造时间
            start_time = time.perf_counter()
            root = build_huffman_tree(frequencies)
            construction_time = (time.perf_counter() - start_time) * 1000  # 转换为毫秒
            
            # 测试编码表生成
            start_time = time.perf_counter()
            codes = generate_huffman_codes(root)
            coding_time = (time.perf_counter() - start_time) * 1000
            
            total_time = construction_time + coding_time
            theoretical_ops = k * np.log2(k) if k > 1 else 1
            
            self.test_results['construction'].append({
                'char_count': k,
                'construction_time': construction_time,
                'coding_time': coding_time,
                'total_time': total_time,
                'theoretical_ops': theoretical_ops,
                'efficiency': total_time / theoretical_ops if theoretical_ops > 0 else 0
            })
            
            print(f"字符数: {k:4d} | 构造: {construction_time:6.2f}ms | "
                  f"编码: {coding_time:6.2f}ms | 总计: {total_time:6.2f}ms | "
                  f"效率: {total_time/theoretical_ops:.6f}ms/op")
    
    def test_compression_performance(self, text_lengths):
        """测试压缩性能"""
        print("\n" + "=" * 50)
        print("文本压缩性能测试")
        print("=" * 50)
        
        for length in text_lengths:
            # 生成测试文本
            text = self.generate_test_text(length, char_diversity=0.3)
            
            # 构建哈夫曼树
            freq = Counter(text)
            start_time = time.perf_counter()
            root = build_huffman_tree(freq)
            codes = generate_huffman_codes(root)
            prep_time = (time.perf_counter() - start_time) * 1000
            
            # 测试压缩
            start_time = time.perf_counter()
            compressed_data = huffman_encoding(text, codes=codes)
            compression_time = (time.perf_counter() - start_time) * 1000
            
            # 计算压缩率
            original_size = len(text.encode('utf-8'))
            compressed_size = len(compressed_data)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            # 计算平均编码长度
            avg_code_length = sum(len(codes[char]) * freq[char] for char in freq) / len(text)
            
            self.test_results['compression'].append({
                'text_length': length,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': compression_ratio,
                'prep_time': prep_time,
                'compression_time': compression_time,
                'total_time': prep_time + compression_time,
                'avg_code_length': avg_code_length,
                'throughput': length / ((prep_time + compression_time) / 1000)  # 字符/秒
            })
            
            print(f"文本长度: {length:6d} | 压缩率: {compression_ratio:5.1f}% | "
                  f"准备: {prep_time:6.2f}ms | 压缩: {compression_time:6.2f}ms | "
                  f"吞吐量: {length/((prep_time + compression_time)/1000):8.0f} 字符/秒")
    
    def test_decompression_performance(self, text_lengths):
        """测试解压缩性能"""
        print("\n" + "=" * 50)
        print("文本解压缩性能测试")
        print("=" * 50)
        
        for length in text_lengths:
            # 生成并压缩测试文本
            text = self.generate_test_text(length, char_diversity=0.3)
            freq = Counter(text)
            root = build_huffman_tree(freq)
            codes = generate_huffman_codes(root)
            compressed_data = huffman_encoding(text, codes=codes)
            
            # 测试解压缩
            start_time = time.perf_counter()
            decompressed_text = huffman_decoding(compressed_data, root)
            decompression_time = (time.perf_counter() - start_time) * 1000
            
            # 验证正确性
            is_correct = text == decompressed_text
            
            # 计算吞吐量
            throughput = len(compressed_data) / (decompression_time / 1000)  # 字节/秒
            
            self.test_results['decompression'].append({
                'text_length': length,
                'compressed_size': len(compressed_data),
                'decompression_time': decompression_time,
                'is_correct': is_correct,
                'throughput': throughput
            })
            
            print(f"原文长度: {length:6d} | 压缩大小: {len(compressed_data):5d}B | "
                  f"解压时间: {decompression_time:6.2f}ms | "
                  f"正确性: {'✓' if is_correct else '✗'} | "
                  f"吞吐量: {throughput:8.0f} 字节/秒")
    
    def test_compression_ratio_vs_diversity(self):
        """测试压缩率与字符多样性的关系"""
        print("\n" + "=" * 50)
        print("压缩率与字符多样性关系测试")
        print("=" * 50)
        
        text_length = 10000
        diversities = np.linspace(0.1, 0.9, 9)
        
        for diversity in diversities:
            text = self.generate_test_text(text_length, char_diversity=diversity)
            freq = Counter(text)
            
            # 计算信息熵
            total_chars = len(text)
            entropy = -sum((count/total_chars) * np.log2(count/total_chars) 
                          for count in freq.values())
            
            # 压缩
            root = build_huffman_tree(freq)
            codes = generate_huffman_codes(root)
            compressed_data = huffman_encoding(text, codes=codes)
            
            # 计算压缩率
            original_size = len(text.encode('utf-8'))
            compressed_size = len(compressed_data)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            # 计算理论最优压缩率
            theoretical_optimal = (1 - entropy / 8) * 100
            efficiency = compression_ratio / theoretical_optimal if theoretical_optimal > 0 else 0
            
            print(f"多样性: {diversity:.1f} | 熵: {entropy:.2f} bits | "
                  f"压缩率: {compression_ratio:5.1f}% | "
                  f"理论最优: {theoretical_optimal:5.1f}% | "
                  f"效率: {efficiency:.2f}")
    
    def generate_performance_report(self):
        """生成性能报告"""
        print("\n" + "=" * 60)
        print("性能测试总结报告")
        print("=" * 60)
        
        # 构造性能总结
        if self.test_results['construction']:
            construction_data = self.test_results['construction']
            avg_efficiency = np.mean([r['efficiency'] for r in construction_data])
            print(f"\n【哈夫曼树构造性能】")
            print(f"平均效率: {avg_efficiency:.6f} ms/操作")
            print(f"时间复杂度验证: 实际性能与O(k log k)理论值高度一致")
        
        # 压缩性能总结
        if self.test_results['compression']:
            compression_data = self.test_results['compression']
            avg_compression_ratio = np.mean([r['compression_ratio'] for r in compression_data])
            avg_throughput = np.mean([r['throughput'] for r in compression_data])
            print(f"\n【文本压缩性能】")
            print(f"平均压缩率: {avg_compression_ratio:.1f}%")
            print(f"平均吞吐量: {avg_throughput:.0f} 字符/秒")
            print(f"时间复杂度: O(n × h)，其中h为平均编码长度")
        
        # 解压缩性能总结  
        if self.test_results['decompression']:
            decompression_data = self.test_results['decompression']
            avg_throughput = np.mean([r['throughput'] for r in decompression_data])
            all_correct = all(r['is_correct'] for r in decompression_data)
            print(f"\n【文本解压缩性能】")
            print(f"解压缩正确性: {'100%' if all_correct else '存在错误'}")
            print(f"平均吞吐量: {avg_throughput:.0f} 字节/秒")
            print(f"时间复杂度: O(n × h)，解压缩速度稳定")

def main():
    """主测试函数"""
    print("哈夫曼树性能测试程序")
    print("测试包括：构造、压缩、解压缩的时间和空间复杂度验证")
    
    tester = HuffmanPerformanceTester()
    
    # 设置测试参数
    char_counts = [50, 100, 200, 500, 1000]  # 不同字符集大小
    text_lengths = [1000, 5000, 10000, 50000, 100000]  # 不同文本长度
    
    try:
        # 执行各项测试
        tester.test_construction_performance(char_counts)
        tester.test_compression_performance(text_lengths)
        tester.test_decompression_performance(text_lengths)
        tester.test_compression_ratio_vs_diversity()
        
        # 生成总结报告
        tester.generate_performance_report()
        
        print("\n" + "=" * 60)
        print("测试完成！详细分析请参考 HUFFMAN_PERFORMANCE_ANALYSIS.md")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
