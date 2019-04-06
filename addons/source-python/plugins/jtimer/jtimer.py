# =============
# >> IMPORTS
# =============
from threading import Timer as ThreadTimer
from threading import Thread

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
from players.helpers import playerinfo_from_index, address_from_playerinfo
from players import PlayerInfo
from filters.players import PlayerIter
from events import Event
from mathlib import Vector
from engines.server import server
from steam import SteamID
from cvars import ConVar

# Custom imports
from .core.timer.timer import Timer
from .core.chat.messages import message_player_join, message_player_join_unranked
from .core.players.player import Player
from .core.players.state import Player_Class, Timer_Mode
from .core.players.state import State
from .core.helpers.converts import userid_to_player, steamid_to_player
from .core.helpers.utils import is_player, get_country, get_player_indices
from .core.map.map import Map
from .core.map.checkpoint import Checkpoint
from .core.zones.zone import Zone
from .core.api.maps import map_info_name
from .core.api.zones import map_zones
from .core.api.auth import on_load as auth_on_load, on_unload as auth_on_unload
from .core.api.players import add_player
from .core.hud.radio import show_map_menu

# =============
# >> GLOBALS
# =============


# =============
# >> FUNCTIONS
# =============


def load():
    auth_on_load()
    get_map()
    # wait for authentication
    ThreadTimer(2, get_players).start()
    print(f"[jtimer] Loaded!")


def unload():
    auth_on_unload()
    print(f"[jtimer] Unloaded!")


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
            Timer.instance().current_map = map_


def get_players():
    for p in PlayerIter():
        if not p.is_fake_client() and not p.is_hltv() and not p.is_bot():
            api_player = add_player(
                p.raw_steamid.to_steamid2(), p.playerinfo.name, "FI"
            )
            player = None
            if api_player is not None:
                player = Player(api_player["id"], p.playerinfo, p.index)
            else:
                player = Player(-1, p.playerinfo, p.index)

            if not p.playerinfo.is_dead():
                player.state.player_class = Player_Class(p.player_class)
            Timer.instance().add_player(player)
            if not p.playerinfo.is_dead:
                player_start(player)


def player_start(player):
    player.state.reset()

    if (
        player.state.player_class == Player_Class.SOLDIER
        or player.state.player_class == Player_Class.DEMOMAN
    ):
        # enable timer if disabled and map zoned
        if Timer.instance().current_map and Timer.instance().current_map.start_zone:
            if player.state.timer_mode == Timer_Mode.NONE:
                player.state.timer_mode = Timer_Mode.MAP

        else:
            # map not zoned
            player.state.timer_mode = Timer_Mode.NONE

    else:
        # unsupported class, disable timer
        player.state.timer_mode = Timer_Mode.NONE

    player.teleport_to_start()


def api_add_player(playerinfo, index):
    ip = address_from_playerinfo(playerinfo).split(":")[0]
    country, code = get_country(ip)

    api_player = add_player(
        SteamID.parse(playerinfo.steamid).to_steamid2(), playerinfo.name, code
    )
    player = None
    if api_player is not None:
        player = Player(api_player["id"], playerinfo, index)
    else:
        player = Player(-1, playerinfo, index)

    message_player_join_unranked.send(
        get_player_indices(), name=playerinfo.name, country=country
    )

    Timer.instance().add_player(player)


@OnLevelInit
def on_level_init(level):
    Timer.instance().clear()
    get_map()
    get_players()


@OnLevelEnd
def on_level_end():
    Timer.instance().clear()


@OnTick
def on_tick():
    Timer.instance().update_timers()
    if server.tick % 67 == 0:
        if Timer.instance().current_map:
            Timer.instance().current_map.start_zone.draw()
            Timer.instance().current_map.end_zone.draw()
            for checkpoint in Timer.instance().current_map.checkpoints:
                checkpoint.draw()


@OnClientActive
def on_client_active(index):
    playerinfo = playerinfo_from_index(index)
    if is_player(playerinfo):
        Thread(target=api_add_player, args=(playerinfo, index)).start()
    else:
        return


@OnClientDisconnect
def on_client_disconnect(index):
    playerinfo = playerinfo_from_index(index)
    if is_player(playerinfo):
        Timer.instance().remove_player(SteamID.parse(playerinfo.steamid).to_steamid2())
    else:
        return


@TypedSayCommand("/timer")
def on_timer(command):
    playerinfo = playerinfo_from_index(command.index)

    if is_player(playerinfo):
        Timer.instance().toggle_timer(
            command.index, SteamID.parse(playerinfo.steamid).to_steamid2()
        )

    return CommandReturn.BLOCK


@TypedSayCommand("/top")
def on_top(command):
    playerinfo = playerinfo_from_index(command.index)
    if is_player(playerinfo):
        if Timer.instance().current_map != None:
            show_map_menu(Timer.instance().current_map.name, command.index)

    return CommandReturn.BLOCK


@TypedSayCommand("/r")
def on_restart(command):
    playerinfo = playerinfo_from_index(command.index)
    if is_player(playerinfo):
        player = steamid_to_player(SteamID.parse(playerinfo.steamid).to_steamid2())
        player.teleport_to_start()

    return CommandReturn.BLOCK


@Event("player_spawn")
def on_player_spawn(game_event):
    cancel_wait = ConVar(name="mp_waitingforplayers_cancel")
    cancel_wait.set_bool(True)

    player = userid_to_player(game_event["userid"])
    if player is not None:
        class_index = game_event["class"]
        player.state.player_class = Player_Class(class_index)
        player_start(player)


@Event("player_death")
def on_player_death(game_event):
    player = userid_to_player(game_event["userid"])
    player.state.reset()
