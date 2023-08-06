from scripts.data_fetcher import DataFetcher
from typing import Dict, List, Tuple
import overpy


class Model:
    def __init__(self, data_fetcher: DataFetcher):
        self.data_fetcher = data_fetcher
        self.config = data_fetcher.config
        self.all_ways = data_fetcher.get_ways()
        self.nodes_on_ways = data_fetcher.get_nodes_on_ways()
        self.centre = data_fetcher.get_centre()

    def get_adj_list(self, threshold=None):
        threshold = threshold if threshold is not None else self.config.threshold
        hyper_edges = [self.nodes_on_ways[way.id] for way in self.all_ways if self.eval_way(way) >= threshold]
        link_counter = self.count_node_links(hyper_edges)
        adj_list = self.ways_to_adj_list(hyper_edges, link_counter)
        return adj_list

    def get_node_pos(self, adj_list: Dict[int, List[int]]) -> Dict[int, Tuple[float, float]]:
        return self.data_fetcher.get_node_pos_by_ids(list(adj_list.keys()))

    def eval_way(self, way: overpy.Way) -> float:
        score = 0
        max_score = self.config.weighted_tags.weight_sum()
        for tag_key, tag_value in way.tags.items():
            tag = self.config.weighted_tags[tag_key]
            weight, mapping = tag.weight, tag.values
            tag_score = 0
            if tag_key == 'maxspeed':
                t_value = int(tag_value.split(' ')[0])
                for m_key, m_value in mapping.items():
                    m_range = m_key.split(',')
                    start, end = int(m_range[0]), int(m_range[1])
                    if start < t_value <= end:
                        tag_score = m_value
                        break
            else:
                tag_score = mapping.get(tag_value, 0)
            score += weight * tag_score
        return score / max_score

    @staticmethod
    def count_node_links(hyper_edges: List[List[overpy.Node]]) -> Dict[int, int]:
        link_counter: Dict[int, int] = {}
        for hyper_edge in hyper_edges:
            for node in hyper_edge:
                link_counter[node.id] = link_counter.get(node.id, 0) + 1
        return link_counter

    @staticmethod
    def ways_to_adj_list(hyper_edges: List[List[overpy.Node]], link_count: Dict[int, int]) -> Dict[int, List[int]]:
        adj_list: Dict[int, List[int]] = {}
        for h_edge in hyper_edges:
            if len(h_edge) == 0:
                continue
            cur_pointer = 0
            cur_node = h_edge[cur_pointer]
            next_pointer = cur_pointer + 1
            while next_pointer < len(h_edge):
                next_node = h_edge[next_pointer]
                if (link_count[next_node.id] > 1 or next_pointer == len(h_edge) - 1) and cur_node.id != next_node.id:
                    neighbours = adj_list.get(cur_node.id, [])
                    neighbours.append(next_node.id)
                    adj_list[cur_node.id] = neighbours
                    adj_list[next_node.id] = adj_list.get(next_node.id, [])

                    cur_pointer = next_pointer
                    next_pointer = cur_pointer + 1
                else:
                    next_pointer += 1
        return adj_list
