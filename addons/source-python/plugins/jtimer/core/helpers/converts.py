from players.dictionary import PlayerDictionary
from engines.server import server
from ..timer import timer

import math

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


def ticks_to_timestamp(ticks):
    milliseconds, seconds = math.modf(ticks * server.tick_interval)
    minutes = math.floor(seconds / 60)
    hours = math.floor(minutes / 60)

    seconds -= minutes * 60
    minutes -= hours * 60

    timestamp = ""

    if hours > 0 and hours < 10:
        timestamp += f"0{hours}:"
    elif hours >= 10:
        timestamp += f"{hours}:"

    if minutes == 0 or (minutes > 0 and minutes < 10):
        timestamp += f"0{minutes}:"
    elif minutes >= 10:
        timestamp += f"{minutes}:"

    if seconds == 0 or (seconds > 0 and seconds < 10):
        timestamp += f"0{str(seconds)[0]}."
    elif seconds >= 10:
        timestamp += f"{str(seconds)[:2]}."

    if milliseconds == 0:
        timestamp += f"00"
    elif milliseconds > 0:
        timestamp += str(milliseconds)[2:4]

    return timestamp
