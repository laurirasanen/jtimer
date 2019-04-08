"""Module for hooking in-game events."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
from threading import Thread

# Source.Python Imports
from listeners import (
    OnTick,
    OnClientActive,
    OnClientDisconnect,
    OnLevelInit,
    OnLevelEnd,
)
from events import Event
from events.hooks import PreEvent, EventAction
from players.helpers import playerinfo_from_index
from steam import SteamID
from cvars import ConVar
from engines.server import server

# Custom Imports
from .timer.timer import Timer
from .helpers.utils import is_player, get_players
from .helpers.converts import userid_to_player
from .players.player import Player
from .map.map import Map
from .players.state import PlayerClass


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnLevelInit
def on_level_init(level):
    """Called when a new map is loaded."""
    Timer.instance().clear()
    Map.get_map()
    for player in get_players():
        Player.add_player(player.playerinfo, player.index)


@OnLevelEnd
def on_level_end():
    """Called when a map is unloaded."""
    Timer.instance().clear()


@OnTick
def on_tick():
    """Called every engine tick."""
    Timer.instance().update_timers()
    if server.tick % 67 == 0:
        if Timer.instance().current_map:
            Timer.instance().current_map.start_zone.draw()
            Timer.instance().current_map.end_zone.draw()
            for checkpoint in Timer.instance().current_map.checkpoints:
                checkpoint.draw()


@OnClientActive
def on_client_active(index):
    """Called when a client has fully joined the game."""
    playerinfo = playerinfo_from_index(index)
    if is_player(playerinfo):
        Thread(target=Player.add_player, args=(playerinfo, index)).start()
    else:
        return


@OnClientDisconnect
def on_client_disconnect(index):
    """Called when a client leaves the game."""
    playerinfo = playerinfo_from_index(index)
    if is_player(playerinfo):
        Timer.instance().remove_player(SteamID.parse(playerinfo.steamid).to_steamid2())
    else:
        return


# =============================================================================
# >> PRE-EVENTS
# =============================================================================
@PreEvent("player_death")
def pre_player_death(game_event):
    """Called before a player dies."""
    # Don't broadcast to other players.
    return EventAction.STOP_BROADCAST


@PreEvent("player_team")
def pre_player_team(game_event):
    """Called before a player joins a team."""
    # Don't broadcast to other players.
    return EventAction.STOP_BROADCAST


# =============================================================================
# >> EVENTS
# =============================================================================
@Event("player_spawn")
def on_player_spawn(game_event):
    """Called when a player spawns."""
    cancel_wait = ConVar(name="mp_waitingforplayers_cancel")
    cancel_wait.set_bool(True)

    player = userid_to_player(game_event["userid"])
    if player is not None:
        class_index = game_event["class"]
        player.state.player_class = PlayerClass(class_index)
        player.start()


@Event("player_death")
def on_player_death(game_event):
    """Called when a player dies."""
    player = userid_to_player(game_event["userid"])
    player.state.reset()
