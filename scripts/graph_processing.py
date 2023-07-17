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


def trim_shortest_path(shortest_path, group_from, group_to):
    enum_edges = list(enumerate(shortest_path))
    edges_in_from = [(i, edge) for (i, edge) in enum_edges if edge[0] in group_from and edge[1] not in group_from]
    edges_in_to = [(i, edge) for (i, edge) in enum_edges if edge[0] not in group_to and edge[1] in group_to]
    start, end = edges_in_from[-1][0], edges_in_to[0][0]
    return shortest_path[start:end + 1]


class GraphProcessing:
    def __init__(self, config: Config):
        self.config = config
        self.model = Model(config)

        adj_list_all = self.model.get_graph(threshold=0)
        self.graph_all = nx.Graph(adj_list_all)
        nodes_all = [self.model.data_fetcher.get_node_by_id(node_id) for node_id in adj_list_all.keys()]
        for node in nodes_all:
            self.graph_all.nodes[node.id]['pos'] = (float(node.lon), float(node.lat))

        adj_list_friendly = self.model.get_graph()
        self.graph_friendly = nx.Graph(adj_list_friendly)
        nodes_friendly = [self.model.data_fetcher.get_node_by_id(node_id) for node_id in
                          adj_list_friendly.keys()]
        for node in nodes_friendly:
            self.graph_friendly.nodes[node.id]['pos'] = (float(node.lon), float(node.lat))

        self.layout = nx.get_node_attributes(self.graph_all, 'pos')

    def shortest_path_among_all_nodes(self):
        sorted_groups = self.get_sorted_groups()
        largest_groups = [sorted_groups[0], sorted_groups[1]]
        dist = float('inf')
        shortest_path = []
        for target in largest_groups[1]:
            distance, path = nx.multi_source_dijkstra(self.graph_all, largest_groups[0], target=target,
                                                      weight=self.get_edge_weight)
            if distance < dist:
                dist = distance
                shortest_path = path
        shortest_path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
        return dist, trim_shortest_path(shortest_path_edges, largest_groups[0], largest_groups[1])

    def shortest_path_between_central_nodes(self):
        sorted_groups = self.get_sorted_groups()
        largest_groups = [sorted_groups[0], sorted_groups[1]]
        largest_centres = [
            min(largest_groups[0], key=lambda n: math.dist(self.layout[n], self.model.data_fetcher.get_centre())),
            min(largest_groups[1], key=lambda n: math.dist(self.layout[n], self.model.data_fetcher.get_centre()))
        ]
        dist, shortest_path = nx.single_source_dijkstra(self.graph_all, largest_centres[0], largest_centres[1],
                                                        weight=self.get_edge_weight)
        shortest_path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
        return dist, trim_shortest_path(shortest_path_edges, largest_groups[0], largest_groups[1])

    def get_edge_weight(self, u, v, attr):
        return math.dist(self.layout[u], self.layout[v])

    def get_sorted_groups(self):
        return sorted(nx.connected_components(self.graph_friendly), key=lambda g: group_area(g, self.layout),
                      reverse=True)

    def draw_graph_with_largest_groups(self, filepath=None):
        fig, ax = plt.subplots()
        sorted_groups = self.get_sorted_groups()
        nx.draw_networkx(self.graph_friendly, pos=self.layout, with_labels=False, node_size=5, ax=ax)
        nx.draw_networkx(self.graph_friendly.subgraph(list(sorted_groups[0])), pos=self.layout, node_color='r',
                         edge_color='r', with_labels=False, node_size=5, ax=ax)
        nx.draw_networkx(self.graph_friendly.subgraph(list(sorted_groups[1])), pos=self.layout, node_color='m',
                         edge_color='m', with_labels=False, node_size=5, ax=ax)
        if filepath is not None:
            fig.savefig(filepath)
        else:
            plt.show()

    def draw_graph_with_suggested_path(self, path, filepath=None):
        fig, ax = plt.subplots()
        sorted_groups = self.get_sorted_groups()
        nx.draw_networkx(self.graph_friendly, pos=self.layout, with_labels=False, node_size=5, ax=ax)
        nx.draw_networkx(self.graph_friendly.subgraph(list(sorted_groups[0])), pos=self.layout, node_color='r',
                         edge_color='r', with_labels=False, node_size=5, ax=ax)
        nx.draw_networkx(self.graph_friendly.subgraph(list(sorted_groups[1])), pos=self.layout, node_color='m',
                         edge_color='m', with_labels=False, node_size=5, ax=ax)
        nx.draw_networkx(nx.Graph(path), pos=self.layout, node_color='y', edge_color='y', with_labels=False,
                         node_size=5, ax=ax)
        if filepath is not None:
            fig.savefig(filepath)
        else:
            plt.show()

    def connect_close_nodes(self):
        new_edges = nx.geometric_edges(self.graph_friendly, radius=self.config.neighbour_eps)
        self.graph_friendly.add_edges_from(new_edges)
        new_edges = nx.geometric_edges(self.graph_all, radius=self.config.neighbour_eps)
        self.graph_all.add_edges_from(new_edges)
