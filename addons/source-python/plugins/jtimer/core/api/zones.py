"""Module for zone related api functionality."""

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
def map_zones(map_id):
    """Get map zones from the api.
    https://jtimer-api.readthedocs.io/en/latest/#get--zones-map-(int-map_id)"""
    zones = None
    r = requests.get(API_CFG["host"] + f"/zones/map/{map_id}")
    if r.status_code == 200:
        zones = r.json()
    return zones, r
