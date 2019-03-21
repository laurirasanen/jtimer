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

# Custom imports
from .core.timer import timer
from .core.chat import messages
from .core.players.player import Player
from .core.players.state import Player_Class
from .core.players.state import State
from .core.helpers.converts import steamid_to_player

# =============
# >> GLOBALS
# =============


# =============
# >> FUNCTIONS
# =============

def load():
    for p in PlayerIter():
        if (not p.is_fake_client()
          and not p.is_hltv()
          and not p.is_bot()):
            player = Player(p.steamid, p.get_name())
            timer.add_player(player)
    print(f'opentimer loaded!')

def unload():
    print(f'opentimer unloaded!')

@OnTick
def on_tick():
    timer.update_timers()

@OnClientActive
def on_client_active(index):
    playerinfo = playerinfo_from_index(index)
    if (PlayerInfo.is_fake_client(playerinfo)
      or PlayerInfo.is_hltv(playerinfo)):
        return
    if PlayerInfo.is_player(playerinfo):
        player = Player(playerinfo.steamid, playerinfo.name)
        timer.add_player(player)

@OnClientDisconnect
def on_client_disconnect(index):
    playerinfo = playerinfo_from_index(index)
    if (PlayerInfo.is_fake_client(playerinfo)
      or PlayerInfo.is_hltv(playerinfo)):
        return
    if PlayerInfo.is_player(playerinfo):
        timer.remove_player(playerinfo.steamid)

@TypedSayCommand('/timer')
def on_timer(command):
    playerinfo = playerinfo_from_index(command.index)
    if (PlayerInfo.is_fake_client(playerinfo)
      or PlayerInfo.is_hltv(playerinfo)):
        return
    if PlayerInfo.is_player(playerinfo):
        timer.toggle_timer(command.index, playerinfo.steamid)

    return CommandReturn.BLOCK

@Event('player_changeclass')
def on_player_changeclass(game_event):
    player = steamid_to_player(game_event['steamid'])
    class_index = game_event['class']
    player.state.player_class = Player_Class(class_index)
    player.state.reset()

@Event('player_death')
def on_player_death(game_event):
    player = steamid_to_player(game_event['steamid'])
    player.state.reset()