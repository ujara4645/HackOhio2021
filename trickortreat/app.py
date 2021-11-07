import dataclasses

import requests
from flask import Flask, render_template, request

from . import geocoding, attom


@dataclasses.dataclass(frozen=True)
class House:
    price: float
    lat: float
    long: float
    acreage: float
    codes: attom.AreaCodes

    @classmethod
    def from_property(cls, property, assesment):
        pass

    @staticmethod
    def is_house(property):
        return property["summary"]["propsubtype"] == "Residential"


app = Flask(__name__)


@app.route("/")
def home():
    return "home"


@app.route("/api/routes?")
def routes():
    location = request.args.get("location")
    radius = request.args.get("radius")
    distance = request.args.get("distance")

    lat, long = geocoding.lat_long(location)

    properties, assesments = attom.all_in_radius(lat, long, radius)

    houses = [
        House.from_property(property)
        for property in properties
        if House.is_house(property)
    ]

    # graph = Graph.from_houses(houses)
    # codes = attom.area_codes(lat, long)


if __name__ == "__main__":
    app.run()
