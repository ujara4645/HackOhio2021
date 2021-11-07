import collections
import dataclasses
import xml.etree.ElementTree
from typing import List

from . import attom, modeling


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
class House:
    price: float
    lat: float
    long: float
    acreage: float
    bedrooms: int
    address: str
    p_candy: float
    node: xml.etree.ElementTree.ElementTree = None
    way: xml.etree.ElementTree.ElementTree = None
    above: bool = False
    codes: attom.AreaCodes = None
    corner: bool = False

    @classmethod
    def from_property(cls, property, assessment):
        price = 0
        assessment = assessment["assessment"]
        if "assessed" in assessment and "assdttlvalue" in assessment["assessed"]:
            price = assessment["assessed"]["assdttlvalue"]
        elif (
            "calculations" in assessment
            and "calcttlvalue" in assessment["calculations"]
        ):
            price = assessment["calculations"]["calcttlvalue"]
        elif "market" in assessment and "mktttlvalue" in assessment["market"]:
            price = assessment["market"]["mktttlvalue"]

        lat = float(property["location"]["latitude"])
        long = float(property["location"]["longitude"])

        acreage = 0
        if "lot" in property and "lotSize1" in property["lot"]:
            acreage = property["lot"]["lotSize1"]

        beds = 0
        if (
            "building" in property
            and "rooms" in property["building"]
            and "beds" in property["building"]["rooms"]
        ):
            beds = property["building"]["rooms"]["beds"]

        address = ""
        if "oneLine" in property["address"]:
            address = property["address"]["oneLine"]

        p_candy = modeling.p_candy(price)

        return cls(price, lat, long, acreage, beds, address, p_candy)

    @staticmethod
    def is_house(property):
        return property["summary"]["propsubtype"] == "Residential"

    @classmethod
    def from_dict(cls, dct):
        way_dct = dct.pop("way")
        nodes = [Node(**node_dct) for node_dct in way_dct.pop("nodes")]
        way = Way(**way_dct, nodes=nodes)
        return cls(**dct, way=way)


@dataclasses.dataclass
class Vertex:
    house: House

    def __hash__(self):
        return hash((self.house.price, self.house.long, self.house.lat))

    @classmethod
    def from_dict(cls, dct):
        return cls(house=House.from_dict(dct.pop("house")))

    @property
    def reward(self):
        return self.house.p_candy * 100


@dataclasses.dataclass
class Edge:
    houses: List[House]
    start: Vertex
    end: Vertex

    @classmethod
    def from_dict(cls, dct):
        houses = [House.from_dict(d) for d in dct.pop("houses")]
        start = Vertex.from_dict(dct.pop("start"))
        end = Vertex.from_dict(dct.pop("end"))

        return cls(houses, start, end)

    @property
    def cost(self) -> float:
        # TODO
        return len(self.houses)

    @property
    def reward(self):
        return sum(house.p_candy for house in self.houses)


@dataclasses.dataclass
class Graph:
    vertices: List[Vertex]
    edges: List[Edge]

    def __post_init__(self):
        self.adjacency = collections.defaultdict(list)
        for edge in self.edges:
            self.adjacency[edge.start].append(edge.end)
            self.adjacency[edge.end].append(edge.start)

    def adjacent(self, v):
        return self.adjacency[v]

    @classmethod
    def from_dict(cls, dct):
        vertices = [Vertex.from_dict(vertex_dct) for vertex_dct in dct["vertices"]]
        edges = [Edge.from_dict(edge_dct) for edge_dct in dct["edges"]]
        return cls(vertices, edges)
