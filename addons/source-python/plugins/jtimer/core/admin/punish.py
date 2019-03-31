#Snake
from players.voice import _MuteManager
from commands.typed import TypedSayCommand
from engines.server import queue_command_string

#jtimer
from ..players.player import Player
from ..helpers.search import findPlayerIdWithName
from ..helpers.converts import userid_to_player

class Admin(Player):
    def __init__(self, player, flags):
        self.admin = player
        self.flags = flags

    @TypedSayCommand("/kick")
    def kick(self, player, reason = ""):
        victim = findPlayerIdWithName(player)
        queue_command_string("kickid {} {}".format(str(victim.userid), reason) )

    @TypedSayCommand("/mute")
    def mute(self, player, reason = ""):
        victim = findPlayerIdWithName(player)
        mute_player(victim.name)

    def commandRestrict(self, player, reason = ""):
        victim = findPlayerIdWithName(player)
        userid_to_player(victim)
