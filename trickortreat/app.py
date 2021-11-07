import heapq
import json
import logging
from flask import Flask, request, url_for

from . import attom, data, geocoding, modeling, osm, path

logger = logging.getLogger("app")


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

    logger.info(
        f"Got request. [location={location}, radius={radius}, distance={distance}]"
    )

    if not location:
        return error_json("query parameter location missing")

    if not radius:
        return error_json("query parameter radius missing")

    if not distance:
        return error_json("query parameter distance missing")

    lat, long = geocoding.lat_long(location)

    logger.info(f"Got lat and long. [lat={lat}, long={long}]")

    properties, assessments = attom.all_in_radius(lat, long, radius)

    logger.info(f"Got properties. [properties={len(properties)}]")

    houses = [
        data.House.from_property(property, assessment)
        for property, assessment in zip(properties, assessments)
        if data.House.is_house(property)
    ]

    logger.info(f"Got houses. [houses={len(houses)}]")

    graph = osm.make_graph(houses)

    # with open("trickortreat/tests/test_graph.json", "r") as file:
    #     graph_dct = json.load(file)

    # graph = osm.make_fully_connected(data.Graph.from_dict(graph_dct))

    logger.info("Made graph.")

    paths = []
    for _ in range(1000):
        start = path.choose_starting(graph, 0.1)
        random_path = path.random_search(graph, start)

        score = path.score_path(graph, random_path)
        heapq.heappush(paths, (score, random_path, start))

    logger.info(f"Got all paths. [paths={len(paths)}]")

    return {"houses": [], "status": 200, "graph": graph, "paths": paths[:4]}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run()
