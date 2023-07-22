import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from scripts.config import Config
from scripts.model import Model
from typing import Dict, List, Set, Tuple


def poly_area(x: List[float], y: List[float]):
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def group_area(group: Set[int], layout: Dict[int, Tuple[float, float]]):
    coordinates = [layout.get(node_id) for node_id in group]
    south = min(coordinates, key=lambda x: x[1])
    west = min(coordinates, key=lambda x: x[0])
    north = max(coordinates, key=lambda x: x[1])
    east = max(coordinates, key=lambda x: x[0])
    bbox = [south, west, north, east]
    return poly_area([n[0] for n in bbox], [n[1] for n in bbox])


def trim_shortest_path(shortest_path: List[Tuple[int, int]], from_region: Set[int], to_region: Set[int]):
    enum_edges = list(enumerate(shortest_path))
    edges_in_from = [(i, edge) for (i, edge) in enum_edges if edge[0] in from_region and edge[1] not in from_region]
    edges_in_to = [(i, edge) for (i, edge) in enum_edges if edge[0] not in to_region and edge[1] in to_region]
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

        self.connect_close_nodes()
        sorted_groups = self.get_sorted_groups()
        self.largest_groups = [sorted_groups[0], sorted_groups[1]]

    def shortest_path_among_all_nodes(self, regions: Tuple[Set[int], Set[int]] = None):
        """
        Find the shortest path between any node in from_region and any node in to_region.
        """
        if regions is None:
            regions = (self.largest_groups[0], self.largest_groups[1])
        from_region, to_region = regions
        dist = float('inf')
        shortest_path = []
        for target in to_region:
            distance, path = nx.multi_source_dijkstra(self.graph_all, from_region, target=target,
                                                      weight=self.get_edge_weight)
            if distance < dist:
                dist = distance
                shortest_path = path
        shortest_path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
        return dist, trim_shortest_path(shortest_path_edges, from_region, to_region)

    def shortest_path_between_central_nodes_in_town(self, regions: Tuple[Set[int], Set[int]] = None):
        """
        Find the shortest path between the central node in from_region and the central node in to_region,
        where the central node in a region is the node nearest to the centre of the town.
        """
        if regions is None:
            regions = (self.largest_groups[0], self.largest_groups[1])
        from_region, to_region = regions
        largest_centres = [
            min(from_region, key=lambda n: math.dist(self.layout[n], self.model.data_fetcher.get_centre())),
            min(to_region, key=lambda n: math.dist(self.layout[n], self.model.data_fetcher.get_centre()))
        ]
        dist, shortest_path = nx.single_source_dijkstra(self.graph_all, largest_centres[0], largest_centres[1],
                                                        weight=self.get_edge_weight)
        shortest_path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
        return dist, trim_shortest_path(shortest_path_edges, from_region, to_region)

    def shortest_path_between_central_nodes_in_region(self, regions: Tuple[Set[int], Set[int]] = None):
        """
        Find the shortest path between the central node in from_region and the central node in to_region,
        where the central node in a region is the node nearest to the centre of the region.
        """
        if regions is None:
            regions = (self.largest_groups[0], self.largest_groups[1])
        from_region, to_region = regions
        centre_from = self.get_centre_of_region(from_region)
        centre_to = self.get_centre_of_region(to_region)
        largest_centres = [
            min(from_region, key=lambda n: math.dist(self.layout[n], centre_from)),
            min(to_region, key=lambda n: math.dist(self.layout[n], centre_to))
        ]
        dist, shortest_path = nx.single_source_dijkstra(self.graph_all, largest_centres[0], largest_centres[1],
                                                        weight=self.get_edge_weight)
        shortest_path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
        return dist, trim_shortest_path(shortest_path_edges, from_region, to_region)

    def shortest_path_with_existing_paths(self, regions: Tuple[Set[int], Set[int]] = None):
        """
        Find the shortest path between any node in from_region and any node in to_region, making use of existing
        cycle-friendly paths.
        """
        if regions is None:
            regions = (self.largest_groups[0], self.largest_groups[1])
        from_region, to_region = regions
        dist = float('inf')
        shortest_path = []
        for target in to_region:
            distance, path = nx.multi_source_dijkstra(self.graph_all, from_region, target=target,
                                                      weight=self.get_edge_weight_except_existing)
            if distance < dist:
                dist = distance
                shortest_path = path
        shortest_path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
        return dist, trim_shortest_path(shortest_path_edges, from_region, to_region)

    def get_centre_of_region(self, region: Set[int]):
        g = nx.subgraph(self.graph_friendly, region)
        centre = list(nx.center(g, weight=self.get_edge_weight))[0]
        return self.graph_friendly.nodes[centre]['pos']

    def get_edge_weight_except_existing(self, u: int, v: int, _):
        if (u, v) in self.graph_friendly.edges:
            return 0
        return math.dist(self.layout[u], self.layout[v]) * 10000

    def get_edge_weight(self, u: int, v: int, _):
        return math.dist(self.layout[u], self.layout[v]) * 10000

    def get_sorted_groups(self):
        return sorted(nx.connected_components(self.graph_friendly), key=lambda g: group_area(g, self.layout),
                      reverse=True)

    def draw_graph_with_largest_groups(self, filepath=None):
        fig, ax = plt.subplots()
        nx.draw_networkx(self.graph_friendly, pos=self.layout, with_labels=False, node_size=5, ax=ax)
        nx.draw_networkx(self.graph_friendly.subgraph(self.largest_groups[0]), pos=self.layout, node_color='r',
                         edge_color='r', with_labels=False, node_size=5, ax=ax)
        nx.draw_networkx(self.graph_friendly.subgraph(self.largest_groups[1]), pos=self.layout, node_color='m',
                         edge_color='m', with_labels=False, node_size=5, ax=ax)
        if filepath is not None:
            fig.savefig(filepath)
        else:
            plt.show()

    def draw_graph_with_suggested_path(self, path: List[Tuple[int, int]], filepath=None):
        fig, ax = plt.subplots()
        nx.draw_networkx(self.graph_friendly, pos=self.layout, with_labels=False, node_size=5, ax=ax)
        nx.draw_networkx(self.graph_friendly.subgraph(self.largest_groups[0]), pos=self.layout, node_color='r',
                         edge_color='r', with_labels=False, node_size=5, ax=ax)
        nx.draw_networkx(self.graph_friendly.subgraph(self.largest_groups[1]), pos=self.layout, node_color='m',
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
