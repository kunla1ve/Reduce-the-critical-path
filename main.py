# -*- coding: utf-8 -*-
"""
关键路径减少算法 - 主程序
合并了阿尔法节点方法和贝塔边方法的统一实现
"""

from common import run_critical_path_reduction


def example_alpha():
    """
    阿尔法示例 - 基于activities字典的数据
    使用起点A和终点I
    """
    print("\n" + "="*70)
    print("阿尔法示例：项目管理场景")
    print("="*70)
    
    # 活动数据
    activities = {
        'A': {'predecessors': [], 'time': 9, 'cost': 5000, 'limit': 3},
        'B': {'predecessors': ['A'], 'time': 5, 'cost': 1500, 'limit': 2},
        'C': {'predecessors': ['A'], 'time': 3, 'cost': 4500, 'limit': 1},
        'D': {'predecessors': ['C'], 'time': 6, 'cost': 2000, 'limit': 2},
        'E': {'predecessors': ['B', 'D'], 'time': 4, 'cost': 2500, 'limit': 2},
        'F': {'predecessors': ['C'], 'time': 7, 'cost': 2500, 'limit': 3},
        'G': {'predecessors': ['E', 'F'], 'time': 5, 'cost': 4000, 'limit': 1},
        'H': {'predecessors': ['F'], 'time': 6, 'cost': 1000, 'limit': 4},
        'I': {'predecessors': ['G', 'H'], 'time': 8, 'cost': 6000, 'limit': 3}
    }
    
    # 从activities生成边列表
    edges = []
    for activity, data in activities.items():
        for predecessor in data['predecessors']:
            edges.append((predecessor, activity, activities[predecessor]['time']))
    
    # 生成节点成本列表
    node_costs = [(activity, data['cost'], data['limit']) 
                  for activity, data in activities.items()]
    
    # 运行算法（指定起点A和终点I）
    result = run_critical_path_reduction(
        edges, 
        node_costs, 
        start='A', 
        end='I',
        verbose=True
    )
    
    return result


def example_beta():
    """
    贝塔示例 - 直接使用边列表的数据
    不指定起点和终点，找全局最长路径
    """
    print("\n" + "="*70)
    print("贝塔示例：通用图场景")
    print("="*70)
    
    # 边列表
    edges = [
        ('A', 'B', 9), ('A', 'C', 9), ('B', 'E', 5), ('C', 'D', 3),
        ('C', 'F', 3), ('D', 'E', 6), ('E', 'G', 4), ('F', 'G', 7),
        ('F', 'H', 7), ('G', 'I', 5), ('H', 'I', 6), ('I', 'I+', 8)
    ]
    
    # 节点成本列表
    node_costs = [
        ('A', 5000, 3), ('B', 1500, 2), ('C', 4500, 1), ('D', 2000, 2),
        ('E', 2500, 2), ('F', 2500, 3), ('G', 4000, 1), ('H', 1000, 4),
        ('I', 6000, 3), ('I+', 100, 0)
    ]
    
    # 运行算法（不指定起点和终点）
    result = run_critical_path_reduction(
        edges, 
        node_costs, 
        verbose=True
    )
    
    return result


def example_simple():
    """
    简单示例 - 用于验证算法正确性
    """
    print("\n" + "="*70)
    print("简单示例：验证算法")
    print("="*70)
    
    # 边列表
    edges = [
        ('A', 'B', 2), ('B', 'D', 5), ('D', 'D+', 3), ('A', 'C', 2),
        ('C', 'D', 4)
    ]
    
    # 节点成本列表
    node_costs = [
        ('A', 4, 1), ('B', 3, 3), ('C', 2, 1), ('D', 2, 2), ('D+', 100, 0)
    ]
    
    # 运行算法
    result = run_critical_path_reduction(
        edges, 
        node_costs, 
        verbose=True
    )
    
    return result


if __name__ == "__main__":
    print("关键路径减少算法演示")
    print("本程序展示了合并后的统一实现")
    
    # 运行三个示例
    print("\n\n" + "#"*70)
    print("示例 1/3: 阿尔法示例（项目管理场景）")
    print("#"*70)
    result_alpha = example_alpha()
    
    print("\n\n" + "#"*70)
    print("示例 2/3: 贝塔示例（通用图场景）")
    print("#"*70)
    result_beta = example_beta()
    
    print("\n\n" + "#"*70)
    print("示例 3/3: 简单示例（验证算法）")
    print("#"*70)
    result_simple = example_simple()
    
    # 总结
    print("\n\n" + "="*70)
    print("所有示例运行完成！")
    print("="*70)
