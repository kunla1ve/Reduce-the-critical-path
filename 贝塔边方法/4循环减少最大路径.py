# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 21:10:42 2025

@author: kunlave
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
    ('A', 'B', 9), ('A', 'C', 9), ('B', 'E', 5), ('C', 'D', 3),
    ('C', 'F', 3), ('D', 'E', 6), ('E', 'G', 4), ('F', 'G', 7),
    ('F', 'H', 7), ('G', 'I', 5), ('H', 'I', 6), ('I', 'I+', 8)
]

original_node_costs = [
    ('A', 5000, 3), ('B', 1500, 2), ('C', 4500, 1), ('D', 2000, 2),
    ('E', 2500, 2), ('F', 2500, 3), ('G', 4000, 1), ('H', 1000, 4),
    ('I', 6000, 3), ('I+', 100, 0)
]

# 创建可修改的副本
edges = copy.deepcopy(original_edges)
node_costs = copy.deepcopy(original_node_costs)

# 初始化变量用于收集结果
all_recommended_nodes = []
total_cost = 0

# 执行4次循环
for iteration in range(1, 100):
    print(f"\n=== Iteration {iteration} ===")
    
    # 执行函数
    result = find_all_longest_paths(edges)
    if result:
        print(f"Current maximum path length: {result['max_length']}")
        
        nodes_to_remove, iteration_cost = find_nodes_to_remove(result, node_costs)
        print(f"Recommended nodes to remove: {nodes_to_remove}")
        print(f"Cost per Iteration: {iteration_cost}")
        
        if not nodes_to_remove:
            print("No more nodes can be removed (all limits reached).")
            break
        
        # 记录推荐节点和总成本
        all_recommended_nodes.append(nodes_to_remove)
        total_cost += iteration_cost
        
        # 更新节点限制
        for i, (node, cost, limit) in enumerate(node_costs):
            if node in nodes_to_remove:
                new_limit = max(0, limit - 1)
                node_costs[i] = (node, cost, new_limit)
                print(f"Updated node {node}: limit decreased to {new_limit}")
        
        # 更新边权重（移除从推荐节点出发的边）
        for i, (u, v, w) in enumerate(edges):
            if u in nodes_to_remove:
                new_weight = max(0, w - 1)
                edges[i] = (u, v, new_weight)
                print(f"Updated edge {u}->{v}: weight decreased to {new_weight}")
    else:
        print("The graph contains a cycle.")
        break

# 最终结果
print("\n=== Final Result ===")
result = find_all_longest_paths(edges)
if result:
    print(f"Final maximum path length: {result['max_length']}")
    print(f"Total reduction: {35 - result['max_length']} (from original 35)")
    print(f"All recommended nodes to remove: {all_recommended_nodes}")
    print(f"Total cost: {total_cost}")
else:
    print("The graph contains a cycle.")