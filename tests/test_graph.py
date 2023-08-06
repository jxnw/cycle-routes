import unittest
from scripts.config import Config
from scripts.exception import NoSuggestedPathException
from scripts.model import Model
from scripts.graph import GraphProcessing
from unittest.mock import Mock


class GraphProcessingTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_config = Mock(spec=Config)
        self.mock_config.zero_cost = False
        self.mock_config.neighbour_eps = 0.1

        self.mock_model = Mock(spec=Model)
        self.mock_model.config = self.mock_config
        self.mock_model.centre = (0.3, 0.5)
        self.mock_model.get_adj_list.return_value = {0: [1],
                                                     1: [0],
                                                     2: [3],
                                                     3: [2]}
        self.mock_model.get_node_pos.return_value = {0: (0.7, 0.5),
                                                     1: (0.3, 0.4),
                                                     2: (0.1, 0.2),
                                                     3: (0.2, 0.3)}

        self.graph = GraphProcessing(self.mock_model)

    def test_preprocessing_fully_connected(self):
        self.mock_model.get_adj_list.return_value = {0: [1],
                                                     1: [0]}
        self.mock_model.get_node_pos.return_value = {0: (0.7, 0.5),
                                                     1: (0.3, 0.4)}

        graph = GraphProcessing(self.mock_model)
        with self.assertRaises(NoSuggestedPathException):
            graph.preprocessing()

    def test_preprocessing_not_fully_connected(self):
        largest_components = self.graph.preprocessing()

        expected = [{0, 1}, {2, 3}]
        self.assertEqual(expected, largest_components)

    def test_set_zero_cost(self):
        pass
