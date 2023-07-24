# import unittest
# import overpy
# from scripts.config import BoundingBox, Config, WeightedTags
# from scripts.data_fetcher import DataFetcher
# from scripts.model import Model
# from unittest.mock import Mock
#
#
# class ModelTestCase(unittest.TestCase):
#     def setUp(self) -> None:
#         self.mock_data_fetcher = Mock(spec=DataFetcher)
#
#         self.mock_config = Mock(spec=Config)
#         self.mock_config.bounding_box = BoundingBox(node_id=123, south=0.1, west=0.2, north=0.3, east=0.4)
#         self.mock_config.threshold = 0.5
#
#         self.mock_data_fetcher.config = self.mock_config
#         self.model = Model(self.mock_data_fetcher)
#
#     def test_eval_way_one_tag(self):
#         weighted_tags = WeightedTags({
#             'tag': {
#                 'weight': 4,
#                 'values': {'val': 1}
#             }
#         })
#         self.mock_config.weighted_tags = weighted_tags
#         self.mock_data_fetcher.config = self.mock_config
#         self.model = Model(self.mock_data_fetcher)
#
#         mock_way = Mock(spec=overpy.Way)
#         mock_way.tags = {
#             'tag': 'val'
#         }
#         score = self.model.eval_way(mock_way)
#
#         self.assertEqual(score, 1)
#
#     def test_eval_way_empty_tag(self):
#         weighted_tags = WeightedTags({
#             'tag': {
#                 'weight': 4,
#                 'values': {'val': 1}
#             }
#         })
#         self.mock_config.weighted_tags = weighted_tags
#         self.mock_data_fetcher.config = self.mock_config
#         self.model = Model(self.mock_data_fetcher)
#
#         mock_way = Mock(spec=overpy.Way)
#         mock_way.tags = {}
#         score = self.model.eval_way(mock_way)
#
#         self.assertEqual(score, 0)
#
#     def test_eval_way_tag_does_not_exist(self):
#         weighted_tags = WeightedTags({
#             'tag': {
#                 'weight': 4,
#                 'values': {'val': 1}
#             }
#         })
#         self.mock_config.weighted_tags = weighted_tags
#         self.mock_data_fetcher.config = self.mock_config
#         self.model = Model(self.mock_data_fetcher)
#
#         mock_way = Mock(spec=overpy.Way)
#         mock_way.tags = {
#             'non_exist_tag': 'value'
#         }
#         score = self.model.eval_way(mock_way)
#
#         self.assertEqual(score, 0)
#
#     def test_eval_way_value_does_not_exist(self):
#         weighted_tags = WeightedTags({
#             'tag': {
#                 'weight': 4,
#                 'values': {'val': 1}
#             }
#         })
#         self.mock_config.weighted_tags = weighted_tags
#         self.mock_data_fetcher.config = self.mock_config
#         self.model = Model(self.mock_data_fetcher)
#
#         mock_way = Mock(spec=overpy.Way)
#         mock_way.tags = {
#             'tag': 'non_exist_val'
#         }
#         score = self.model.eval_way(mock_way)
#
#         self.assertEqual(score, 0)
#
#     def test_filter_ways(self):
#         pass
#
#     def test_node_in_area(self):
#         node = Mock(spec=overpy.Node)
#         node.lat, node.lon = 0.2, 0.3
#
#         is_in_area = self.model.node_in_area(node)
#
#         self.assertTrue(is_in_area)
#
#     def test_ways_to_dol(self):
#         pass
