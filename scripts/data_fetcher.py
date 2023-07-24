import overpy
from scripts.config import Config
from typing import Dict, List, Tuple


class DataFetcher:
    def __init__(self, config: Config):
        api = overpy.Overpass()
        box = config.bounding_box

        self.config = config
        self.result = api.query(f"nwr({box.south}, {box.west}, {box.north}, {box.east}); out;")
        self.centre = api.query(f"node({box.node_id}); out;")

        self.ways_to_nodes_mapping = self.get_ways_to_nodes_mapping()

    def get_node_by_id(self, node_id: int) -> overpy.Node:
        return self.result.get_node(node_id, resolve_missing=True)

    def get_ways(self) -> List[overpy.Way]:
        return self.result.ways

    def get_ways_to_nodes_mapping(self):
        mapping: Dict[int, List[overpy.Node]] = {}
        for way in self.result.ways:
            nodes = way.get_nodes(resolve_missing=True)
            mapping[way.id] = nodes
        return mapping

    def get_centre(self) -> Tuple[float, float]:
        return float(self.centre.nodes[0].lon), float(self.centre.nodes[0].lat)
