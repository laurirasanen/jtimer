from engines.server import Server

from .segment import Segment
from ..players.state import Run_State
from ..players.state import Timer_Mode


class Map(Segment):
    def __init__(self, tier):
        super().__init__(tier)
        self.courses = []
        self.bonuses = []

    def on_enter_start(self, player):
        """reset state when entering start again in map mode"""
        if (player.state.timer_mode == Timer_Mode.MAP
          and player.state.map_state != Run_State.START):
            player.state.reset()

    def on_leave_start(self, player):
        if (player.state.map_state == Run_State.START
          and player.state.timer_mode == Timer_Mode.MAP):

            # start run
            subtick = self.start_zone.time_to_zone_edge(player.state.previous_center, player.state.previous_extents, player.state.previous_velocity)
            start_time = Server.tick - 1 + subtick

            player.state.map_state = Run_State.RUN
            player.state.map[0] = self
            player.state.map[1] = start_time

    def on_enter_end(self, player):
        if (player.state.map_state == Run_State.RUN
          and player.state.timer_mode == Timer_Mode.MAP):

            # finish run
            subtick = self.end_zone.time_to_zone_edge(player.state.previous_center, player.state.previous_extents, player.state.previous_velocity)
            end_time = Server.tick - 1 + subtick

            player.state.map[2] = end_time
            player.state.map_state = Run_State.END         

    def on_enter_checkpoint(self, player, checkpoint):
        if (player.state.map_state == Run_State.RUN
          and player.state.timer_mode == Timer_Mode.MAP):
            for cp in player.state.checkpoints:
                if cp[0] == checkpoint:
                    return
            
            # entered checkpoint
            subtick = checkpoint.time_to_zone_edge(player.state.previous_center, player.state.previous_extents, player.state.previous_velocity)
            enter_time = Server.tick - 1 + subtick
            player.state.checkpoints.append(checkpoint, enter_time)