from messages import HintText, KeyHintText
from engines.server import server
from players.entity import Player
from players.helpers import index_from_userid

from ..helpers.converts import ticks_to_timestamp
from ..players import state
from ..helpers.utils import returnSpectators

bufferWhiteSpace = "\n\n\n\n\n\n"


def draw(player, current_map):
    currentPlayer = index_from_userid(player.userid)
    if Player(currentPlayer).is_observer():
        # Hud will be drawn by other player
        pass
    else:
        specIndexes = returnSpectators(currentPlayer, "index")
        draw_timer(player, current_map, specIndexes)
        draw_rightHud(player, current_map, specIndexes)


def draw_rightHud(player, current_map, specIndexes):
    currentPlayer = index_from_userid(player.userid)
    spectators = "Spectators: " + returnSpectators(currentPlayer)

    if Player(currentPlayer).is_observer():
        # Display hud of other player?
        pass
    else:
        if player.state.player_class == state.Player_Class.SOLDIER:
            currentClass = "soldier"
        elif player.state.player_class == state.Player_Class.DEMOMAN:
            currentClass = "demoman"

        if current_map.records[currentClass] is not None:
            wr = (
                "World Record:\n"
                + current_map.records[currentClass]["player"]["name"]
                + " - "
                + str(
                    ticks_to_timestamp(current_map.records[currentClass]["time"]) + "\n"
                )
            )
        else:
            wr = "World Record:\nNone\n"

        rightHint = KeyHintText(wr + "\n" + spectators + bufferWhiteSpace)
        rightHint.send(currentPlayer, specIndexes)


def draw_timer(player, current_map, specIndexes):
    # lines for timer hud
    time_line = ""
    zone_line = ""
    mode_line = ""
    cp_line = ""

    if player.state.map_state == state.Run_State.NONE:
        return

    if player.state.timer_mode == state.Timer_Mode.NONE:
        hintText = HintText("Timer Disabled")
        hintText.send(index_from_userid(player.userid))
        return

    if player.state.timer_mode == state.Timer_Mode.MAP:
        mode_line = "Map Mode"

        if player.state.map_state == state.Run_State.START:
            zone_line = "[Map Start]"
            time_line = current_map.name

        elif player.state.map_state == state.Run_State.RUN:
            zone_line = "[Map]"
            time_line = ticks_to_timestamp(server.tick - player.state.map[1])

        elif player.state.map_state == state.Run_State.END:
            zone_line = "[Map End]"
            time_line = ticks_to_timestamp(player.state.map[2] - player.state.map[1])

    elif player.state.timer_mode == state.Timer_Mode.COURSE:
        mode_line = "Course Mode"

        if player.state.course_state == state.Run_State.START:
            zone_line = f"[Course {player.state.course_index} Start]"

        elif player.state.course_state == state.Run_State.RUN:
            zone_line = f"[Course {player.state.course_index}]"
            time_line = ticks_to_timestamp(server.tick - player.state.courses[0][1])

        elif player.state.course_state == state.Run_State.END:
            zone_line = f"[Course {player.state.course_index} End]"
            time_line = ticks_to_timestamp(
                player.state.courses[0][2] - player.state.courses[0][1]
            )

    elif player.state.timer_mode == state.Timer_Mode.BONUS:
        mode_line = "Bonus Mode"

        if player.state.bonus_state == state.Run_State.START:
            zone_line = f"[Bonus {player.state.bonus_index} Start]"

        elif player.state.bonus_state == state.Run_State.RUN:
            zone_line = f"[Bonus {player.state.bonus_index}]"
            time_line = ticks_to_timestamp(server.tick - player.state.bonus[1])

        elif player.state.bonus_state == state.Run_State.END:
            zone_line = f"[Bonus {player.state.bonus_index} End]"
            time_line = ticks_to_timestamp(
                player.state.bonus[2] - player.state.bonus[1]
            )

    # show last checkpoint if player has any
    if player.state.running:
        if len(player.state.checkpoints) > 0:
            last_cp = player.state.checkpoints[-1]

            class_string = None
            if player.state.player_class == state.Player_Class.SOLDIER:
                class_string = "soldier"
            elif player.state.player_class == state.Player_Class.DEMOMAN:
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

    if len(time_line) > 0:
        combined += time_line

    if len(cp_line) > 0:
        combined += "\n" + cp_line + "\n"
    else:
        # NOTE:
        # HintText needs something on "empty" lines or it freaks out,
        # use space between multiple newlines
        combined += "\n \n"

    if len(zone_line) > 0:
        combined += f"{zone_line}\n \n"

    combined += mode_line

    hintText = HintText(combined)

    # draw
    hintText.send(index_from_userid(player.userid))
    # TODO: handle spectators
