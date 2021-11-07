import math
import random
import statistics
import string
from typing import Dict, List, Set, Tuple

DEG2MILES_FACTOR = 69.172


class Graph:
    def __init__(self, nodes, edges):
        self.nodes = set(nodes)
        self.edges = set(edges)

        # precomputing
        lookup = {node.id: node for node in nodes}
        self._adjacent: Dict[Node, Set[Tuple[Node, Edge]]] = {
            node: set() for node in nodes
        }

        for edge in self.edges:
            self._adjacent[lookup[edge.start]].add((lookup[edge.end], edge))
            self._adjacent[lookup[edge.end]].add((lookup[edge.start], edge))

    def adjacent(self, node):
        if isinstance(node, str):
            return self._adjacent[Node(node, None)]
        else:
            return self._adjacent[node]

    def __repr__(self):
        return f"Graph(nodes={self.nodes}, edges={self.edges})"

    def __eq__(self, other):
        return self.nodes == other.nodes and self.edges == other.edges


class Node:
    id: str
    reward: float

    def __init__(self, id: str, reward: float):
        self.id = id
        self.reward = reward

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f"Node(id='{self.id}', reward={self.reward})"

    def __lt__(self, other):
        return self.reward < other.reward


@dataclasses.dataclass(frozen=True)
class Edge:
    start: str
    end: str
    cost: float


def _halving_initialization(houses):
    """
    Given a list of houses, find half the area with the best probabilty of candy. Remove the other half, and repeat until the area is small.
    """

    lats = [house.lat for house in houses]
    longs = [house.long for house in houses]

    range_lat = max(lats) - min(lats)
    range_long = max(longs) - min(longs)

    if range_lat > range_long:
        mean_lat = statistics.mean(lats)
        left_half = [house for house in houses if house.lat < mean_lat]
        right_half = [house for house in houses if house.lat > mean_lat]

        left_total = sum(house.p_candy for house in left_half)
        right_total = sum(house.p_candy for house in right_half)

        if right_total > left_total:
            return right_half
        else:
            return left_half

    else:
        mean_long = statistics.mean(longs)
        top_half = [house for house in houses if house.long > mean_long]
        bottom_half = [house for house in houses if house.long < mean_long]

        top_total = sum(house.p_candy for house in top_half)
        bottom_total = sum(house.p_candy for house in bottom_half)

        if bottom_total > top_total:
            return bottom_half
        else:
            return top_half


def _radius(houses) -> float:
    """
    Gets an approximation of the radius of the group of `houses` in miles.
    """
    lats = [house.lat for house in houses]
    longs = [house.long for house in houses]

    range_lat = max(lats) - min(lats)
    range_long = max(longs) - min(longs)

    return deg_to_miles(statistics.mean(lats), (range_lat + range_long) / 4)


def _total_candy(houses):
    return sum(house.p_candy for house in houses)


def _mean(houses):
    lats = [house.lat for house in houses]
    longs = [house.long for house in houses]
    return statistics.mean(lats), statistics.mean(longs)


def choose_starting(houses, walk_distance):
    while _radius(houses) > walk_distance * 1.1:
        print(len(houses), _radius(houses), _total_candy(houses))
        houses = _halving_initialization(houses)

    return _mean(houses)


def deg_to_miles(lat, degree) -> float:
    return degree * math.cos(math.radians(lat)) * DEG2MILES_FACTOR


def random_search(graph: Graph, start: Node) -> List[Node]:
    """
    Start and end at `start` node.

    Do random search.
    """
    current = start
    path = [current]
    while True:
        next_node, _ = random.choice(list(graph.adjacent(current)))
        path.append(next_node)
        current = next_node

        if next_node == start:
            break

    return path


def _random_graph() -> Graph:
    nodes = {Node(i, random.randint(1, 20)) for i in string.ascii_lowercase}
    edges = {
        Edge(
            random.choice(string.ascii_lowercase),
            random.choice(string.ascii_lowercase),
            random.randint(0, 5),
        )
        for _ in range(20)
    }

    return Graph(nodes, edges), Node(list(edges)[0].start, None)
