"""Module for registering commands"""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Custom Imports
from .clientcommands import CommandHandler, Argument
from ..timer.timer import Timer
from ..hud.radio import show_map_menu
from ..chat.messages import message_hidechat_off, message_hidechat_on


# =============================================================================
# >> COMMAND CALLBACK HANDLERS
# =============================================================================
def _restart_handler(player, command):
    """Called when player uses /r command."""
    player.start()


def _timer_handler(player, command):
    """Called when player uses /timer command."""
    Timer.instance().toggle_timer(player)


def _top_handler(player, command):
    """Called when player uses /top command."""
    if command.args[0].value not in [None, "None"]:
        return show_map_menu(command.args[0].value, player.index)

    if Timer.instance().current_map is not None:
        show_map_menu(Timer.instance().current_map.name, player.index)


def _hidechat_handler(player, command):
    """Called when player uses /hidechat command."""
    player.hidechat = not player.hidechat
    if player.hidechat:
        message_hidechat_on.send(player.index)
    else:
        message_hidechat_off.send(player.index)


# =============================================================================
# >> REGISTER COMMANDS
# =============================================================================
def register_commands():
    """Register commands"""

    CommandHandler.instance().add_command(
        name="restart",
        callback=_restart_handler,
        alias=["r"],
        description="Teleport to start of segment",
        usage="/r",
    )

    CommandHandler.instance().add_command(
        name="timer",
        callback=_timer_handler,
        description="Toggle timer",
        usage="/timer",
    )

    CommandHandler.instance().add_command(
        name="top",
        callback=_top_handler,
        args=[Argument(str, False, None)],
        description="Show top times",
        usage="/top <map>",
    )

    CommandHandler.instance().add_command(
        name="hidechat",
        callback=_hidechat_handler,
        description="Toggles chat visibility",
        usage="/hidechat",
    )
