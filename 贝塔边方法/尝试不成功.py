# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 17:30:50 2025

@author: kunla1ve
"""



import networkx as nx

def longest_path_networkx(edges):
    # 创建有向图
    G = nx.DiGraph()
    # 添加带权重的边
    G.add_weighted_edges_from(edges)
    try:
        # 寻找最长路径
        path = nx.dag_longest_path(G, weight='weight')
        # 计算最长路径长度
        length = nx.dag_longest_path_length(G, weight='weight')
        return length, path
    except nx.NetworkXUnfeasible:
        # 如果图中存在环，返回空值
        return None, None

def reduce_path_cost(edges, node_costs, reductions_needed):
    # 初始化总成本和缩减顺序列表
    total_cost = 0
    reduction_sequence = []
    # 创建节点缩减限制字典
    reduction_limits = {node: limit for node, cost, limit in node_costs}
    # 创建节点成本字典
    node_cost_dict = {node: cost for node, cost, limit in node_costs}

    while reductions_needed > 0:
        # 查找当前最长路径
        current_length, current_path = longest_path_networkx(edges)
        if current_length is None:
            break

        # 计算当前路径中每个节点的缩减成本
        possible_reductions = []
        for node in current_path:
            if reduction_limits[node] > 0:
                possible_reductions.append((node_cost_dict[node], node))

        # 按成本排序可能的缩减节点
        possible_reductions.sort()

        # 尝试通过选择最便宜的选项来减少路径长度
        for cost, node in possible_reductions:
            if reduction_limits[node] > 0:
                reduction_sequence.append(node)
                total_cost += cost
                reduction_limits[node] -= 1
                reductions_needed -= 1
                break

        # 如果需要一次减少多个节点
        if reductions_needed > 0:
            # 尝试节点组合
            for i in range(len(possible_reductions)):
                for j in range(i + 1, len(possible_reductions)):
                    node1 = possible_reductions[i][1]
                    node2 = possible_reductions[j][1]
                    if reduction_limits[node1] > 0 and reduction_limits[node2] > 0:
                        reduction_sequence.append([node1, node2])
                        total_cost += node_cost_dict[node1] + node_cost_dict[node2]
                        reduction_limits[node1] -= 1
                        reduction_limits[node2] -= 1
                        reductions_needed -= 2
                        break
                if reductions_needed <= 0:
                    break

    return total_cost, reduction_sequence

edges = [
    ('A', 'B', 9), ('A', 'C', 9), ('B', 'E', 5), ('C', 'D', 3),
    ('C', 'F', 3), ('D', 'E', 6), ('E', 'G', 4), ('F', 'G', 7),
    ('F', 'H', 7), ('G', 'I', 5), ('H', 'I', 6), ('I', 'I+', 8)
]

node_costs = [
    ('A', 5000, 3), ('B', 1500, 2), ('C', 4500, 1), ('D', 2000, 2),
    ('E', 2500, 2), ('F', 2500, 3), ('G', 4000, 1), ('H', 1000, 4),
    ('I', 6000, 3), ('I+', 100, 0)
]

reductions_needed = 4
total_cost, reduction_sequence = reduce_path_cost(edges, node_costs, reductions_needed)

print(f"总成本: {total_cost}")
print(f"缩减顺序: {reduction_sequence}")  # 输出最终的总成本和节点缩减顺序