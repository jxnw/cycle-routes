import igraph as ig
from typing import Dict, List
from config import Config
import matplotlib.pyplot as plt
import overpy


def eval_way(way, config: Config = Config()):
    score = 0
    max_score = config.weight_sum()
    for tag, value in way.tags.items():
        weight, mapping = config[tag]
        score += weight * mapping.get(value, 0)
    return score / max_score


def ways_to_edges(ways: List[overpy.Way]):
    link_counter: Dict[str, int] = {}
    for way in ways:
        nodes = way.get_nodes(resolve_missing=True)
        for node in nodes:
            link_counter[node.id] = link_counter.get(node.id, 0) + 1

    edges = []
    all_nodes = set()
    for way in ways:
        nodes = way.get_nodes(resolve_missing=True)
        if len(nodes) == 2:
            edges.append([nodes[0].id, nodes[1].id])  # add way as an edge
            all_nodes.add(nodes[0].id)
            all_nodes.add(nodes[1].id)
            continue
        head = nodes[0]
        tail = nodes[len(nodes) - 1]
        prev = head
        for i in range(1, len(nodes) - 1):
            node = nodes[i]
            if link_counter[node.id] > 1:
                # break the way on node
                edges.append([prev.id, node.id])
                all_nodes.add(prev.id)
                all_nodes.add(node.id)
                prev = node
                if i == len(nodes) - 2:
                    edges.append([node.id, tail.id])
                    all_nodes.add(tail.id)
    return edges, list(all_nodes)


def main():
    api = overpy.Overpass()
    result = api.query("nwr(56.3344, -2.8153, 56.3434, -2.7836); out;")
    # result = api.query("nwr(56.3384, -2.8037, 56.3425, -2.7883); out;")

    ways = []
    for way in result.ways:
        score = eval_way(way)
        if score > 0:
            ways.append(way)

    edges, all_nodes = ways_to_edges(ways)
    node_mapping = {node_id: idx for idx, node_id in enumerate(all_nodes)}
    mapped_edges = [[node_mapping[edge[0]], node_mapping[edge[1]]] for edge in edges]

    g = ig.Graph(n=len(all_nodes), edges=mapped_edges)
    fig, ax = plt.subplots()
    ig.plot(g, target=ax)
    plt.show()


if __name__ == '__main__':
    main()
