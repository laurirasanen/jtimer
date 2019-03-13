from players.entity import Player as Source_Player
from ..players.player import Player
from ..timer import timer

def steamid_to_player(steamid):
    for p in timer.players:
        if p.steamid == steamid:
            return p
    return None

def steamid_to_source_player(steamid):
    return Source_Player.from_steamid(steamid)    