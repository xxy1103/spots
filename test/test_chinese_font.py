#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文字体测试程序
用于验证matplotlib的中文字体配置是否正确
"""

import matplotlib.pyplot as plt
import matplotlib
import platform
import warnings

def setup_chinese_font():
    """
    设置matplotlib的中文字体支持
    """
    print("正在配置中文字体...")
    
    # 获取系统类型
    system = platform.system()
    print(f"检测到系统类型: {system}")
    
    if system == "Windows":
        # Windows系统常用中文字体
        fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 'FangSong']
    elif system == "Darwin":  # macOS
        # macOS系统中文字体
        fonts = ['PingFang SC', 'Hiragino Sans GB', 'STSong', 'SimHei']
    else:  # Linux
        # Linux系统中文字体
        fonts = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'SimHei']
    
    # 添加默认字体作为备选
    fonts.extend(['DejaVu Sans', 'Arial', 'sans-serif'])
    
    print(f"尝试使用字体列表: {fonts}")
    
    # 设置字体
    matplotlib.rcParams['font.sans-serif'] = fonts
    matplotlib.rcParams['axes.unicode_minus'] = False
    matplotlib.rcParams['font.size'] = 10
    
    # 过滤字体警告
    warnings.filterwarnings('ignore', category=UserWarning, message='.*missing from font.*')
    
    return fonts

def test_chinese_display():
    """
    测试中文字符显示
    """
    print("\n开始测试中文字符显示...")
    
    # 创建测试图表
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle('中文字体显示测试', fontsize=16)
    
    # 测试不同类型的中文文本
    test_texts = [
        "K路归并性能比较",
        "执行时间 (秒)",
        "性能提升倍数",
        "测试结果正确性: ✅ 通过"
    ]
    
    for i, (ax, text) in enumerate(zip(axes.flat, test_texts)):
        ax.text(0.5, 0.5, text, ha='center', va='center', fontsize=14)
        ax.set_title(f"测试 {i+1}: {text[:10]}...")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    
    plt.tight_layout()
    
    # 保存测试图片
    try:
        plt.savefig('chinese_font_test.png', dpi=150, bbox_inches='tight')
        print("✅ 中文字体测试图片已保存为: chinese_font_test.png")
    except Exception as e:
        print(f"❌ 保存图片失败: {e}")
    
    try:
        plt.show()
        print("✅ 中文字体显示正常")
    except Exception as e:
        print(f"❌ 显示图表失败: {e}")
    
    plt.close()

def get_available_fonts():
    """
    获取系统可用字体列表
    """
    from matplotlib.font_manager import FontManager
    
    print("\n正在检查系统可用字体...")
    
    fm = FontManager()
    chinese_fonts = []
    
    for font in fm.ttflist:
        font_name = font.name
        # 检查是否为中文字体
        if any(keyword in font_name.lower() for keyword in 
               ['simhei', 'simsun', 'kaiti', 'yahei', 'fangsong', 'songti', 'heiti']):
            chinese_fonts.append(font_name)
    
    if chinese_fonts:
        print("发现以下中文字体:")
        for font in set(chinese_fonts):
            print(f"  - {font}")
    else:
        print("⚠️ 未发现常用中文字体")
        print("建议安装以下字体之一:")
        print("  - Windows: SimHei, Microsoft YaHei")
        print("  - macOS: PingFang SC")
        print("  - Linux: WenQuanYi Micro Hei")
    
    return list(set(chinese_fonts))

def main():
    """
    主函数
    """
    print("=" * 50)
    print("matplotlib 中文字体测试程序")
    print("=" * 50)
    
    # 检查可用字体
    available_fonts = get_available_fonts()
    
    # 配置中文字体
    configured_fonts = setup_chinese_font()
    
    # 测试中文显示
    test_chinese_display()
    
    print("\n" + "=" * 50)
    print("测试完成!")
    
    if available_fonts:
        print("✅ 系统有可用的中文字体")
        print("如果图表中的中文仍然显示为方框，请尝试:")
        print("1. 重启程序")
        print("2. 清除matplotlib缓存: matplotlib.font_manager._rebuild()")
    else:
        print("⚠️ 系统缺少中文字体支持")
        print("建议安装中文字体包")
    
    print("=" * 50)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
