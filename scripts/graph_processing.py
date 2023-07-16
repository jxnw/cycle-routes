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
        self.dol, self.nodes = self.model.get_graph()
        # TODO: add weight (length of edges)
        self.graph = nx.Graph(self.dol)
        self.edges = set(self.graph.edges)
        self.layout = {node.id: (float(node.lon), float(node.lat)) for node in self.nodes}
        for node_name in self.graph.nodes:
            self.graph.nodes[node_name]['pos'] = self.layout[node_name]

    def shortest_path_among_all_nodes(self):
        pass

    def shortest_path_between_central_nodes(self):
        unfiltered_graph = self.model.get_graph(threshold=0)
        sorted_groups = self.get_sorted_groups()
        largest_groups = [sorted_groups[0], sorted_groups[1]]
        largest_centres = [
            min(largest_groups[0], key=lambda n: math.dist(self.layout[n], self.model.data_fetcher.get_centre())),
            min(largest_groups[1], key=lambda n: math.dist(self.layout[n], self.model.data_fetcher.get_centre()))
        ]
        shortest_path = nx.shortest_path(unfiltered_graph, largest_centres[0], largest_centres[1])
        shortest_path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
        return self.trim_shortest_path(shortest_path_edges, largest_groups[0], largest_groups[1])

    def trim_shortest_path(self, shortest_path, group_from, group_to):
        enum_edges = list(enumerate(shortest_path))
        edges_in_from = [(i, edge) for (i, edge) in enum_edges if edge[0] in group_from and edge[1] not in group_from]
        edges_in_to = [(i, edge) for (i, edge) in enum_edges if edge[0] not in group_to and edge[1] in group_to]
        start, end = edges_in_from[-1][0], edges_in_to[0][0]
        return shortest_path[start:end + 1]

    def get_sorted_groups(self):
        return sorted(nx.connected_components(self.graph), key=lambda g: group_area(g, self.layout), reverse=True)

    def draw_graph_with_largest_groups(self, filepath=None):
        sorted_groups = self.get_sorted_groups()
        nx.draw_networkx(self.graph, pos=self.layout, with_labels=False, node_size=5)
        nx.draw_networkx(self.graph.subgraph(list(sorted_groups[0])), pos=self.layout, node_color='r', edge_color='r',
                         with_labels=False, node_size=5)
        nx.draw_networkx(self.graph.subgraph(list(sorted_groups[1])), pos=self.layout, node_color='m', edge_color='m',
                         with_labels=False, node_size=5)
        if filepath is not None:
            plt.savefig(filepath)
        else:
            plt.show()

    def connect_close_nodes(self):
        new_edges = nx.geometric_edges(self.graph, radius=self.config.neighbour_eps)
        self.edges = self.edges.union(set(new_edges))
        self.graph = nx.Graph(self.edges)
