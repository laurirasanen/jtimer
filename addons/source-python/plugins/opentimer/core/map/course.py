from engines.server import server

from .segment import Segment
from ..players.state import Run_State
from ..players.state import Timer_Mode

class Course(Segment):
    def __init__(self, tier, course_index):
        super().__init__(tier)
        self.index = course_index

    def on_enter_start(self, player):
        if player.state.timer_mode == Timer_Mode.COURSE:
            if player.state.course_state != Run_State.START:
                # reset state when entering start again in course mode
                player.state.reset()
                player.state.course_state = Run_State.START

        elif player.state.timer_mode == Timer_Mode.MAP:
            if player.state.course_index == self.index - 1:
                # coming from previous course
                player.state.course_index = self.index
                player.state.course_state = Run_State.START

                # TODO:
                # course enter time checkpoint

            elif player.state.course_index < self.index - 1:
                # entered earlier course
                pass

            elif player.state.course_index > self.index - 1:
                # entered in wrong order
                # TODO:
                # print message to player
                player.state.reset()
                player.timer_mode = Timer_Mode.NONE            


    def on_leave_start(self, player):
        if (player.state.course_state == Run_State.START
          and (player.state.timer_mode == Timer_Mode.MAP
          or player.state.timer_mode == Timer_Mode.COURSE)
          and player.state.course_index == self.index):

            # start run
            subtick = self.start_zone.time_to_zone_edge(player.state.previous_center, player.state.previous_extents, player.state.previous_velocity)
            start_time = server.tick - 1 + subtick

            player.state.course_state = Run_State.RUN
            player.state.courses.append((self, start_time))

            # TODO:
            # course start time checkpoint?

    def on_enter_end(self, player):
        if (player.state.course_state == Run_State.RUN
          and (player.state.timer_mode == Timer_Mode.MAP
          or player.state.timer_mode == Timer_Mode.COURSE)
          and player.state.course_index == self.index):

            # finish run
            subtick = self.end_zone.time_to_zone_edge(player.state.previous_center, player.state.previous_extents, player.state.previous_velocity)
            end_time = server.tick - 1 + subtick

            for c in player.state.courses:
                if c[0] == self:
                    c[2] = end_time
            player.state.course_state = Run_State.END        

    def on_enter_checkpoint(self, player, checkpoint):
        # only print course cps in course mode
        if (player.state.course_state == Run_State.RUN
          and player.state.timer_mode == Timer_Mode.COURSE):

            # check if already entered
            for cp in player.state.checkpoints:
                if cp[0] == checkpoint:
                    return
            
            # enter checkpoint
            subtick = checkpoint.time_to_zone_edge(player.state.previous_center, player.state.previous_extents, player.state.previous_velocity)
            enter_time = server.tick - 1 + subtick 
            player.state.checkpoints.append(checkpoint, enter_time)

            # TODO:
            # print cps