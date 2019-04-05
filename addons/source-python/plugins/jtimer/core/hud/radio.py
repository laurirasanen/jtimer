from threading import Thread
from collections.abc import Iterable
import json
from menus.radio import PagedRadioMenu, PagedRadioOption

from ..api.times import map_times
from ..api.maps import map_info_name
from ..helpers.converts import ticks_to_timestamp
from ..chat.messages import messag_no_match

"""
List for storing cached menus.
Deleted from cache when all players have closed menu.

schema =
{
    "menu": <menu>,
    "map_id": <int>,
    "opened_by": [<int:player_index>,],
    "map_top": {
        "menu": <menu>,
        "map_times": [
            {
                "menu": <menu>,
                <time keys>
            }
        ]
    },
    "course_top": {
        "menu": <menu>,
        "course_times": [
            {
                "menu": <menu>,
                <time keys>
            }
        ]
    },
    "bonus_top": {
        "menu": <menu>,
        "bonus_times": [
            {
                "menu": <menu>,
                <time keys>
            }
        ]
    }
}
"""
_cached_map_menus = []


def show_map_menu(map_name, player_index):
    """Show map times radio menu to player."""
    thread = _ThreadWithCallback(
        target=_map_top_parent_menu,
        args=(map_name, player_index),
        callback=_show_map_menu_callback,
    )
    thread.start()


def _show_map_menu_callback(result, player_index):
    if result is False:
        messag_no_match.send(player_index)


def _map_top_parent_menu(map_name, player_index):
    """Construct PagedRadioMenu with map, course and bonus times."""
    map_info, r = map_info_name(map_name)
    if map_info is None:
        return False, player_index

    global _cached_map_menus
    for cached_menu in _cached_map_menus:
        if cached_menu["map_id"] == map_info["id"]:
            cached_menu["menu"].send(player_index)
            if player_index not in cached_menu["opened_by"]:
                cached_menu["opened_by"].append(player_index)
            return True, player_index

    data = [PagedRadioOption("Map", value=map_info)]
    menu = PagedRadioMenu(
        data=data,
        title="Top Times",
        description=map_info["name"],
        select_callback=_map_parent_select,
        close_callback=_map_parent_close,
        top_separator="",
        bottom_separator="",
    )
    _cached_map_menus.append(
        {
            "menu": menu,
            "map_id": map_info["id"],
            "opened_by": [player_index],
            "map_top": None,
            "course_top": None,
            "bonus_top": None,
        }
    )
    menu.send(player_index)

    return True, player_index


def _map_parent_select(menu, player_index, selected_option):
    map_info = selected_option.value

    global _cached_map_menus

    for cached_menu in _cached_map_menus:
        if cached_menu["map_id"] == map_info["id"]:
            new_cache = cached_menu.copy()
            _cached_map_menus.remove(cached_menu)

            map_top = new_cache["map_top"]

            if map_top is None:
                top_menu, soldier_times, demoman_times = _map_top_menu(
                    map_info["id"], map_info["name"]
                )
                map_top = {"menu": top_menu, "map_times": []}

                for stime in soldier_times:
                    map_top["map_times"].append(stime)
                for dtime in demoman_times:
                    map_top["map_times"].append(dtime)

            map_top["menu"].parent_menu = menu
            new_cache["map_top"] = map_top

            _cached_map_menus.append(new_cache)

            map_top["menu"].send(player_index)
            break


def _map_parent_close(menu, player_index):
    global _cached_map_menus
    for cached_menu in _cached_map_menus:
        if cached_menu["menu"] == menu:
            new_cache = cached_menu.copy()
            _cached_map_menus.remove(cached_menu)

            new_cache["opened_by"].remove(player_index)
            if len(new_cache["opened_by"]) == 0:
                # menu closed by all players, remove cache
                del new_cache
            else:
                _cached_map_menus.append(new_cache)


