# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 13:23:11 2025

@author: kunla1ve
"""

import networkx as nx
from collections import defaultdict
import copy

# 更新后的 activities 数据结构，包含您提供的 cost 和 limit 值
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

# 从 activities 生成 original_edges
original_edges = []
for activity, data in activities.items():
    for predecessor in data['predecessors']:
        original_edges.append((predecessor, activity, activities[predecessor]['time']))

# 从 activities 生成 original_node_costs
original_node_costs = []
for activity, data in activities.items():
    original_node_costs.append((activity, data['cost'], data['limit']))

def find_all_longest_paths(edges):
    G = nx.DiGraph()
    G.add_weighted_edges_from(edges)
    
    try:
        max_length = nx.dag_longest_path_length(G, weight='weight')
        all_paths = []
        for source in G.nodes():
            for target in G.nodes():
                if source != target:
                    for path in nx.all_simple_paths(G, source, target):
                        path_length = sum(G[u][v]['weight'] for u, v in zip(path[:-1], path[1:]))
                        if path_length == max_length:
                            all_paths.append((path_length, path))
        
        unique_paths = []
        seen = set()
        for length, path in all_paths:
            tuple_path = tuple(path)
            if tuple_path not in seen:
                seen.add(tuple_path)
                unique_paths.append((length, path))
        
        if not unique_paths:
            return None
        
        result = {
            'max_length': max_length,
            'paths': [],
            'common_nodes': set()
        }
        
        for node in G.nodes():
            if all(node in path for _, path in unique_paths):
                result['common_nodes'].add(node)
        
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
    
    node_cost_dict = {node: (cost, limit) for node, cost, limit in node_costs}
    all_path_nodes = set()
    for path_info in result['paths']:
        all_path_nodes.update(path_info['path'])
    
    common_nodes = result['common_nodes']
    common_candidates = [node for node in common_nodes if node_cost_dict[node][1] > 0]
    if common_candidates:
        min_common_node = min(common_candidates, key=lambda x: node_cost_dict[x][0])
        min_common_cost = node_cost_dict[min_common_node][0]
    else:
        min_common_node = None
        min_common_cost = float('inf')
    
    unique_min_nodes = []
    total_unique_cost = 0
    for path_info in result['paths']:
        unique_nodes = [node for node in path_info['unique_nodes'] if node_cost_dict[node][1] > 0]
        if unique_nodes:
            min_node = min(unique_nodes, key=lambda x: node_cost_dict[x][0])
            unique_min_nodes.append(min_node)
            total_unique_cost += node_cost_dict[min_node][0]
        else:
            unique_min_nodes = None
            break
    
    if unique_min_nodes and total_unique_cost < min_common_cost:
        return unique_min_nodes, total_unique_cost
    elif min_common_node:
        return [min_common_node], min_common_cost
    else:
        return [], 0

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