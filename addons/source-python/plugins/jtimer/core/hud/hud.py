"""Module for drawing hud elements."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
from messages import HintText, KeyHintText
from engines.server import server
from players.entity import Player
from players.helpers import index_from_userid

# Custom Imports
from ..helpers.converts import ticks_to_timestamp
from ..players import state
from ..helpers.utils import return_spectators

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
buffer_white_space = "\n\n\n\n\n\n"


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def draw(player, current_map):
    """Draw hud to player."""
    current_player = index_from_userid(player.userid)
    if Player(current_player).is_observer():
        # Hud will be drawn by other player
        pass
    else:
        spec_indexes = return_spectators(current_player, "index")
        _draw_timer(player, current_map, spec_indexes)
        _draw_right_hud(player, current_map, spec_indexes)


def _draw_right_hud(player, current_map, spec_indexes):
    """Draw right side hud to player."""
    current_player = index_from_userid(player.userid)
    spectators = "Spectators: " + return_spectators(current_player)

    if Player(current_player).is_observer():
        # Display hud of other player?
        pass
    else:
        if player.state.player_class == state.PlayerClass.SOLDIER:
            current_class = "soldier"
        elif player.state.player_class == state.PlayerClass.DEMOMAN:
            current_class = "demoman"
        else:
            return

        if current_map.records[current_class] is not None:
            wr = (
                "World Record:\n"
                + current_map.records[current_class]["player"]["name"]
                + " - "
                + str(
                    ticks_to_timestamp(current_map.records[current_class]["time"])
                    + "\n"
                )
            )
        else:
            wr = "World Record:\nNone\n"

        right_hint = KeyHintText(wr + "\n" + spectators + buffer_white_space)
        right_hint.send(current_player, spec_indexes)


def _draw_timer(player, current_map, spec_indexes):
    """Draw timer for player."""

    # lines for timer hud
    time_line = ""
    zone_line = ""
    mode_line = ""
    cp_line = ""

    if player.state.map_state == state.RunState.NONE:
        return

    if player.state.timer_mode == state.TimerMode.NONE:
        hint_text = HintText("Timer Disabled")
        hint_text.send(index_from_userid(player.userid))
        return

    if player.state.timer_mode == state.TimerMode.MAP:
        mode_line = "Map Mode"

        if player.state.map_state == state.RunState.START:
            zone_line = "[Map Start]"
            time_line = current_map.name

        elif player.state.map_state == state.RunState.RUN:
            zone_line = "[Map]"
            time_line = ticks_to_timestamp(server.tick - player.state.map[1])

        elif player.state.map_state == state.RunState.END:
            zone_line = "[Map End]"
            time_line = ticks_to_timestamp(player.state.map[2] - player.state.map[1])

    elif player.state.timer_mode == state.TimerMode.COURSE:
        mode_line = "Course Mode"

        if player.state.course_state == state.RunState.START:
            zone_line = f"[Course {player.state.course_index} Start]"

        elif player.state.course_state == state.RunState.RUN:
            zone_line = f"[Course {player.state.course_index}]"
            time_line = ticks_to_timestamp(server.tick - player.state.courses[0][1])

        elif player.state.course_state == state.RunState.END:
            zone_line = f"[Course {player.state.course_index} End]"
            time_line = ticks_to_timestamp(
                player.state.courses[0][2] - player.state.courses[0][1]
            )

    elif player.state.timer_mode == state.TimerMode.BONUS:
        mode_line = "Bonus Mode"

        if player.state.bonus_state == state.RunState.START:
            zone_line = f"[Bonus {player.state.bonus_index} Start]"

        elif player.state.bonus_state == state.RunState.RUN:
            zone_line = f"[Bonus {player.state.bonus_index}]"
            time_line = ticks_to_timestamp(server.tick - player.state.bonus[1])

        elif player.state.bonus_state == state.RunState.END:
            zone_line = f"[Bonus {player.state.bonus_index} End]"
            time_line = ticks_to_timestamp(
                player.state.bonus[2] - player.state.bonus[1]
            )

    # show last checkpoint if player has any
    if player.state.running:
        if player.state.checkpoints:
            last_cp = player.state.checkpoints[-1]

            class_string = None
            if player.state.player_class == state.PlayerClass.SOLDIER:
                class_string = "soldier"
            elif player.state.player_class == state.PlayerClass.DEMOMAN:
                class_string = "demoman"

            split_line = ticks_to_timestamp(last_cp[1] - player.state.map[1])

            if current_map.records[class_string] is not None:
                for record_checkpoint in current_map.records[class_string][
                    "checkpoints"
                ]:
                    if record_checkpoint["cp_index"] == last_cp[0].index:
                        split_time = (
                            last_cp[1] - player.state.map[1] - record_checkpoint["time"]
                        )
                        split_sign = "+" if split_time > 0 else "-"
                        split_line = f"WR{split_sign}{ticks_to_timestamp(split_time)}"
                        break

            cp_line = " (cp" + str(last_cp[0].index) + ": "
            cp_line += split_line
            cp_line += ")"

    # combine lines
    combined = ""

    if time_line:
        combined += time_line

    if cp_line:
        combined += "\n" + cp_line + "\n"
    else:
        # NOTE:
        # HintText needs something on "empty" lines or it freaks out,
        # use space between multiple newlines
        combined += "\n \n"

    if zone_line:
        combined += f"{zone_line}\n \n"

    combined += mode_line

    hint_text = HintText(combined)

    # draw
    hint_text.send(index_from_userid(player.userid), spec_indexes)
