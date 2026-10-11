# Publication review

Prepared locally on 11 October 2026. The owner subsequently confirmed publication to the public repository [SMag96/ten-t-supply-chain-simulation](https://github.com/SMag96/ten-t-supply-chain-simulation). This document preserves the preparation review and its verification limits.

## Confirmed GitHub repository

- Name: **ten-t-supply-chain-simulation**
- Description: **Educational TEN-T disruption simulation with interactive maps, rerouting and network analysis for Germany and neighboring hubs.**
- Account: **SMag96**, confirmed by the owner and verified through the authenticated GitHub API.
- Visibility: **public**, explicitly confirmed by the owner. The repository was created through the GitHub API using existing authentication.
- License: **none selected**; no license was added.

The supplied directory had no `.git` repository, parent repository, nested history or remotes. A new local repository was initialized on `main`. Existing local files, virtual environment, cached wheels and logs were preserved. The 26-file manifest was staged and reviewed before approval. Publication uses a new, current-date initial commit; no historical commits were reconstructed or backdated.

## Changes in this preparation

- Replaced the README with verified scope, commands, architecture, metric definitions, a reproducible disruption and limitations.
- Recorded personal university-project context and Codex-assisted coding as confirmed by the author; did not assign unverified component-level authorship.
- Added third-party notices with evidence and unresolved provenance, an OSM attribution link and an illustrative-data label in the browser UI.
- Added ignore rules and a tested dependency snapshot; raised the Streamlit minimum to the tested version because the application uses modern width parameters.
- Fixed empty centrality/bottleneck tables so disabling all links or nodes does not crash Streamlit.
- Made default scenario-file lookup independent of the current directory and made the PowerShell launcher run from its own directory, use constraints and stop on failed setup.
- Added five regression tests; preserved the routing/demand formulas and existing datasets.

## Verification record

Environment: Windows, Python 3.12. A separate `.venv-verify` was created and installed from `requirements-lock.txt`; the documented `requirements.txt` plus constraints command also succeeded. It remains ignored for local reuse.

| Check | Result |
| --- | --- |
| Existing checks/tests | No test suite or CI configuration was present initially |
| pip dependency consistency | `python -m pip check`: no broken requirements, original and fresh environments |
| Regression suite | `python -m unittest discover -s tests -v`: 5 passed in fresh environment |
| Dataset consistency | 42 unique nodes, 55 unique undirected edges; positive capacities/times; valid endpoints; embedded CSV copies and route JSON/JS copies match |
| Streamlit interaction via AppTest | All six presets render without exceptions; Duisburg shutdown gives 41 nodes, 50 links and capacity 28,360 |
| Empty network regression | All links disabled, then all nodes disabled, then reset: no exceptions and baseline restored |
| HTTP startup | Standalone dashboard returns HTTP 200 at port 8000; Streamlit health endpoint returns HTTP 200 on test port 18501 |
| Notebook | All three code cells executed successfully using Python; Jupyter frontend/optional dependency installation not tested |
| Screenshots and browser interaction | Unavailable: browser-control tool reported no available browsers. Existing screenshots are stale/loading-only and excluded |
| External maps | Source URLs inspected; live overlays/tile rendering not verified |
| Platform coverage | Windows/Python 3.12 only; macOS/Linux commands not executed |

The server smoke tests stopped their own subprocesses afterward. Automatic browser opening was suppressed in the standalone server smoke test. Programmatic Streamlit AppTest interaction exercises application logic and controls, but does not test browser rendering. Warnings remain for deprecated Plotly `Scattermapbox`, AppTest's bare script context, and reset assigning a slider value through session state as well as a default. These did not cause test failures.

## Sensitive-material review

The initial source/data/notebook/log text review checked common credential/token/private-key patterns, credential assignments, email addresses, local user paths and confidentiality markers, without printing matched values. No such findings were detected. The final scan of all 23 staged text files also found no matches. The 26-file manifest exactly matched the Git index, local documentation links resolved, and `git diff --cached --check` passed. Existing screenshots and map images were visually inspected; they show maps or application UI, not personal records. Map PNG metadata contained no source identity or credentials. The notebook has no saved outputs. The author name is intentionally included with the owner's authorization.

Virtual environments, third-party wheel caches, bytecode, temporary files, logs and local configuration are excluded. The scope is a pattern-based and manual review, not a guarantee that arbitrary encoded secrets can be detected. There was no supplied Git history to scan; the repository had no commits at the time of the preparation review. If an older repository/history is later recovered, scan it before publication. Any exposed secret would require revocation/rotation and history remediation; ignoring a file alone would not remove it from history.

## Remaining attribution limitations

Confirmed: personal university Supply Chain module project by Soufiane Maghnouj, inspired by TEN-T, with Codex assistance for coding.

Still unverified: personal component-level responsibilities/design decisions, any adapted third-party code, and the original numerical-data/route-generation sources. Bundled reference maps visibly identify the European Commission; their exact downloaded edition and reuse terms have not been established. The OSM background lacks acquisition metadata. The notices document what can and cannot be established from code, image metadata, visible credits and official source pages. No source or rights clearance was invented.

## Reviewed initial commit manifest

```text
.gitignore
README.md
THIRD_PARTY_NOTICES.md
app/assets/edge_routes.js
app/assets/normal_map_osm.png
app/assets/ten_t_central_europe_map.png
app/assets/ten_t_schematic_map.png
app/index.html
app/streamlit_app.py
data/edge_routes.json
data/edges.csv
data/nodes.csv
data/scenarios.csv
docs/PUBLICATION.md
notebooks/01_model_analysis.ipynb
requirements-lock.txt
requirements-notebook.txt
requirements.txt
run_app.py
run_streamlit.ps1
src/__init__.py
src/graph_builder.py
src/metrics.py
src/simulation.py
src/visualization.py
tests/test_project.py
```

26 files. The three bundled maps and both route-geometry copies are retained. The two historical schematic images are unused by the current app but preserve supplied reference material and visible attribution. Excluded: `.venv/`, `.venv-verify/`, `wheels/`, `__pycache__/`, logs, and the two old app screenshots. No `.env.example` is needed because the application does not read environment configuration.

## Publication and employer review

The owner confirmed the account, repository name and public visibility after reviewing the preparation summary. GitHub CLI was unavailable, so the repository was created through GitHub's REST API using existing Git Credential Manager authentication. Credentials were handled in memory and were not displayed or written to project files.

The initial commit is titled `Prepare TEN-T simulation for code review`. The remote is `https://github.com/SMag96/ten-t-supply-chain-simulation.git`, with `main` as the publication branch. No project license was selected and no employer invitation or message was sent.

Share the repository URL with the employer. The README provides setup instructions and the reproducible Duisburg shutdown example; the contribution statement explicitly discloses Codex assistance and avoids an unsupported component-level authorship claim. The attribution limitations above remain documented even though public visibility was authorized.

For subsequent changes, inspect the changes and run the checks before committing and pushing. Do not recreate the repository or overwrite history:

```powershell
git status
git diff
git diff --cached --check
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
