# TEN-T Supply Chain Simulation

A personal university Supply Chain module project by **Soufiane Maghnouj**, inspired by the Trans-European Transport Network (TEN-T). Coding was assisted by **OpenAI Codex**.

This interactive educational model explores how shutting down a logistics hub, removing a connection, or changing capacity and demand affects a Germany-centered transport network. It supports discussion of connectivity, alternative routes and vulnerable hubs. It is not an operational planning tool or an official European Commission model.

The supplied dataset contains **42 nodes and 55 undirected links**: 48 rail, 4 inland-waterway, 2 maritime and 1 road link. Cities, ports, airports and intermodal hubs are aggregated nodes; there are no air-service links. Numerical inputs are illustrative and have no recorded statistical source or reference year.

## Installation and launch

Run commands from the repository root. Python **3.12** is the tested version. No API keys, environment variables, database or `.env` file are required.

### Standalone browser dashboard

```sh
python run_app.py
```

Open **http://127.0.0.1:8000/app/index.html** if the browser does not open automatically. Stop with Ctrl+C. Port 8000 must be free. Alternatively, open `app/index.html` directly. This version needs only Python's standard library and a modern browser; computation runs in JavaScript. Live map tiles and optional TENtec overlays need internet access; the bundled base image supports offline context.

### Python / Streamlit dashboard

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -c requirements-lock.txt
.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
```

macOS / Linux (commands supplied; not tested on these systems):

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -c requirements-lock.txt
.venv/bin/python -m streamlit run app/streamlit_app.py
```

Visit **http://localhost:8501**. Add `--server.port 8502` if that port is occupied. Do not launch `app/streamlit_app.py` with plain Python. `run_streamlit.ps1` is a Windows convenience launcher that creates the environment and installs dependencies constrained to the tested snapshot.

Dependencies remain managed with pip requirements files. `requirements.txt` declares direct packages; `requirements-lock.txt` records exact versions from the tested Windows/Python 3.12 environment, without wheel hashes. It is a reproducibility snapshot, not a guarantee for every platform or future package index.

For the optional notebook, use the environment's Python to run:

```sh
python -m pip install -r requirements-notebook.txt
python -m jupyter notebook notebooks/01_model_analysis.ipynb
```

The notebook contains starter summary/centrality/bottleneck analysis, not a completed research report.

## Implemented features

- Six presets: baseline, Duisburg shutdown, Hamburg congestion, Rhine link disruption, eastern demand growth and Alpine capacity pressure.
- Multiple manual hub shutdowns and link failures; one selected hub's capacity reduction also reduces its incident links' capacities.
- Global demand control, regional demand in the eastern-growth preset, and a selectable accessibility origin.
- Shortest-travel-time routing and flow reallocation after network changes.
- Baseline/scenario comparisons, connectivity, utilization rankings, strategic-hub rankings and travel-time accessibility tables.
- Interactive maps with tooltips and disruption colors. The browser dashboard also has animated flow particles, layer controls and optional European Commission TENtec overlays.

No fresh screenshot is included: browser automation was unavailable during repository preparation. Existing local captures were outdated or showed only a loading screen and are excluded from publication.

## Reproduce a disruption

1. Launch Streamlit. Leave manual controls at their defaults: demand 100%, no manual removals, no capacity-reduction node.
2. Keep **Accessibility origin** at **Frankfurt am Main (frankfurt)**.
3. Select **Duisburg shutdown** under **Preset**.
4. Inspect **Impact** and **Accessibility**.

Verified Python results with the supplied data:

| Metric | Baseline | Duisburg shutdown |
| --- | ---: | ---: |
| Active nodes | 42 | 41 |
| Active links | 55 | 50 |
| Total edge capacity (model units) | 32,200 | 28,360 |
| Connected components | 1 | 1 |
| Simulated flow (rounded model units) | 1,011.8 | 966.0 |
| Removed-node GDP exposure (illustrative billions) | 0 | 34 |
| Frankfurt to Essen shortest travel time (h) | 2.4 | 11.6 |

Duisburg becomes unreachable from Frankfurt. The remaining 41 nodes stay connected. Exposure is a sum of dataset attributes, **not predicted economic damage**. Select **Baseline** and **Reset manual controls** to restore the initial state. The automated tests check this example.

## Technology and architecture

```text
data/*.csv -> graph_builder -> simulation -> metrics / visualization -> Streamlit
embedded CSV + edge_routes.js -> JavaScript simulation -> HTML/CSS/SVG dashboard
```

| File / directory | Responsibility |
| --- | --- |
| `run_app.py` | Standard-library HTTP server, bound to loopback on port 8000 |
| `app/index.html` | Standalone HTML/CSS/JavaScript application, embedded CSV and preset copies |
| `app/streamlit_app.py` | Streamlit controls, tables and Plotly map |
| `src/graph_builder.py` | Pandas CSV loading and NetworkX graph construction |
| `src/simulation.py` | Scenarios, pair-demand estimates and flow allocation |
| `src/metrics.py` | Connectivity, centrality, utilization and accessibility |
| `src/visualization.py` | Plotly map and metric comparison frame |
| `data/` | CSV model inputs and display route coordinates |
| `app/assets/` | JavaScript route geometry and map images |
| `notebooks/` | Optional Jupyter analysis starter |
| `tests/` | Dataset consistency, scenario and Streamlit regression tests |

Python dependencies are Streamlit, NetworkX, Pandas, Plotly and NumPy. The browser interface has no JavaScript package manager or build step. The interfaces implement simulation logic independently; they are not a shared backend and their outputs are not guaranteed identical.

## Data, sources and assumptions

