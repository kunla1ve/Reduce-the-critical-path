# -*- coding: utf-8 -*-
"""
公共模块 - 关键路径减少算法的核心函数
合并了阿尔法节点方法和贝塔边方法
"""

import networkx as nx
import copy
from typing import List, Tuple, Dict, Set, Optional


def validate_graph(edges: List[Tuple[str, str, int]], 
                   node_costs: List[Tuple[str, int, int]]) -> None:
    """
    验证图的有效性
    
    Args:
        edges: 边列表 [(u, v, weight), ...]
        node_costs: 节点成本列表 [(node, cost, limit), ...]
    
    Raises:
        ValueError: 图不是DAG或数据不匹配
    """
    G = nx.DiGraph()
    G.add_weighted_edges_from(edges)
    
    # 检查是否为DAG
    if not nx.is_directed_acyclic_graph(G):
        raise ValueError("图必须是有向无环图(DAG)")
    
    # 检查节点成本数据完整性
    nodes_in_edges = set()
    for u, v, _ in edges:
        nodes_in_edges.add(u)
        nodes_in_edges.add(v)
    
    nodes_in_costs = {node for node, _, _ in node_costs}
    
    if nodes_in_edges != nodes_in_costs:
        missing_in_costs = nodes_in_edges - nodes_in_costs
        missing_in_edges = nodes_in_costs - nodes_in_edges
        error_msg = "边中的节点与节点成本数据不匹配"
        if missing_in_costs:
            error_msg += f"\n  缺少成本数据的节点: {missing_in_costs}"
        if missing_in_edges:
            error_msg += f"\n  在边中不存在的节点: {missing_in_edges}"
        raise ValueError(error_msg)


def find_all_longest_paths(edges: List[Tuple[str, str, int]], 
                          start: Optional[str] = None,
                          end: Optional[str] = None) -> Optional[Dict]:
    """
    找到图中所有最长路径
    
    Args:
        edges: 边列表 [(u, v, weight), ...]
        start: 起点节点（可选）
        end: 终点节点（可选）
    
    Returns:
        包含最长路径信息的字典，或None（如果图中有环）
        {
            'max_length': 最长路径长度,
            'paths': [{
                'path_id': 路径ID,
                'path': 路径节点列表,
                'length': 路径长度,
                'unique_nodes': 独特节点列表
            }, ...],
            'common_nodes': 所有路径共有的节点集合
        }
    """
    G = nx.DiGraph()
    G.add_weighted_edges_from(edges)
    
    try:
        # 计算最长路径长度
        if start and end:
            # 如果指定了起点和终点，计算两点间的最长路径
            max_length = _longest_path_between(G, start, end)
        else:
            # 否则计算全局最长路径
            max_length = nx.dag_longest_path_length(G, weight='weight')
        
        # 找到所有最长路径
        all_paths = []
        
        if start and end:
            # 只找起点到终点的路径
            for path in nx.all_simple_paths(G, start, end):
                path_length = sum(G[u][v]['weight'] for u, v in zip(path[:-1], path[1:]))
                if path_length == max_length:
                    all_paths.append((path_length, path))
        else:
            # 找所有节点对之间的最长路径
            for source in G.nodes():
                for target in G.nodes():
                    if source != target:
                        for path in nx.all_simple_paths(G, source, target):
                            path_length = sum(G[u][v]['weight'] for u, v in zip(path[:-1], path[1:]))
                            if path_length == max_length:
                                all_paths.append((path_length, path))
        
        # 去重
        unique_paths = []
        seen = set()
        for length, path in all_paths:
            tuple_path = tuple(path)
            if tuple_path not in seen:
                seen.add(tuple_path)
                unique_paths.append((length, path))
        
        if not unique_paths:
            return None
        
        # 创建结果数据结构
        result = {
            'max_length': max_length,
            'paths': [],
            'common_nodes': set()
        }
        
        # 找出所有路径共有的节点
        for node in G.nodes():
            if all(node in path for _, path in unique_paths):
                result['common_nodes'].add(node)
        
        # 为每条路径计算独特节点
        for i, (length, path) in enumerate(unique_paths):
            path_info = {
                'path_id': i + 1,
                'path': path,
                'length': length,
                'unique_nodes': [node for node in path if node not in result['common_nodes']]
            }
            result['paths'].append(path_info)
        
        return result
    
    except nx.NetworkXUnfeasible:
        return None


