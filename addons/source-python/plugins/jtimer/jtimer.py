# =============
# >> IMPORTS
# =============

# Source.Python imports
from listeners import (
    OnTick,
    OnClientActive,
    OnClientDisconnect,
    OnLevelInit,
    OnLevelEnd,
)
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
from .core.api.maps import map_info_name
from .core.api.zones import map_zones

# =============
# >> GLOBALS
# =============


# =============
# >> FUNCTIONS
# =============


def load():
    get_map()
    get_players()
    print(f"jtimer loaded!")


def unload():
    print(f"jtimer unloaded!")


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
        map_ = Map(map_info["tiers"]["soldier"])

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
                    map_.add_start_zone(Zone(p1, p2))

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
            timer.current_map = map_


def get_players():
    for p in PlayerIter():
        if not p.is_fake_client() and not p.is_hltv() and not p.is_bot():
            player = Player(p.playerinfo, p.index)
            timer.add_player(player)


@OnLevelInit
def on_level_init(level):
    timer.clear()
    get_map()
    get_players()


@OnLevelEnd
def on_level_end():
    timer.clear()


@OnTick
def on_tick():
    timer.update_timers()
    if server.tick % 67 == 0:
        if timer.current_map:
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
