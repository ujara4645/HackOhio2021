import collections
import dataclasses
import heapq
from typing import Set, Dict, Tuple, List


class Graph:
    def __init__(self, nodes, edges):
        self.nodes = set(nodes)
        self.edges = set(edges)

        # precomputing
        lookup = {node.id: node for node in nodes}
        self.adjacent: Dict[Node, Set[Tuple[Node, Edge]]] = {
            node: set() for node in nodes
        }

        for edge in self.edges:
            self.adjacent[lookup[edge.start]].add((lookup[edge.end], edge))
            self.adjacent[lookup[edge.end]].add((lookup[edge.start], edge))


class Node:
    id: str
    reward: float

    def __init__(self, id: str, reward: float):
        self.id = id
        self.reward = reward

    def __hash__(self):
        return hash(self.id + str(self.reward))

    def __repr__(self):
        return f"Node(id='{self.id}', reward={self.reward})"

    def __lt__(self, other):
        return self.reward < other.reward


@dataclasses.dataclass(frozen=True)
class Edge:
    start: str
    end: str
    cost: float


def reconstruct_path(came_from: Dict, current: Node) -> List[Node]:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)

    return list(reversed(path))


def heuristic(graph, node, end) -> float:
    return 0


def best_path(graph, start, end) -> Set[Node]:

    # Reduce any cycles in the graph to a single point
    # graph = reduce_cycles(graph)

    # Find best path using shitty search

    path = [(start, 0)]

    current = path[-1]

    g = collections.defaultdict(lambda: float("inf"))
    g[start] = 0

    f = collections.defaultdict(lambda: float("inf"))
    f[start] = heuristic(graph, start, end)

    while open_set:
        current = heapq.heappop(open_set)

        if current == end and came_from:
            return reconstruct_path(came_from, current)

        for neighbor, edge in graph.adjacent[current]:
            maybe_g_score = g[current] + edge.cost

            if maybe_g_score < g[neighbor]:
                came_from[neighbor] = current
                g[neighbor] = maybe_g_score
                f[neighbor] = g[neighbor] + heuristic(graph, neighbor, end)
                heapq.heappush(open_set, neighbor)

    breakpoint()
    raise ValueError("No path found!")
