import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from scripts.config import Config
from scripts.model import Model


def poly_area(x, y):
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def group_area(group, layout):
    coordinates = [layout.get(node_id) for node_id in group]
    south = min(coordinates, key=lambda x: x[1])
    west = min(coordinates, key=lambda x: x[0])
    north = max(coordinates, key=lambda x: x[1])
    east = max(coordinates, key=lambda x: x[0])
    bbox = [south, west, north, east]
    return poly_area([n[0] for n in bbox], [n[1] for n in bbox])


def main(config: Config = Config()):
    model = Model(config)
    edges, all_nodes = model.get_graph()
    layout = {node.id: (float(node.lon), float(node.lat)) for node in all_nodes}

    G = nx.Graph(edges)

    sorted_groups = sorted(nx.connected_components(G), key=lambda g: group_area(g, layout), reverse=True)

    nx.draw_networkx(G, pos=layout, with_labels=False, node_size=5)
    nx.draw_networkx(G.subgraph(list(sorted_groups[0])), pos=layout, node_color='r', edge_color='r', with_labels=False,
                     node_size=5)
    nx.draw_networkx(G.subgraph(list(sorted_groups[1])), pos=layout, node_color='m', edge_color='m', with_labels=False,
                     node_size=5)
    nx.draw_networkx(G.subgraph(list(sorted_groups[2])), pos=layout, node_color='g', edge_color='g', with_labels=False,
                     node_size=5)
    plt.show()


if __name__ == '__main__':
    main()
