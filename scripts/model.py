from scripts.config import Config
from scripts.data_fetcher import DataFetcher
from typing import Dict, List
import overpy


class Model:
    def __init__(self, config: Config):
        self.data_fetcher = DataFetcher(config.bounding_box)
        self.config = config

    def get_graph(self, threshold=None):
        ways = self.data_fetcher.get_ways()
        filtered_ways = self.filter_ways(ways, threshold)
        dol, all_nodes = self.ways_to_dol(filtered_ways)
        return dol, all_nodes

    def eval_way(self, way: overpy.Way):
        score = 0
        max_score = self.config.weighted_tags.weight_sum()
        for tag, value in way.tags.items():
            weight, mapping = self.config.weighted_tags[tag]
            score += weight * mapping.get(value, 0)
        return score / max_score

    def filter_ways(self, ways: list[overpy.Way], threshold=None):
        threshold = threshold if threshold is not None else self.config.threshold
        return [way for way in ways if self.eval_way(way) >= threshold]

    def node_in_area(self, node: overpy.Node):
        lon, lat = float(node.lon), float(node.lat)
        box = self.config.bounding_box
        return (lon <= box.East) and (lon >= box.West) and (lat >= box.South) and (lat <= box.North)

    def ways_to_dol(self, ways: List[overpy.Way]):
        link_counter: Dict[int, int] = {}
        for way in ways:
            nodes = way.get_nodes(resolve_missing=True)
            nodes = [node for node in nodes if self.node_in_area(node)]
            for node in nodes:
                link_counter[node.id] = link_counter.get(node.id, 0) + 1

        all_nodes = set()
        dol: Dict[int, List[int]] = {}
        for way in ways:
            nodes = way.get_nodes(resolve_missing=True)
            nodes = [node for node in nodes if self.node_in_area(node)]

            cur_pointer = 0
            next_pointer = cur_pointer + 1
            while next_pointer < len(nodes):
                next_node = nodes[next_pointer]
                if (link_counter[next_node.id] > 1 or next_pointer == len(nodes) - 1) \
                        and nodes[cur_pointer].id != next_node.id:
                    neighbours = dol.get(nodes[cur_pointer].id, [])
                    neighbours.append(next_node.id)
                    dol[nodes[cur_pointer].id] = neighbours
                    all_nodes.add(nodes[cur_pointer])
                    all_nodes.add(next_node)
                    cur_pointer = next_pointer
                    next_pointer = cur_pointer + 1
                else:
                    next_pointer += 1
        return dol, all_nodes
