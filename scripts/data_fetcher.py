import overpy
from scripts.config import Config
from typing import Dict, List, Tuple


class DataFetcher:
    def __init__(self, config: Config):
        api = overpy.Overpass()

        self.config = config
        self.box = config.bounding_box
        self.result = api.query(f"nwr({self.box.south}, {self.box.west}, {self.box.north}, {self.box.east}); out;")
        self.centre = api.query(f"node({self.box.node_id}); out;")

    def get_node_pos_by_ids(self, node_ids: List[int]) -> Dict[int, Tuple[float, float]]:
        node_pos: Dict[int, Tuple[float, float]] = {}
        for node_id in node_ids:
            node = self.result.get_node(node_id)
            node_pos[node_id] = (float(node.lon), float(node.lat))
        return node_pos

    def get_nodes_on_ways(self) -> Dict[int, List[overpy.Node]]:
        mapping: Dict[int, List[overpy.Node]] = {}
        for way in self.result.ways:
            nodes = way.get_nodes(resolve_missing=True)
            nodes = [node for node in nodes if self.node_in_area(node)]
            mapping[way.id] = nodes
        return mapping

    def get_ways(self) -> List[overpy.Way]:
        return self.result.ways

    def get_centre(self) -> Tuple[float, float]:
        return float(self.centre.nodes[0].lon), float(self.centre.nodes[0].lat)

    def node_in_area(self, node: overpy.Node) -> bool:
        lon, lat = float(node.lon), float(node.lat)
        return (lon <= self.box.east) and (lon >= self.box.west) and (lat >= self.box.south) and (lat <= self.box.north)
