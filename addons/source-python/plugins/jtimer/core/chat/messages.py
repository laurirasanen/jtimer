from ..translations import chat_strings
from messages.base import SayText2
from messages.colors.saytext2 import (
    BLUE,
    BRIGHT_GREEN,
    DARK_BLUE,
    DULL_RED,
    GRAY,
    GREEN,
    LIGHT_BLUE,
    ORANGE,
    PALE_GREEN,
    PALE_RED,
    PINK,
    RED,
    WHITE,
    YELLOW,
)

message_prefix = SayText2(chat_strings["prefix default"])
message_prefix_multiline = SayText2(chat_strings["prefix multiline"])

message_timer_enable = SayText2(chat_strings["timer enable"])
message_timer_disable = SayText2(chat_strings["timer disable"])

message_checkpoint_enter = SayText2(chat_strings["checkpoint enter"])
message_checkpoint_enter_no_split = SayText2(chat_strings["checkpoint enter no split"])
message_checkpoint_wrong_order = SayText2(chat_strings["checkpoint enter wrong order"])
message_checkpoint_missed = SayText2(chat_strings["checkpoint missed"])

message_map_finish = SayText2(chat_strings["map finish"])
message_map_finish_no_split = SayText2(chat_strings["map finish no split"])
message_map_improvement = SayText2(chat_strings["map improvement"])
message_map_record = SayText2(chat_strings["map record"])
message_map_record_set = SayText2(chat_strings["map record set"])

message_points_gain = SayText2(chat_strings["points gain"])

__all__ = (
    message_timer_enable,
    message_timer_disable,
    message_checkpoint_enter,
    message_checkpoint_enter_no_split,
    message_map_finish,
    message_map_finish_no_split,
    message_map_improvement,
    message_map_record,
    message_map_record_set,
    message_points_gain,
)

color_formats = {
    "blue": BLUE,
    "brightgreen": BRIGHT_GREEN,
    "darkblue": DARK_BLUE,
    "dullred": DULL_RED,
    "gray": GRAY,
    "grey": GRAY,
    "green": GREEN,
    "lightblue": LIGHT_BLUE,
    "orange": ORANGE,
    "lightgreen": PALE_GREEN,
    "lightred": PALE_RED,
    "pink": PINK,
    "red": RED,
    "white": WHITE,
    "yellow": YELLOW,
}


class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


# add prefix to all messages
for saytext in __all__:
    for key in saytext.message.keys():
        if key in message_prefix.message:
            saytext.message[key] = message_prefix.message[key] + saytext.message[key]

        # format colors
        saytext.message[key] = saytext.message[key].format_map(SafeDict(color_formats))