def _map_top_menu(map_id, map_name):
    """Construct PagedRadioMenu with top 50 times for map."""
    times = map_times(map_id)
    if times is None:
        times = {"soldier": [], "demoman": []}

    soldier_options = []
    demoman_options = []

    for soldier_time in times["soldier"]:
        timestamp = ticks_to_timestamp(soldier_time["time"])
        split = ticks_to_timestamp(soldier_time["time"] - times["soldier"][0]["time"])
        rank = soldier_time["rank"]
        name = soldier_time["player"]["name"]

        text = f"[#{rank}] {timestamp} +{split} :: {name}"

        soldier_options.append(
            PagedRadioOption(text, value=(map_id, map_name, 2, rank))
        )

    for demoman_time in times["demoman"]:
        timestamp = ticks_to_timestamp(demoman_time["time"])
        split = ticks_to_timestamp(demoman_time["time"] - times["demoman"][0]["time"])
        rank = demoman_time["rank"]
        name = demoman_time["player"]["name"]

        text = f"[#{rank}] {timestamp} +{split} :: {name}"

        demoman_options.append(
            PagedRadioOption(text, value=(map_id, map_name, 4, rank))
        )

    menu = PagedRadioMenu(
        data=soldier_options,
        title="Soldier Top Times",
        description=f"{map_name} - Map",
        select_callback=_map_top_select,
        close_callback=_map_top_close,
        top_separator="",
        bottom_separator="",
    )

    return menu, times["soldier"], times["demoman"]


def _map_top_select(menu, player_index, selected_option):
    selected_value = selected_option.value

    global _cached_map_menus
    map_time = None
    for cached_menu in _cached_map_menus:
        if cached_menu["map_id"] == selected_value[0]:
            new_cache = cached_menu.copy()
            _cached_map_menus.remove(cached_menu)
            for cached_time in new_cache["map_top"]["map_times"]:
                if (
                    cached_time["class"] == selected_value[2]
                    and cached_time["rank"] == selected_value[3]
                ):
                    cached_time["menu"] = _map_time_menu(selected_value[1], cached_time)

                    cached_time["menu"].parent_menu = menu

                    _cached_map_menus.append(new_cache)
                    cached_time["menu"].send(player_index)
                    break


def _map_top_close(menu, player_index):
    global _cached_map_menus
    for cached_menu in _cached_map_menus:
        if cached_menu["map_top"]["menu"] == menu:
            new_cache = cached_menu.copy()
            _cached_map_menus.remove(cached_menu)
            new_cache["opened_by"].remove(player_index)

            if len(new_cache["opened_by"]) == 0:
                del new_cache
            else:
                _cached_map_menus.append(new_cache)


def _map_time_menu(map_name, map_time):
    data = None

    player_name = map_time["player"]["name"]
    class_string = "Soldier" if map_time["class"] == 2 else "Demoman"
    duration = ticks_to_timestamp(map_time["time"])

    description = (
        " \n"
        + f"Player: {player_name}\n"
        + f"Map: {map_name}\n"
        + f"Class: {class_string}\n"
        + " \n"
        + f"Duration: {duration}\n"
        + f"Date: -\n"
        + f"Server: -\n"
    )

    menu = PagedRadioMenu(
        data=data,
        title="Map Run Info",
        description=description,
        close_callback=_map_time_close,
        top_separator="",
        bottom_separator="",
    )
    return menu


def _map_time_close(menu, player_index):
    global _cached_map_menus
    for cached_menu in _cached_map_menus:
        for map_time in cached_menu["map_top"]["map_times"]:
            if map_time["menu"] == menu:
                new_cache = cached_menu.copy()
                _cached_map_menus.remove(cached_menu)
                new_cache["opened_by"].remove(player_index)

                if len(new_cache["opened_by"]) == 0:
                    del new_cache
                else:
                    _cached_map_menus.append(new_cache)


class _ThreadWithCallback(Thread):
    def __init__(self, target, args, callback=None):
        Thread.__init__(self)
        self.target = target
        self.args = args
        self.callback = callback

    def run(self):
        result = None
        if isinstance(self.args, Iterable):
            result = self.target(*self.args)
        else:
            result = self.target(self.args)

        if self.callback is not None:
            if isinstance(result, Iterable):
                self.callback(*result)
            else:
                self.callback(result)


__all__ = show_map_menu
