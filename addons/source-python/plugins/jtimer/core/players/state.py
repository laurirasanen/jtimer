"""Module for holding Player's state."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
from enum import IntEnum

# Source.Python Imports
import mathlib
from engines.server import server
from players.entity import Player
from players.helpers import index_from_userid

# Custom Imports
from ..hud import hud


# =============================================================================
# >> STATE CLASS
# =============================================================================
class State:
    """Class for Player state."""

    def __init__(self, player):
        """Create a new State."""
        self.player_reference = player
        self.player_class = PlayerClass.NONE

        self.origin = mathlib.NULL_VECTOR
        self.center = mathlib.NULL_VECTOR
        self.extents = mathlib.NULL_VECTOR
        self.bounds = [mathlib.NULL_VECTOR, mathlib.NULL_VECTOR]
        self.velocity = mathlib.NULL_VECTOR

        self.previous_origin = self.origin
        self.previous_center = self.center
        self.previous_extents = self.extents
        self.previous_bounds = self.bounds
        self.previous_velocity = self.velocity

        self.timer_mode = TimerMode.NONE
        self.map_state = RunState.NONE
        self.course_state = RunState.NONE
        self.bonus_state = RunState.NONE

        # [[Segment, start_time, end_time]]
        self.courses = []

        # [Segment, start_time, end_time]
        self.bonus = [None, None, None]
        self.map = [None, None, None]

        # [(Checkpoint, enter_time)]
        self.checkpoints = []

        # Overlapping zones
        self.overlaps = []

        self.bonus_index = 0
        self.course_index = 0

    def reset(self):
        """Reset state."""
        self.checkpoints = []
        self.courses = []
        self.bonus = [None, None, None]
        self.map = [None, None, None]
        self.bonus_index = 0
        self.course_index = 0
        self.overlaps = []

        self.origin = mathlib.NULL_VECTOR
        self.center = mathlib.NULL_VECTOR
        self.extents = mathlib.NULL_VECTOR
        self.bounds = [mathlib.NULL_VECTOR, mathlib.NULL_VECTOR]
        self.velocity = mathlib.NULL_VECTOR

        self.previous_origin = self.origin
        self.previous_center = self.center
        self.previous_bounds = self.bounds
        self.previous_extents = self.extents
        self.previous_velocity = self.velocity

    def running(self):
        """Returns True if player is currently running."""
        if self.timer_mode != TimerMode.NONE:
            return True
        return False

    def update(self, current_map, origin, vec_mins_maxs, velocity):
        """Update player state."""

        # are we running?
        if self.running:
            if type(origin) != mathlib.Vector:
                print(
                    f"ERR: Trying to update Player State but origin is not Type(mathlib.Vector)!"
                )
                return

            if type(vec_mins_maxs) != mathlib.Vector:
                print(
                    f"ERR: Trying to update Player State but vec_mins_maxs is not Type(mathlib.Vector)!"
                )
                return

            self.previous_origin = self.origin
            self.origin = origin

            self.previous_extents = self.extents
            self.extents = vec_mins_maxs
            self.extents[2] /= 2

            self.previous_bounds = self.bounds
            self.bounds[0] = origin + vec_mins_maxs
            self.bounds[1] = origin - vec_mins_maxs
            self.bounds[1][2] += vec_mins_maxs[2]

            self.previous_center = self.center
            self.center = self.origin
            self.center[2] += vec_mins_maxs[2] / 2

            self.previous_velocity = self.velocity
            self.velocity = velocity

            # first update
            if self.previous_origin == mathlib.NULL_VECTOR:
                return

            to_check = []
            if self.timer_mode == TimerMode.MAP:
                to_check.append(current_map)
                to_check.extend(current_map.courses)
            elif self.timer_mode == TimerMode.COURSE:
                to_check.append(current_map.courses[self.course_index])
            if self.timer_mode == TimerMode.BONUS:
                to_check.append(current_map.bonuses[self.bonus_index])

            for segment in to_check:
                # check start_zone
                if segment.start_zone.is_overlapping(self.center, self.extents):
                    segment.on_enter_start(self.player_reference)
                else:
                    segment.on_leave_start(self.player_reference)

                # check end zone
                if segment.end_zone.is_overlapping(self.center, self.extents):
                    segment.on_enter_end(self.player_reference)

                # check checkpoints
                for cp in segment.checkpoints:
                    if cp.is_overlapping(self.center, self.extents):
                        segment.on_enter_checkpoint(self.player_reference, cp)

        # If player is spec, reset and blank timer/modes
        if Player(index_from_userid(self.player_reference.userid)).is_observer():
            self.reset()
            self.timer_mode = TimerMode.NONE
            self.map_state = RunState.NONE
            self.course_state = RunState.NONE
            self.bonus_state = RunState.NONE
        # update hud every half a second
        if server.tick % 33 == 0:
            hud.draw(self.player_reference, current_map)


# =============================================================================
# >> ENUMS
# =============================================================================
class RunState(IntEnum):
    """Enum for run states."""

    NONE = 0
    START = 1
    RUN = 2
    END = 3


class TimerMode(IntEnum):
    """Enum for Timer modes."""

    NONE = 0
    MAP = 1
    COURSE = 2
    BONUS = 3


class PlayerClass(IntEnum):
    """Enum for player classes."""

    # Source.Python returns silly values for class indices
    NONE = 0
    SCOUT = 1
    SOLDIER = 3
    PYRO = 7
    DEMOMAN = 4
    HEAVY = 6
    ENGINEER = 9
    MEDIC = 5
    SNIPER = 2
    SPY = 8
