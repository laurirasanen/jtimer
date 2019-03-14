from enum import Enum
import mathlib
from engines.server import Server
from ..map.map import Map
from ..map.course import Course
from ..map.bonus import Bonus
from ..map.checkpoint import Checkpoint

class State():
    def __init__(self):
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
        self.bonus = (None, None, None)
        self.map = (None, None, None)
        self.overlaps = []

    def reset(self):
        self.checkpoints = []
        self.courses = []
        self.bonus = (None, None, None)
        self.map = (None, None, None)

    def running(self):
        if (self.timer_mode != Timer_Mode.NONE
          and (self.map_state == Run_State.RUN
          or self.course_state == Run_State.RUN
          or self.bonus_state == Run_State.RUN)):
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

            # TODO:
            # check if we've left or entered a zone.
            # if we have, use previous position for getting sub-tick enter/leave time for zone,
            # then call the appropriate function for updating state
            # (start_segment, end_segment, enter_checkpoint)
            """pseudo
            for s in segments:
                for z in s.zones:
                    if(z.is_overlapping(self.center, self.extents)):
                        # check if we were already overlapping before
                        same = False
                        for o in self.overlaps:
                            if o == z:
                                same = True
                        if same:
                            continue
                        
                        # just entered
                        subtick = z.time_to_zone_edge(self.previous_center, self.previous_extents, self.previous_velocity)
                        start_segment(s, Server.tick - 1 + subtick)

                    else:
                        # check if we were overlapping before
                        index = -1
                        for i in range(0, len(self.overlaps)):
                            if self.overlaps[i] == z:
                                index = i

                        if index == -1:
                            continue

                        # just left
                        subtick = z.time_to_zone_edge(self.previous_center, self.previous_extents, self.previous_velocity)
                        end_segment(s, Server.tick - 1 + subtick)

                        # remove from overlaps
                        self.overlaps.pop(index)

            for cp in checkpoints:
                if(cp.is_overlapping(self.center, self.center)):
                    # check if we were already overlapping before
                    same = False
                    for o in self.overlaps:
                        if o == cp:
                            same = True
                    if same:
                        continue

                    # just entered
                    subtick = cp.time_to_zone_edge(self.previous_center, self.previous_extents, self.previous_velocity)
                    enter_checkpoint(cp, Server.tick - 1 + subtick)             

            """
        else:
            # not running
            pass

    """
    Called when starting any segment (map, course, bonus)
    """
    def start_segment(segment, start_time):
        if not issubclass(segment, Segment):
            print(f'ERR: Wrong type {type(segment)} passed to end_segment!')

        # check type of start_time
        if type(start_time) != type(float) and type(start_time) != type(int):
            print(f'ERR: Tried to start_segment a {type(segment)} but start_time is not Type(float) or Type(int)!')
            return

        if type(segment) == type(Map):
            # check for existing Map Segment
            if self.map[0] != None:
                print('ERR: Tried to start_segment a map but self.map[0] is not None!')
                return

            # check for existing start_time
            if self.map[1] != None:
                print('ERR: Tried to start_segment a map but self.map[1] is not None!')
                return

            self.map[0] = segment
            self.map[1] = start_time

        elif type(segment) == type(Course):
            # check for existing Course Segment
            for c in self.courses:
                if c[0] == segment:
                    print('ERR: Tried to start_segment a course that has already been started!')
                    return

            self.checkpoints.append((segment, start_time))

        elif type(segment) == type(Bonus):
            # check for existing Bonus Segment
            if self.bonus[0] != None:
                print('ERR: Tried to start_segment a bonus but self.bonus[0] is not None!')
                return

            # check for existing start_time
            if self.bonus[1] != None:
                print('ERR: Tried to start_segment a bonus but self.bonus[1] is not None!')
                return

            self.bonus[0] = segment
            self.bonus[1] = start_segment

        else:
            print('ERR: Type passed to end_segment is not Map, Course or Bonus!')

    """
    Called when ending any segment (map, course, bonus)
    """
    def end_segment(segment, end_time):
        if not issubclass(segment, Segment):
            print(f'ERR: Wrong type {type(segment)} passed to end_segment!')

        # check type of end_time
        if type(end_time) != type(float) and type(end_time) != type(int):
            print(f'ERR: Tried to end_segment a {type(segment)} but end_time is not Type(float) or Type(int)!')
            return

        if type(segment) == type(Map):
            # check type of Map Segment
            if self.map[0] == None:
                print('ERR: Tried to end_segment a map but self.map[0] is None!')
                return
            if type(self.map[0] != type(Map)):
                print('ERR: Tried to end_segment a map but self.map[0] is not Type(Map)!')
                return

            # check type of start_time
            if self.map[1] == None:
                print('ERR: Tried to end_segment a map but self.map[1] is None!')
                return
            if type(self.map[1]) != type(float) and type(self.map[1]) != type(int):
                print('ERR: Tried to end_segment a map but self.map[1] is not Type(float) or Type(int)!')
                return

            # check for existing end_time
            if self.map[2] != None:
                print('ERR: Tried to end_segment a map but self.map[2] is not None!')
                return

            self.map[2] = end_time

        elif type(segment) == type(Course):
            # check for existing Course Segment
            index = -1
            for i in range(0, len(self.courses)):
                if self.courses[i] == segment:
                    index = i
                    break

            # no need to check if self.courses[index][0] is type(Course)
            # because the index will be -1 then
            if index == -1:
                print('ERR: Tried to end_segment a course that hasn\'t been started!')
                return

            # check type of start_time
            if self.courses[index][1] == None:
                print('ERR: Tried to end_segment a bonus but self.courses[index][1] is None!')
                return
            if type(self.courses[index][1]) != type(float) and type(self.courses[index][1]) != type(int):
                print('ERR: Tried to end_segment a bonus but self.courses[index][1] is not Type(float) or Type(int)!')
                return

            # check for existing end_time
            if self.courses[index][2] != None:
                print('ERR: Tried to end_segment a course but self.courses[index][2] is not None!')
                return

            self.courses[index][2] = end_time

        elif type(segment) == type(Bonus):
            # check type of Bonus Segment
            if self.bonus[0] == None:
                print('ERR: Tried to end_segment a bonus but self.bonus[0] is None!')
                return
            if type(self.bonus[0]) != type(Bonus):
                print('ERR: Tried to end_segment a bonus but self.bonus[0] is not Type(Bonus)!')
                return

            # check type of start_time
            if self.bonus[1] == None:
                print('ERR: Tried to end_segment a bonus but self.bonus[1] is None!')
                return
            if type(self.bonus[1]) != type(float) and type(self.bonus[1]) != type(int):
                print('ERR: Tried to end_segment a bonus but self.bonus[1] is not Type(float) or Type(int)!')
                return

            # check for existing end_time
            if self.bonus[2] != None:
                print('ERR: Tried to end_segment a bonus but self.bonus[2] is not None!')
                return

            self.bonus[2] = end_time

        else:
            print('ERR: Type passed to end_segment is not Map, Course or Bonus!')

    """
    Called when entering any checkpoint
    """
    def enter_checkpoint(checkpoint, enter_time):
        # check type of Checkpoint
        if type(checkpoint) != type(Checkpoint):
            print('ERR: Wrong type passed to enter_checkpoint!')
            return

        # check for existing checkpoints
        for cp in self.checkpoints:
            if cp[0] == checkpoint:
                print('ERR: Tried to enter_checkpoint a checkpoint that has already been entered!')
                return

        # check type of enter_time
        if type(enter_time) != type(float) and type(enter_time) != type(int):
            print('ERR: Tried to enter_checkpoint but enter_time is not Type(float) or Type(int)!')
            return

        self.checkpoints.append((checkpoint, enter_time))


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