import requests

from ..config import API_CFG


def map_info(map_id):
    map_ = None
    r = requests.get(API_CFG["host"] + f"/maps/{map_id}/info")
    if r.status_code == 200:
        map_ = r.json()
    return map_


def map_info_name(name):
    map_ = None
    r = requests.get(API_CFG["host"] + f"/maps/name/{name}")
    if r.status_code == 200:
        map_ = r.json()
    return map_, r
