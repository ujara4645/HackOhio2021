import json
import heapq

from .. import data, path, osm


def test_path_generation():
    with open("trickortreat/tests/test_graph.json", "r") as file:
        graph_dct = json.load(file)

    graph = osm.make_fully_connected(data.Graph.from_dict(graph_dct))

    start = path.choose_starting(graph, 0.1)
    random_path = path.random_search(graph, start)

    path.score_path(graph, random_path)


def test_path_sort():
    with open("trickortreat/tests/test_graph.json", "r") as file:
        graph_dct = json.load(file)

    graph = osm.make_fully_connected(data.Graph.from_dict(graph_dct))

    paths = []
    for _ in range(100):
        start = path.choose_starting(graph, 0.1)
        random_path = path.random_search(graph, start)

        score = path.score_path(graph, random_path)
        heapq.heappush(paths, (score, random_path, start))
