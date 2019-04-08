"""Module for assorted utility functions."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
from geolite2 import geolite2

# Source.Python Imports
from filters.players import PlayerIter
from players.entity import Player
from players import PlayerInfo
from players.helpers import index_from_playerinfo, index_from_userid


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def is_player(player):
    """Check if Source.Python player or playerinfo belongs to a valid human player."""
    if isinstance(player, PlayerInfo):
        player = Player(index_from_playerinfo(player))

    if (
        PlayerInfo.is_fake_client(player.playerinfo)
        or PlayerInfo.is_hltv(player.playerinfo)
        or player.steamid == "BOT"
    ):
        return False

    return True


def return_spectators(player_index, format_type="name"):
    """Get a list of players spectators."""
    spectators = Player(player_index).spectators
    spec_list = []
    for player in spectators:
        spec_list.append(player.name)

    if format_type == "name":
        if not spec_list:
            return "None"

        if len(spec_list) == 1:
            return spec_list[0]

        if len(spec_list) == 2:
            return f"{spec_list[0]} & {spec_list[1]}"

        last = spec_list.pop()
        return ", ".join(str(spectator) for spectator in spec_list) + " & " + last

    if format_type == "count":
        return str(len(spec_list))

    for player in spectators:
        spec_list.append(index_from_userid(player.userid))
    return spec_list


def get_players():
    """Get a list of currently connected players."""
    players = []
    for p in PlayerIter():
        if is_player(p):
            players.append(p)
    return players


def get_player_indices():
    """Get a list of currently connected players' indices."""
    indices = []
    for p in PlayerIter():
        if is_player(p):
            indices.append(p.index)
    return indices


def get_country(ip):
    """Get country from ip address."""
    name = "United States"
    code = "US"

    if ip is None:
        return (name, code)

    reader = geolite2.reader()
    match = reader.get(ip)

    if match is not None:
        code = match["country"]["iso_code"]
        name = match["country"]["names"]["en"]

    return (name, code)
