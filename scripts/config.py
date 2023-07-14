from dataclasses import dataclass
from typing import Dict, Tuple

TAG_MAPPINGS = {
    'cycleway:right': 'cycleway',
    'cycleway:left': 'cycleway',
    'cycleway:both': 'cycleway'
}


@dataclass
class BoundingBox:
    South: float
    West: float
    North: float
    East: float


@dataclass
class Config:
    # SMALL
    # bounding_box: BoundingBox = BoundingBox(
    #     South=56.3375,
    #     West=-2.8059,
    #     North=56.3437,
    #     East=-2.7855
    # )

    # BIG
    bounding_box: BoundingBox = BoundingBox(
        South=56.3284,
        West=-2.8350,
        North=56.3437,
        East=-2.7855
    )

    threshold: float = 0.15

    highway: Tuple[float, Dict[str, float]] = (1, {'cycleway': 1,
                                                   'footway': 0.8,
                                                   'path': 0.8,
                                                   'residential': 0.7,
                                                   'track': 0.7,
                                                   'tertiary': 0.3,
                                                   'secondary': 0.2,
                                                   'primary': 0.1,
                                                   'service': 0.1
                                                   })
    bicycle: Tuple[float, Dict[str, float]] = (1, {'designated': 0.8,
                                                   'yes': 0.8
                                                   })
    bicycle_road: Tuple[float, Dict[str, float]] = (1, {'yes': 1})
    cycleway: Tuple[float, Dict[str, float]] = (1, {'track': 1,
                                                    'lane': 0.8,
                                                    'shared_lane': 0.6,
                                                    'share_busway': 0.6,
                                                    'opposite_share_busway': 0.6
                                                    })
    surface: Tuple[float, Dict[str, float]] = (0.8, {'paved': 0.8,
                                                     'asphalt': 0.8,
                                                     'concrete': 0.8,
                                                     'paving_stones': 0.8})
    smoothness: Tuple[float, Dict[str, float]] = (0.8, {'excellent': 0.8,
                                                        'good': 0.8,
                                                        'intermediate': 0.8,
                                                        'bad': 0.5,
                                                        'very_bad': 0.5})
    segregated: Tuple[float, Dict[str, float]] = (0.6, {'yes': 0.7,
                                                        'no': 0.3})
    foot: Tuple[float, Dict[str, float]] = (0.6, {'designated': 0.8})

    def __getitem__(self, item):
        if item in TAG_MAPPINGS.keys():
            item = TAG_MAPPINGS[item]
        return getattr(self, item, (0, {}))

    def weight_sum(self):
        return self.highway[0] + self.bicycle[0] + self.bicycle_road[0] + self.cycleway[0] + self.foot[0] + \
            self.surface[0] + self.smoothness[0] + self.segregated[0]
