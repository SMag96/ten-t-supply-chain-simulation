from __future__ import annotations

from dataclasses import dataclass, field

import networkx as nx
import pandas as pd

from .graph_builder import DATA_DIR, edge_key


EAST_GROWTH_NODES = {"leipzig_halle", "dresden", "prague", "wroclaw", "poznan", "berlin"}
ALPINE_EDGES = {edge_key("basel", "zurich"), edge_key("munich", "zurich")}


@dataclass(frozen=True)
class SimulationRequest:
    scenario_id: str = "custom"
    deactivate_nodes: list[str] = field(default_factory=list)
    deactivate_edges: list[str] = field(default_factory=list)
    reduce_node: str | None = None
    node_capacity_multiplier: float = 1.0
    demand_multiplier: float = 1.0
    origin: str = "frankfurt"


def apply_scenario(graph: nx.Graph, scenario: pd.Series | dict | None) -> nx.Graph:
    graph = graph.copy()
    if scenario is None:
        return graph

    target_type = scenario.get("target_type")
    target_id = scenario.get("target_id")
    capacity_multiplier = float(scenario.get("capacity_multiplier", 1.0))
    demand_multiplier = float(scenario.get("demand_multiplier", 1.0))
    blocked = str(scenario.get("blocked", "false")).lower() == "true"

    if target_type == "node" and target_id in graph:
        if blocked:
            graph.remove_node(target_id)
        else:
            reduce_node_capacity(graph, target_id, capacity_multiplier)
    elif target_type == "edge" and target_id:
        apply_edge_capacity(graph, target_id, capacity_multiplier, blocked)
    elif target_type == "region" and target_id == "east_growth":
        graph.graph["regional_demand_multiplier"] = {"nodes": EAST_GROWTH_NODES, "multiplier": demand_multiplier}
    elif target_type == "region" and target_id == "alpine":
        for key in ALPINE_EDGES:
            apply_edge_capacity(graph, key, capacity_multiplier, blocked=False)

    graph.graph["demand_multiplier"] = 1.0 if target_type == "region" else demand_multiplier
    return graph


def run_custom_simulation(base_graph: nx.Graph, request: SimulationRequest) -> nx.Graph:
    graph = base_graph.copy()

    for edge_id in request.deactivate_edges:
        apply_edge_capacity(graph, edge_id, 0, blocked=True)

    for node_id in request.deactivate_nodes:
        if node_id in graph:
            graph.remove_node(node_id)

    if request.reduce_node and request.reduce_node in graph and request.reduce_node not in request.deactivate_nodes:
        reduce_node_capacity(graph, request.reduce_node, request.node_capacity_multiplier)

    graph.graph["demand_multiplier"] = request.demand_multiplier
    return allocate_flows(graph)


def reduce_node_capacity(graph: nx.Graph, node: str, multiplier: float) -> None:
    if node not in graph:
        return
    graph.nodes[node]["node_capacity"] = float(graph.nodes[node].get("node_capacity", 0)) * multiplier
    for neighbor in list(graph.neighbors(node)):
        attrs = graph.edges[node, neighbor]
        attrs["capacity"] = float(attrs.get("capacity", 0)) * multiplier


def apply_edge_capacity(graph: nx.Graph, key: str, multiplier: float, blocked: bool) -> None:
    for source, target, attrs in list(graph.edges(data=True)):
        if attrs.get("edge_id") == key:
            if blocked:
                graph.remove_edge(source, target)
            else:
                attrs["capacity"] = float(attrs.get("capacity", 0)) * multiplier
            return


def allocate_flows(graph: nx.Graph) -> nx.Graph:
    graph = graph.copy()
    for _, _, attrs in graph.edges(data=True):
        attrs["simulated_flow"] = 0.0

    if graph.number_of_edges() == 0:
        return graph

    demand_multiplier = float(graph.graph.get("demand_multiplier", 1.0))
    regional = graph.graph.get("regional_demand_multiplier", {})
    regional_nodes = set(regional.get("nodes", []))
    regional_multiplier = float(regional.get("multiplier", 1.0))

    nodes = list(graph.nodes)
    for idx, source in enumerate(nodes):
        for target in nodes[idx + 1 :]:
            demand = estimate_pair_demand(graph, source, target) * demand_multiplier
            if source in regional_nodes or target in regional_nodes:
                demand *= regional_multiplier
            if demand <= 0:
                continue
            try:
                path = nx.shortest_path(graph, source, target, weight="travel_time_h")
            except nx.NetworkXNoPath:
                continue
            if len(path) < 2:
                continue
            path_flow = demand / max(1, len(path) - 1)
            for left, right in zip(path, path[1:]):
                graph.edges[left, right]["simulated_flow"] += path_flow

    return graph


def estimate_pair_demand(graph: nx.Graph, source: str, target: str) -> float:
    left = graph.nodes[source]
    right = graph.nodes[target]
    population_factor = (float(left.get("population_m", 0)) * float(right.get("population_m", 0))) ** 0.5
    industry_factor = (float(left.get("industry_index", 50)) + float(right.get("industry_index", 50))) / 100
    gdp_factor = (float(left.get("regional_gdp_billion", 1)) * float(right.get("regional_gdp_billion", 1))) ** 0.5 / 100
    return max(0.2, population_factor * industry_factor + 0.35 * gdp_factor)


def scenario_options(path: str | None = None) -> pd.DataFrame:
    return pd.read_csv(path or DATA_DIR / "scenarios.csv")
