"""Module for defining client commands."""


# =============================================================================
# >> COMMAND HANDLER CLASS
# =============================================================================
class CommandHandler:
    """Class for validating and handling client commands."""

    __instance = None

    def instance():
        """Singleton instance"""
        if CommandHandler.__instance is None:
            CommandHandler()
        return CommandHandler.__instance

    def __init__(self):
        if CommandHandler.__instance is not None:
            raise Exception("This class is a singleton, use .instance() access method.")

        self.command_list = {}
        self.no_prefix_commands = {}
        self.prefix = ["/", "!"]

        CommandHandler.__instance = self

    def add_command(
        self,
        name,
        callback,
        alias=[],
        arg_count=0,
        flags={},
        allowed_states={},
        description="",
        usage="",
        prefix_required=True,
        log=False,
        visibility={},
    ):
        """Register a new command."""
        command = Command(
            name,
            callback,
            alias,
            arg_count,
            flags,
            allowed_states,
            description,
            usage,
            prefix_required,
            log,
            visibility,
        )
        self.commandList.append(command)

    def execute_command(self, command, player, *args):
        """Execute command if player has permissions."""
        if len(args) < command.arg_count:
            return "Usage: " + command.usage

        if not player:
            return

        if player.flags not in command.flags:
            return

        # Not quite sure about this one yet
        # if player.State

        command.callback()

    def check_command(self, message, player):
        # Message should be "<prefix><command> *args"
        message = message.split()
        command = message[0]
        args = message.pop(0)

        if player.command_restricted:
            return

        if command[0] in self.command_list:
            command = self.command_list.get()
            self.execute_command(command, player, args)


# =============================================================================
# >> COMMAND CLASS
# =============================================================================
class Command:
    """Class for defining new commands."""

    def __init__(
        self,
        name,
        callback,
        alias,
        flags,
        allowed_states,
        description,
        usage,
        prefix_required,
        log,
        visibility,
    ):
        self.name = name
        self.callback = callback
        self.alias = alias

        # To restrict commands based on level of access
        self.admin_flags = flags

        # To restrict commands based on player state (timer on/off, certain modes, spectate etc.)
        self.allowed_states = allowed_states

        # Response to incorrect command args
        self.usage = usage

        # Elaborate explanation of a command (potentially !help <command>)
        self.description = description

        # If command can be used without any prefix
        self.prefix_required = prefix_required

        # If command should be logged
        self.log = log

        # Who the response should be visible to (person who used it, admin, everyone)
        self.visibility = visibility
