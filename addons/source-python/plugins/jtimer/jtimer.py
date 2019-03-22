# =============
# >> IMPORTS
# =============

# Source.Python imports
from listeners import OnTick, OnClientActive, OnClientDisconnect
from commands.typed import TypedSayCommand
from commands import CommandReturn
from players.helpers import playerinfo_from_index
from players import PlayerInfo
from filters.players import PlayerIter
from events import Event
from mathlib import Vector
from engines.server import server

# Custom imports
from .core.timer import timer
from .core.chat import messages
from .core.players.player import Player
from .core.players.state import Player_Class
from .core.players.state import State
from .core.helpers.converts import userid_to_player, steamid_to_player
from .core.map.map import Map
from .core.zones.zone import Zone

# =============
# >> GLOBALS
# =============


# =============
# >> FUNCTIONS
# =============


def load():
    # test zones
    m = Map(0)

    szc1 = Vector(-12115, -12195, -11805)
    szc2 = Vector(-12905, -11995, -11580)
    szcenter = (szc1 + szc2) / 2
    szextents = szcenter - szc2
    for i in range(0, 3):
        szextents[i] = abs(szextents[i])
    sz = Zone(szcenter, szextents)
    m.add_start_zone(sz)

    ezc1 = Vector(-10300, -13910, -12720)
    ezc2 = Vector(-9700, -12980, -12230)
    ezcenter = (ezc1 + ezc2) / 2
    ezextents = ezcenter - ezc2
    for i in range(0, 3):
        ezextents[i] = abs(ezextents[i])
    ez = Zone(ezcenter, ezextents)
    m.add_end_zone(ez)

    timer.current_map = m

    for p in PlayerIter():
        if not p.is_fake_client() and not p.is_hltv() and not p.is_bot():
            player = Player(p.playerinfo)
            timer.add_player(player)
    print(f"jtimer loaded!")


def unload():
    print(f"jtimer unloaded!")


@OnTick
def on_tick():
    timer.update_timers()
    if server.tick % 67 == 0:
        timer.current_map.start_zone.draw()
        timer.current_map.end_zone.draw()


@OnClientActive
def on_client_active(index):
    playerinfo = playerinfo_from_index(index)
    if PlayerInfo.is_fake_client(playerinfo) or PlayerInfo.is_hltv(playerinfo):
        return
    if PlayerInfo.is_player(playerinfo):
        player = Player(playerinfo)
        timer.add_player(player)


@OnClientDisconnect
def on_client_disconnect(index):
    playerinfo = playerinfo_from_index(index)
    if PlayerInfo.is_fake_client(playerinfo) or PlayerInfo.is_hltv(playerinfo):
        return
    if PlayerInfo.is_player(playerinfo):
        timer.remove_player(playerinfo.steamid)


@TypedSayCommand("/timer")
def on_timer(command):
    playerinfo = playerinfo_from_index(command.index)
    if PlayerInfo.is_fake_client(playerinfo) or PlayerInfo.is_hltv(playerinfo):
        return
    if PlayerInfo.is_player(playerinfo):
        timer.toggle_timer(command.index, playerinfo.steamid)

    return CommandReturn.BLOCK


@TypedSayCommand("/r")
def on_restart(command):
    playerinfo = playerinfo_from_index(command.index)
    if PlayerInfo.is_fake_client(playerinfo) or PlayerInfo.is_hltv(playerinfo):
        return
    if PlayerInfo.is_player(playerinfo):
        player = steamid_to_player(playerinfo.steamid)
        player.teleport_to_start()

    return CommandReturn.BLOCK


@Event("player_changeclass")
def on_player_changeclass(game_event):
    player = userid_to_player(game_event["userid"])
    class_index = game_event["class"]
    player.state.player_class = Player_Class(class_index)
    player.state.reset()


@Event("player_death")
def on_player_death(game_event):
    player = userid_to_player(game_event["userid"])
    player.state.reset()
