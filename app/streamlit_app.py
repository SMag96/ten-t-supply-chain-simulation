from __future__ import annotations

from pathlib import Path
import sys

try:
    import networkx as nx
    import pandas as pd
    import streamlit as st
except ModuleNotFoundError as exc:
    missing = exc.name
    print(
        f"Missing Python package: {missing}\n\n"
        "For the working no-install interactive app, run:\n"
        "  python run_app.py\n\n"
        "For the Streamlit version, install dependencies first and run:\n"
        "  .\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt\n"
        "  .\\.venv\\Scripts\\python.exe -m streamlit run app\\streamlit_app.py\n\n"
        "Do not start this file with plain python unless the dependencies are already installed."
    )
    raise SystemExit(1) from exc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.graph_builder import build_graph, edge_key, load_edges, load_nodes
from src.metrics import accessibility_table, calculate_centrality, edge_bottlenecks, network_summary
from src.simulation import SimulationRequest, allocate_flows, apply_scenario, scenario_options, run_custom_simulation
from src.visualization import metric_delta_frame, network_figure


st.set_page_config(page_title="TEN-T Supply Chain Simulation", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: #210B2C; color: #f7fbfc; }
    .block-container { padding-top: 1.2rem; }
    section[data-testid="stSidebar"], div[data-testid="stVerticalBlockBorderWrapper"] { background: #19535F; }
    h1, h2, h3, label, p, span { color: #f7fbfc; }
    div[data-testid="stExpander"] {
        border: 1px solid rgba(209, 214, 70, 0.32);
        border-radius: 8px;
        background: rgba(15, 48, 56, 0.76);
    }
    div[data-testid="stExpander"] summary p { color: #D1D646; font-weight: 700; }
    div[data-baseweb="select"] > div {
        background: #0f3038;
        border-color: rgba(209, 214, 70, 0.32);
        color: #f7fbfc;
    }
    .stButton button {
        background: #0f3038;
        border: 1px solid rgba(209, 214, 70, 0.42);
        color: #f7fbfc;
    }
    .stButton button:hover {
        border-color: #D1D646;
        color: #D1D646;
    }
    div[data-testid="stMetricValue"] { font-size: 1.45rem; }
    div[data-testid="stMetricLabel"] { font-size: .86rem; color: #c7d5d8; }
    .stDataFrame { border: 1px solid rgba(209, 214, 70, 0.24); border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return load_nodes(), load_edges(), scenario_options(str(ROOT / "data" / "scenarios.csv"))


@st.cache_resource
def baseline_graph() -> nx.Graph:
    return allocate_flows(build_graph())


nodes, edges, scenarios = load_data()
base_graph = baseline_graph()


def reset_manual_controls() -> None:
    for row in nodes.itertuples():
        st.session_state[f"deactivate_node_{row.id}"] = False
    for row in edges.itertuples():
        st.session_state[f"deactivate_edge_{edge_key(row.source, row.target)}"] = False
    st.session_state["reduce_node"] = "None"
    st.session_state["node_capacity"] = 55
    st.session_state["demand_multiplier"] = 100


st.title("TEN-T Supply Chain Simulation")

left_panel, main_panel = st.columns([0.30, 0.70], gap="large")

with left_panel:
    st.subheader("Scenario")
    scenario_names = dict(zip(scenarios["name"], scenarios["scenario_id"]))
    selected_scenario_name = st.selectbox("Preset", list(scenario_names.keys()), index=0)
    selected_scenario = scenarios[scenarios["scenario_id"] == scenario_names[selected_scenario_name]].iloc[0]

    st.divider()
    st.subheader("Manual disruption")
    node_labels = ["None"] + [f"{row.name} ({row.id})" for row in nodes.itertuples()]
    node_lookup = {"None": None} | {f"{row.name} ({row.id})": row.id for row in nodes.itertuples()}

    selected_deactivate_nodes_count = sum(
        1 for row in nodes.itertuples() if st.session_state.get(f"deactivate_node_{row.id}", False)
    )
    deactivate_nodes: list[str] = []
    with st.expander(f"Deactivate nodes ({selected_deactivate_nodes_count} selected)", expanded=False):
        for row in nodes.itertuples():
            if st.checkbox(f"{row.name} ({row.id})", key=f"deactivate_node_{row.id}"):
                deactivate_nodes.append(row.id)

    reduce_label = st.selectbox("Reduce node capacity", node_labels, index=0, key="reduce_node")
    node_multiplier = st.slider("Remaining node/link capacity", 0, 100, 55, 5, key="node_capacity") / 100

    edge_rows = []
    for row in edges.itertuples():
        source_name = base_graph.nodes[row.source]["name"]
        target_name = base_graph.nodes[row.target]["name"]
        key = edge_key(row.source, row.target)
        label = f"{source_name} -> {target_name} ({row.mode})"
        edge_rows.append((key, label))

    selected_deactivate_edges_count = sum(
        1 for edge_id, _ in edge_rows if st.session_state.get(f"deactivate_edge_{edge_id}", False)
    )
    deactivate_edges: list[str] = []
    with st.expander(f"Deactivate links ({selected_deactivate_edges_count} selected)", expanded=False):
        for edge_id, label in edge_rows:
            if st.checkbox(label, key=f"deactivate_edge_{edge_id}"):
                deactivate_edges.append(edge_id)

    demand_multiplier = st.slider("Demand multiplier", 50, 180, 100, 5, key="demand_multiplier") / 100

    st.divider()
    origin_labels = [f"{row.name} ({row.id})" for row in nodes.itertuples()]
    origin_lookup = {f"{row.name} ({row.id})": row.id for row in nodes.itertuples()}
    origin_label = st.selectbox("Accessibility origin", origin_labels, index=origin_labels.index("Frankfurt am Main (frankfurt)"))
    origin = origin_lookup[origin_label]

    st.button("Reset manual controls", on_click=reset_manual_controls)


scenario_graph = apply_scenario(base_graph, selected_scenario)
scenario_graph = allocate_flows(scenario_graph)

manual_request = SimulationRequest(
    scenario_id="custom",
    deactivate_nodes=deactivate_nodes,
    deactivate_edges=deactivate_edges,
    reduce_node=node_lookup[reduce_label],
    node_capacity_multiplier=node_multiplier,
    demand_multiplier=demand_multiplier,
    origin=origin,
)

if any([manual_request.deactivate_nodes, manual_request.deactivate_edges, manual_request.reduce_node]) or demand_multiplier != 1:
    active_graph = run_custom_simulation(scenario_graph, manual_request)
else:
    active_graph = scenario_graph

baseline_summary = network_summary(base_graph)
scenario_summary = network_summary(active_graph, base_graph)
centrality = calculate_centrality(active_graph)
bottlenecks = edge_bottlenecks(active_graph)
accessibility = accessibility_table(active_graph, base_graph, origin)

with main_panel:
    metric_cols = st.columns(5)
    metric_cols[0].metric("Active nodes", scenario_summary["nodes"], scenario_summary["nodes"] - baseline_summary["nodes"])
    metric_cols[1].metric("Active links", scenario_summary["edges"], scenario_summary["edges"] - baseline_summary["edges"])
    metric_cols[2].metric("Capacity", f"{scenario_summary['total_capacity']:.0f}", f"{scenario_summary['total_capacity'] - baseline_summary['total_capacity']:.0f}")
    metric_cols[3].metric("Overloaded links", scenario_summary["overloaded_edges"], scenario_summary["overloaded_edges"] - baseline_summary["overloaded_edges"])
    metric_cols[4].metric("GDP exposure", f"{scenario_summary.get('lost_gdp_billion', 0):.1f} bn")

    fig = network_figure(
        active_graph,
        base_graph,
        selected_node=origin,
        deactivated_nodes=manual_request.deactivate_nodes,
        deactivated_edges=manual_request.deactivate_edges,
    )
    st.plotly_chart(fig, width="stretch", config={"scrollZoom": True, "displayModeBar": True})

tabs = st.tabs(["Impact", "Bottlenecks", "Strategic hubs", "Accessibility", "Data"])

with tabs[0]:
    st.dataframe(metric_delta_frame(baseline_summary, scenario_summary), width="stretch", hide_index=True)

    unreachable = accessibility[accessibility["status"] == "unreachable"]
    slower = accessibility[accessibility["status"] == "slower"].head(10)
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Unreachable nodes")
        st.dataframe(unreachable[["name", "country", "population_m", "regional_gdp_billion"]], width="stretch", hide_index=True)
    with col_b:
        st.subheader("Largest travel-time increases")
        st.dataframe(slower[["name", "country", "baseline_time_h", "scenario_time_h", "delta_h"]], width="stretch", hide_index=True)

with tabs[1]:
    table = bottlenecks.head(15).copy()
    table["utilization"] = table["utilization"].map(lambda value: "blocked" if value == float("inf") else f"{value:.0%}")
    st.dataframe(table[["edge", "mode", "corridor", "capacity", "simulated_flow", "utilization", "risk_score"]], width="stretch", hide_index=True)

with tabs[2]:
    st.dataframe(
        centrality.head(15)[["name", "country", "hub_type", "degree", "closeness", "betweenness", "pagerank", "strategic_score"]],
        width="stretch",
        hide_index=True,
    )

with tabs[3]:
    st.dataframe(
        accessibility[["name", "country", "baseline_time_h", "scenario_time_h", "delta_h", "status", "regional_gdp_billion"]],
        width="stretch",
        hide_index=True,
    )

with tabs[4]:
    data_tabs = st.tabs(["Nodes", "Links", "Scenarios"])
    with data_tabs[0]:
        st.dataframe(nodes, width="stretch", hide_index=True)
    with data_tabs[1]:
        st.dataframe(edges, width="stretch", hide_index=True)
    with data_tabs[2]:
        st.dataframe(scenarios, width="stretch", hide_index=True)
