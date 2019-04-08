# =============
# >> IMPORTS
# =============
from threading import Timer as ThreadTimer
from threading import Thread

# Source.Python imports
from commands.typed import TypedSayCommand
from commands import CommandReturn
from players.helpers import playerinfo_from_index, address_from_playerinfo, index_from_playerinfo
from players import PlayerInfo
from players.entity import Player as SourcePlayer
from filters.players import PlayerIter
from steam import SteamID

# Custom imports
from .core.timer.timer import Timer
from .core.chat.messages import message_player_join, message_player_join_unranked
from .core.players.player import Player
from .core.players.state import Player_Class, Timer_Mode
from .core.players.state import State
from .core.helpers.converts import userid_to_player, steamid_to_player
from .core.helpers.utils import is_player, get_country, get_players
from .core.map.map import Map
from .core.map.checkpoint import Checkpoint
from .core.zones.zone import Zone
from .core.api.maps import map_info_name
from .core.api.zones import map_zones
from .core.api.auth import on_load as auth_on_load, on_unload as auth_on_unload
from .core.api.players import add_player as api_add_player
from .core.hud.radio import show_map_menu
from .core.hooks import *

# =============
# >> FUNCTIONS
# =============


def load():
    auth_on_load()
    Map.get_map()
    # wait for authentication
    ThreadTimer(2, add_players).start()
    print(f"[jtimer] Loaded!")


def add_players():
    for player in get_players():
        Player.add_player(player.playerinfo, player.index)


def unload():
    auth_on_unload()
    print(f"[jtimer] Unloaded!")


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
