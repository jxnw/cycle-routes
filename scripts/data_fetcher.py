import overpy
from scripts.config import BoundingBox


class DataFetcher:
    api = overpy.Overpass()

    def __init__(self, box: BoundingBox):
        self.result = self.api.query(f"nwr({box.South}, {box.West}, {box.North}, {box.East}); out;")
        self.centre = self.api.query(f"node({box.Node_id}); out;")

    def get_ways(self):
        return self.result.ways

    def get_centre(self):
        return float(self.centre.nodes[0].lon), float(self.centre.nodes[0].lat)
