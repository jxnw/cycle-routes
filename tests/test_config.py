import unittest
from scripts.config import BoundingBox, Config, Tag, WeightedTags
from scripts.exception import AreaNotDefinedException


class ConfigTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.box_data = {
            'nodeId': 123,
            'south': 0.1,
            'west': 0.2,
            'north': 0.3,
            'east': 0.4
        }

    def test_bounding_box(self):
        box = BoundingBox.from_dict(self.box_data)

        self.assertEqual(123, box.node_id)
        self.assertEqual(0.1, box.south)
        self.assertEqual(0.2, box.west)
        self.assertEqual(0.3, box.north)
        self.assertEqual(0.4, box.east)

    def test_weighted_tags(self):
        dictionary = {
            'cycleway': {
                'weight': 4,
                'values': {'val': 1}
            }
        }

        weighted_tags = WeightedTags(dictionary)

        self.assertEqual(Tag(weight=4, values={'val': 1}), weighted_tags['cycleway:right'])
        self.assertEqual(Tag(weight=0, values={}), weighted_tags['key_does_not_exist'])

    def test_config(self):
        data = {
            'area': 'SomePlace',
            'boundingBoxes': {
                'SomePlace': self.box_data
            },
            'weightedTags': {}
        }

        config = Config.from_dict(data)

        self.assertEqual('SomePlace', config.area)

    def test_config_no_such_area(self):
        data = {
            'area': 'SomePlace',
            'boundingBoxes': {
                'SomePlace': self.box_data
            },
            'weightedTags': {}
        }

        with self.assertRaises(AreaNotDefinedException):
            config = Config.from_dict(data, area='NoSuchPlace')
