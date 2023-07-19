import os
from scripts.config import Config
from scripts.graph_processing import GraphProcessing


def main(config: Config = Config()):
    root = os.path.dirname(__file__)

    graph_processing = GraphProcessing(config)
    graph_processing.draw_graph_with_largest_groups(os.path.join(root, '..', 'images', 'largest_groups.png'))

    dist, path = graph_processing.shortest_path_among_all_nodes(graph_processing.largest_groups[0],
                                                                graph_processing.largest_groups[1])
    graph_processing.draw_graph_with_suggested_path(path,
                                                    os.path.join(root, '..', 'images', 'path_all.png'))

    dist, path = graph_processing.shortest_path_between_central_nodes_in_town(graph_processing.largest_groups[0],
                                                                              graph_processing.largest_groups[1])
    graph_processing.draw_graph_with_suggested_path(path,
                                                    os.path.join(root, '..', 'images', 'path_central_town.png'))

    dist, path = graph_processing.shortest_path_between_central_nodes_in_region(graph_processing.largest_groups[0],
                                                                                graph_processing.largest_groups[1])
    graph_processing.draw_graph_with_suggested_path(path,
                                                    os.path.join(root, '..', 'images', 'path_central_region.png'))


if __name__ == '__main__':
    main()
