# Third-party notices and provenance

Investigation date: 11 October 2026. This file records evidence, not a new license for the project or a claim of permission for every asset.

## OpenStreetMap

The browser code requests `https://tile.openstreetmap.org/{z}/{x}/{y}.png`; the Streamlit Plotly map uses the `open-street-map` style. Preserve **© OpenStreetMap contributors**. OpenStreetMap data is available under the [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/1-0/); see [OpenStreetMap copyright and attribution](https://www.openstreetmap.org/copyright) and the [tile usage policy](https://operations.osmfoundation.org/policies/tiles/).

`app/assets/normal_map_osm.png` is a bundled map background. Its name, appearance and existing application attribution are consistent with OSM mapping. It has no embedded source URL, capture date or author metadata. Its exact generation/download procedure and rendering provenance are unverified. The existing OSM credit is retained and linked in the dashboard; do not relabel the image as an original map by the project author.

## European Commission / TENtec

`app/assets/ten_t_schematic_map.png` visibly bears the European Commission and TENtec branding, the title “Trans-European Transport Network”, and a footer referring to Regulation (EU) 2024/1679. `ten_t_central_europe_map.png` visually appears to be a crop of that schematic; the exact crop workflow is not recorded. These two reference images are retained but neither is referenced by the current application code.

The Commission publishes a [TEN-T schematic map](https://transport.ec.europa.eu/transport-themes/infrastructure-and-investment/trans-european-transport-network-ten-t/tentec-information-system-and-ten-t-map-library/ten-t-schematic-map-european-transport-corridors_en) in its [TENtec map library](https://transport.ec.europa.eu/transport-themes/infrastructure-and-investment/trans-european-transport-network-ten-t/tentec-information-system-and-ten-t-map-library_en). The publication page currently labels its download as a 2026 map. The bundled PNG's exact edition, original download URL and byte-level correspondence to that publication have not been established. Branding and geographic similarity are evidence of attribution, not proof of a particular download.

The browser also references this display endpoint:

```text
https://webgate.ec.europa.eu/tentec-maps/api/public/gis/TENT_Regulation_2024/MapServer/export
```

The source code credits official layers to the European Commission. This service's live response and layer rendering were not verified. Nothing in this project establishes Commission endorsement or validates its model against TENtec data. Confirm the applicable reuse terms for the bundled reference images before public redistribution; preserve their branding and footer.

## Model inputs and route geometry

There is no recorded upstream source or generation script for `data/nodes.csv`, `data/edges.csv`, `data/scenarios.csv`, `data/edge_routes.json`, or their embedded browser copies. No demographic/statistical source, calibration, reference year or measurement units for flow/capacity are documented. Treat them as illustrative model inputs, not official TEN-T or measured operational data.

The route files contain only edge IDs and coordinate arrays, with no provider, license or timestamp metadata. Their shape alone cannot establish whether they came from OSM, a routing service or manual editing. All 55 canonical edge keys have display geometry; two additional reverse-order keys (`regensburg--passau`, `passau--linz`) are unused and retain different historical geometry. They have not been substituted into the model.

## Code, dependencies and AI assistance

The author confirmed Codex assistance with coding. This preparation also used Codex. No vendored third-party code with explicit license headers was identified in the supplied application/source files; this is not proof that no code was adapted. A source-level contribution breakdown and any adapted-code references remain to be confirmed by the author.

Python libraries are installed through pip and retain their respective licenses. Local wheels and virtual environments are excluded from the repository. No license has been added for the project's own code.
