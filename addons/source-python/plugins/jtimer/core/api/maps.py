"""Module for map related api functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
import requests

# Custom Imports
from ..config import API_CFG


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def map_info(map_id):
    """Get map info by id.
    https://jtimer-api.readthedocs.io/en/latest/#post--times-insert-map-(int-map_id)"""
    map_ = None
    r = requests.get(API_CFG["host"] + f"/maps/{map_id}/info")
    if r.status_code == 200:
        map_ = r.json()
    return map_


def map_info_name(name):
    """Get map info by name.
    https://jtimer-api.readthedocs.io/en/latest/#get--maps-name-(string-mapname)"""
    map_ = None
    r = requests.get(API_CFG["host"] + f"/maps/name/{name}")
    if r.status_code == 200:
        map_ = r.json()
    return map_, r
