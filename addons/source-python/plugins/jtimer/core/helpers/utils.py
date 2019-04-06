from players import PlayerInfo

def isPlayer(playerObj):
    if PlayerInfo.is_fake_client(playerObj) or PlayerInfo.is_hltv(playerObj) or playerObj.steamid == "BOT":
        return False
    else:
        return True