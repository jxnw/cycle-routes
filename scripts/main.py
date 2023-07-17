import os
from scripts.config import Config
from scripts.graph_processing import GraphProcessing


def main(config: Config = Config()):
    root = os.path.dirname(__file__)

    graph_processing = GraphProcessing(config)
    graph_processing.draw_graph_with_largest_groups(os.path.join(root, '..', 'images', 'groups.png'))
    graph_processing.connect_close_nodes()
    graph_processing.draw_graph_with_largest_groups(os.path.join(root, '..', 'images', 'connected_close_nodes.png'))

    dist, path = graph_processing.shortest_path_between_central_nodes()
    graph_processing.draw_graph_with_suggested_path(path,
                                                    os.path.join(root, '..', 'images', 'shortest_path_central.png'))
    print(dist)
    dist, path = graph_processing.shortest_path_among_all_nodes()
    graph_processing.draw_graph_with_suggested_path(path,
                                                    os.path.join(root, '..', 'images', 'shortest_path_all.png'))
    print(dist)


if __name__ == '__main__':
    main()
