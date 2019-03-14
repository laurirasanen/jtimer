from .state import State

class Player():
    def __init__(self, steamid, name):
        self.steamid = steamid
        self.name = name
        self.state = State()