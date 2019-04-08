"""Module for conversions."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
import math

# Source.Python Imports
from players.dictionary import PlayerDictionary
from engines.server import server

# Custom Imports
from ..timer import timer

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
player_instances = PlayerDictionary()


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def steamid_to_player(steamid):
    """Convert steamid to player."""
    for player in timer.Timer.instance().players:
        if player.steamid == steamid:
            return player
    return None


def userid_to_player(userid):
    """Conver userid to player."""
    steamid = userid_to_source_player(userid).raw_steamid.to_steamid2()
    return steamid_to_player(steamid)


def userid_to_source_player(userid):
    """Conver userid to Source.Python player."""
    try:
        return player_instances.from_userid(userid)
    except ValueError:
        return None


def ticks_to_timestamp(ticks):
    """Convert ticks to a timestamp."""
    ticks = abs(ticks)

    milliseconds, seconds = math.modf(ticks * server.tick_interval)
    minutes = math.floor(seconds / 60)
    hours = math.floor(minutes / 60)

    seconds -= minutes * 60
    minutes -= hours * 60

    timestamp = ""

    if 0 < hours < 10:
        timestamp += f"0{hours}:"
    elif hours >= 10:
        timestamp += f"{hours}:"

    if minutes == 0 or 0 < minutes < 10:
        timestamp += f"0{minutes}:"
    elif minutes >= 10:
        timestamp += f"{minutes}:"

    if seconds == 0 or 0 < seconds < 10:
        timestamp += f"0{str(seconds)[0]}."
    elif seconds >= 10:
        timestamp += f"{str(seconds)[:2]}."

    if milliseconds == 0:
        timestamp += f"00"
    elif milliseconds > 0:
        timestamp += str(milliseconds)[2:4]

    return timestamp
