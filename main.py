import argparse
import json
import os
from scripts.config import Config
from scripts.data_fetcher import DataFetcher
from scripts.graph import GraphProcessing
from scripts.model import Model


def main():
    parser = argparse.ArgumentParser(description='PICI - A planner for improving cycling infrastructure.')
    parser.add_argument('--config', type=str, default='configuration.json', help='path to the configuration file')
    parser.add_argument('--save', type=str, default='images/', help='save the generated graphs to a directory')

    args = parser.parse_args()

    root = os.path.dirname(__file__)

    with open(os.path.join(root, args.config), 'r') as f:
        config_json = json.load(f)
        config = Config.from_dict(config_json)

    data_fetcher = DataFetcher(config)
    model = Model(data_fetcher)
    graph = GraphProcessing(model)

    components = graph.preprocessing()
    graph.display(filepath=os.path.join(root, args.save, 'cycle_friendly.svg'))
    graph.display(components, filepath=os.path.join(root, args.save, 'components.svg'))

    if len(components) < 2:
        print('Graph is fully connected, no paths suggested')
    else:
        region_from, region_to = components[0], components[1]
        strategies = config.strategies

        if strategies.get('overall', False):
            dist, path = graph.shortest_path_overall(region_from, region_to)
            graph.display_path_between_subgraph(path, region_from, region_to,
                                                filepath=os.path.join(root, args.save, 'path_overall.svg'))

        if strategies.get('centreTown', False):
            dist, path = graph.shortest_path_town_centre(region_from, region_to)
            graph.display_path_between_subgraph(path, region_from, region_to,
                                                filepath=os.path.join(root, args.save, 'path_town_centre.svg'))

        if strategies.get('centreLocal', False):
            dist, path = graph.shortest_path_local_centre(region_from, region_to)
            graph.display_path_between_subgraph(path, region_from, region_to,
                                                filepath=os.path.join(root, args.save, 'path_local_centre.svg'))

        if strategies.get('existing', False):
            dist, path = graph.shortest_path_existing(region_from, region_to)
            graph.display_path_between_subgraph(path, region_from, region_to,
                                                filepath=os.path.join(root, args.save, 'path_existing.svg'))


if __name__ == '__main__':
    main()