| Dataset | Fields and use |
| --- | --- |
| `nodes.csv` | `id`, `name`, `country`, `lat`, `lon`, `hub_type`; `population_m`, `regional_gdp_billion`, `gdp_growth_pct`, `industry_index`, `node_capacity`, `damage_level` |
| `edges.csv` | `source`, `target`, `mode`, `corridor_name`, `distance_km`, `travel_time_h`, `capacity`, `current_flow`, `cost_per_ton`, `emissions_factor`, `risk_score`, `damage_level` |
| `scenarios.csv` | `scenario_id`, `name`, `description`, `target_type`, `target_id`, `capacity_multiplier`, `demand_multiplier`, `blocked` |
| `edge_routes.json` | Edge keys map to sequences of `[longitude, latitude]`; 55 canonical keys plus 2 unused noncanonical keys |

Canonical edge IDs join alphabetically sorted node IDs with `--`. `app/assets/edge_routes.js` contains the same geometry as JSON. Browser-embedded node/link CSV copies currently match `data/`; its presets are separately hardcoded. Update both interfaces when changing data or presets.

Place names and maps provide geographic context. No source bibliography, collection scripts, timestamps, statistical reference years or calibration records were supplied for the model inputs. Treat coordinates, corridor assignments, distances, times, population, GDP, industry indices, capacities, flows and risk scores as unverified illustrative inputs. Capacity and flow have no documented physical unit or time interval; GDP has no documented currency/year or consistent regional boundary.

`gdp_growth_pct`, `damage_level`, cost and emissions fields are not used to calculate scenario impacts. Distance does not drive route selection. `current_flow` is replaced by estimated flow when allocation runs. Airport node types do not create an air-transport model.

The browser requests OpenStreetMap tiles and optional European Commission TENtec layers. These are background/display services, not sources for CSV economic or capacity figures. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the provenance investigation, sources and unresolved asset origins.

## Main metrics and model behavior

- **Connectivity:** count of connected components and size of the largest component in the remaining undirected graph.
- **Capacity:** sum of remaining edge capacities, not a maximum-flow result. Node capacity reduction scales incident links; node handling limits are not separately enforced.
- **Pair demand:** `max(0.2, sqrt(population_i * population_j) * (industry_i + industry_j) / 100 + 0.35 * sqrt(GDP_i * GDP_j) / 100)`, multiplied by applicable demand factors. Every unordered active-node pair generates demand.
- **Simulated flow:** demand is assigned to one shortest path by `travel_time_h`, divided by the number of edges in that path, and added to each edge. Unreachable pairs are skipped. This heuristic is not physical freight-flow conservation; total edge flow is not measured tonnage.
- **Utilization:** simulated flow divided by edge capacity. The UI's “Overloaded links” count uses **>=90%**, thus includes near-capacity links; map overload coloring starts at 100%. Zero-capacity links remain routable, are excluded from that count, and have infinite table utilization.
- **Accessibility:** shortest time from the selected origin; delta is scenario minus baseline. “Slower” means an increase greater than 0.05 hours. Removed/disconnected destinations are unreachable.
- **Exposure:** sum of population/GDP attributes for removed nodes only. Disconnected but active nodes are not included; there is no monetary loss or causal economic model.
- **Strategic score (Python):** `0.35 * betweenness + 0.25 * closeness + 0.20 * degree + 0.20 * PageRank`. NetworkX betweenness and closeness use travel time; PageRank uses capacity, with a local iterative fallback if SciPy is unavailable.
- **Strategic score (browser):** `0.35 * betweenness + 0.35 * closeness + 0.30 * degree`, without PageRank. Its betweenness counts one selected path per pair and normalizes by the largest count; its closeness also differs on disconnected graphs. Rankings are not directly interchangeable with Python results.

## Known limitations

- Small aggregated, undirected graph with one edge per node pair; no direction-specific services, parallel modes, transfer penalties, timetable, inventory, queues or dynamic recovery.
- Routing ignores capacity and congestion. Capacity reduction changes utilization but does not itself reroute traffic. Demand from removed nodes disappears.
- Tied shortest paths can differ between implementations. No cross-interface numerical equivalence is claimed.
- With manual overrides, Python replaces the preset's global demand multiplier with the manual value; JavaScript multiplies them. Unmodified presets and the documented example avoid that difference. Eastern growth also includes Berlin in code.
- Optional map services require connectivity and can fail independently of the simulation. External overlays do not validate the illustrative network. Plotly's `Scattermapbox` API emits deprecation warnings.
- No performance benchmark, operational validation or claimed business benefit. Browser interaction and external overlay rendering were not verified during this preparation session.

## Development and contribution

Soufiane Maghnouj identifies this as a personal project completed as part of a university Supply Chain module, inspired by TEN-T, with Codex assistance for coding. The repository exposes implemented components for review; it does not claim that each component was written without assistance. A detailed account of personal design decisions, independently implemented work, adapted code and any collaborators has not yet been supplied.

This repository preparation added documentation, ignore rules, a dependency snapshot and regression tests, and fixed empty-network table handling and working-directory assumptions. These changes are also Codex-assisted. There was no Git repository/history in the supplied folder; no historical commits were reconstructed.

To verify changes, run with the environment's Python:

```sh
python -m pip check
python -m unittest discover -s tests -v
```

On Windows without activation, replace `python` with `.\.venv\Scripts\python.exe`; on macOS/Linux use `.venv/bin/python`. Tests cover input consistency, the documented shutdown, all six presets, empty networks and reset behavior. Document model changes explicitly, preserve third-party credits and keep both data copies synchronized.

No project license has been selected. Third-party assets retain their own notices and terms. See [docs/PUBLICATION.md](docs/PUBLICATION.md) for verification results, the reviewed publication manifest and remaining attribution limitations.
