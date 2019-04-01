import requests

from ..config import API_CFG


def map_zones(map_id):
    zones = None
    r = requests.get(API_CFG["host"] + f"/zones/map/{map_id}")
    if r.status_code == 200:
        zones = r.json()
    return zones, r
