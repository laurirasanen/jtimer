"""Module for bonuses."""

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
# >> BONUS CLASS
# =============================================================================
class Bonus(Segment):
    def __init__(self, tier, bonus_index):
        """Create a new bonus."""
        super().__init__(tier)
        self.index = bonus_index

    def on_enter_start(self, player):
        """Called when entering the bonus start zone."""

        # change to bonus mode if timer enabled
        if player.state.timer_mode != TimerMode.NONE:
            player.state.timer_mode = TimerMode.Bonus

        # reset state
        if player.state.bonus_state != RunState.START:
            player.state.reset()
            player.state.bonus_index = self.index
            player.state.bonus_state = RunState.START

    def on_leave_start(self, player):
        """Called when leaving the bonus start zone."""

        if (
            player.state.bonus_state == RunState.START
            and player.state.timer_mode == TimerMode.BONUS
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

            player.state.bonus_state = RunState.RUN
            player.state.bonus = (self, start_time)

    def on_enter_end(self, player):
        """Called when entering the bonus end zone."""

        if (
            player.state.bonus_state == RunState.RUN
            and player.state.timer_mode == TimerMode.BONUS
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
            player.state.bonus_state = RunState.END

    def on_enter_checkpoint(self, player, checkpoint):
        """Called when entering a bonus checkpoint."""

        if (
            player.state.bonus_state == RunState.RUN
            and player.state.timer_mode == TimerMode.BONUS
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
