from players.helpers import index_from_userid
from ..helpers.converts import ticks_to_timestamp
from messages import HintText
from engines.server import server
from ..players import state


def draw_timer(player):
    # lines for timer hud
    time_line = ""
    zone_line = ""
    mode_line = ""
    cp_line = ""

    if player.state.timer_mode == state.Timer_Mode.NONE:
        hintText = HintText("Timer Disabled")
        hintText.send(index_from_userid(player.userid))
        return

    if player.state.timer_mode == state.Timer_Mode.MAP:
        mode_line = "Map Mode"

        if player.state.map_state == state.Run_State.START:
            zone_line = "[Map Start]"
            time_line = "jump_mapname"

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
            # TODO: wr / pr splits
            # just prints the time since the map started now
            last_cp = player.state.checkpoints[-1]
            cp_line = " (cp" + str(last_cp[0].index) + ": "
            cp_line += ticks_to_timestamp(last_cp[1] - player.state.map[1])
            cp_line += ")"

    # combine lines
    combined = ""

    if len(time_line) > 0:
        combined += time_line

    if len(cp_line) > 0:
        combined += cp_line

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
