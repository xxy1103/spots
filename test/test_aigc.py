#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIGC类使用示例
演示如何使用AIGC类进行图片到视频的完整工作流
"""

import sys
import os
# 导入AIGC类
from module.AIGC import AIGC

def test_aigc_workflow():
    """测试AIGC完整工作流"""
    try:
        # 创建AIGC实例
        print("正在初始化AIGC...")
        aigc = AIGC()
        
        # 测试图片路径（请替换为实际存在的图片路径）
        test_image_path = "data/scenic_spots/spot_1/images/0_0.jpg"

        if not os.path.exists(test_image_path):
            print(f"测试图片不存在: {test_image_path}")
            print("请提供一个有效的图片路径")
            return
        
        print(f"使用测试图片: {test_image_path}")
        
        # 方案1：使用自动生成的提示词
        print("\n=== 方案1：自动生成提示词 ===")
        result1 = aigc.generate_video_complete_workflow(test_image_path)
        
        if result1["success"]:
            print("✓ 自动生成提示词方案成功")
            print(f"  任务ID: {result1['task_id']}")
            print(f"  生成的提示词: {result1['prompt']}")
        else:
            print("✗ 自动生成提示词方案失败")
            print(f"  错误: {result1['error']}")
        
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")

if __name__ == "__main__":
    print("AIGC类测试程序")
    print("=" * 50)
    
    # 检查环境变量
    if not os.getenv("volcengine_api_key"):
        print("警告: 环境变量 'volcengine_api_key' 未设置")
        print("请确保已正确配置 .env 文件")
        print("参考 .env.example 文件进行配置")
        print()
        
    
    # 执行测试
    try:
        # 测试提示词生成
        #test_prompt_generation_only()
        
        # 测试完整工作流
        test_aigc_workflow()
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试执行失败: {e}")
    
    print("\n测试完成")
