from ..players.state import State, Run_State, Timer_Mode
from ..chat.messages import message_timer_enable, message_timer_disable, message_prefix
from ..helpers.converts import steamid_to_player, userid_to_source_player
from ..map.map import Map


class Timer:
    __instance = None
    players = []
    current_map = None

    def instance():
        """Singleton instance"""
        if Timer.__instance == None:
            Timer()
        return Timer.__instance

    def __init__(self):
        """Private constructor"""
        if Timer.__instance != None:
            raise Exception("This class is a singleton, use .instance() access method.")
        else:
            self.players = []
            self.current_map = None
            Timer.__instance = self

    def add_player(self, player):
        """add player reference to timer,
	    this will allow runs"""
        for p in self.players:
            if p.steamid == player.steamid:
                print(
                    f"ERR: Trying to add player {player.steamid} to timer array but player already exists!"
                )
                return
        self.players.append(player)

    def remove_player(self, steamid):
        """remove player reference from timer,
	    this will prevent runs"""
        for x in range(0, len(self.players)):
            if self.players[x].steamid == steamid:
                self.players.pop(x)
                return
        print(f"ERR: Tried to remove nonexistent player {steamid} from timer!")

    def clear(self):
        """Reset everything on map load"""
        self.players = []
        self.current_map = None

    def update_timers(self):
        """update all timers of active players"""
        for p in self.players:
            source_player = userid_to_source_player(p.userid)
            p.state.update(
                self.current_map,
                source_player.origin,
                source_player.maxs,
                source_player.velocity,
            )

    def toggle_timer(self, index, steamid):
        """toggle player timer on and off"""
        player = steamid_to_player(steamid)
        if player != None:
            if player.state.timer_mode != Timer_Mode.NONE:
                player.state.timer_mode = Timer_Mode.NONE
                message_timer_disable.send(index)
                return
            else:
                player.state.timer_mode = Timer_Mode.MAP
                message_timer_enable.send(index)
                player.teleport_to_start()
                return
        print(f"ERR: Tried to toggle player {steamid} timer but couldn't find player!")
