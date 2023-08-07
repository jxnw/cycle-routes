import overpy
import unittest
from scripts.config import BoundingBox, Config, WeightedTags
from scripts.data_fetcher import DataFetcher
from scripts.model import Model
from unittest.mock import Mock


class ModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_config = Mock(spec=Config)
        self.mock_config.bounding_box = BoundingBox(node_id=123, south=0.1, west=0.2, north=0.3, east=0.4)
        self.mock_config.threshold = 0.5

        self.mock_data_fetcher = Mock(spec=DataFetcher)
        self.mock_data_fetcher.config = self.mock_config
        self.mock_data_fetcher.get_ways.return_value = []

        self.model = Model(self.mock_data_fetcher)

    def test_get_node_pos(self):
        adj_list = {123: [], 456: []}
        self.model.get_node_pos(adj_list)
        self.mock_data_fetcher.get_node_pos_by_ids.assert_called_once_with([123, 456])

    def test_get_node_pos_empty(self):
        adj_list = {}
        self.model.get_node_pos(adj_list)
        self.mock_data_fetcher.get_node_pos_by_ids.assert_called_once_with([])

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

        self.assertEqual(1, score)

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

        mock_way = Mock(spec=overpy.Way, tags={})
        score = self.model.eval_way(mock_way)

        self.assertEqual(0, score)

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

        self.assertEqual(0, score)

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

        self.assertEqual(0, score)

    def test_eval_way_maxspeed_in_range(self):
        weighted_tags = WeightedTags({
            'maxspeed': {
                'weight': 1,
                'values': {'10, 15': 0.5}
            }
        })
        self.mock_config.weighted_tags = weighted_tags
        self.mock_data_fetcher.config = self.mock_config
        self.model = Model(self.mock_data_fetcher)

        mock_way = Mock(spec=overpy.Way)
        mock_way.tags = {
            'maxspeed': '13'
        }
        score = self.model.eval_way(mock_way)

        self.assertEqual(0.5, score)

    def test_eval_way_maxspeed_not_in_range(self):
        weighted_tags = WeightedTags({
            'maxspeed': {
                'weight': 1,
                'values': {'10, 15': 0.5}
            }
        })
        self.mock_config.weighted_tags = weighted_tags
        self.mock_data_fetcher.config = self.mock_config
        self.model = Model(self.mock_data_fetcher)

        mock_way = Mock(spec=overpy.Way)
        mock_way.tags = {
            'maxspeed': '8'
        }
        score = self.model.eval_way(mock_way)

        self.assertEqual(0, score)

    def test_eval_way_maxspeed_has_unit(self):
        weighted_tags = WeightedTags({
            'maxspeed': {
                'weight': 1,
                'values': {'10, 15': 0.5}
            }
        })
        self.mock_config.weighted_tags = weighted_tags
        self.mock_data_fetcher.config = self.mock_config
        self.model = Model(self.mock_data_fetcher)

        mock_way = Mock(spec=overpy.Way)
        mock_way.tags = {
            'maxspeed': '13 mph'
        }
        score = self.model.eval_way(mock_way)

        self.assertEqual(0.5, score)

    def test_count_node_links(self):
        mock_node_0 = Mock(spec=overpy.Node, id=0)
        mock_node_1 = Mock(spec=overpy.Node, id=1)
        mock_node_2 = Mock(spec=overpy.Node, id=2)
        hyper_edges = [[mock_node_0, mock_node_1], [mock_node_0, mock_node_2]]

        link_counter = self.model.count_node_links(hyper_edges)
        expected = {0: 2, 1: 1, 2: 1}

        self.assertEqual(expected, link_counter)

    def test_ways_to_adj_list(self):
        mock_node_0 = Mock(spec=overpy.Node, id=0)
        mock_node_1 = Mock(spec=overpy.Node, id=1)
        mock_node_2 = Mock(spec=overpy.Node, id=2)
        hyper_edges = [[mock_node_0, mock_node_1], [mock_node_0, mock_node_2]]
        link_counter = {0: 2, 1: 1, 2: 1}

        adj_list = self.model.ways_to_adj_list(hyper_edges, link_counter)
        expected = {0, 1, 2}

        self.assertEqual(expected, adj_list.keys())

    def test_ways_to_adj_list_empty_edge(self):
        mock_node_0 = Mock(spec=overpy.Node, id=0)
        mock_node_1 = Mock(spec=overpy.Node, id=1)
        mock_node_2 = Mock(spec=overpy.Node, id=2)
        hyper_edges = [[], [mock_node_0, mock_node_2]]
        link_counter = {0: 1, 2: 1}

        adj_list = self.model.ways_to_adj_list(hyper_edges, link_counter)
        expected = {0, 2}

        self.assertEqual(expected, adj_list.keys())

    def test_ways_to_adj_list_cycle_edge(self):
        mock_node_0 = Mock(spec=overpy.Node, id=0)
        mock_node_1 = Mock(spec=overpy.Node, id=1)
        mock_node_2 = Mock(spec=overpy.Node, id=2)
        hyper_edges = [[mock_node_0, mock_node_0], [mock_node_1, mock_node_2]]
        link_counter = {0: 2, 1: 1, 2: 1}

        adj_list = self.model.ways_to_adj_list(hyper_edges, link_counter)
        expected = {1, 2}

        self.assertEqual(expected, adj_list.keys())

    def test_get_adj_list(self):
        mock_way = Mock(spec=overpy.Way, id=12)
        self.model.all_ways = [mock_way]
        self.model.nodes_on_ways = {12: [1, 2]}
        self.model.eval_way = Mock(return_value=0.7)
        self.model.count_node_links = Mock(return_value={1: 1, 2: 1})
        self.model.ways_to_adj_list = Mock(return_value={1: [2], 2: []})

        adj_list = self.model.get_adj_list()

        self.assertEqual({1: [2], 2: []}, adj_list)
        self.model.eval_way.assert_called_once_with(mock_way)
        self.model.ways_to_adj_list.assert_called_once_with([[1, 2]], {1: 1, 2: 1})
