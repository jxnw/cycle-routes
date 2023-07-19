import overpy
from scripts.config import BoundingBox
from typing import List, Tuple


class DataFetcher:
    api = overpy.Overpass()

    def __init__(self, box: BoundingBox):
        self.result = self.api.query(f"nwr({box.South}, {box.West}, {box.North}, {box.East}); out;")
        self.centre = self.api.query(f"node({box.Node_id}); out;")

    def get_node_by_id(self, node_id: int) -> overpy.Node:
        return self.result.get_node(node_id, resolve_missing=True)

    def get_ways(self) -> List[overpy.Way]:
        return self.result.ways

    def get_centre(self) -> Tuple[float, float]:
        return float(self.centre.nodes[0].lon), float(self.centre.nodes[0].lat)