def _longest_path_between(G: nx.DiGraph, start: str, end: str) -> int:
    """
    计算两点间的最长路径长度（使用动态规划）
    
    Args:
        G: 有向无环图
        start: 起点
        end: 终点
    
    Returns:
        最长路径长度
    """
    # 拓扑排序
    topo_order = list(nx.topological_sort(G))
    
    # 初始化距离
    dist = {node: float('-inf') for node in G.nodes()}
    dist[start] = 0
    
    # 动态规划
    for u in topo_order:
        if dist[u] != float('-inf'):
            for v in G.successors(u):
                dist[v] = max(dist[v], dist[u] + G[u][v]['weight'])
    
    return dist[end]


def find_nodes_to_remove(result: Dict, 
                        node_costs: List[Tuple[str, int, int]]) -> Tuple[List[str], int]:
    """
    确定要移除的节点，以最小化成本减少最长路径
    
    策略比较：
    1. 移除所有路径共有的最便宜节点
    2. 移除每条路径独特节点中的最便宜节点
    
    Args:
        result: find_all_longest_paths的返回结果
        node_costs: 节点成本列表 [(node, cost, limit), ...]
    
    Returns:
        (要移除的节点列表, 总成本)
    """
    if not result:
        return [], 0
    
    # 创建节点成本字典
    node_cost_dict = {node: (cost, limit) for node, cost, limit in node_costs}
    
    # 策略1：找公共节点中的最小成本节点
    common_nodes = result['common_nodes']
    common_candidates = [node for node in common_nodes if node_cost_dict[node][1] > 0]
    
    if common_candidates:
        min_common_node = min(common_candidates, key=lambda x: node_cost_dict[x][0])
        min_common_cost = node_cost_dict[min_common_node][0]
    else:
        min_common_node = None
        min_common_cost = float('inf')
    
    # 策略2：找每条路径独特节点中的最小成本节点
    unique_min_nodes = []
    total_unique_cost = 0
    
    for path_info in result['paths']:
        unique_nodes = [node for node in path_info['unique_nodes'] 
                       if node_cost_dict[node][1] > 0]
        
        if unique_nodes:
            min_node = min(unique_nodes, key=lambda x: node_cost_dict[x][0])
            unique_min_nodes.append(min_node)
            total_unique_cost += node_cost_dict[min_node][0]
        else:
            # 如果某条路径没有可移除的独特节点，则必须移除公共节点
            unique_min_nodes = None
            break
    
    # 选择成本更低的策略
    if unique_min_nodes and total_unique_cost < min_common_cost:
        return unique_min_nodes, total_unique_cost
    elif min_common_node:
        return [min_common_node], min_common_cost
    else:
        # 所有节点的限制都为0，无法移除
        return [], 0


def update_graph_state(edges: List[Tuple[str, str, int]],
                      node_costs: List[Tuple[str, int, int]],
                      nodes_to_remove: List[str]) -> Tuple[List[Tuple[str, str, int]], 
                                                           List[Tuple[str, int, int]]]:
    """
    更新图状态：减少被移除节点的限制和相关边的权重
    
    Args:
        edges: 当前边列表
        node_costs: 当前节点成本列表
        nodes_to_remove: 要移除的节点列表
    
    Returns:
        更新后的 (边列表, 节点成本列表)
    """
    # 更新节点限制
    for i, (node, cost, limit) in enumerate(node_costs):
        if node in nodes_to_remove:
            new_limit = max(0, limit - 1)
            node_costs[i] = (node, cost, new_limit)
    
    # 更新边权重（减少从被移除节点出发的边的权重）
    for i, (u, v, w) in enumerate(edges):
        if u in nodes_to_remove:
            new_weight = max(0, w - 1)
            edges[i] = (u, v, new_weight)
    
    return edges, node_costs


def print_iteration_details(iteration: int, 
                           result: Dict,
                           nodes_to_remove: List[str],
                           iteration_cost: int,
                           edges: List[Tuple[str, str, int]],
                           node_costs: List[Tuple[str, int, int]]) -> None:
    """
    打印详细的迭代信息
    
    Args:
        iteration: 迭代次数
        result: find_all_longest_paths的返回结果
        nodes_to_remove: 要移除的节点列表
        iteration_cost: 本次迭代成本
        edges: 当前边列表
        node_costs: 当前节点成本列表
    """
    print(f"\n{'='*60}")
    print(f"迭代 {iteration}")
    print(f"{'='*60}")
    print(f"当前最长路径长度: {result['max_length']}")
    print(f"最长路径数量: {len(result['paths'])}")
    
    # 打印每条路径的详细信息
    for path_info in result['paths']:
        print(f"\n  路径 {path_info['path_id']}: {' -> '.join(path_info['path'])}")
        print(f"    长度: {path_info['length']}")
        print(f"    独特节点: {path_info['unique_nodes'] if path_info['unique_nodes'] else '无'}")
    
    # 打印公共节点
    print(f"\n  公共节点: {sorted(result['common_nodes']) if result['common_nodes'] else '无'}")
    
    # 打印移除决策
    print(f"\n  推荐移除的节点: {nodes_to_remove}")
    print(f"  本次迭代成本: {iteration_cost}")
    
    # 打印状态变化
    print(f"\n  状态更新:")
    for node in nodes_to_remove:
        # 找到节点的新限制
        for n, c, l in node_costs:
            if n == node:
                print(f"    节点 {node}: 限制减少至 {l}")
                break
    
    for u, v, w in edges:
        if u in nodes_to_remove:
            print(f"    边 {u}->{v}: 权重减少至 {w}")


