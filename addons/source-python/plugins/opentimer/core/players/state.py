from enum import Enum
import mathlib
from engines.server import Server
from ..timer import timer

class State():
    def __init__(self, player):
        self.player_reference = player
        self.player_class = Player_Class.NONE
        self.origin = mathlib.NULL_VECTOR
        self.center = mathlib.NULL_VECTOR
        self.bounds = (mathlib.NULL_VECTOR, mathlib.NULL_VECTOR)
        self.extents = mathlib.NULL_VECTOR
        self.velocity = mathlib.NULL_VECTOR

        self.previous_origin = self.origin
        self.previous_bounds = self.bounds
        self.previous_center = self.center
        self.previous_extents = self.extents
        self.previous_velocity = self.velocity

        self.timer_mode = Timer_Mode.NONE
        self.map_state = Run_State.NONE
        self.course_state = Run_State.NONE
        self.bonus_state = Run_State.NONE        

        # (Segment, start_time, end_time)
        self.checkpoints = []
        self.courses = []
        self.course_index = 0
        self.bonus = (None, None, None)
        self.bonus_index = 0
        self.map = (None, None, None)
        self.overlaps = []

    def reset(self):
        self.checkpoints = []
        self.courses = []
        self.bonus = (None, None, None)
        self.map = (None, None, None)
        self.bonus_index = 0
        self.course_index = 0
        self.overlaps = []

        self.origin = mathlib.NULL_VECTOR
        self.center = mathlib.NULL_VECTOR
        self.bounds = (mathlib.NULL_VECTOR, mathlib.NULL_VECTOR)
        self.extents = mathlib.NULL_VECTOR
        self.velocity = mathlib.NULL_VECTOR

        self.previous_origin = self.origin
        self.previous_bounds = self.bounds
        self.previous_center = self.center
        self.previous_extents = self.extents
        self.previous_velocity = self.velocity

    def running(self):
        if self.timer_mode != Timer_Mode.NONE:
            return True
        return False

    def update(self, origin, bounds, velocity):
        # are we running?
        if self.running:
            if type(origin) != type(mathlib.Vector):
                print(f'ERR: Trying to update Player State but origin is not Type(mathlib.Vector)!')
                return
            if type(bounds) != type(tuple(mathlib.Vector, mathlib.Vector)):
                print(f'ERR: Trying to update Player State but bounds is not Type(tuple(mathlib.Vector, mathlib.Vector))!')
                return

            self.previous_bounds = self.bounds
            self.previous_origin = self.origin
            self.origin = origin
            self.bounds = bounds

            self.previous_center = self.center
            yOffset = (self.bounds[0][2] + self.bounds[1][2])/2
            self.center = self.origin
            self.center[2] += yOffset

            self.previous_extents = self.extents
            self.extents[0] = self.extents[1] = self.bounds[1][0]
            self.extents[2] = yOffset

            self.previous_velocity = self.velocity
            self.velocity = velocity

            # first update
            if self.previous_origin == mathlib.NULL_VECTOR:
                return

            to_check = []
            if self.map_state == Run_State.RUN:
                to_check.append(timer.current_map)
            if self.course_state == Run_State.RUN:
                to_check.append(timer.current_map.courses[self.course_index])
            if self.bonus_state == Run_State.RUN:
                to_check.append(timer.current_map.bonuses[self.bonus_index])

            for segment in to_check:
                # check start_zone
                if(segment.start_zone.is_overlapping(self.center, self.extents)):
                    segment.on_enter_start(self.player_reference)
                else:
                    segment.on_leave_start(self.player_reference)

                # check end zone
                if(segment.start_zone.is_overlapping(self.center, self.extents)):
                    segment.on_enter_end(self.player_reference)

                # check checkpoints
                for cp in segment.checkpoints:
                    if cp.is_overlapping(self.center, self.center):
                        segment.on_enter_checkpoint(self.player_reference, cp)                               

        else:
            # not running
            pass


class Run_State(Enum):
    NONE = 0
    START = 1,
    RUN = 2,
    END = 3

class Timer_Mode(Enum):
    NONE = 0
    MAP = 1
    COURSE = 2
    BONUS = 3

class Player_Class(Enum):
    NONE = 0,
    SCOUT = 1,
    SOLDIER = 2,
    PYRO = 3,
    DEMOMAN = 4,
    HEAVY = 5,
    ENGINEER = 6,
    MEDIC = 7,
    SNIPER = 8,
    SPY = 9