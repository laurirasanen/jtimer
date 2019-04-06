from players import PlayerInfo
from players.entity import Player

def isPlayer(playerObj):
    if PlayerInfo.is_fake_client(playerObj) or PlayerInfo.is_hltv(playerObj) or playerObj.steamid == "BOT":
        return False
    else:
        return True

def returnSpectators(playerIndex, formatType = "name"):
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