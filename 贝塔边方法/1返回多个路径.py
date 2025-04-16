# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 16:59:51 2025

@author: kunla1ve
"""

import networkx as nx

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
        
        return unique_paths
    except nx.NetworkXUnfeasible:
        return None

edges = [
    ('A', 'B', 9), ('A', 'C', 9), ('B', 'E', 5), ('C', 'D', 3),
    ('C', 'F', 3), ('D', 'E', 4),  # 修改为4
    ('E', 'G', 4), ('F', 'G', 7),
    ('F', 'H', 7), ('G', 'I', 5), ('H', 'I', 6), ('I', 'I+', 8)
]

result = find_all_longest_paths(edges)
if result:
    for length, path in result:
        print(f"Length: {length}, Path: {path}")
else:
    print("The graph contains a cycle.")