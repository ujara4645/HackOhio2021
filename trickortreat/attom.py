import requests
import dataclasses

API_KEY = "92639ad4ddf2479340d09e7c255f206f"


HEADERS = {
    "accept": "application/json",
    "apikey": API_KEY,
}

PAGE_ARGS = {"PageSize": 1_000_000}


def _raise_for_atomm_status(response):
    if int(response["status"]["code"]) != 0:
        raise RuntimeError("API error: " + response["status"]["long_description"])


def community(area_code):
    r = requests.get(
        "https://api.gateway.attomdata.com/communityapi/v2.0.0/Area/Full",
        params={"AreaId": area_code},
        headers=HEADERS,
    )
    r.raise_for_status()

    res = r.json()["response"]

    _raise_for_atomm_status(res)

    return res["result"]["package"]["item"][0]


@dataclasses.dataclass(frozen=True)
class AreaCodes:
    state: str = None  # ST
    county: str = None  # CO
    neighborhood: str = None  # ND
    residential_subdivision: str = None  # RS
    school_attendance_zone: str = None  # SB
    school_district: str = None  # DB
    place: str = None  # PL
    county_subdivision: str = None  # CS
    zip_code: str = None  # ZI


def area_codes(lat, long):
    r = requests.get(
        "https://api.gateway.attomdata.com/areaapi/v2.0.0/hierarchy/lookup",
        params={"latitude": lat, "longitude": long},
        headers=HEADERS,
    )
    r.raise_for_status()

    res = r.json()["response"]

    _raise_for_atomm_status(res)

    codes = {}
    for item in res["result"]["package"]["item"]:
        if item["type"] == "ST":
            codes["state"] = item["id"]
        elif item["type"] == "CO":
            codes["county"] = item["id"]
        elif item["type"] == "ND":
            codes["neighborhood"] = item["id"]
        elif item["type"] == "RS":
            codes["residential_subdivision"] = item["id"]
        elif item["type"] == "SB":
            codes["school_attendance_zone"] = item["id"]
        elif item["type"] == "DB":
            codes["school_district"] = item["id"]
        elif item["type"] == "PL":
            codes["place"] = item["id"]
        elif item["type"] == "CS":
            codes["county_subdivision"] = item["id"]
        elif item["type"] == "ZI":
            codes["zip_code"] = item["id"]

    return AreaCodes(**codes)


def all_in_radius(lat, long, radius):
    r = requests.get(
        "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/snapshot",
        params={"latitude": lat, "longitude": long, "radius": radius, **PAGE_ARGS},
        headers=HEADERS,
    )
    r.raise_for_status()

    res = r.json()
    _raise_for_atomm_status(res)

    properties = res["property"]

    r = requests.get(
        "https://api.gateway.attomdata.com/propertyapi/v1.0.0/assessment/snapshot",
        params={"latitude": lat, "longitude": long, "radius": radius, **PAGE_ARGS},
        headers=HEADERS,
    )
    r.raise_for_status()

    res = r.json()
    _raise_for_atomm_status(res)

    assessments = res["property"]

    return properties, assessments
