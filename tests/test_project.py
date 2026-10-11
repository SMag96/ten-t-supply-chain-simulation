"""Run from the repository root: python -m unittest discover -s tests -v."""
import csv
import io
import json
import os
from pathlib import Path
import re
import tempfile
import unittest

import networkx as nx
from streamlit.testing.v1 import AppTest

from src.graph_builder import ROOT, build_graph, edge_key, load_edges, load_nodes
from src.metrics import accessibility_table, edge_bottlenecks, network_summary
from src.simulation import allocate_flows, apply_scenario, scenario_options


class DatasetTests(unittest.TestCase):
    def test_dataset_integrity_and_browser_copies(self):
        nodes, edges = load_nodes(), load_edges()
        self.assertEqual((len(nodes), len(edges)), (42, 55))
        self.assertTrue(nodes.id.is_unique)
        keys = [edge_key(r.source, r.target) for r in edges.itertuples()]
        self.assertEqual(len(set(keys)), 55)
        self.assertTrue(set(edges.source) | set(edges.target) <= set(nodes.id))
        self.assertTrue((edges.travel_time_h > 0).all())
        self.assertTrue((edges.capacity > 0).all())
        html = (ROOT / 'app/index.html').read_text(encoding='utf-8')
        for name in ('nodes', 'edges'):
            embedded = re.search(rf'<script id="{name}Csv" type="text/plain">(.*?)</script>', html, re.S)[1]
            actual = list(csv.DictReader(io.StringIO(embedded.strip())))
            with (ROOT / 'data' / f'{name}.csv').open(encoding='utf-8') as f:
                self.assertEqual(actual, list(csv.DictReader(f)))
        routes = json.loads((ROOT / 'data/edge_routes.json').read_text())
        js = (ROOT / 'app/assets/edge_routes.js').read_text()
        self.assertEqual(routes, json.loads(js[js.index('{'):].strip().rstrip(';')))
        self.assertTrue(set(keys) <= set(routes))
        # Two noncanonical historical keys are unused; keep their geometry intact.
        self.assertEqual(set(routes) - set(keys), {'regensburg--passau', 'passau--linz'})
        for route in routes.values():
            self.assertGreaterEqual(len(route), 2)
            self.assertTrue(all(len(p) == 2 and -180 <= p[0] <= 180 and -90 <= p[1] <= 90 for p in route))

    def test_scenarios_load_outside_project_directory(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                self.assertEqual(len(scenario_options()), 6)
            finally:
                os.chdir(previous)


class SimulationTests(unittest.TestCase):
    def test_duisburg_shutdown_and_baseline_preservation(self):
        base = allocate_flows(build_graph())
        preset = scenario_options().set_index('scenario_id').loc['duisburg_out']
        scenario = allocate_flows(apply_scenario(base, preset))
        result = network_summary(scenario, base)
        self.assertEqual((result['nodes'], result['edges']), (41, 50))
        self.assertEqual(result['total_capacity'], 28360)
        self.assertEqual(result['lost_gdp_billion'], 34)
        self.assertEqual(result['components'], 1)
        access = accessibility_table(scenario, base, 'frankfurt').set_index('node')
        self.assertEqual(access.loc['duisburg', 'status'], 'unreachable')
        self.assertEqual(access.loc['essen', 'delta_h'], 9.2)
        self.assertEqual((base.number_of_nodes(), base.number_of_edges()), (42, 55))
        self.assertEqual(network_summary(base)['total_capacity'], 32200)

    def test_all_presets(self):
        base = allocate_flows(build_graph())
        for preset in scenario_options().to_dict('records'):
            with self.subTest(preset=preset['scenario_id']):
                graph = allocate_flows(apply_scenario(base, preset))
                self.assertTrue(nx.is_connected(graph))
                self.assertFalse(edge_bottlenecks(graph).empty)
                self.assertTrue(all(a['simulated_flow'] >= 0 for _, _, a in graph.edges(data=True)))


class InterfaceTests(unittest.TestCase):
    def test_streamlit_presets_and_empty_network(self):
        app = AppTest.from_file(str(ROOT / 'app/streamlit_app.py'), default_timeout=60).run()
        self.assertFalse(app.exception)
        for preset in scenario_options()['name']:
            app.selectbox[0].select(preset).run()
            self.assertFalse(app.exception, preset)
            if preset == 'Duisburg shutdown':
                self.assertEqual([m.value for m in app.metric[:3]], ['41', '50', '28360'])
        app.selectbox[0].select('Baseline').run()
        for checkbox in app.checkbox:
            if checkbox.key.startswith('deactivate_edge_'):
                checkbox.check()
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[1].value, '0')
        for checkbox in app.checkbox:
            if checkbox.key.startswith('deactivate_node_'):
                checkbox.check()
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, '0')
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual([m.value for m in app.metric[:2]], ['42', '55'])


if __name__ == '__main__':
    unittest.main()
