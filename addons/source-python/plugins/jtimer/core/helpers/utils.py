from geolite2 import geolite2

from filters.players import PlayerIter
from players.entity import Player
from players import PlayerInfo
from players.helpers import index_from_playerinfo


def is_player(player):
    if isinstance(player, PlayerInfo):
        player = Player(index_from_playerinfo(player))

    if (
        PlayerInfo.is_fake_client(player.playerinfo)
        or PlayerInfo.is_hltv(player.playerinfo)
        or player.steamid == "BOT"
    ):
        return False
    else:
        return True


def returnSpectators(playerIndex, formatType="name"):
    spectators = Player(playerIndex).spectators
    specList = []
    for player in spectators:
        specList.append(player.name)

    if formatType == "name":
        if len(specList) == 0:
            return "None"
        if len(specList) == 1:
            return specList[0]
        elif len(specList) == 2:
            return "%s & %s".format(specList[0], specList[1])
        else:
            last = specList.pop()
            return specList.join(", ") + " & " + last

    else:
        return str(len(specList))


def get_players():
    players = []
    for p in PlayerIter():
        if is_player(p):
            players.append(p)
    return players


def get_player_indices():
    indices = []
    for p in PlayerIter():
        if is_player(p):
            indices.append(p.index)
    return indices


def get_country(ip):
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
