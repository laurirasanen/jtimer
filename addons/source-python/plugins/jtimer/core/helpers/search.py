from filters.players import PlayerIter

def findPlayerIdWithName(name):
    for player in PlayerIter():
        if not player.is_fake_client():
            if name in player.name.lower():
                return player