def run_critical_path_reduction(edges: List[Tuple[str, str, int]],
                               node_costs: List[Tuple[str, int, int]],
                               start: Optional[str] = None,
                               end: Optional[str] = None,
                               max_iterations: int = 100,
                               verbose: bool = True) -> Dict:
    """
    运行关键路径减少算法
    
    Args:
        edges: 初始边列表 [(u, v, weight), ...]
        node_costs: 节点成本列表 [(node, cost, limit), ...]
        start: 起点节点（可选）
        end: 终点节点（可选）
        max_iterations: 最大迭代次数
        verbose: 是否打印详细信息
    
    Returns:
        {
            'original_max_length': 原始最长路径长度,
            'final_max_length': 最终最长路径长度,
            'total_reduction': 总减少量,
            'all_recommended_nodes': 所有推荐移除的节点列表,
            'total_cost': 总成本,
            'final_edges': 最终边列表,
            'final_node_costs': 最终节点成本列表
        }
    """
    # 验证输入
    validate_graph(edges, node_costs)
    
    # 保存原始数据
    original_edges = copy.deepcopy(edges)
    original_node_costs = copy.deepcopy(node_costs)
    
    # 创建可修改的副本
    current_edges = copy.deepcopy(edges)
    current_node_costs = copy.deepcopy(node_costs)
    
    # 计算原始最长路径长度
    original_result = find_all_longest_paths(current_edges, start, end)
    if not original_result:
        raise ValueError("无法找到有效路径")
    original_max_length = original_result['max_length']
    
    # 初始化结果变量
    all_recommended_nodes = []
    total_cost = 0
    
    if verbose:
        print(f"\n{'#'*60}")
        print(f"关键路径减少算法")
        print(f"{'#'*60}")
        print(f"原始最长路径长度: {original_max_length}")
        if start and end:
            print(f"起点: {start}, 终点: {end}")
        print(f"最大迭代次数: {max_iterations}")
    
    # 迭代减少关键路径
    for iteration in range(1, max_iterations + 1):
        # 找到当前最长路径
        result = find_all_longest_paths(current_edges, start, end)
        if not result:
            break
        
        # 确定要移除的节点
        nodes_to_remove, iteration_cost = find_nodes_to_remove(result, current_node_costs)
        
        # 如果没有可移除的节点，停止迭代
        if not nodes_to_remove:
            if verbose:
                print(f"\n{'='*60}")
                print(f"迭代 {iteration}: 无法继续减少（所有节点限制已用完）")
                print(f"{'='*60}")
            break
        
        # 记录推荐节点和成本
        all_recommended_nodes.append(nodes_to_remove)
        total_cost += iteration_cost
        
        # 打印迭代详情
        if verbose:
            print_iteration_details(iteration, result, nodes_to_remove, 
                                   iteration_cost, current_edges, current_node_costs)
        
        # 更新图状态
        current_edges, current_node_costs = update_graph_state(
            current_edges, current_node_costs, nodes_to_remove
        )
    
    # 计算最终结果
    final_result = find_all_longest_paths(current_edges, start, end)
    final_max_length = final_result['max_length'] if final_result else 0
    
    # 打印最终结果
    if verbose:
        print(f"\n{'#'*60}")
        print(f"最终结果")
        print(f"{'#'*60}")
        print(f"原始最长路径长度: {original_max_length}")
        print(f"最终最长路径长度: {final_max_length}")
        print(f"总减少量: {original_max_length - final_max_length}")
        print(f"总成本: {total_cost}")
        print(f"\n推荐移除节点序列:")
        for i, nodes in enumerate(all_recommended_nodes, 1):
            print(f"  迭代 {i}: {nodes}")
    
    return {
        'original_max_length': original_max_length,
        'final_max_length': final_max_length,
        'total_reduction': original_max_length - final_max_length,
        'all_recommended_nodes': all_recommended_nodes,
        'total_cost': total_cost,
        'final_edges': current_edges,
        'final_node_costs': current_node_costs
    }
