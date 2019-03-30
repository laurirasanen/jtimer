import requests

from ..config import API_CFG


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
