import collections
import dataclasses
import xml.etree.ElementTree
from typing import List, Set

import quads
import requests

from . import app, attom, geocoding


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


@dataclasses.dataclass(frozen=True)
class Node:
    id: str
    lat: float
    long: float


@dataclasses.dataclass
class Way:
    id: str
    name: str
    nodes: List[Node]


@dataclasses.dataclass
class Vertex:
    house: app.House

    def __hash__(self):
        return hash((self.house.price, self.house.long, self.house.lat))


@dataclasses.dataclass
class Edge:
    houses: List[app.House]
    start: Vertex
    end: Vertex


class Graph:
    def __init__(self, vertices, edges):
        self.vertices = vertices
        self.edges = edges
        self.adjacency = collections.defaultdict(list)
        for edge in self.edges:
            self.adjacency[edge.start].append(edge.end)
            self.adjacency[edge.end].append(edge.start)

    def adjacent(self, v):
        return self.adjacency[v]


def parse_xml(raw_xml) -> List[Way]:
    root = xml.etree.ElementTree.fromstring(raw_xml)
    node_lookup = {}
    for node in root.iter(tag="node"):
        node_lookup[node.get("id")] = Node(
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
                print(name)

        if is_highway:
            way = Way(
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
    return Edge(houses=houses, start=Vertex(start), end=Vertex(end))


def main():
    location = "8050 N Clippinger Drive, Cincinnati OH 45243"
    radius = 0.5

    lat, long = geocoding.lat_long(location)

    properties, assessments = attom.all_in_radius(lat, long, radius)

    houses = [
        app.House.from_property(p, a)
        for p, a in zip(properties, assessments)
        if app.House.is_house(p)
    ]

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

    graph = Graph(vertices, edges)

    return graph


main()
