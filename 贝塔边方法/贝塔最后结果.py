# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 13:28:06 2025

@author: kunla1ve
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 22:06:00 2025

@author: kunla1ve
"""

import networkx as nx
from collections import defaultdict
import copy

# 您的原始函数保持不变
def find_all_longest_paths(edges):
    G = nx.DiGraph()
    G.add_weighted_edges_from(edges)
    
    try:
        # 先计算最长路径的长度
        max_length = nx.dag_longest_path_length(G, weight='weight')

        # 找到所有可能的路径，并筛选出长度等于 max_length 的
        all_paths = []
        for source in G.nodes():
            for target in G.nodes():
                if source != target:
                    for path in nx.all_simple_paths(G, source, target):
                        path_length = sum(G[u][v]['weight'] for u, v in zip(path[:-1], path[1:]))
                        if path_length == max_length:
                            all_paths.append((path_length, path))
        
        # 去重（因为可能重复添加）
        unique_paths = []
        seen = set()
        for length, path in all_paths:
            tuple_path = tuple(path)
            if tuple_path not in seen:
                seen.add(tuple_path)
                unique_paths.append((length, path))
        
        # 如果没有路径，返回None
        if not unique_paths:
            return None
        
        # 创建数据结构存储结果
        result = {
            'max_length': max_length,
            'paths': [],
            'common_nodes': set()
        }
        
        # 找出所有路径共有的节点
        for node in G.nodes():
            if all(node in path for _, path in unique_paths):
                result['common_nodes'].add(node)
        
        # 为每条路径计算 unique_nodes (Full path - Common nodes)
        for i, (length, path) in enumerate(unique_paths):
            path_info = {
                'path_id': i+1,
                'path': path,
                'length': length,
                'unique_nodes': [node for node in path if node not in result['common_nodes']]
            }
            result['paths'].append(path_info)
        
        return result
    except nx.NetworkXUnfeasible:
        return None

def find_nodes_to_remove(result, node_costs):
    if not result:
        return [], 0
    
    # 创建节点成本字典
    node_cost_dict = {node: (cost, limit) for node, cost, limit in node_costs}
    
    # 找出所有候选节点（在所有路径中出现的节点）
    all_path_nodes = set()
    for path_info in result['paths']:
        all_path_nodes.update(path_info['path'])
    candidate_nodes = all_path_nodes
    
    # 找出公共节点中的最小成本节点
    common_nodes = result['common_nodes']
    common_candidates = [node for node in common_nodes if node_cost_dict[node][1] > 0]
    if common_candidates:
        min_common_node = min(common_candidates, key=lambda x: node_cost_dict[x][0])
        min_common_cost = node_cost_dict[min_common_node][0]
    else:
        min_common_node = None
        min_common_cost = float('inf')
    
    # 找出每条路径中unique节点的最小成本节点
    unique_min_nodes = []
    total_unique_cost = 0
    for path_info in result['paths']:
        unique_nodes = [node for node in path_info['unique_nodes'] if node_cost_dict[node][1] > 0]
        if unique_nodes:
            min_node = min(unique_nodes, key=lambda x: node_cost_dict[x][0])
            unique_min_nodes.append(min_node)
            total_unique_cost += node_cost_dict[min_node][0]
        else:
            # 如果没有可移除的unique节点，则必须移除公共节点
            unique_min_nodes = None
            break
    
    # 比较两种策略的成本
    if unique_min_nodes and total_unique_cost < min_common_cost:
        return unique_min_nodes, total_unique_cost
    elif min_common_node:
        return [min_common_node], min_common_cost
    else:
        # 如果没有可移除的节点（所有限制为0），返回空列表
        return [], 0

# 初始数据
original_edges = [
    ('A', 'B', 2), ('B', 'D', 5), ('D', 'D+', 3), ('A', 'C', 2),
    ('C', 'D', 4)
]

original_node_costs = [
    ('A', 4, 1), ('B', 3, 3), ('C', 2, 1), ('D', 2, 2), ('D+', 100, 0)
]

# 创建可修改的副本
edges = copy.deepcopy(original_edges)
node_costs = copy.deepcopy(original_node_costs)

# 初始化变量用于收集结果
all_recommended_nodes = []
total_cost = 0

# 执行循环直到无法再减少最长路径
while True:
    result = find_all_longest_paths(edges)
    if not result:
        break
    
    nodes_to_remove, iteration_cost = find_nodes_to_remove(result, node_costs)
    if not nodes_to_remove:
        break
    
    all_recommended_nodes.append(nodes_to_remove)
    total_cost += iteration_cost
    
    # 更新节点限制
    for i, (node, cost, limit) in enumerate(node_costs):
        if node in nodes_to_remove:
            new_limit = max(0, limit - 1)
            node_costs[i] = (node, cost, new_limit)
    
    # 更新边权重
    for i, (u, v, w) in enumerate(edges):
        if u in nodes_to_remove:
            new_weight = max(0, w - 1)
            edges[i] = (u, v, new_weight)

# 计算原始最长路径长度
original_G = nx.DiGraph()
original_G.add_weighted_edges_from(original_edges)
original_max_length = nx.dag_longest_path_length(original_G, weight='weight')

# 最终结果
final_result = find_all_longest_paths(edges)
if final_result:
    print("=== Final Result ===")
    print(f"Final maximum path length: {final_result['max_length']}")
    print(f"Total reduction: {original_max_length - final_result['max_length']} (from original {original_max_length})")
    print(f"All recommended nodes to remove: {all_recommended_nodes}")
    print(f"Total cost: {total_cost}")
else:
    print("The graph contains a cycle.")
    
    
    
    

# === Iteration 1 ===
# Current maximum path length: 10
# Recommended nodes to remove: ['D']
# Cost per Iteration: 2
# Updated node D: limit decreased to 1
# Updated edge D->D+: weight decreased to 2

# === Iteration 2 ===
# Current maximum path length: 9
# Recommended nodes to remove: ['D']
# Cost per Iteration: 2
# Updated node D: limit decreased to 0
# Updated edge D->D+: weight decreased to 1

# === Iteration 3 ===
# Current maximum path length: 8
# Recommended nodes to remove: ['B']
# Cost per Iteration: 3
# Updated node B: limit decreased to 2
# Updated edge B->D: weight decreased to 4

# === Iteration 4 ===
# Current maximum path length: 7
# Recommended nodes to remove: ['A']
# Cost per Iteration: 4
# Updated node A: limit decreased to 0
# Updated edge A->B: weight decreased to 1
# Updated edge A->C: weight decreased to 1

# === Iteration 5 ===
# Current maximum path length: 6
# Recommended nodes to remove: ['B', 'C']
# Cost per Iteration: 5
# Updated node B: limit decreased to 1
# Updated node C: limit decreased to 0
# Updated edge B->D: weight decreased to 3
# Updated edge C->D: weight decreased to 3

# === Final Result ===
# Final maximum path length: 5
# Total reduction: 30 (from original 35)
# All recommended nodes to remove: [['D'], ['D'], ['B'], ['A'], ['B', 'C']]
# Total cost: 16
    