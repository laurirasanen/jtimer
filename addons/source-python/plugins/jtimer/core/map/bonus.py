from engines.server import server

from .segment import Segment
from ..players.state import Run_State
from ..players.state import Timer_Mode


class Bonus(Segment):
    def __init__(self, tier, bonus_index):
        super().__init__(tier)
        self.index = bonus_index

    def on_enter_start(self, player):
        # change to bonus mode if timer enabled
        if player.state.timer_mode != Timer_Mode.NONE:
            player.state.timer_mode = Timer_Mode.Bonus

        # reset state
        if player.state.bonus_state != Run_State.START:
            player.state.reset()
            player.state.bonus_index = self.index
            player.state.bonus_state = Run_State.START

    def on_leave_start(self, player):
        if (
            player.state.bonus_state == Run_State.START
            and player.state.timer_mode == Timer_Mode.BONUS
            and player.state.bonus_index == self.index
        ):

            # start run
            subtick = self.start_zone.time_to_zone_edge(
                player.state.previous_center,
                player.state.previous_extents,
                player.state.previous_velocity,
                (player.state.origin - player.state.previous_origin).length,
            )
            start_time = float(server.tick - 1 + subtick)

            player.state.bonus_state = Run_State.RUN
            player.state.bonus = (self, start_time)

    def on_enter_end(self, player):
        if (
            player.state.bonus_state == Run_State.RUN
            and player.state.timer_mode == Timer_Mode.BONUS
            and player.state.bonus_index == self.index
        ):

            # finish run
            subtick = self.end_zone.time_to_zone_edge(
                player.state.previous_center,
                player.state.previous_extents,
                player.state.previous_velocity,
                (player.state.origin - player.state.previous_origin).length,
            )
            end_time = float(server.tick - 1 + subtick)

            if player.state.bonus[0] == self:
                player.state.bonus[2] = end_time
            player.state.bonus_state = Run_State.END

    def on_enter_checkpoint(self, player, checkpoint):
        if (
            player.state.bonus_state == Run_State.RUN
            and player.state.timer_mode == Timer_Mode.BONUS
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
