"""Module for courses."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
from engines.server import server

# Custom Imports
from .segment import Segment
from ..players.state import RunState
from ..players.state import TimerMode


# =============================================================================
# >> COURSE CLASS
# =============================================================================
class Course(Segment):
    def __init__(self, tier, course_index):
        """Create a new course."""
        super().__init__(tier)
        self.index = course_index

    def on_enter_start(self, player):
        """Called when entering the course start zone."""

        if player.state.timer_mode == TimerMode.COURSE:
            if player.state.course_state != RunState.START:
                # reset state when entering start again in course mode
                player.state.reset()
                player.state.course_state = RunState.START

        elif player.state.timer_mode == TimerMode.MAP:
            if player.state.course_index == self.index - 1:
                # coming from previous course
                player.state.course_index = self.index
                player.state.course_state = RunState.START

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
                player.timer_mode = TimerMode.NONE

    def on_leave_start(self, player):
        """Called when leaving the course start zone."""

        if (
            player.state.course_state == RunState.START
            and (
                player.state.timer_mode == TimerMode.MAP
                or player.state.timer_mode == TimerMode.COURSE
            )
            and player.state.course_index == self.index
        ):

            # start run
            subtick = self.start_zone.time_to_zone_edge(
                player.state.previous_center,
                player.state.previous_extents,
                player.state.previous_velocity,
                (player.state.origin - player.state.previous_origin).length,
            )
            start_time = float(server.tick - 1 + subtick)

            player.state.course_state = RunState.RUN
            player.state.courses.append((self, start_time))

            # TODO:
            # course start time checkpoint?

    def on_enter_end(self, player):
        """Called when entering the course end zone."""

        if (
            player.state.course_state == RunState.RUN
            and (
                player.state.timer_mode == TimerMode.MAP
                or player.state.timer_mode == TimerMode.COURSE
            )
            and player.state.course_index == self.index
        ):

            # finish run
            subtick = self.end_zone.time_to_zone_edge(
                player.state.previous_center,
                player.state.previous_extents,
                player.state.previous_velocity,
                (player.state.origin - player.state.previous_origin).length,
            )
            end_time = float(server.tick - 1 + subtick)

            for c in player.state.courses:
                if c[0] == self:
                    c[2] = end_time
            player.state.course_state = RunState.END

    def on_enter_checkpoint(self, player, checkpoint):
        """Called when entering a course checkpoint."""

        # only print course cps in course mode
        if (
            player.state.course_state == RunState.RUN
            and player.state.timer_mode == TimerMode.COURSE
        ):

            # check if already entered
            for cp in player.state.checkpoints:
                if cp[0] == checkpoint:
                    return

            # enter checkpoint
            subtick = checkpoint.time_to_zone_edge(
                player.state.previous_center,
                player.state.previous_extents,
                player.state.previous_velocity,
                (player.state.origin - player.state.previous_origin).length,
            )
            enter_time = float(server.tick - 1 + subtick)
            player.state.checkpoints.append(checkpoint, enter_time)

            # TODO:
            # print cps
