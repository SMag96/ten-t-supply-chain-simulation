from __future__ import annotations

from pathlib import Path

import networkx as nx
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def load_nodes(path: Path | None = None) -> pd.DataFrame:
    nodes = pd.read_csv(path or DATA_DIR / "nodes.csv")
    required = {"id", "name", "country", "lat", "lon", "node_capacity"}
    missing = required - set(nodes.columns)
    if missing:
        raise ValueError(f"nodes.csv is missing required columns: {sorted(missing)}")
    return nodes


def load_edges(path: Path | None = None) -> pd.DataFrame:
    edges = pd.read_csv(path or DATA_DIR / "edges.csv")
    required = {"source", "target", "mode", "distance_km", "travel_time_h", "capacity", "current_flow"}
    missing = required - set(edges.columns)
    if missing:
        raise ValueError(f"edges.csv is missing required columns: {sorted(missing)}")
    return edges


def build_graph(nodes: pd.DataFrame | None = None, edges: pd.DataFrame | None = None) -> nx.Graph:
    nodes = load_nodes() if nodes is None else nodes.copy()
    edges = load_edges() if edges is None else edges.copy()

    graph = nx.Graph()
    for row in nodes.to_dict("records"):
        graph.add_node(row["id"], **row)

    valid_nodes = set(nodes["id"])
    invalid_edges = edges[~edges["source"].isin(valid_nodes) | ~edges["target"].isin(valid_nodes)]
    if not invalid_edges.empty:
        raise ValueError(f"edges.csv references missing nodes: {invalid_edges[['source', 'target']].to_dict('records')}")

    for row in edges.to_dict("records"):
        edge_id = edge_key(row["source"], row["target"])
        graph.add_edge(row["source"], row["target"], edge_id=edge_id, **row)

    return graph


def edge_key(source: str, target: str) -> str:
    return "--".join(sorted([source, target]))


def graph_to_edge_frame(graph: nx.Graph) -> pd.DataFrame:
    rows = []
    for source, target, attrs in graph.edges(data=True):
        rows.append({"source": source, "target": target, **attrs})
    return pd.DataFrame(rows)


def graph_to_node_frame(graph: nx.Graph) -> pd.DataFrame:
    return pd.DataFrame([attrs for _, attrs in graph.nodes(data=True)])
