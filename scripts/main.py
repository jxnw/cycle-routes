from scripts.config import Config
from scripts.graph_processing import GraphProcessing


def main(config: Config = Config()):
    graph = GraphProcessing(config)
    graph.draw_graph_with_largest_groups()


if __name__ == '__main__':
    main()
