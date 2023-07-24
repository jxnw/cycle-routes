import argparse
import json
import os
from scripts.config import Config
from scripts.data_fetcher import DataFetcher
from scripts.model import Model
from scripts.graph_processing import GraphProcessing


def main():
    parser = argparse.ArgumentParser(description='PICI - A planner for improving cycling infrastructure.')
    parser.add_argument('--config', type=str, default='configuration.json', help='path to the configuration file')
    parser.add_argument('--save', type=str, default='../images/', help='save the generated graphs to a directory')

    args = parser.parse_args()

    root = os.path.dirname(__file__)

    with open(os.path.join(root, args.config), 'r') as f:
        config_json = json.load(f)
        config = Config.from_dict(config_json)

    data_fetcher = DataFetcher(config)
    model_default = Model(data_fetcher, threshold=0)
    model_friendly = Model(data_fetcher)
    graph_default = GraphProcessing(model_default)
    graph_friendly = GraphProcessing(model_friendly)

    # graph_processing.draw_graph_with_largest_groups(os.path.join(root, args.save, 'connected_components.png'))
    #
    # dist, path = graph_processing.shortest_path_among_all_nodes()
    # graph_processing.draw_graph_with_suggested_path(path, os.path.join(root, args.save, 'path_all.png'))
    #
    # dist, path = graph_processing.shortest_path_between_central_nodes_in_town()
    # graph_processing.draw_graph_with_suggested_path(path, os.path.join(root, args.save, 'path_central_town.png'))
    #
    # dist, path = graph_processing.shortest_path_between_central_nodes_in_region()
    # graph_processing.draw_graph_with_suggested_path(path, os.path.join(root, args.save, 'path_central_region.png'))
    #
    # dist, path = graph_processing.shortest_path_with_existing_paths()
    # graph_processing.draw_graph_with_suggested_path(path, os.path.join(root, args.save, 'path_with_existing.png'))


if __name__ == '__main__':
    main()
