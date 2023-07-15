import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from scripts.config import Config
from scripts.model import Model


def poly_area(x, y):
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def group_area(group, layout):
    coordinates = [layout.get(node_id) for node_id in group]
    south = min(coordinates, key=lambda x: x[1])
    west = min(coordinates, key=lambda x: x[0])
    north = max(coordinates, key=lambda x: x[1])
    east = max(coordinates, key=lambda x: x[0])
    bbox = [south, west, north, east]
    return poly_area([n[0] for n in bbox], [n[1] for n in bbox])


class GraphProcessing:
    def __init__(self, config: Config):
        self.config = config
        self.model = Model(config)
        self.edges, self.all_nodes = self.model.get_graph()
        self.layout = {node.id: (float(node.lon), float(node.lat)) for node in self.all_nodes}
        self.graph = nx.Graph(self.edges)
        for node_name in self.graph.nodes:
            self.graph.nodes[node_name]['pos'] = self.layout[node_name]

    def suggest_edges(self):
        unfiltered_graph = self.model.get_graph(threshold=0)
        sorted_groups = self.get_sorted_groups()
        largest, larger = sorted_groups[0], sorted_groups[1]
        largest_centre = max(largest, key=lambda n: math.dist(self.layout[n], self.model.data_fetcher.get_centre()))
        larger_centre = max(larger, key=lambda n: math.dist(self.layout[n], self.model.data_fetcher.get_centre()))
        # TODO: add weight (length of edges)
        shortest_path = nx.shortest_path(unfiltered_graph, largest_centre, larger_centre)
        shortest_path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]

    def get_sorted_groups(self):
        return sorted(nx.connected_components(self.graph), key=lambda g: group_area(g, self.layout), reverse=True)

    def draw_graph_with_largest_groups(self, filepath):
        sorted_groups = self.get_sorted_groups()
        nx.draw_networkx(self.graph, pos=self.layout, with_labels=False, node_size=5)
        nx.draw_networkx(self.graph.subgraph(list(sorted_groups[0])), pos=self.layout, node_color='r', edge_color='r',
                         with_labels=False, node_size=5)
        nx.draw_networkx(self.graph.subgraph(list(sorted_groups[1])), pos=self.layout, node_color='m', edge_color='m',
                         with_labels=False, node_size=5)
        plt.savefig(filepath)

    def connect_close_nodes(self):
        new_edges = nx.geometric_edges(self.graph, radius=self.config.neighbour_eps)
        self.edges = self.edges.union(set(new_edges))
        self.graph = nx.Graph(self.edges)
