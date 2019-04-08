from threading import Thread
from engines.server import server

from mathlib import Vector

from .segment import Segment
from .checkpoint import Checkpoint
from ..zones.zone import Zone
from ..players.state import Run_State, Player_Class, Timer_Mode
from ..chat.messages import (
    message_map_record_set,
    message_map_record,
    message_map_finish,
    message_map_improvement,
    message_checkpoint_enter,
    message_checkpoint_enter_no_split,
    message_checkpoint_wrong_order,
    message_checkpoint_missed,
    message_points_gain,
)
from ..helpers.converts import ticks_to_timestamp
from ..api.times import add_map_time
from ..api.maps import map_info_name
from ..api.zones import map_zones
from ..timer import timer


class Map(Segment):
    def __init__(
        self, id_, name, stier=0, dtier=0, records={"soldier": None, "demoman": None}
    ):
        super().__init__(stier, dtier)
        self.id_ = id_
        self.name = name
        self.courses = []
        self.bonuses = []
        self.records = records

    @staticmethod
    def get_map():
        # check if current map exists in api
        print(f"[jtimer] Getting map info for '{server.map_name}'")
        map_info, response = map_info_name(server.map_name)

        if map_info is None:
            print(f"[jtimer] Couldn't get map info for '{server.map_name}'.")
            if response.status_code < 500:
                print(f"api response: {response.status_code}\n{response.json()}")
            else:
                print(f"api response: {response.status_code}")

        else:
            print(f"[jtimer] Loaded map info for '{server.map_name}'!")
            map_ = Map(
                map_info["id"],
                map_info["name"],
                map_info["tiers"]["soldier"],
                map_info["tiers"]["demoman"],
                map_info["records"],
            )

            zones, response = map_zones(map_info["id"])

            if zones is None:
                print(f"[jtimer] Couldn't get map zones for '{server.map_name}'.")
                if response.status_code < 500:
                    print(f"api response: {response.status_code}\n{response.json()}")
                else:
                    print(f"api response: {response.status_code}")

            else:
                for z in zones:
                    if z["zone_type"] == "start":
                        p1 = Vector(z["p1"][0], z["p1"][1], z["p1"][2])
                        p2 = Vector(z["p2"][0], z["p2"][1], z["p2"][2])
                        map_.add_start_zone(Zone(p1, p2, z["orientation"]))

                    elif z["zone_type"] == "end":
                        p1 = Vector(z["p1"][0], z["p1"][1], z["p1"][2])
                        p2 = Vector(z["p2"][0], z["p2"][1], z["p2"][2])
                        map_.add_end_zone(Zone(p1, p2))

                    elif z["zone_type"] == "cp":
                        p1 = Vector(
                            z["zone"]["p1"][0], z["zone"]["p1"][1], z["zone"]["p1"][2]
                        )
                        p2 = Vector(
                            z["zone"]["p2"][0], z["zone"]["p2"][1], z["zone"]["p2"][2]
                        )
                        map_.add_checkpoint(Checkpoint(z["cp_index"], p1, p2))

                print(f"[jtimer] Loaded zones for '{server.map_name}'!")
                timer.Timer.instance().current_map = map_


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

            thread = MapTimeUploader(self.id_, player, self.upload_map_time_callback)
            thread.start()

    def upload_map_time_callback(self, result, player):
        if result is None:
            return

        class_string = None
        if player.state.player_class == Player_Class.SOLDIER:
            class_string = "soldier"
        elif player.state.player_class == Player_Class.DEMOMAN:
            class_string = "demoman"

        self.records = result["records"]

        if result["result"] == 0:
            message_map_finish.send(
                player.index,
                player=player.name,
                time=ticks_to_timestamp(result["duration"]),
                split_type="WR",
                split_sign="+",
                split_time=ticks_to_timestamp(
                    result["duration"] - result["records"][class_string]["time"]
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
                        player.index, points=result["points_gained"]
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
                    result["old_records"][class_string]["time"] - result["duration"]
                ),
            )
            if result["points_gained"] > 0:
                message_points_gain.send(player.index, points=result["points_gained"])
            return

        message_map_improvement.send(
            player.index,
            player=player.name,
            time=ticks_to_timestamp(result["duration"]),
            split_type="WR",
            split_sign="+",
            split_time=ticks_to_timestamp(
                result["duration"] - result["records"][class_string]["time"]
            ),
            rank=result["rank"],
            completions=result["completions"][class_string],
        )
        if result["points_gained"] > 0:
            message_points_gain.send(player.index, points=result["points_gained"])

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

            class_string = None
            if player.state.player_class == Player_Class.SOLDIER:
                class_string = "soldier"
            elif player.state.player_class == Player_Class.DEMOMAN:
                class_string = "demoman"

            relative_enter_time = enter_time - player.state.map[1]

            if self.records[class_string] is not None:
                for record_checkpoint in self.records[class_string]["checkpoints"]:
                    if record_checkpoint["cp_index"] is checkpoint.index:
                        split_time = relative_enter_time - record_checkpoint["time"]
                        split_sign = "+" if split_time > 0 else "-"
                        message_checkpoint_enter.send(
                            player.index,
                            index=checkpoint.index,
                            time=ticks_to_timestamp(relative_enter_time),
                            split_type="WR",
                            split_sign=split_sign,
                            split_time=ticks_to_timestamp(split_time),
                        )
                        return

            message_checkpoint_enter_no_split.send(
                player.index,
                index=checkpoint.index,
                time=ticks_to_timestamp(relative_enter_time),
            )


class MapTimeUploader(Thread):
    def __init__(self, map_id, player, callback=None):
        Thread.__init__(self)
        self.map_id = map_id
        self.player = player
        self.callback = callback

    def run(self):
        player_class = None
        if self.player.state.player_class == Player_Class.SOLDIER:
            player_class = 2
        elif self.player.state.player_class == Player_Class.DEMOMAN:
            player_class = 4

        checkpoints = []
        for checkpoint in self.player.state.checkpoints:
            checkpoints.append({"cp_index": checkpoint[0].index, "time": checkpoint[1]})

        result = add_map_time(
            self.map_id,
            self.player.id_,
            player_class,
            self.player.state.map[1],
            self.player.state.map[2],
            checkpoints,
        )

        if self.callback is not None:
            self.callback(result, self.player)
