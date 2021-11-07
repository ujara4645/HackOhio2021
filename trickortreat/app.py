import dataclasses

import requests
from flask import Flask, request

from . import geocoding, attom, modeling


@dataclasses.dataclass(frozen=True)
class House:
    price: float
    lat: float
    long: float
    acreage: float
    bedrooms: int
    address: str
    p_candy: float
    codes: attom.AreaCodes

    @classmethod
    def from_property(cls, property, assessment):
        price = None
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

        lat = property["location"]["latitude"]
        long = property["location"]["longitude"]

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

        p_candy = modeling.p_candy(price)

        return cls(price, lat, long, acreage, beds, "", p_candy, None)

    @staticmethod
    def is_house(property):
        return property["summary"]["propsubtype"] == "Residential"


def error_json(msg: str):
    return {"status": 500, "message": msg}


app = Flask(__name__)


@app.route("/")
def home():
    return "home"


@app.route("/api/routes")
def routes():
    location = request.args.get("location")
    radius = request.args.get("radius")
    distance = request.args.get("distance")

    if not location:
        return error_json("query parameter location missing")

    if not radius:
        return error_json("query parameter radius missing")

    if not distance:
        return error_json("query parameter distance missing")

    lat, long = geocoding.lat_long(location)

    properties, assessments = attom.all_in_radius(lat, long, radius)

    houses = [
        House.from_property(property, assessment)
        for property, assessment in zip(properties, assessments)
        if House.is_house(property)
    ]

    return {"houses": houses}

    # graph = Graph.from_houses(houses)
    # codes = attom.area_codes(lat, long)


if __name__ == "__main__":
    app.run()
