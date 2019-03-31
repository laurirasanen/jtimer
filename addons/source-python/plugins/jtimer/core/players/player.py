from mathlib import Vector

from .state import State
from .state import Timer_Mode
from ..timer import timer
from ..helpers.converts import userid_to_source_player


NULL_VECTOR = Vector(0.0, 0.0, 0.0)


class Player:
    def __init__(self, playerinfo, index):
        self.userid = playerinfo.userid
        self.steamid = playerinfo.steamid
        self.index = index
        self.name = playerinfo.name
        self.state = State(self)

        self.gag = False
        self.mute = False
        self.commandRestricted = False

    def teleport_to_start(self):
        if self.state.timer_mode == Timer_Mode.MAP:
            start_zone = timer.current_map.start_zone
            start = Vector(
                start_zone.center[0],
                start_zone.center[1],
                start_zone.center[2] - start_zone.extents[2],
            )
            orientation = Vector(0, start_zone.orientation, 0)
            source_player = userid_to_source_player(self.userid)
            source_player.teleport(start, angle=orientation, velocity=NULL_VECTOR)
