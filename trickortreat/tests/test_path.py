from ..path import best_path, Graph, Node, Edge


def test_best_path1():
    start = Node("s", 0)
    end = start
    graph = Graph(
        nodes=[start, Node("a", 10), Node("b", 15), Node("c", 10)],
        edges=[
            Edge("s", "a", 1),
            Edge("a", "b", 2),
            Edge("b", "c", 2),
            Edge("a", "c", 3),
        ],
    )

    expected = [start, Node("a", 10), Node("b", 15), Node("c", 10), Node("a", 10), end]

    actual = best_path(graph, start, end)

    assert actual == expected
