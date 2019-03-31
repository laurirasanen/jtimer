from ...players import player, state

class CommandController:
    def __init__(self):
        self.commandList = {}
        self.noPrefixCommands = {}
        self.prefix = ["/", "!"]

    def addCommand(self, name, callback, alias = [], argCount = 0, flags = {}, allowedStates = {}, description = "", usage = "", prefixRequired = True, log = False, visibility = {}):
        command = Command(name, callback, alias, argCount, flags, allowedStates, description, usage, prefixRequired, log, visibility)
        self.commandList.append(command)

    def executeCommand(self, command, player, *args):
        if len(args) < command.argCount:
            return "Usage: " + command.usage

        if not player:
            return
        
        if player.flags not in command.flags:
            return
        
        #Not quite sure about this one yet
        ##if player.State

        command.callback()

    def checkCommand(self, message, player):
            #Message should be "<prefix><command> *args"
            message = message.split()
            command = message[0]
            args = message.pop(0)
            
            if player.commandRestricted:
                return

            if command[0] in self.commandList:
                command = self.commandList.get()
                return self.executeCommand(command, player, args)


class Command:
    def __init__(self, name, callback, alias, flags, allowedStates, description, usage, prefixRequired, log, visibility):
        self.name = name
        self.callback = callback
        self.alias = alias

        #To restrict commands based on level of access
        self.adminFlags = flags

        #To restrict commands based on player state (timer on/off, certain modes, spectate etc.)
        self.allowedStates = allowedStates
        
        #Response to incorrect command args
        self.usage = usage

        #Elaborate explanation of a command (potentially !help <command>)
        self.description = description

        #If command can be used without any prefix
        self.prefixRequired = prefixRequired

        #If command should be logged
        self.log = log

        #Who the response should be visible to (person who used it, admin, everyone)
        self.visibility = visibility
