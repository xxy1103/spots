# -*- coding: utf-8 -*-
"""
大规模测试数据生成器
为景点推荐算法性能测试生成各种规模和复杂度的测试数据
"""

import random
import json
import numpy as np
from datetime import datetime, timedelta
from module.Model.Model import User, Spot
from module.user_class import userManager
from module.Spot_class import spotManager
import module.printLog as log

class TestDataGenerator:
    """测试数据生成器"""
    
    def __init__(self):
        self.spot_types = ['自然风光', '历史文化', '现代建筑', '休闲娱乐', '购物中心', 
                          '美食街区', '艺术博物馆', '体育场馆', '宗教建筑', '科技园区']
        
        self.user_preferences_pool = [
            ['自然风光', '休闲娱乐'],
            ['历史文化', '艺术博物馆'],
            ['现代建筑', '科技园区'],
            ['购物中心', '美食街区'],
            ['体育场馆', '休闲娱乐'],
            ['宗教建筑', '历史文化'],
            ['自然风光', '体育场馆'],
            ['美食街区', '艺术博物馆'],
            ['现代建筑', '购物中心'],
            ['科技园区', '历史文化']
        ]
        
        self.generated_users = []
        self.generated_spots = []
    
    def generate_test_users(self, count=1000, complexity_level='medium'):
        """
        生成测试用户数据
        
        Args:
            count: 用户数量
            complexity_level: 复杂度级别 ('simple', 'medium', 'complex')
        """
        print(f"🧑‍🤝‍🧑 生成 {count} 个测试用户 (复杂度: {complexity_level})")
        
        users = []
        
        for i in range(count):
            user_id = i + 1
            username = f"test_user_{user_id:06d}"
            password = "test123"
            age = random.randint(18, 80)
            gender = random.choice(['male', 'female'])
            
            # 根据复杂度级别设置不同的偏好复杂度
            if complexity_level == 'simple':
                preferences = random.choice(self.user_preferences_pool[:3])
            elif complexity_level == 'medium':
                preferences = random.choice(self.user_preferences_pool)
            else:  # complex
                # 复杂用户可能有更多偏好
                base_prefs = random.choice(self.user_preferences_pool)
                additional_prefs = random.sample(self.spot_types, random.randint(1, 3))
                preferences = list(set(base_prefs + additional_prefs))
            
            # 创建用户对象
            user = User(
                id=user_id,
                username=username,
                password=password,
                age=age,
                gender=gender,
                preferences=preferences
            )
            
            users.append(user)
        
        self.generated_users = users
        print(f"✅ 成功生成 {len(users)} 个用户")
        return users
    
    def generate_test_spots(self, count=5000, complexity_level='medium'):
        """
        生成测试景点数据
        
        Args:
            count: 景点数量
            complexity_level: 复杂度级别
        """
        print(f"🏞️ 生成 {count} 个测试景点 (复杂度: {complexity_level})")
        
        spots = []
        
        # 景点名称模板
        name_templates = [
            "{}公园", "{}博物馆", "{}广场", "{}大厦", "{}商场",
            "{}湖", "{}山", "{}寺", "{}塔", "{}街",
            "{}中心", "{}花园", "{}宫", "{}院", "{}楼"
        ]
        
        # 地名前缀
        location_prefixes = [
            "东方", "西湖", "南山", "北海", "中央", "新华", "人民", "和平",
            "建设", "解放", "青年", "文化", "科技", "未来", "阳光", "明珠",
            "金山", "银河", "碧海", "蓝天", "绿洲", "红旗", "紫禁", "黄金"
        ]
        
        for i in range(count):
            spot_id = i + 1
            
            # 生成景点名称
            prefix = random.choice(location_prefixes)
            template = random.choice(name_templates)
            name = template.format(prefix)
            
            # 随机分配景点类型
            spot_type = random.choice(self.spot_types)
            
            # 根据复杂度级别设置评分分布
            if complexity_level == 'simple':
                # 简单模式：评分相对集中
                score = random.normalvariate(7.5, 1.0)
            elif complexity_level == 'medium':
                # 中等模式：评分分布更广
                score = random.normalvariate(7.0, 1.5)
            else:  # complex
                # 复杂模式：可能有多峰分布
                if random.random() < 0.3:
                    score = random.normalvariate(9.0, 0.5)  # 高分景点
                elif random.random() < 0.6:
                    score = random.normalvariate(6.0, 1.0)  # 中等景点
                else:
                    score = random.normalvariate(4.0, 1.0)  # 低分景点
            
            score = max(1.0, min(10.0, score))  # 限制在1-10范围内
            
            # 生成访问次数（受评分影响）
            base_visits = int(score * 100 + random.normalvariate(0, 50))
            visited_time = max(0, base_visits)
            
            # 生成位置信息
            latitude = 39.9 + random.uniform(-0.5, 0.5)  # 北京附近
            longitude = 116.4 + random.uniform(-0.5, 0.5)
            
            # 生成描述
            descriptions = [
                f"这是一个美丽的{spot_type}，位于城市的中心地带。",
                f"著名的{spot_type}，拥有悠久的历史和独特的文化价值。",
                f"现代化的{spot_type}，提供优质的服务和良好的环境。",
                f"受欢迎的{spot_type}，是市民休闲娱乐的好去处。"
            ]
            description = random.choice(descriptions)
            
            # 创建景点对象
            spot = Spot(
                id=spot_id,
                name=name,
                type=spot_type,
                score=round(score, 1),
                visited_time=visited_time,
                latitude=latitude,
                longitude=longitude,
                description=description
            )
            
            spots.append(spot)
        
        self.generated_spots = spots
        print(f"✅ 成功生成 {len(spots)} 个景点")
        return spots
    
    def generate_user_interaction_data(self, users, spots, interaction_density='medium'):
        """
        生成用户交互数据（访问记录、评分等）
        
        Args:
            users: 用户列表
            spots: 景点列表
            interaction_density: 交互密度 ('low', 'medium', 'high')
        """
        print(f"🔗 生成用户交互数据 (密度: {interaction_density})")
        
        # 根据密度设置每个用户的平均交互次数
        if interaction_density == 'low':
            avg_interactions = 5
        elif interaction_density == 'medium':
            avg_interactions = 15
        else:  # high
            avg_interactions = 30
        
        total_interactions = 0
        
        for user in users:
            # 为每个用户生成交互次数
            num_interactions = max(1, int(random.normalvariate(avg_interactions, avg_interactions * 0.3)))
            
            # 根据用户偏好选择景点
            preferred_spots = [spot for spot in spots if spot.type in user.preferences]
            other_spots = [spot for spot in spots if spot.type not in user.preferences]
            
            # 80%的交互是偏好景点，20%是其他景点
            preferred_count = int(num_interactions * 0.8)
            other_count = num_interactions - preferred_count
            
            selected_spots = []
            
            if preferred_spots and preferred_count > 0:
                selected_spots.extend(random.sample(
                    preferred_spots, 
                    min(preferred_count, len(preferred_spots))
                ))
            
            if other_spots and other_count > 0:
                selected_spots.extend(random.sample(
                    other_spots, 
                    min(other_count, len(other_spots))
                ))
            
            # 为选中的景点生成交互记录
            for spot in selected_spots:
                # 生成访问时间
                visit_date = datetime.now() - timedelta(days=random.randint(1, 365))
                
                # 生成用户评分（偏好景点评分更高）
                if spot.type in user.preferences:
                    user_rating = random.normalvariate(8.0, 1.0)
                else:
                    user_rating = random.normalvariate(6.0, 1.5)
                
                user_rating = max(1.0, min(10.0, user_rating))
                
                # 这里可以扩展存储用户交互数据的逻辑
                total_interactions += 1
        
        print(f"✅ 生成了 {total_interactions} 条用户交互记录")
        return total_interactions
    
    def create_performance_test_scenarios(self):
        """创建性能测试场景"""
        scenarios = {
            'small_scale': {
                'users': 100,
                'spots': 500,
                'complexity': 'simple',
                'interaction_density': 'low',
                'description': '小规模测试：100用户，500景点，简单偏好'
            },
            'medium_scale': {
                'users': 1000,
                'spots': 2000,
                'complexity': 'medium',
                'interaction_density': 'medium',
                'description': '中等规模测试：1000用户，2000景点，中等复杂度'
            },
            'large_scale': {
                'users': 5000,
                'spots': 10000,
                'complexity': 'medium',
                'interaction_density': 'high',
                'description': '大规模测试：5000用户，10000景点，高交互密度'
            },
            'complex_scenario': {
                'users': 2000,
                'spots': 5000,
                'complexity': 'complex',
                'interaction_density': 'high',
                'description': '复杂场景测试：复杂用户偏好，高交互密度'
            },
            'stress_test': {
                'users': 10000,
                'spots': 20000,
                'complexity': 'complex',
                'interaction_density': 'high',
                'description': '压力测试：10000用户，20000景点，最高复杂度'
            }
        }
        
        return scenarios
    
    def setup_test_scenario(self, scenario_name):
        """设置特定的测试场景"""
        scenarios = self.create_performance_test_scenarios()
        
        if scenario_name not in scenarios:
            raise ValueError(f"未知的测试场景: {scenario_name}")
        
        scenario = scenarios[scenario_name]
        print(f"🎯 设置测试场景: {scenario['description']}")
        
        # 生成用户数据
        users = self.generate_test_users(
            count=scenario['users'],
            complexity_level=scenario['complexity']
        )
        
        # 生成景点数据
        spots = self.generate_test_spots(
            count=scenario['spots'],
            complexity_level=scenario['complexity']
        )
        
        # 生成交互数据
        interactions = self.generate_user_interaction_data(
            users=users,
            spots=spots,
            interaction_density=scenario['interaction_density']
        )
        
        return {
            'users': users,
            'spots': spots,
            'interactions': interactions,
            'scenario_info': scenario
        }
    
    def save_test_data(self, data, filename_prefix="test_data"):
        """保存测试数据到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存用户数据
        users_data = [
            {
                'id': user.id,
                'username': user.username,
                'age': user.age,
                'gender': user.gender,
                'preferences': user.preferences
            }
            for user in data['users']
        ]
        
        with open(f"{filename_prefix}_users_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
        
        # 保存景点数据
        spots_data = [
            {
                'id': spot.id,
                'name': spot.name,
                'type': spot.type,
                'score': spot.score,
                'visited_time': spot.visited_time,
                'latitude': getattr(spot, 'latitude', 0),
                'longitude': getattr(spot, 'longitude', 0),
                'description': getattr(spot, 'description', '')
            }
            for spot in data['spots']
        ]
        
        with open(f"{filename_prefix}_spots_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(spots_data, f, ensure_ascii=False, indent=2)
        
        # 保存场景信息
        scenario_info = {
            'scenario': data['scenario_info'],
            'statistics': {
                'total_users': len(data['users']),
                'total_spots': len(data['spots']),
                'total_interactions': data['interactions'],
                'generation_time': timestamp
            }
        }
        
        with open(f"{filename_prefix}_scenario_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(scenario_info, f, ensure_ascii=False, indent=2)
        
        print(f"📁 测试数据已保存，前缀: {filename_prefix}_{timestamp}")
        return timestamp
    
    def generate_all_test_scenarios(self):
        """生成所有测试场景的数据"""
        scenarios = self.create_performance_test_scenarios()
        
        print("🔄 开始生成所有测试场景数据...")
        
        for scenario_name, scenario_info in scenarios.items():
            print(f"\n📋 生成场景: {scenario_name}")
            
            try:
                data = self.setup_test_scenario(scenario_name)
                self.save_test_data(data, f"scenario_{scenario_name}")
                print(f"✅ 场景 {scenario_name} 数据生成完成")
            except Exception as e:
                print(f"❌ 场景 {scenario_name} 数据生成失败: {e}")
        
        print("\n🎉 所有测试场景数据生成完成！")

def main():
    """主函数"""
    print("大规模测试数据生成器")
    print("="*60)
    
    generator = TestDataGenerator()
    
    # 生成所有测试场景
    generator.generate_all_test_scenarios()
    
    # 也可以单独生成特定场景
    # data = generator.setup_test_scenario('large_scale')
    # generator.save_test_data(data, "large_scale_test")

if __name__ == "__main__":
    main()
