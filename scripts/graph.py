import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib import colormaps
from scripts.model import Model
from shapely import area, Polygon
from typing import List, Set, Tuple


class GraphProcessing:
    def __init__(self, model: Model):
        self.model = model
        self.config = model.config
        self.centre = model.centre

        adj_list_complete = self.model.get_adj_list(threshold=0)
        adj_list = self.model.get_adj_list()

        self.layout = self.model.get_node_pos(adj_list_complete)

        self.graph_complete = nx.Graph(adj_list_complete)
        self.graph = nx.Graph(adj_list)

        edge_length = {edge: self.__get_edge_length(edge) for edge in self.graph_complete.edges}
        nx.set_node_attributes(self.graph_complete, self.layout, 'pos')
        nx.set_edge_attributes(self.graph_complete, edge_length, 'length')
        nx.set_node_attributes(self.graph, self.layout, 'pos')
        nx.set_edge_attributes(self.graph, edge_length, 'length')

        self.connect_close_nodes()
        sorted_groups = self.get_connected_components()
        self.largest_groups = [sorted_groups[0], sorted_groups[1]]

    def shortest_path_overall(self, from_region: Set[int], to_region: Set[int]):
        """
        Find the shortest path between any node in from_region and any node in to_region.
        """
        dist = float('inf')
        shortest_path = []
        for target in to_region:
            distance, path = nx.multi_source_dijkstra(self.graph_complete, from_region, target=target, weight='length')
            if distance < dist:
                dist = distance
                shortest_path = path
        shortest_path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
        return dist, self.trim_path(shortest_path_edges, from_region, to_region)

    def shortest_path_town_centre(self, from_region: Set[int], to_region: Set[int]):
        """
        Find the shortest path between the central node in from_region and the central node in to_region,
        where the central node in a region is the node nearest to the centre of the town.
        """
        node_from = min(from_region, key=lambda n: math.dist(self.layout[n], self.centre))
        node_to = min(to_region, key=lambda n: math.dist(self.layout[n], self.centre))
        dist, shortest_path = nx.single_source_dijkstra(self.graph_complete, node_from, node_to, weight='length')
        shortest_path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
        return dist, self.trim_path(shortest_path_edges, from_region, to_region)

    def shortest_path_local_centre(self, from_region: Set[int], to_region: Set[int]):
        """
        Find the shortest path between the central node in from_region and the central node in to_region,
        where the central node in a region is the node nearest to the centre of the region.
        """
        centre_from, centre_to = self.get_centre_of_nodes(from_region), self.get_centre_of_nodes(to_region)
        node_from = min(from_region, key=lambda n: math.dist(self.layout[n], centre_from))
        node_to = min(to_region, key=lambda n: math.dist(self.layout[n], centre_to))
        dist, shortest_path = nx.single_source_dijkstra(self.graph_complete, node_from, node_to, weight='length')
        shortest_path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
        return dist, self.trim_path(shortest_path_edges, from_region, to_region)

    @staticmethod
    def trim_path(path: List[Tuple[int, int]], from_region: Set[int], to_region: Set[int]):
        enum_edges = list(enumerate(path))
        edges_in_from = [(i, edge) for (i, edge) in enum_edges if edge[0] in from_region and edge[1] not in from_region]
        edges_in_to = [(i, edge) for (i, edge) in enum_edges if edge[0] not in to_region and edge[1] in to_region]
        start, end = edges_in_from[-1][0], edges_in_to[0][0]
        return path[start:end + 1]

    def get_connected_components(self) -> List[Set[int]]:
        return sorted(nx.connected_components(self.graph), key=self.__group_area, reverse=True)

    def get_centre_of_nodes(self, nodes: Set[int]) -> Tuple[float, float]:
        g = nx.subgraph(self.graph, nodes)
        centre = list(nx.center(g, weight='length'))[0]
        return self.layout[centre]

    def add_edges_to_graph(self, edges: List[Tuple[int, int]]):
        self.graph.add_edges_from(edges)

    def display(self, subgraph: List[Set[int]] = None, filepath=None):
        fig, ax = plt.subplots()
        nx.draw_networkx(self.graph, pos=self.layout, with_labels=False, node_size=5, ax=ax)
        if subgraph is not None:
            color = iter(colormaps['rainbow'](np.linspace(0, 1, len(subgraph))))
            for graph in subgraph:
                c = next(color)
                nx.draw_networkx(self.graph.subgraph(graph), pos=self.layout, with_labels=False, node_size=5, ax=ax,
                                 node_color=[c], edge_color=[c])
        if filepath is not None:
            fig.savefig(filepath)
        else:
            plt.show()

    def display_path_between_subgraph(self, path: List[Tuple[int, int]], from_region, to_region, filepath=None):
        fig, ax = plt.subplots()
        nx.draw_networkx(self.graph, pos=self.layout, with_labels=False, node_size=5, ax=ax)
        nx.draw_networkx(self.graph.subgraph(from_region), pos=self.layout, with_labels=False, node_size=5, ax=ax,
                         node_color='m', edge_color='m')
        nx.draw_networkx(self.graph.subgraph(to_region), pos=self.layout, with_labels=False, node_size=5, ax=ax,
                         node_color='r', edge_color='r')
        nx.draw_networkx(nx.Graph(path), pos=self.layout, with_labels=False, node_size=5, ax=ax,
                         node_color='y', edge_color='y')
        if filepath is not None:
            fig.savefig(filepath)
        else:
            plt.show()

    def connect_close_nodes(self):
        new_edges = nx.geometric_edges(self.graph, radius=self.config.neighbour_eps)
        self.graph.add_edges_from(new_edges)
        new_edges = nx.geometric_edges(self.graph_complete, radius=self.config.neighbour_eps)
        self.graph_complete.add_edges_from(new_edges)

    def __group_area(self, group: Set[int]):
        coordinates = [self.layout.get(node_id) for node_id in group]
        south = min(coordinates, key=lambda x: x[1])
        west = min(coordinates, key=lambda x: x[0])
        north = max(coordinates, key=lambda x: x[1])
        east = max(coordinates, key=lambda x: x[0])
        bbox: List[Tuple[float, float]] = [south, west, north, east]
        return area(Polygon(bbox))

    def __get_edge_length(self, edge: Tuple[int, int]):
        if self.config.zero_cost and edge in self.graph.edges:
            return 0
        return math.dist(self.layout[edge[0]], self.layout[edge[1]]) * 10000

    def __get_geometric_edges(self, graph) -> List[Tuple[int, int]]:
        return nx.geometric_edges(graph, radius=self.config.neighbour_eps)
