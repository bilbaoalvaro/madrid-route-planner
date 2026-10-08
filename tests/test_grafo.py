import unittest
import networkx as nx

from grafo_pesado import camino_minimo, dijkstra, kruskal, prim


def edge_weight(graph, u, v):
    return graph[u][v]["weight"]


class DijkstraTests(unittest.TestCase):
    def setUp(self):
        self.graph = nx.DiGraph()
        self.graph.add_weighted_edges_from([
            ("start", 1, 2),
            ("start", "detour", 5),
            (1, "finish", 2),
            ("detour", "finish", 1),
        ])

    def test_finds_minimum_weight_path(self):
        self.assertEqual(
            camino_minimo(self.graph, edge_weight, "start", "finish"),
            ["start", 1, "finish"],
        )

    def test_unreachable_destination_returns_empty_path(self):
        self.graph.add_node("isolated")
        self.assertEqual(
            camino_minimo(self.graph, edge_weight, "start", "isolated"), []
        )

    def test_path_to_same_vertex(self):
        self.assertEqual(
            camino_minimo(self.graph, edge_weight, "start", "start"), ["start"]
        )

    def test_negative_weight_is_rejected(self):
        self.graph["start"][1]["weight"] = -1
        with self.assertRaises(ValueError):
            dijkstra(self.graph, edge_weight, "start")


class SpanningTreeTests(unittest.TestCase):
    def setUp(self):
        self.graph = nx.Graph()
        self.graph.add_weighted_edges_from([
            (1, 2, 1),
            (2, 3, 2),
            (1, 3, 5),
            (3, 4, 1),
            (2, 4, 4),
        ])

    def test_prim_returns_parent_for_each_vertex(self):
        tree = prim(self.graph, edge_weight)
        self.assertEqual(set(tree), set(self.graph.nodes()))
        self.assertEqual(sum(parent is not None for parent in tree.values()), 3)

    def test_kruskal_returns_spanning_tree(self):
        tree = kruskal(self.graph, edge_weight)
        self.assertEqual(len(tree), self.graph.number_of_nodes() - 1)
        tree_graph = nx.Graph()
        tree_graph.add_nodes_from(self.graph.nodes())
        tree_graph.add_edges_from(tree)
        self.assertTrue(nx.is_connected(tree_graph))


if __name__ == "__main__":
    unittest.main()
