import math
import random
import statistics
import string
from typing import Dict, List, Set, Tuple

from . import data

DEG2MILES_FACTOR = 69.172


def _halving_initialization(vertices):
    """
    Given a list of houses, find half the area with the best probabilty of candy. Remove the other half, and repeat until the area is small.
    """

    lats = [vertex.house.lat for vertex in vertices]
    longs = [vertex.house.long for vertex in vertices]

    range_lat = max(lats) - min(lats)
    range_long = max(longs) - min(longs)

    if range_lat > range_long:
        mean_lat = statistics.mean(lats)
        left_half = [vertex for vertex in vertices if vertex.house.lat < mean_lat]
        right_half = [vertex for vertex in vertices if vertex.house.lat > mean_lat]

        left_total = sum(vertex.house.p_candy for vertex in left_half)
        right_total = sum(vertex.house.p_candy for vertex in right_half)

        if right_total > left_total:
            return right_half
        else:
            return left_half

    else:
        mean_long = statistics.mean(longs)
        top_half = [vertex for vertex in vertices if vertex.house.long > mean_long]
        bottom_half = [vertex for vertex in vertices if vertex.house.long < mean_long]

        top_total = sum(vertex.house.p_candy for vertex in top_half)
        bottom_total = sum(vertex.house.p_candy for vertex in bottom_half)

        if bottom_total > top_total:
            return bottom_half
        else:
            return top_half


def _radius(vertices) -> float:
    """
    Gets an approximation of the radius of the group of `houses` in miles.
    """
    lats = [vertex.house.lat for vertex in vertices]
    longs = [vertex.house.long for vertex in vertices]

    range_lat = max(lats) - min(lats)
    range_long = max(longs) - min(longs)

    return deg_to_miles(statistics.mean(lats), (range_lat + range_long) / 4)


def _total_candy(houses):
    return sum(house.p_candy for house in houses)


def _mean(houses):
    lats = [house.lat for house in houses]
    longs = [house.long for house in houses]
    return statistics.mean(lats), statistics.mean(longs)


def choose_starting(graph: data.Graph, walk_distance: float) -> data.Vertex:
    vertices = graph.vertices
    while _radius(vertices) > walk_distance * 1.1:
        # print(len(vertices), _radius(vertices), _total_candy(vertices))
        vertices = _halving_initialization(vertices)

    return random.choice(vertices)


def deg_to_miles(lat, degree) -> float:
    return degree * math.cos(math.radians(lat)) * DEG2MILES_FACTOR


def random_search(graph: data.Graph, start: data.Vertex) -> List[data.Vertex]:
    """
    Start and end at `start` node.

    Do random search.
    """
    current = start
    path = [current]
    while True:
        next_node = random.choice(list(graph.adjacent(current)))
        path.append(next_node)
        current = next_node

        if next_node == start and len(path) > 5:
            break

    return path


def score_path(graph, path):

    edge_lookup = {}

    for edge in graph.edges:
        edge_lookup[(edge.start, edge.end)] = edge

    total_net_value_array = []
    seen = set()
    for start, end in zip(path, path[1:]):
        try:
            edge = edge_lookup[start, end]
        except KeyError:
            edge = edge_lookup[end, start]

        net_val = end.reward + edge.reward

        if (start, end) in seen:
            net_val -= 1

        total_net_value_array.append(net_val)

        seen.add((start, end))
        seen.add((end, start))

    return sum(total_net_value_array) + random.uniform(-0.1, 0.1)
