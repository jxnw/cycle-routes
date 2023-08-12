import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from geopy import distance
from matplotlib import colormaps
from scripts.model import Model
from typing import Dict, List, Set, Tuple


class GraphProcessing:
    def __init__(self, model: Model):
        self.model = model
        self.config = model.config
        self.centre = model.centre

        adj_list_unfiltered = self.model.get_adj_list(threshold=0)
        adj_list = self.model.get_adj_list()

        self.layout = self.model.get_node_pos(adj_list_unfiltered)

        self.graph_unfiltered = nx.Graph(adj_list_unfiltered)
        self.graph = nx.Graph(adj_list)

        self.edge_length = {edge: self.get_edge_length(edge) for edge in self.graph_unfiltered.edges}

    def preprocessing(self):
        nx.set_node_attributes(self.graph_unfiltered, self.layout, 'pos')
        nx.set_edge_attributes(self.graph_unfiltered, self.edge_length, 'length')
        nx.set_node_attributes(self.graph, self.layout, 'pos')
        nx.set_edge_attributes(self.graph, self.edge_length, 'length')
        self.connect_close_nodes()
        sorted_groups = self.get_connected_components(self.graph)
        return sorted_groups

    def shortest_path_overall(self, from_region: Set[int], to_region: Set[int]):
        """
        Find the shortest path between any node in from_region and any node in to_region.
        """
        dist = float('inf')
        shortest_path = []
        for target in to_region:
            dist_temp, path = nx.multi_source_dijkstra(self.graph_unfiltered, from_region, target=target,
                                                       weight='length')
            if dist_temp < dist:
                dist = dist_temp
                shortest_path = path
        shortest_path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
        return dist, shortest_path_edges

    def shortest_path_town_centre(self, from_region: Set[int], to_region: Set[int]):
        """
        Find the shortest path between the central node in from_region and the central node in to_region,
        where the central node in a region is the node nearest to the centre of the town.
        """
        node_from = min(from_region, key=lambda n: self.get_geodesic_distance(self.layout[n], self.centre))
        node_to = min(to_region, key=lambda n: self.get_geodesic_distance(self.layout[n], self.centre))
        dist, shortest_path = nx.single_source_dijkstra(self.graph_unfiltered, node_from, node_to, weight='length')
        shortest_path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
        path = self.trim_path(shortest_path_edges, from_region, to_region)
        return self.get_path_length(path), path

    def shortest_path_local_centre(self, from_region: Set[int], to_region: Set[int]):
        """
        Find the shortest path between the central node in from_region and the central node in to_region,
        where the central node in a region is the node nearest to the centre of the region.
        """
        centre_from, centre_to = self.get_centre_of_nodes(from_region), self.get_centre_of_nodes(to_region)
        node_from = min(from_region, key=lambda n: self.get_geodesic_distance(self.layout[n], centre_from))
        node_to = min(to_region, key=lambda n: self.get_geodesic_distance(self.layout[n], centre_to))
        dist, shortest_path = nx.single_source_dijkstra(self.graph_unfiltered, node_from, node_to, weight='length')
        shortest_path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
        path = self.trim_path(shortest_path_edges, from_region, to_region)
        return self.get_path_length(path), path

    def shortest_path_existing(self, from_region: Set[int], to_region: Set[int]):
        """
        Find the shortest path between any node in from_region and any node in to_region, with path cost of
        existing cycle-friendly paths set to zero.
        """
        graph_unfiltered_copy = self.graph_unfiltered.copy()
        edge_length = self.set_zero_cost(self.edge_length)
        nx.set_edge_attributes(graph_unfiltered_copy, edge_length, 'length')

        dist = float('inf')
        shortest_path = []
        for target in to_region:
            dist_temp, path = nx.multi_source_dijkstra(graph_unfiltered_copy, from_region, target=target,
                                                       weight='length')
            if dist_temp < dist:
                dist = dist_temp
                shortest_path = path
        shortest_path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
        path = self.trim_path(shortest_path_edges, from_region, to_region)
        return self.get_path_length(path, graph_unfiltered_copy), path

    def set_zero_cost(self, edge_length: Dict[Tuple[int, int], float]):
        for edge in edge_length.keys():
            if edge in self.graph.edges:
                edge_length[edge] = 0
        return edge_length

    def get_connected_components(self, graph) -> List[Set[int]]:
        return sorted(nx.connected_components(graph), key=self.group_size, reverse=True)

    def get_centre_of_nodes(self, nodes: Set[int]) -> Tuple[float, float]:
        g = nx.subgraph(self.graph, nodes)
        centre = list(nx.center(g, weight='length'))[0]
        return self.layout[centre]

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
        new_edges_with_length = self.get_geometric_edges(self.graph)
        self.graph.add_weighted_edges_from(new_edges_with_length, weight='length')
        new_edges_with_length = self.get_geometric_edges(self.graph_unfiltered)
        self.graph_unfiltered.add_weighted_edges_from(new_edges_with_length, weight='length')

    def get_geometric_edges(self, graph) -> List[Tuple[int, int, float]]:
        new_edges = nx.geometric_edges(graph, radius=self.config.neighbour_eps)
        new_edges_with_length = [(u, v, self.get_edge_length((u, v))) for (u, v) in new_edges]
        return new_edges_with_length

    def group_size(self, group: Set[int]):
        subgraph = self.graph.subgraph(group)
        size = 0
        for edge in subgraph.edges:
            size += subgraph.get_edge_data(*edge)['length']
        return size

    def get_edge_length(self, edge: Tuple[int, int]):
        return self.get_geodesic_distance(self.layout[edge[0]], self.layout[edge[1]])

    def get_path_length(self, path: List[Tuple[int, int]], graph=None):
        if graph is None:
            graph = self.graph_unfiltered
        length = 0
        for (u, v) in path:
            length += graph.edges[u, v]['length']
        return length

    @staticmethod
    def get_geodesic_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]):
        return distance.distance(tuple(reversed(pos1)), tuple(reversed(pos2))).km

    @staticmethod
    def trim_path(path: List[Tuple[int, int]], from_region: Set[int], to_region: Set[int]):
        enum_edges = list(enumerate(path))
        edges_from = [(i, edge) for (i, edge) in enum_edges if edge[0] in from_region and edge[1] not in from_region]
        start = edges_from[-1][0]
        edges_to = [(i, edge) for (i, edge) in enum_edges[start:] if edge[0] not in to_region and edge[1] in to_region]
        end = edges_to[0][0]
        return path[start:end + 1]
