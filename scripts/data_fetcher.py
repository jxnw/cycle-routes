import overpy
from scripts.config import BoundingBox


class DataFetcher:
    api = overpy.Overpass()

    def __init__(self, box: BoundingBox):
        self.result = self.api.query(f"way({box.South}, {box.West}, {box.North}, {box.East}); out;")

    def get_ways(self):
        return self.result.ways
