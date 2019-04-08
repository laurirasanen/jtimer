"""Module for custom player."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
from mathlib import Vector
from steam import SteamID
from players.helpers import address_from_playerinfo, index_from_playerinfo
from players.entity import Player as SourcePlayer

# Custom Imports
from .state import State
from .state import TimerMode, PlayerClass
from ..timer.timer import Timer
from ..helpers.converts import userid_to_source_player
from ..helpers.utils import get_player_indices, get_country
from ..api.players import (
    add_player as api_add_player,
    search_player as api_search_player,
)
from ..chat.messages import message_player_join, message_player_join_unranked
from ..config import API_CFG

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# TODO: why use this instead of mathlib.NULL_VECTOR ?
NULL_VECTOR = Vector(0.0, 0.0, 0.0)


class Player:
    """Custom Player class for use with the timer."""

    def __init__(self, id_, playerinfo, index):
        """Create a new player."""
        self.id_ = id_
        self.userid = playerinfo.userid
        self.steamid = SteamID.parse(playerinfo.steamid).to_steamid2()
        self.index = index
        self.name = playerinfo.name
        self.state = State(self)
        self.has_start = False

    def start(self):
        """Reset player state and teleport to the start."""
        self.state.reset()

        if (
            self.state.player_class == PlayerClass.SOLDIER
            or self.state.player_class == PlayerClass.DEMOMAN
        ):
            # enable timer if disabled and map zoned
            if Timer.instance().current_map and Timer.instance().current_map.start_zone:
                if self.state.timer_mode == TimerMode.NONE:
                    self.state.timer_mode = TimerMode.MAP

            else:
                # map not zoned
                self.state.timer_mode = TimerMode.NONE

        else:
            # unsupported class, disable timer
            self.state.timer_mode = TimerMode.NONE

        self._teleport_to_start()

    def _teleport_to_start(self):
        """Teleport to the start."""
        if (
            self.state.timer_mode == TimerMode.MAP
            or self.state.timer_mode == TimerMode.NONE
        ):
            # TODO: add setstart
            if self.has_start:
                pass

            else:
                # no saved start, use map
                if not self._tp_map_start():
                    # failed
                    # TODO: send chat msg
                    pass

    def _tp_map_start(self):
        """Teleport to map start.
        Return True on success"""
        if Timer.instance().current_map and Timer.instance().current_map.start_zone:
            start_zone = Timer.instance().current_map.start_zone
            start = Vector(
                start_zone.center[0],
                start_zone.center[1],
                start_zone.center[2] - start_zone.extents[2],
            )
            orientation = Vector(0, start_zone.orientation, 0)
            source_player = userid_to_source_player(self.userid)
            source_player.teleport(start, angle=orientation, velocity=NULL_VECTOR)
            return True
        return False

    @staticmethod
    def add_player(playerinfo, index):
        """Add a player to the Timer."""
        ip = address_from_playerinfo(playerinfo).split(":")[0]
        country, code = get_country(ip)

        api_player = None
        if API_CFG["authenticate"]:
            api_player = api_add_player(
                SteamID.parse(playerinfo.steamid).to_steamid2(), playerinfo.name, code
            )
        else:
            # Don't try to update or add player to api
            api_player = api_search_player(
                steamid=SteamID.parse(playerinfo.steamid).to_steamid2()
            )

        player = None
        if api_player is not None:
            player = Player(api_player["id"], playerinfo, index)
        else:
            player = Player(-1, playerinfo, index)

        if not playerinfo.is_dead():
            p = SourcePlayer(index_from_playerinfo(playerinfo))
            player.state.player_class = PlayerClass(p.player_class)
            player.start()

        Timer.instance().add_player(player)

        if api_player is None:
            return

        # Send join message
        srank = api_player["rank_info"].get("soldier_rank")
        drank = api_player["rank_info"].get("demoman_rank")

        if srank > 0 or drank > 0:
            is_soldier = drank == 0 or (0 < srank <= drank)

            rank = srank if is_soldier else drank
            class_name = "Soldier" if is_soldier else "Demoman"

            message_player_join.send(
                get_player_indices(),
                name=playerinfo.name,
                rank=rank,
                class_name=class_name,
                country=country,
            )
            return

        message_player_join_unranked.send(
            get_player_indices(), name=playerinfo.name, country=country
        )
