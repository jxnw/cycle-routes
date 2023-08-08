from dataclasses import dataclass
from scripts.exception import AreaNotDefinedException
from typing import Dict

TAG_MAPPINGS = {
    'cycleway:right': 'cycleway',
    'cycleway:left': 'cycleway',
    'cycleway:both': 'cycleway'
}


@dataclass
class BoundingBox:
    node_id: int
    south: float
    west: float
    north: float
    east: float

    @classmethod
    def from_dict(cls, data):
        return cls(
            node_id=data['nodeId'],
            south=data['south'],
            west=data['west'],
            north=data['north'],
            east=data['east']
        )


@dataclass
class Tag:
    weight: float
    values: Dict[str, float]

    @classmethod
    def from_dict(cls, data):
        return cls(
            weight=data.get('weight', 0),
            values=data.get('values', {})
        )


@dataclass
class WeightedTags:
    tags: Dict[str, Tag]

    def __init__(self, dictionary):
        self.tags = {}
        for k, v in dictionary.items():
            self.tags[k] = Tag.from_dict(v)

    def __getitem__(self, item):
        if item in TAG_MAPPINGS.keys():
            item = TAG_MAPPINGS[item]
        return self.tags.get(item, Tag(weight=0, values={}))

    def weight_sum(self):
        return sum([tag.weight for tag in self.tags.values()])


@dataclass
class Config:
    area: str
    threshold: float
    neighbour_eps: float
    strategies: Dict[str, bool]
    bounding_box: BoundingBox
    weighted_tags: WeightedTags

    @classmethod
    def from_dict(cls, data, area=None):
        if area is None:
            area = data.get("area")
        bounding_boxes = data.get('boundingBoxes')
        if area not in bounding_boxes.keys():
            raise AreaNotDefinedException(f"{area} does not have a corresponding bounding box in configuration.json")
        return cls(
            area=area,
            threshold=data.get('threshold'),
            neighbour_eps=data.get('neighbourEps'),
            strategies=data.get('strategies'),
            bounding_box=BoundingBox.from_dict(data.get('boundingBoxes').get(area)),
            weighted_tags=WeightedTags(data.get('weightedTags'))
        )
