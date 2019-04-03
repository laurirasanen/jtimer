import json
import requests

from ..config import API_CFG
from .auth import get_token


def search_player(playerid=None, steamid=None, name=None):
    player = None
    r = requests.get(
        API_CFG["host"] + "/players/search",
        params={"playerid": playerid, "steamid": steamid, "name": name},
    )
    if r.status_code == 200:
        player = r.json()
    return player


def list_players(start=1, limit=50):
    players = []
    r = requests.get(
        API_CFG["host"] + "/players/list", params={"start": start, "limit": limit}
    )
    if r.status_code == 200:
        players = r.json()
    return players


def add_player(steam_id, username, country):
    """Add a player to the api or update an existing one."""
    if not API_CFG["authenticate"]:
        return None

    access_token = get_token()
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
