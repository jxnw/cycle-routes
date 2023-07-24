from scripts.data_fetcher import DataFetcher
from typing import Dict, List, Tuple
import overpy


class Model:
    def __init__(self, data_fetcher: DataFetcher, threshold=None):
        self.config = data_fetcher.config
        self.threshold = threshold if threshold is not None else self.config.threshold

        all_ways = data_fetcher.get_ways()
        nodes_on_ways = data_fetcher.get_nodes_on_ways()
        filtered_way_ids = self.filter_ways(all_ways)

        self.filtered_hyper_edges = [nodes_on_ways[way_id] for way_id in filtered_way_ids]
        self.link_counter = self.count_node_links()
        self.adj_list = self.ways_to_adj_list()
        self.node_list = [data_fetcher.get_node_by_id(node_id) for node_id in self.adj_list.keys()]

    def get_adj_list(self) -> Dict[int, List[int]]:
        return self.adj_list

    def get_node_list(self) -> List[overpy.Node]:
        return self.node_list

    def count_node_links(self) -> Dict[int, int]:
        link_counter: Dict[int, int] = {}
        for hyper_edge in self.filtered_hyper_edges:
            for node in hyper_edge:
                link_counter[node.id] = link_counter.get(node.id, 0) + 1
        return link_counter

    def ways_to_adj_list(self) -> Dict[int, List[int]]:
        adj_list: Dict[int, List[int]] = {}

        for hyper_edge in self.filtered_hyper_edges:
            cur_pointer = 0
            cur_node = hyper_edge[cur_pointer]
            next_pointer = cur_pointer + 1
            while next_pointer < len(hyper_edge):
                next_node = hyper_edge[next_pointer]
                if (self.link_counter[next_node.id] > 1 or next_pointer == len(hyper_edge) - 1) \
                        and cur_node.id != next_node.id:
                    neighbours = adj_list.get(cur_node.id, [])
                    neighbours.append(next_node.id)
                    adj_list[cur_node.id] = neighbours

                    adj_list[next_node.id] = adj_list.get(next_node.id, [])

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
