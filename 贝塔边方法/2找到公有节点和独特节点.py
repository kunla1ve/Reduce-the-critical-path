# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 17:05:59 2025

@author: kunla1ve
"""


import networkx as nx
from collections import defaultdict

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

edges = [
    ('A', 'B', 9), ('A', 'C', 9), ('B', 'E', 5), ('C', 'D', 3),
    ('C', 'F', 3), ('D', 'E', 4),  # 修改为4
    ('E', 'G', 3), ('F', 'G', 7),
    ('F', 'H', 7), ('G', 'I', 5), ('H', 'I', 5), ('I', 'I+', 8)
]

result = find_all_longest_paths(edges)
if result:
    print(f"Maximum path length: {result['max_length']}")
    print(f"Common nodes in all paths: {sorted(result['common_nodes'])}")
    print("\nDetails of each path:")
    for path_info in result['paths']:
        print(f"\nPath {path_info['path_id']}:")
        print(f"Full path: {path_info['path']}")
        print(f"Unique nodes in this path: {path_info['unique_nodes']}")
else:
    print("The graph contains a cycle.")
    
    
    
    
    