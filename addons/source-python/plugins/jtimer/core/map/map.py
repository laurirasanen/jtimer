from engines.server import server

from .segment import Segment
from ..players.state import Run_State
from ..players.state import Timer_Mode
from ..chat.messages import (
    message_map_finish_no_split,
    message_checkpoint_enter_no_split,
    message_checkpoint_wrong_order,
    message_checkpoint_missed,
    message_prefix,
)
from ..helpers.converts import ticks_to_timestamp


class Map(Segment):
    def __init__(self, tier):
        super().__init__(tier)
        self.courses = []
        self.bonuses = []

    def on_enter_start(self, player):
        if player.state.timer_mode == Timer_Mode.MAP:
            # reset state when entering start again in map mode
            if player.state.map_state != Run_State.START:
                print("entered map > setting state to start")
                player.state.reset()
                player.state.map_state = Run_State.START

    def on_leave_start(self, player):
        if (
            player.state.map_state == Run_State.START
            and player.state.timer_mode == Timer_Mode.MAP
        ):

            # start run
            subtick = self.start_zone.time_to_zone_edge(
                player.state.previous_center,
                player.state.previous_extents,
                player.state.previous_velocity,
                (player.state.origin - player.state.previous_origin).length,
            )
            print(f"left start, subtick: {subtick}")
            start_time = server.tick - 1 + subtick

            player.state.map_state = Run_State.RUN
            player.state.map[0] = self
            player.state.map[1] = start_time

    def on_enter_end(self, player):
        if (
            player.state.map_state == Run_State.RUN
            and player.state.timer_mode == Timer_Mode.MAP
        ):
            # verify we hit all checkpoints
            if len(player.state.checkpoints) != len(player.state.map[0].checkpoints):
                # find what checkpoints we missed
                missed = set()
                for cp in player.state.map[0].checkpoints:
                    if cp not in map(lambda cps: cps[0], player.state.checkpoints):
                        missed.add(cp.index)
                if len(missed) == 1:
                    plural = ""
                else:
                    plural = "s"
                message_checkpoint_missed.send(
                    player.index, plural=plural, checkpoints=str(missed)[1:-1]
                )
                player.state.map_state = Run_State.NONE
                return

            # finish run
            subtick = self.end_zone.time_to_zone_edge(
                player.state.previous_center,
                player.state.previous_extents,
                player.state.previous_velocity,
                (player.state.origin - player.state.previous_origin).length,
            )
            print(f"entered end, subtick: {subtick}")
            end_time = server.tick - 1 + subtick

            player.state.map[2] = end_time
            player.state.map_state = Run_State.END
            message_map_finish_no_split.send(
                player.index,
                player=player.name,
                time=ticks_to_timestamp(player.state.map[2] - player.state.map[1]),
            )

    def on_enter_checkpoint(self, player, checkpoint):
        if (
            player.state.map_state == Run_State.RUN
            and player.state.timer_mode == Timer_Mode.MAP
        ):
            for cp in player.state.checkpoints:
                if cp[0] == checkpoint:
                    return

            # verify we hit the correct checkpoint
            if len(player.state.checkpoints) == 0:
                # checkpoints are 1 indexed: check if the first one we hit is cp1
                if checkpoint.index != 1:
                    player.state.map_state = Run_State.NONE
                    message_checkpoint_wrong_order.send(player.index)
                    return
            # we hit an incorrect checkpoint
            elif player.state.checkpoints[-1][0].index != checkpoint.index - 1:
                player.state.map_state = Run_State.NONE
                message_checkpoint_wrong_order.send(player.index)
                return

            # entered checkpoint
            subtick = self.start_zone.time_to_zone_edge(
                player.state.previous_center,
                player.state.previous_extents,
                player.state.previous_velocity,
                (player.state.origin - player.state.previous_origin).length,
            )
            enter_time = server.tick - 1 + subtick
            player.state.checkpoints.append((checkpoint, enter_time))
            message_checkpoint_enter_no_split.send(
                player.index,
                index=checkpoint.index,
                time=ticks_to_timestamp(enter_time - player.state.map[1]),
            )
