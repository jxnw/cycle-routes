import os
from scripts.config import Config
from scripts.graph_processing import GraphProcessing
from scripts.model import Model
import time


def main(config: Config = Config()):
    root = os.path.dirname(__file__)

    graph = GraphProcessing(config)
    graph.draw_graph_with_largest_groups(os.path.join(root, '..', 'images', 'groups.png'))
    # graph.connect_close_nodes()
    # graph.draw_graph_with_largest_groups(os.path.join(root, '..', 'images', 'connected_close_nodes.png'))


if __name__ == '__main__':
    main()
