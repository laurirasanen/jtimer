from ..players.state import State, Run_State, Timer_Mode
from ..chat.messages import message_timer_enable, message_timer_disable, message_prefix
from ..helpers.converts import steamid_to_player, userid_to_source_player
from ..map.map import Map

players = []
current_map = None


def add_player(player):
    """add player reference to timer,
    this will allow runs"""
    for p in players:
        if p.steamid == player.steamid:
            print(
                f"ERR: Trying to add player {player.steamid} to timer array but player already exists!"
            )
            return
    players.append(player)


def remove_player(steamid):
    """remove player reference from timer,
    this will prevent runs"""
    for x in range(0, len(players)):
        if players[x].steamid == steamid:
            players.pop(x)
            return
    print(f"ERR: Tried to remove nonexistent player {steamid} from timer!")


def clear():
    """Reset everything on map load"""
    players = []
    current_map = None


def update_timers():
    """update all timers of active players"""
    for p in players:
        source_player = userid_to_source_player(p.userid)
        p.state.update(source_player.origin, source_player.maxs, source_player.velocity)


def toggle_timer(index, steamid):
    """toggle player timer on and off"""
    player = steamid_to_player(steamid)
    if player != None:
        if player.state.timer_mode != Timer_Mode.NONE:
            player.state.timer_mode = Timer_Mode.NONE
            message_timer_disable.send(index)
            return
        else:
            player.state.timer_mode = Timer_Mode.MAP
            message_timer_enable.send(index)
            player.teleport_to_start()
            return
    print(f"ERR: Tried to toggle player {steamid} timer but couldn't find player!")
