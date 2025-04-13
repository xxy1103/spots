from module.Spot_class import spotManager as spot
from module.user_class import userManager

if __name__ == "__main__":
# 获取每个类型前10个景点并保存索引

    # 获取"自然风光"类型的前10个评分最高的景点
    a = natural_spots = spot.getTopKByType("历史建筑")
    print(a)

    # 获取"历史古迹"类型的前5个评分最高的景点
    b = historical_spots = spot.getTopKByType("历史古迹", 5)
    print(b)

    # 获取所有景点并排序
    all_sorted = spot.getAllSpotsSorted()
    print("\nAll spots sorted by score and visited time:")
    # 打印前几个看看效果
    for s in all_sorted[:5]: 
        print(f"ID: {s['id']}, Name: {s['name']}, Score: {s['score']}, Visited: {s['visited_time']}")

    # 获取所有景点并按访问次数排序
    all_sorted_by_visited_time = spot.getAllSortedByVisitedTime()
    # 打印前几个看看效果
    print("\nAll spots sorted by visited time:")
    for s in all_sorted_by_visited_time[:5]: 
        print(f"ID: {s['id']}, Name: {s['name']}, Score: {s['score']}, Visited: {s['visited_time']}")

    