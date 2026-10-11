from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import networkx as nx
import pandas as pd
import plotly.graph_objects as go


MODE_COLORS = {
    "rail": "#00A9C7",
    "road": "#00A9C7",
    "inland_waterway": "#00A9C7",
    "maritime": "#00A9C7",
}

MODE_WIDTHS = {
    "rail": 4.2,
    "road": 4.2,
    "inland_waterway": 4.2,
    "maritime": 4.2,
}

ROOT = Path(__file__).resolve().parents[1]
EDGE_ROUTES_PATH = ROOT / "data" / "edge_routes.json"


@lru_cache(maxsize=1)
def edge_routes() -> dict[str, list[list[float]]]:
    if not EDGE_ROUTES_PATH.exists():
        return {}
    return json.loads(EDGE_ROUTES_PATH.read_text(encoding="utf-8"))


def network_figure(
    graph: nx.Graph,
    baseline_graph: nx.Graph,
    selected_node: str | None = None,
    deactivated_nodes: list[str] | set[str] | None = None,
    deactivated_edges: list[str] | set[str] | None = None,
) -> go.Figure:
    traces = []
    routes = edge_routes()
    deactivated_node_set = set(deactivated_nodes or [])
    deactivated_edge_set = set(deactivated_edges or [])

    for source, target, attrs in baseline_graph.edges(data=True):
        left = baseline_graph.nodes[source]
        right = baseline_graph.nodes[target]
        active = graph.has_edge(source, target)
        utilization = 0
        capacity = float(attrs.get("capacity", 0))
        flow = 0.0
        if active:
            scenario_attrs = graph.edges[source, target]
            capacity = float(scenario_attrs.get("capacity", 0))
            flow = float(scenario_attrs.get("simulated_flow", scenario_attrs.get("current_flow", 0)))
            utilization = flow / capacity if capacity > 0 else 0

        edge_id = attrs.get("edge_id")
        if edge_id in deactivated_edge_set:
            color = "#d64545"
            width = 4
        elif not active:
            color = "#d64545"
            width = 4
        elif utilization >= 1.0:
            color = "#c92a2a"
            width = 5
        elif utilization >= 0.9:
            color = "#f08c00"
            width = 4
        else:
            color = MODE_COLORS.get(attrs.get("mode", ""), "#6b7280")
            width = MODE_WIDTHS.get(attrs.get("mode", ""), 3.0)

        route = routes.get(edge_id, [[left["lon"], left["lat"]], [right["lon"], right["lat"]]])
        route_lons = [point[0] for point in route]
        route_lats = [point[1] for point in route]
        status = (
            "Manually deactivated"
            if edge_id in deactivated_edge_set
            else "Stopped by node disruption"
            if source not in graph or target not in graph
            else "Overloaded"
            if active and utilization >= 1.0
            else "Near capacity"
            if active and utilization >= 0.9
            else "Moving"
            if active
            else "Stopped"
        )
        traces.append(
            go.Scattermapbox(
                lon=route_lons,
                lat=route_lats,
                mode="lines",
                line=dict(width=width + 4.5, color="rgba(15, 48, 56, 0.88)"),
                opacity=0.9,
                hoverinfo="skip",
                showlegend=False,
            )
        )
        traces.append(
            go.Scattermapbox(
                lon=route_lons,
                lat=route_lats,
                mode="lines",
                line=dict(width=width, color=color),
                opacity=0.55 if not active else 0.96,
                hoverinfo="text",
                text=(
                    f"{left['name']} -> {right['name']}<br>"
                    f"Status: {status}<br>"
                    f"Mode: {attrs.get('mode')}<br>"
                    f"Corridor: {attrs.get('corridor_name')}<br>"
                    f"Capacity: {capacity:.0f}<br>"
                    f"Simulated flow: {flow:.1f}<br>"
                    f"Utilization: {utilization:.0%}<br>"
                    f"Travel time: {attrs.get('travel_time_h')} h<br>"
                    f"Distance: {attrs.get('distance_km')} km<br>"
                    f"Emissions factor: {attrs.get('emissions_factor')}<br>"
                    f"Risk score: {attrs.get('risk_score')}"
                ),
                showlegend=False,
            )
        )

    node_lons = []
    node_lats = []
    node_text = []
    node_colors = []
    node_sizes = []

    for node, attrs in baseline_graph.nodes(data=True):
        active = node in graph
        current_attrs = graph.nodes[node] if active else attrs
        status = (
            "Manually deactivated"
            if node in deactivated_node_set
            else "Unavailable"
            if not active
            else "Affected"
            if any(neighbor not in graph or not graph.has_edge(node, neighbor) for neighbor in baseline_graph.neighbors(node))
            else "Active"
        )
        node_lons.append(attrs["lon"])
        node_lats.append(attrs["lat"])
        node_text.append(
            f"{attrs['name']} ({attrs['country']})<br>"
            f"Status: {status}<br>"
            f"Hub type: {attrs['hub_type']}<br>"
            f"Capacity: {float(current_attrs.get('node_capacity', attrs['node_capacity'])):.0f}<br>"
            f"Population: {attrs.get('population_m', 0)} m<br>"
            f"GDP: {attrs['regional_gdp_billion']} bn<br>"
            f"Industry index: {attrs.get('industry_index', '')}"
        )
        if node in deactivated_node_set or not active:
            node_colors.append("#d64545")
            node_sizes.append(14)
        elif selected_node == node:
            node_colors.append("#D1D646")
            node_sizes.append(15)
        elif active and any(neighbor not in graph or not graph.has_edge(node, neighbor) for neighbor in baseline_graph.neighbors(node)):
            node_colors.append("#f08c00")
            node_sizes.append(12)
        else:
            node_colors.append("#19535F")
            node_sizes.append(9)

    traces.append(
        go.Scattermapbox(
            lon=node_lons,
            lat=node_lats,
            mode="markers",
            marker=dict(size=node_sizes, color=node_colors),
            text=node_text,
            hoverinfo="text",
            showlegend=False,
        )
    )

    fig = go.Figure(data=traces)
    fig.update_layout(
        height=650,
        margin=dict(l=0, r=0, t=0, b=0),
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=51.3, lon=9.5),
            zoom=4.7,
        ),
        paper_bgcolor="#210B2C",
        plot_bgcolor="#210B2C",
    )
    return fig


def metric_delta_frame(baseline: dict, scenario: dict) -> pd.DataFrame:
    labels = {
        "nodes": "Active nodes",
        "edges": "Active links",
        "components": "Connected components",
        "largest_component": "Largest component",
        "total_capacity": "Total edge capacity",
        "total_flow": "Simulated flow",
        "overloaded_edges": "Overloaded links",
        "lost_population_m": "Population exposure (m)",
        "lost_gdp_billion": "GDP exposure (bn)",
    }
    rows = []
    for key, label in labels.items():
        if key in baseline or key in scenario:
            base = baseline.get(key, 0)
            current = scenario.get(key, 0)
            rows.append({"metric": label, "baseline": base, "scenario": current, "delta": round(current - base, 2)})
    return pd.DataFrame(rows)
