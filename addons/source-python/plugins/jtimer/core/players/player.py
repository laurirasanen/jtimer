import mathlib

from .state import State
from .state import Timer_Mode
from ..timer import timer
from ..helpers.converts import userid_to_source_player


class Player:
    def __init__(self, playerinfo, index):
        self.userid = playerinfo.userid
        self.steamid = playerinfo.steamid
        self.index = index
        self.name = playerinfo.name
        self.state = State(self)

    def teleport_to_start(self):
        if self.state.timer_mode == Timer_Mode.MAP:
            start = mathlib.Vector(
                timer.current_map.start_zone.center[0],
                timer.current_map.start_zone.center[1],
                timer.current_map.start_zone.center[2]
                - timer.current_map.start_zone.extents[2],
            )
            source_player = userid_to_source_player(self.userid)
            source_player.teleport(start, mathlib.NULL_QANGLE, mathlib.NULL_VECTOR)
