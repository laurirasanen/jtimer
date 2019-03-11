from enum import Enum
from .checkpoint import Checkpoint

class State():
    def __init__(self):
        self.timer_mode = Timer_Mode.MAP
        self.map_state = Run_State.START
        self.course_state = Run_State.START
        self.bonus_state = Run_State.NONE
        self.map_id = 0
        self.course_num = 0
        self.bonus_num = 0
        self.checkpoints = []
        self.time = 0

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