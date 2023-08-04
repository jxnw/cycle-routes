import unittest
from scripts.config import Config
from scripts.model import Model
from scripts.graph import GraphProcessing
from unittest.mock import Mock


class GraphProcessingTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_model = Mock(spec=Model)
        self.mock_config = Mock(spec=Config)
        self.mock_config.zero_cost = False
        self.mock_config.neighbour_eps = 0.1
        self.mock_model.config = self.mock_config
        self.mock_model.centre = (0.3, 0.5)
        self.mock_model.get_adj_list.return_value = {0: [1],
                                                     1: [0]}
        self.mock_model.get_node_pos.return_value = {0: (0.7, 0.5),
                                                     1: (0.3, 0.4)}

        self.graph = GraphProcessing(self.mock_model)

    def test(self):
        pass
