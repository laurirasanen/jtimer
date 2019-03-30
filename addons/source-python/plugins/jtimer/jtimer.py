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
from .core.map.checkpoint import Checkpoint
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

    # soar start
    p1 = Vector(1590, -2340, -1900)
    p2 = Vector(1162, -2215, -1500)
    m.add_start_zone(Zone(p1, p2, 90))

    # end of lvl 1
    p1 = Vector(1635, -940, -1560)
    p2 = Vector(1250, -850, -1000)
    m.add_checkpoint(Checkpoint(1, p1, p2))

    p1 = Vector(1550, -135, -1500)
    p2 = Vector(1690, 8, -1000)
    m.add_checkpoint(Checkpoint(2, p1, p2))

    # start of lvl 2
    p1 = Vector(1290, 8, -1500)
    p2 = Vector(1100, -135, -1000)
    m.add_end_zone(Zone(p1, p2))

    timer.current_map = m

    for p in PlayerIter():
        if not p.is_fake_client() and not p.is_hltv() and not p.is_bot():
            player = Player(p.playerinfo, p.index)
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
        for checkpoint in timer.current_map.checkpoints:
            checkpoint.draw()


@OnClientActive
def on_client_active(index):
    playerinfo = playerinfo_from_index(index)
    if PlayerInfo.is_fake_client(playerinfo) or PlayerInfo.is_hltv(playerinfo):
        return
    if PlayerInfo.is_player(playerinfo):
        player = Player(playerinfo, index)
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
