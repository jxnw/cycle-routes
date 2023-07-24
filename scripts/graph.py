import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from scripts.model import Model
from shapely import area, Polygon
from typing import Dict, List, Set, Tuple


class Graph:
    def __init__(self, model: Model):
        self.model = model
        self.config = model.config

        adj_list, node_list = self.model.get_graph()
        self.graph = nx.Graph(adj_list)

        for node in node_list:
            self.graph.nodes[node.id]['pos'] = (float(node.lon), float(node.lat))
        self.layout = nx.get_node_attributes(self.graph, 'pos')

        for edge in self.graph.edges:
            self.graph.edges[edge]['length'] = self.__get_edge_length(edge)
        self.edge_length = nx.get_edge_attributes(self.graph, 'length')

    def get_suggested_path(self, complete_graph: nx.Graph, from_region, to_region, strategy=None):
        dist = float('inf')
        shortest_path = []
        for target in to_region:
            distance, path = nx.multi_source_dijkstra(complete_graph, from_region, target=target, weight='length')
            if distance < dist:
                dist = distance
                shortest_path = path
        shortest_path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
        return dist, shortest_path_edges

    def get_connected_components(self) -> List[Set[int]]:
        return sorted(nx.connected_components(self.graph), key=self.__group_area, reverse=True)

    def get_centre_of_nodes(self, nodes: Set[int]) -> Tuple[float, float]:
        g = nx.subgraph(self.graph, nodes)
        centre = list(nx.center(g, weight='length'))[0]
        return self.layout[centre]

    def get_geometric_edges(self) -> List[Tuple[int, int]]:
        """
        Get new edges that connect geometrically close nodes.
        """
        return nx.geometric_edges(self.graph, radius=self.config.neighbour_eps)

    def add_edges_to_graph(self, edges: List[Tuple[int, int]]):
        self.graph.add_edges_from(edges)

    def display_graph(self, filepath=None):
        fig, ax = plt.subplots()
        nx.draw_networkx(self.graph, pos=self.layout, with_labels=False, node_size=5, ax=ax)
        if filepath is not None:
            fig.savefig(filepath)
        else:
            plt.show()

    def __group_area(self, group: Set[int]):
        coordinates = [self.layout.get(node_id) for node_id in group]
        south = min(coordinates, key=lambda x: x[1])
        west = min(coordinates, key=lambda x: x[0])
        north = max(coordinates, key=lambda x: x[1])
        east = max(coordinates, key=lambda x: x[0])
        bbox: List[Tuple[float, float]] = [south, west, north, east]
        return area(Polygon(bbox))

    def __get_edge_length(self, edge: Tuple[int, int]):
        return math.dist(self.layout[edge[0]], self.layout[edge[1]]) * 10000
