from scripts.config import Config
from scripts.data_fetcher import DataFetcher
from typing import Dict, List
import overpy


class Model:
    def __init__(self, config: Config):
        self.data_fetcher = DataFetcher(config.bounding_box)
        self.config = config

    def get_graph(self):
        ways = self.data_fetcher.get_ways()
        filtered_ways = self.filter_ways(ways)
        edges, all_nodes = self.ways_to_edges(filtered_ways)
        edges = self.connect_close_nodes(edges, all_nodes)
        return edges, all_nodes

    def connect_close_nodes(self, edges, all_nodes):
        eps = self.config.neighbour_eps
        for centre in all_nodes:
            for node in all_nodes:
                if abs(float(node.lon) - float(centre.lon)) <= eps and abs(float(node.lat) - float(centre.lat)) <= eps:
                    if node is not centre:
                        edges.add((centre.id, node.id))
        return edges

    def eval_way(self, way: overpy.Way):
        score = 0
        max_score = self.config.weight_sum()
        for tag, value in way.tags.items():
            weight, mapping = self.config[tag]
            score += weight * mapping.get(value, 0)
        return score / max_score

    def filter_ways(self, ways: list[overpy.Way]):
        return [way for way in ways if self.eval_way(way) > self.config.threshold]

    def node_in_area(self, node: overpy.Node):
        lon, lat = float(node.lon), float(node.lat)
        box = self.config.bounding_box
        return (lon <= box.East) and (lon >= box.West) and (lat >= box.South) and (lat <= box.North)

    def ways_to_edges(self, ways: List[overpy.Way]):
        link_counter: Dict[str, int] = {}
        for way in ways:
            nodes = way.get_nodes(resolve_missing=True)
            for node in nodes:
                link_counter[node.id] = link_counter.get(node.id, 0) + 1

        edges = set()
        all_nodes = set()
        for way in ways:
            nodes = way.get_nodes(resolve_missing=True)
            nodes = [node for node in nodes if self.node_in_area(node)]
            if len(nodes) == 2:
                edges.add((nodes[0].id, nodes[1].id))  # add way as an edge
                all_nodes.add(nodes[0])
                all_nodes.add(nodes[1])
                continue
            head = nodes[0]
            tail = nodes[len(nodes) - 1]
            prev = head
            for i in range(1, len(nodes)):
                node = nodes[i]
                if (link_counter[node.id] > 1 or node is tail) and prev.id != node.id:
                    edges.add((prev.id, node.id))
                    all_nodes.add(prev)
                    all_nodes.add(node)
                    prev = node
        return edges, list(all_nodes)