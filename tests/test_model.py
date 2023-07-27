import unittest
import overpy
from scripts.config import BoundingBox, Config, WeightedTags
from scripts.data_fetcher import DataFetcher
from scripts.model import Model
from unittest.mock import Mock


class ModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_data_fetcher = Mock(spec=DataFetcher)

        self.mock_config = Mock(spec=Config)
        self.mock_config.bounding_box = BoundingBox(node_id=123, south=0.1, west=0.2, north=0.3, east=0.4)
        self.mock_config.threshold = 0.5

        self.mock_data_fetcher.config = self.mock_config
        self.model = Model(self.mock_data_fetcher)

    def test_eval_way_one_tag(self):
        weighted_tags = WeightedTags({
            'tag': {
                'weight': 4,
                'values': {'val': 1}
            }
        })
        self.mock_config.weighted_tags = weighted_tags
        self.mock_data_fetcher.config = self.mock_config
        self.model = Model(self.mock_data_fetcher)

        mock_way = Mock(spec=overpy.Way)
        mock_way.tags = {
            'tag': 'val'
        }
        score = self.model.eval_way(mock_way)

        self.assertEqual(score, 1)

    def test_eval_way_empty_tag(self):
        weighted_tags = WeightedTags({
            'tag': {
                'weight': 4,
                'values': {'val': 1}
            }
        })
        self.mock_config.weighted_tags = weighted_tags
        self.mock_data_fetcher.config = self.mock_config
        self.model = Model(self.mock_data_fetcher)

        mock_way = Mock(spec=overpy.Way)
        mock_way.tags = {}
        score = self.model.eval_way(mock_way)

        self.assertEqual(score, 0)

    def test_eval_way_tag_does_not_exist(self):
        weighted_tags = WeightedTags({
            'tag': {
                'weight': 4,
                'values': {'val': 1}
            }
        })
        self.mock_config.weighted_tags = weighted_tags
        self.mock_data_fetcher.config = self.mock_config
        self.model = Model(self.mock_data_fetcher)

        mock_way = Mock(spec=overpy.Way)
        mock_way.tags = {
            'non_exist_tag': 'value'
        }
        score = self.model.eval_way(mock_way)

        self.assertEqual(score, 0)

    def test_eval_way_value_does_not_exist(self):
        weighted_tags = WeightedTags({
            'tag': {
                'weight': 4,
                'values': {'val': 1}
            }
        })
        self.mock_config.weighted_tags = weighted_tags
        self.mock_data_fetcher.config = self.mock_config
        self.model = Model(self.mock_data_fetcher)

        mock_way = Mock(spec=overpy.Way)
        mock_way.tags = {
            'tag': 'non_exist_val'
        }
        score = self.model.eval_way(mock_way)

        self.assertEqual(score, 0)

    def test_count_node_links(self):
        mock_node_0 = Mock(spec=overpy.Node)
        mock_node_0.id = 0
        mock_node_1 = Mock(spec=overpy.Node)
        mock_node_1.id = 1
        mock_node_2 = Mock(spec=overpy.Node)
        mock_node_2.id = 2
        hyper_edges = [[mock_node_0, mock_node_1], [mock_node_0, mock_node_2]]

        link_counter = self.model.count_node_links(hyper_edges)
        expected = {0: 2, 1: 1, 2: 1}

        self.assertEqual(expected, link_counter)

    def test_ways_to_adj_list(self):
        mock_node_0 = Mock(spec=overpy.Node)
        mock_node_0.id = 0
        mock_node_1 = Mock(spec=overpy.Node)
        mock_node_1.id = 1
        mock_node_2 = Mock(spec=overpy.Node)
        mock_node_2.id = 2
        hyper_edges = [[mock_node_0, mock_node_1], [mock_node_0, mock_node_2]]
        link_counter = {0: 2, 1: 1, 2: 1}

        adj_list = self.model.ways_to_adj_list(hyper_edges, link_counter)
        expected = {0, 1, 2}

        self.assertEqual(expected, adj_list.keys())
