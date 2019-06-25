"""Module for punitive admin commands."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
from commands.typed import TypedSayCommand
from players.voice import mute_manager
from engines.server import queue_command_string

# Custom Imports
from ..players.player import Player
from ..helpers.search import find_player_with_name


# =============================================================================
# >> ADMIN CLASS
# =============================================================================
class Admin(Player):
    """Admin class for storing permission flags and commands."""

    def __init__(self, player, flags):
        self.admin = player
        self.flags = flags

    @TypedSayCommand("/kick")
    def kick(self, player, reason=""):
        """Kick player."""
        victim = find_player_with_name(player)
        queue_command_string(f"kickid {victim.userid} {reason}")

    @TypedSayCommand("/mute")
    def mute(self, player, reason=""):
        """Mute player."""
        victim = find_player_with_name(player)
        mute_manager.mute_player(victim.name)
