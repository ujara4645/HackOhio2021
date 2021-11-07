import requests

API_KEY = "9d2ebef0-3f60-11ec-8c88-e7f140e5f156"

HEADERS = {
    "accept": "application/json",
    "apikey": API_KEY,
}


def lat_long(address):
    r = requests.get(
        "https://app.geocodeapi.io/api/v1/search",
        params={"text": address},
        headers=HEADERS,
    )
    r.raise_for_status()

    res = r.json()

    return tuple(reversed(res["features"][0]["geometry"]["coordinates"]))
