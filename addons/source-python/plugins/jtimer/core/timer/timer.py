"""Module for main timer."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Custom Imports
from ..players.state import TimerMode
from ..chat.messages import message_timer_enable, message_timer_disable
from ..helpers.converts import steamid_to_player, userid_to_source_player


# =============================================================================
# >> TIMER CLASS
# =============================================================================
class Timer:
    """Singleton Timer class"""

    __instance = None
    players = []
    current_map = None

    def instance():
        """Singleton instance"""
        if Timer.__instance is None:
            Timer()
        return Timer.__instance

    def __init__(self):
        """Private constructor."""
        if Timer.__instance is not None:
            raise Exception("This class is a singleton, use .instance() access method.")

        self.players = []
        self.current_map = None
        Timer.__instance = self

    def add_player(self, player):
        """Add player reference to timer,
	    this will allow runs."""
        for p in self.players:
            if p.steamid == player.steamid:
                return
        self.players.append(player)

    def remove_player(self, steamid):
        """Remove player reference from timer,
	    this will prevent runs."""
        for x in range(0, len(self.players)):
            if self.players[x].steamid == steamid:
                self.players.pop(x)
                return

    def clear(self):
        """Reset everything on map load."""
        self.players = []
        self.current_map = None

    def update_timers(self):
        """Update all timers of active players."""
        for p in self.players:
            source_player = userid_to_source_player(p.userid)
            if source_player is None:
                self.players.remove(p)
                continue
            p.state.update(
                self.current_map,
                source_player.origin,
                source_player.maxs,
                source_player.velocity,
            )

    def toggle_timer(self, index, steamid):
        """Toggle player timer on and off."""
        player = steamid_to_player(steamid)
        if player is not None:
            if player.state.timer_mode != TimerMode.NONE:
                player.state.timer_mode = TimerMode.NONE
                message_timer_disable.send(index)
                return

            player.state.timer_mode = TimerMode.MAP
            message_timer_enable.send(index)
            player.teleport_to_start()
            return
