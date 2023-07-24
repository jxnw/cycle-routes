from scripts.data_fetcher import DataFetcher
from typing import Dict, List, Tuple
import overpy


class Model:
    def __init__(self, data_fetcher: DataFetcher, threshold=None):
        self.config = data_fetcher.config
        self.ways_to_nodes_mapping = data_fetcher.ways_to_nodes_mapping
        self.threshold = threshold if threshold is not None else self.config.threshold

        all_ways = data_fetcher.get_ways()
        friendly_way_ids = self.filter_ways(all_ways)
        link_counter = self.get_link_counter()

        self.adj_list = self.get_adj_list_from_ways(link_counter, friendly_way_ids)
        self.node_list = [data_fetcher.get_node_by_id(node_id) for node_id in self.adj_list.keys()]

    def get_graph(self) -> Tuple[Dict[int, List[int]], List[overpy.Node]]:
        return self.adj_list, self.node_list

    def get_link_counter(self) -> Dict[int, int]:
        link_counter: Dict[int, int] = {}
        for _, nodes in self.ways_to_nodes_mapping.items():
            for node in set(nodes):
                link_counter[node.id] = link_counter.get(node.id, 0) + 1
        return link_counter

    def get_adj_list_from_ways(self, link_counter: Dict[int, int], way_ids: List[int]) -> Dict[int, List[int]]:
        adj_list: Dict[int, List[int]] = {}

        friendly_mapping = [self.ways_to_nodes_mapping[way_id] for way_id in way_ids]
        for nodes in friendly_mapping:
            nodes = [node for node in nodes if self.node_in_area(node)]

            cur_pointer = 0
            cur_node = nodes[cur_pointer]
            next_pointer = cur_pointer + 1
            while next_pointer < len(nodes):
                next_node = nodes[next_pointer]
                if (link_counter[next_node.id] > 1 or next_pointer == len(nodes) - 1) and cur_node.id != next_node.id:
                    neighbours = adj_list.get(cur_node.id, [])
                    neighbours.append(next_node.id)
                    adj_list[cur_node.id] = neighbours

                    neighbours = adj_list.get(next_node.id, [])
                    neighbours.append(cur_node.id)
                    adj_list[next_node.id] = neighbours

                    cur_pointer = next_pointer
                    next_pointer = cur_pointer + 1
                else:
                    next_pointer += 1
        return adj_list

    def filter_ways(self, ways: List[overpy.Way]) -> List[int]:
        return [way.id for way in ways if self.eval_way(way) >= self.threshold]

    def eval_way(self, way: overpy.Way) -> float:
        score = 0
        max_score = self.config.weighted_tags.weight_sum()
        for tag_key, tag_value in way.tags.items():
            tag = self.config.weighted_tags[tag_key]
            weight, mapping = tag.weight, tag.values
            tag_score = 0
            if tag_key == 'maxspeed':
                for m_key, m_value in mapping.items():
                    m_range = m_key.split(',')
                    start, end = int(m_range[0]), int(m_range[1])
                    if start < m_value <= end:
                        tag_score = m_value
                        break
            else:
                tag_score = mapping.get(tag_value, 0)
            score += weight * tag_score
        return score / max_score

    def node_in_area(self, node: overpy.Node) -> bool:
        lon, lat = float(node.lon), float(node.lat)
        box = self.config.bounding_box
        return (lon <= box.east) and (lon >= box.west) and (lat >= box.south) and (lat <= box.north)
