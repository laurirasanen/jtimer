from threading import Thread

from engines.server import server

from .segment import Segment
from ..players.state import Run_State, Player_Class, Timer_Mode
from ..chat.messages import (
    message_map_record_set,
    message_map_record,
    message_map_finish,
    message_map_improvement,
    message_checkpoint_enter_no_split,
    message_checkpoint_wrong_order,
    message_checkpoint_missed,
    message_points_gain,
)
from ..helpers.converts import ticks_to_timestamp
from ..api.times import add_map_time
from .. import timer


class Map(Segment):
    def __init__(self, id_, stier=0, dtier=0):
        super().__init__(stier, dtier)
        self.id_ = id_
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
            start_time = float(server.tick - 1 + subtick)

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
            end_time = float(server.tick - 1 + subtick)

            player.state.map[2] = end_time
            player.state.map_state = Run_State.END
            Thread(target=self.upload_map_time, args=(player,)).start()


    def upload_map_time(self, player):
        player_class = None
        class_string = None
        if player.state.player_class == Player_Class.SOLDIER:
            player_class = 2
            class_string = "soldier"
        elif player.state.player_class == Player_Class.DEMOMAN:
            player_class = 4
            class_string = "demoman"

        checkpoints = []
        for checkpoint in player.state.checkpoints:
            checkpoints.append({"cp_index": checkpoint[0].index, "time": checkpoint[1]})

        result = add_map_time(
            self.id_,
            player.id_,
            player_class,
            player.state.map[1],
            player.state.map[2],
            checkpoints,
        )

        if result is None:
            return

        if result["result"] == 0:
            message_map_finish.send(
                player.index,
                player=player.name,
                time=ticks_to_timestamp(result["duration"]),
                split_type="WR",
                split_sign="+",
                split_time=ticks_to_timestamp(
                    result["duration"] - result["records"][class_string]
                ),
            )
            return

        if result["result"] == 1:
            if result["completions"][class_string] == 1:
                message_map_record_set.send(
                    player.index,
                    player=player.name,
                    time=ticks_to_timestamp(result["duration"]),
                )
                if result["points_gained"] > 0:
                    message_points_gain.send(
                        player.index,
                        points=result["points_gained"]
                    )
                return

        if result["rank"] == 1:
            message_map_record.send(
                player.index,
                player=player.name,
                time=ticks_to_timestamp(result["duration"]),
                split_type="WR",
                split_sign="-",
                split_time=ticks_to_timestamp(
                    result["records"][class_string] - result["duration"]
                ),
            )
            if result["points_gained"] > 0:
                message_points_gain.send(
                    player.index,
                    points=result["points_gained"]
                )
            return

        message_map_improvement.send(
            player.index,
            player=player.name,
            time=ticks_to_timestamp(result["duration"]),
            split_type="WR",
            split_sign="+",
            split_time=ticks_to_timestamp(
                result["duration"] - result["records"][class_string]
            ),
            rank=result["rank"],
            completions=result["completions"][class_string],
        )
        if result["points_gained"] > 0:
            message_points_gain.send(
                player.index,
                points=result["points_gained"]
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
            subtick = checkpoint.time_to_zone_edge(
                player.state.previous_center,
                player.state.previous_extents,
                player.state.previous_velocity,
                (player.state.origin - player.state.previous_origin).length,
            )
            enter_time = float(server.tick - 1 + subtick)
            player.state.checkpoints.append((checkpoint, enter_time))
            message_checkpoint_enter_no_split.send(
                player.index,
                index=checkpoint.index,
                time=ticks_to_timestamp(enter_time - player.state.map[1]),
            )
