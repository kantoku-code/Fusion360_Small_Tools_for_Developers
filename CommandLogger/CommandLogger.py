#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

_ui = adsk.core.UserInterface.cast(None)
_cmdDefs = adsk.core.CommandDefinitions.cast(None)
_handlers =[]

class CommandTerminatedHandler(adsk.core.ApplicationCommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmdId :str = args.commandId
            cmdDef :adsk.core.CommandDefinition = _cmdDefs.itemById(cmdId)
            cmdName :str = cmdDef.name if cmdDef else '(unknown)'

            dumpMsg('{} : {}'.format(cmdName, cmdId))

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def dumpMsg(msg :str):
    _ui.palettes.itemById('TextCommands').writeText(str(msg))

def run(context):
    try:
        app :adsk.core.Application = adsk.core.Application.get()
        
        global _ui, _cmdDefs, _handlers
        _ui = app.userInterface
        _cmdDefs = _ui.commandDefinitions

        onCommandTerminated = CommandTerminatedHandler()
        _ui.commandTerminated.add(onCommandTerminated)
        _handlers.append(onCommandTerminated)

        app.executeTextCommand(u'Commands.Start ShowTextCommandsCommand')

        dumpMsg('-- start command logger --')

    except:
        _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        dumpMsg('-- stop command logger --')

    except:
        _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
