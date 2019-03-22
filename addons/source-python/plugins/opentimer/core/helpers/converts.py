from players.dictionary import PlayerDictionary
from ..timer import timer

player_instances = PlayerDictionary()


def steamid_to_player(steamid):
    for p in timer.players:
        if p.steamid == steamid:
            return p
    return None


def userid_to_player(userid):
    steamid = userid_to_source_player(userid).steamid
    return steamid_to_player(steamid)


def userid_to_source_player(userid):
    return player_instances.from_userid(userid)
