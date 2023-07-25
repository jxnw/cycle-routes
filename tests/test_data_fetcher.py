import overpy
import unittest
from scripts.config import BoundingBox, Config
from scripts.data_fetcher import DataFetcher
from unittest.mock import Mock, patch, call


class DataFetcherTestCase(unittest.TestCase):
    @patch('overpy.Overpass')
    def setUp(self, mock_api) -> None:
        self.mock_api = mock_api
        self.mock_config = Mock(spec=Config)
        self.mock_config.bounding_box = BoundingBox(node_id=123, south=0.1, west=0.2, north=0.3, east=0.4)
        self.data_fetcher = DataFetcher(self.mock_config)

        self.mock_node = Mock(spec=overpy.Node)
        self.mock_node.lon, self.mock_node.lat = 0.5, 0.6

    def test_makes_query(self):
        calls = [call('nwr(0.1, 0.2, 0.3, 0.4); out;'), call('node(123); out;')]
        self.mock_api.return_value.query.assert_has_calls(calls)

    def test_get_node_pos_by_ids(self):
        mock_result = Mock(spec=overpy.Result)
        mock_result.get_node.return_value = self.mock_node
        self.data_fetcher.result = mock_result

        pos = self.data_fetcher.get_node_pos_by_ids([123])

        mock_result.get_node.assert_called_once_with(123)
        self.assertEqual(pos[123], (0.5, 0.6))

    def test_get_ways(self):
        mock_result = Mock(spec=overpy.Result)
        mock_result.ways = []
        self.data_fetcher.result = mock_result

        ways = self.data_fetcher.get_ways()

        self.assertEqual(ways, [])

    def test_get_centre(self):
        mock_centre = Mock(spec=overpy.Result)
        mock_centre.nodes = [self.mock_node]
        self.data_fetcher.centre = mock_centre

        centre = self.data_fetcher.get_centre()

        self.assertEqual(centre, (0.5, 0.6))
