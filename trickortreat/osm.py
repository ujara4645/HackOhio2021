import collections
import dataclasses
import xml.etree.ElementTree
from typing import List
import logging

import quads
import requests

logger = logging.getLogger("osm")

from . import data, geocoding


def _data(bbox):
    """"""
    r = requests.get(
        "https://overpass-api.de/api/map?bbox=-83.01389,39.99656,-83.00804,39.99973",
        params={"bbox": ",".join(map(str, bbox))},
    )
    r.raise_for_status()

    return r.text


def get_data(houses):
    return _data(_bbox(houses))


def _bbox(houses):
    return (
        min(house.long for house in houses),
        min(house.lat for house in houses),
        max(house.long for house in houses),
        max(house.lat for house in houses),
    )


def _dfs(graph: data.Graph, start: data.Vertex) -> List[data.Vertex]:
    queue = [start]
    vertices = [start]
    seen = set([start])

    while queue:
        print(len(queue), len(seen))
        current = queue.pop()
        seen.add(current)
        for vertex in graph.adjacent(current):
            vertices.append(vertex)
            if vertex not in seen:
                queue.append(vertex)

    return vertices


def _get_components(graph: data.Graph) -> List[List[data.Vertex]]:
    components = []
    current_component = []
    seen = set()
    for vertex in graph.vertices:
        if vertex in seen:
            continue

        current_component.append(vertex)
        current_component.extend(_dfs(graph, vertex))

        for v in current_component:
            seen.add(v)

        components.append(current_component)
        current_component = []

    return components


def _min_dist_between_components(c1: List[data.Vertex], c2: List[data.Vertex]) -> float:
    min_dist = float("inf")
    best_pair = (None, None)

    for v1 in c1:
        for v2 in c2:
            dist = (v1.house.lat - v2.house.lat) ** 2 + (
                v1.house.long - v2.house.long
            ) ** 2
            if dist < min_dist:
                min_dist = dist
                best_pair = (v1, v2)

    return min_dist, best_pair


def _graph_with_connected_components(graph, vertex_pair) -> data.Graph:
    v1, v2 = vertex_pair
    edge = data.Edge([], v1, v2)

    graph.edges.append(edge)
    graph.adjacency[edge.start].append(edge.end)
    graph.adjacency[edge.end].append(edge.start)

    return graph


def make_fully_connected(graph: data.Graph) -> data.Graph:
    """
    Takes a graph and identifies disconnected components. Then it iterates through all the vertices of each pair of connected components and finds the shortest pair, and adds another edge there.
    """
    components = _get_components(graph)

    print(len(components))

    if len(components) < 2:
        logger.info("No need to connect graph!")
        return graph

    best_pair = (None, None)
    best_dist = float("inf")

    for c1 in components:
        for c2 in components:
            if c1 == c2:
                continue

            dist, pair = _min_dist_between_components(c1, c2)
            if dist < best_dist:
                best_dist = dist
                best_pair = pair

    graph = _graph_with_connected_components(graph, best_pair)

    return make_fully_connected(graph)


def make_node_lookup(root):
    node_lookup = {}
    for node in root.iter(tag="node"):
        node_lookup[node.get("id")] = node

    return node_lookup


def is_above(node, way, loc):
    # checks if the node is "above" the way
    # get the node and it's two neighbor nodes

    for before, after in zip(way.nodes, way.nodes[1:]):
        if before.id == node.id:
            break

    # now we have before and after
    x1 = before.lat
    y1 = before.long

    x2 = after.lat
    y2 = after.long

    x, y = loc

    d = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
    return d < 0


def parse_xml(raw_xml) -> List[data.Way]:
    root = xml.etree.ElementTree.fromstring(raw_xml)
    node_lookup = {}
    for node in root.iter(tag="node"):
        node_lookup[node.get("id")] = data.Node(
            node.get("id"), float(node.get("lat")), float(node.get("lon"))
        )

    ways = []
    for way in root.iter(tag="way"):
        is_highway = False
        name = "no-name"
        for tag in way.iter(tag="tag"):
            if tag.get("k") == "highway":
                is_highway = True

            if tag.get("k") == "name":
                name = tag.get("v")

        if is_highway:
            way = data.Way(
                way.get("id"),
                name,
                [node_lookup[nd.get("ref")] for nd in way.iter(tag="nd")],
            )
            ways.append(way)

    return ways


def make_quadtree(houses, ways):
    lats = [house.lat for house in houses]
    longs = [house.long for house in houses]

    range_lat = max(lats) - min(lats)
    range_long = max(longs) - min(longs)

    center = ((max(lats) + min(lats)) / 2, (max(longs) + min(longs)) / 2)

    tree = quads.QuadTree(center, range_lat, range_long)

    for way in ways:
        for node in way.nodes:
            try:
                tree.insert((node.lat, node.long), data=(way, node))
            except ValueError:
                pass

    return tree


def min_distance_squared_to_any(houses, other):
    dist = float("inf")

    for house in houses:
        dist = min(dist, (house.lat - other.lat) ** 2 + (house.long - other.long) ** 2)

    return dist


def make_edge(houses, corners):
    # start and end are the houses in way_to_corner_lookup[way_id] that are closest to any house in the edge
    if len(corners) < 2:
        return None

    (_, start), (_, end) = sorted(
        ((min_distance_squared_to_any(houses, other), other) for other in corners)
    )[:2]
    return data.Edge(houses=houses, start=data.Vertex(start), end=data.Vertex(end))


def make_graph(houses):
    raw_xml = get_data(houses)
    ways = parse_xml(raw_xml)

    way_lookup = collections.defaultdict(list)
    for way in ways:
        for node in way.nodes:
            way_lookup[node].append(way)

    tree = make_quadtree(houses, ways)

    valid_houses = []
    for house in houses:
        closest = tree.nearest_neighbors((house.lat, house.long), count=1)
        if not closest:
            continue
        way, node = closest[0].data
        house.way = way
        house.node = node
        house.above = is_above(node, way, (house.lat, house.long))
        if len(way_lookup[house.node]) > 1:
            house.corner = True
        valid_houses.append(house)

    # Now for each house, I have an osm node and the osm way it's closest to.
    # So I can find the side of the way for the house

    # edges are all houses that are on a way that's named the same.
    way_to_house_lookup = collections.defaultdict(list)
    way_to_corner_lookup = collections.defaultdict(list)
    for house in valid_houses:
        if house.corner:
            way_to_corner_lookup[house.way.id].append(house)
        else:
            way_to_house_lookup[house.way.id].append(house)

    edges = []
    vertices = set()

    for way_id in way_to_house_lookup:
        above_houses = []
        below_houses = []
        for house in way_to_house_lookup[way_id]:
            if house.above:
                above_houses.append(house)
            else:
                below_houses.append(house)

        maybe_edge = None
        if above_houses:
            maybe_edge = make_edge(above_houses, way_to_corner_lookup[way_id])
        if below_houses:
            maybe_edge = make_edge(below_houses, way_to_corner_lookup[way_id])

        if maybe_edge:
            edges.append(maybe_edge)
            vertices.add(maybe_edge.start)
            vertices.add(maybe_edge.end)

    graph = data.Graph(list(vertices), list(edges))

    return make_fully_connected(graph)
