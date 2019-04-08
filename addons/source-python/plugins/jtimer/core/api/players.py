"""Module for players related api functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
import json
import requests

# Custom Imports
from ..config import API_CFG
from ..api import auth


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def search_player(player_id=None, steam_id=None, name=None):
    """Search for a player by player_id, steam_id or name.
    https://jtimer-api.readthedocs.io/en/latest/#get--players-search"""
    player = None
    r = requests.get(
        API_CFG["host"] + "/players/search",
        params={"player_id": player_id, "steam_id": steam_id, "name": name},
    )
    if r.status_code == 200:
        player = r.json()
    return player


def list_players(start=1, limit=50):
    """Get a list of players.
    https://jtimer-api.readthedocs.io/en/latest/#get--players-list"""
    players = []
    r = requests.get(
        API_CFG["host"] + "/players/list", params={"start": start, "limit": limit}
    )
    if r.status_code == 200:
        players = r.json()
    return players


def add_player(steam_id, username, country):
    """Add a player to the api or update an existing one.
    https://jtimer-api.readthedocs.io/en/latest/#post--players-add"""
    if not API_CFG["authenticate"]:
        return None

    access_token = auth.get_token()
    if access_token is None:
        return None

    player = None
    r = requests.post(
        API_CFG["host"] + "/players/add",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {"steam_id": steam_id, "username": username, "country": country}
        ),
    )

    if r.status_code == 200:
        player = r.json()
    else:
        print("[jtimer] Failed to add/update player.")
        print(f"Api response: {r.status_code}")
        print(r.content)

    return player
