from __future__ import annotations

import math

import networkx as nx
import pandas as pd


def calculate_centrality(graph: nx.Graph) -> pd.DataFrame:
    if graph.number_of_nodes() == 0:
        return pd.DataFrame(columns=[
            "id", "name", "country", "hub_type", "degree", "closeness",
            "betweenness", "pagerank", "strategic_score",
        ])

    closeness = nx.closeness_centrality(graph, distance="travel_time_h")
    betweenness = nx.betweenness_centrality(graph, weight="travel_time_h", normalized=True)
    degree = nx.degree_centrality(graph)

    try:
        pagerank = nx.pagerank(graph, weight="capacity")
    except (nx.PowerIterationFailedConvergence, ModuleNotFoundError):
        pagerank = _simple_pagerank(graph, weight="capacity")

    rows = []
    for node, attrs in graph.nodes(data=True):
        strategic_score = (
            0.35 * betweenness.get(node, 0)
            + 0.25 * closeness.get(node, 0)
            + 0.20 * degree.get(node, 0)
            + 0.20 * pagerank.get(node, 0)
        )
        rows.append(
            {
                "id": node,
                "name": attrs.get("name", node),
                "country": attrs.get("country", ""),
                "hub_type": attrs.get("hub_type", ""),
                "degree": degree.get(node, 0),
                "closeness": closeness.get(node, 0),
                "betweenness": betweenness.get(node, 0),
                "pagerank": pagerank.get(node, 0),
                "strategic_score": strategic_score,
            }
        )

    return pd.DataFrame(rows).sort_values("strategic_score", ascending=False)


def _simple_pagerank(graph: nx.Graph, weight: str = "capacity", damping: float = 0.85, iterations: int = 80) -> dict:
    nodes = list(graph.nodes)
    if not nodes:
        return {}

    rank = {node: 1 / len(nodes) for node in nodes}
    base = (1 - damping) / len(nodes)

    for _ in range(iterations):
        next_rank = {node: base for node in nodes}
        for source in nodes:
            weighted_neighbors = [
                (target, max(float(graph.edges[source, target].get(weight, 1)), 0.0))
                for target in graph.neighbors(source)
            ]
            total_weight = sum(value for _, value in weighted_neighbors)
            if total_weight <= 0:
                share = damping * rank[source] / len(nodes)
                for target in nodes:
                    next_rank[target] += share
                continue
            for target, value in weighted_neighbors:
                next_rank[target] += damping * rank[source] * (value / total_weight)
        rank = next_rank

    return rank


def network_summary(graph: nx.Graph, baseline_graph: nx.Graph | None = None) -> dict[str, float | int]:
    components = list(nx.connected_components(graph))
    largest_component = max((len(component) for component in components), default=0)
    total_capacity = sum(float(attrs.get("capacity", 0)) for _, _, attrs in graph.edges(data=True))
    total_flow = sum(float(attrs.get("simulated_flow", attrs.get("current_flow", 0))) for _, _, attrs in graph.edges(data=True))
    overloaded_edges = sum(
        1
        for _, _, attrs in graph.edges(data=True)
        if float(attrs.get("capacity", 0)) > 0
        and float(attrs.get("simulated_flow", attrs.get("current_flow", 0))) / float(attrs.get("capacity", 1)) >= 0.9
    )

    summary: dict[str, float | int] = {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "components": len(components),
        "largest_component": largest_component,
        "total_capacity": round(total_capacity, 1),
        "total_flow": round(total_flow, 1),
        "overloaded_edges": overloaded_edges,
    }

    if baseline_graph is not None:
        baseline_nodes = set(baseline_graph.nodes)
        active_nodes = set(graph.nodes)
        lost_nodes = baseline_nodes - active_nodes
        summary["lost_nodes"] = len(lost_nodes)
        summary["lost_population_m"] = round(sum(float(baseline_graph.nodes[node].get("population_m", 0)) for node in lost_nodes), 2)
        summary["lost_gdp_billion"] = round(sum(float(baseline_graph.nodes[node].get("regional_gdp_billion", 0)) for node in lost_nodes), 1)

    return summary


def edge_bottlenecks(graph: nx.Graph) -> pd.DataFrame:
    rows = []
    for source, target, attrs in graph.edges(data=True):
        capacity = float(attrs.get("capacity", 0))
        flow = float(attrs.get("simulated_flow", attrs.get("current_flow", 0)))
        utilization = flow / capacity if capacity > 0 else math.inf
        rows.append(
            {
                "edge": f"{graph.nodes[source].get('name', source)} -> {graph.nodes[target].get('name', target)}",
                "source": source,
                "target": target,
                "mode": attrs.get("mode", ""),
                "corridor": attrs.get("corridor_name", ""),
                "capacity": capacity,
                "simulated_flow": round(flow, 1),
                "utilization": utilization,
                "risk_score": attrs.get("risk_score", 0),
            }
        )
    return pd.DataFrame(rows, columns=[
        "edge", "source", "target", "mode", "corridor", "capacity",
        "simulated_flow", "utilization", "risk_score",
    ]).sort_values(["utilization", "risk_score"], ascending=False)


def accessibility_table(graph: nx.Graph, baseline_graph: nx.Graph, origin: str) -> pd.DataFrame:
    if origin not in baseline_graph:
        return pd.DataFrame()

    baseline_lengths = nx.single_source_dijkstra_path_length(baseline_graph, origin, weight="travel_time_h")
    scenario_lengths = nx.single_source_dijkstra_path_length(graph, origin, weight="travel_time_h") if origin in graph else {}

    rows = []
    for node, attrs in baseline_graph.nodes(data=True):
        if node == origin:
            continue
        before = baseline_lengths.get(node)
        after = scenario_lengths.get(node)
        if before is None:
            status = "unreachable_baseline"
            delta = None
        elif after is None:
            status = "unreachable"
            delta = None
        else:
            delta = after - before
            status = "slower" if delta > 0.05 else "stable"
        rows.append(
            {
                "node": node,
                "name": attrs.get("name", node),
                "country": attrs.get("country", ""),
                "baseline_time_h": round(before, 2) if before is not None else None,
                "scenario_time_h": round(after, 2) if after is not None else None,
                "delta_h": round(delta, 2) if delta is not None else None,
                "status": status,
                "population_m": attrs.get("population_m", 0),
                "regional_gdp_billion": attrs.get("regional_gdp_billion", 0),
            }
        )

    return pd.DataFrame(rows).sort_values(["status", "delta_h"], ascending=[True, False], na_position="first")
