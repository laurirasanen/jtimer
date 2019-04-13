"""Main module for jtimer plugin."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python imports
from commands.typed import TypedSayCommand
from commands import CommandReturn
from players.helpers import playerinfo_from_index
from steam import SteamID

# Custom imports
from .core.timer.timer import Timer
from .core.helpers.converts import steamid_to_player
from .core.helpers.utils import is_player
from .core.map.map import Map
from .core.api.auth import on_load as auth_on_load, on_unload as auth_on_unload
from .core.hud.radio import show_map_menu
from .core.hooks import *
from .core.chat.messages import message_hidechat_on, message_hidechat_off

# =============================================================================
# >> FUNCTIONS
# =============================================================================
def load():
    """Called when Source.Python loads the plugin."""
    Map.get_map()
    auth_on_load()
    print(f"[jtimer] Loaded!")


def unload():
    """Called when Source.Python unloads the plugin."""
    auth_on_unload()
    print(f"[jtimer] Unloaded!")


# =============================================================================
# >> COMMANDS
# =============================================================================
@TypedSayCommand("/timer")
def on_timer(command):
    """Called when player uses /timer command."""
    playerinfo = playerinfo_from_index(command.index)

    if is_player(playerinfo):
        Timer.instance().toggle_timer(
            command.index, SteamID.parse(playerinfo.steamid).to_steamid2()
        )

    return CommandReturn.BLOCK


@TypedSayCommand("/top")
def on_top(command):
    """Called when player uses /top command."""
    playerinfo = playerinfo_from_index(command.index)
    if is_player(playerinfo):
        if Timer.instance().current_map is not None:
            show_map_menu(Timer.instance().current_map.name, command.index)

    return CommandReturn.BLOCK


@TypedSayCommand("/r")
def on_restart(command):
    """Called when player uses /r command."""
    playerinfo = playerinfo_from_index(command.index)
    if is_player(playerinfo):
        player = steamid_to_player(SteamID.parse(playerinfo.steamid).to_steamid2())
        player.teleport_to_start()

    return CommandReturn.BLOCK


@TypedSayCommand("/hidechat")
def on_timer(command):
    """Called when player uses /hidechat command."""
    playerinfo = playerinfo_from_index(command.index)

    if is_player(playerinfo):
        player = steamid_to_player(SteamID.parse(playerinfo.steamid).to_steamid2())
        player.hidechat = not player.hidechat
        if player.hidechat:
            message_hidechat_on.send(player.index)
        else:
            message_hidechat_off.send(player.index)

    return CommandReturn.BLOCK