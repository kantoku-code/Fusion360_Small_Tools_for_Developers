#FusionAPI_python_script
#Author-kantoku
#Description-get object information

import adsk.core, adsk.fusion, traceback
# import json

# command
_cmdInfo = ['getObjInfo','Object Info','Object Info']

# dialog
_selInfo = ['selEnt','entity','Select Entity']
_selIpt = adsk.core.SelectionCommandInput.cast(None)

_objInfo = ['objInfo', '', '', 2, True]
_objIpt = adsk.core.TextBoxCommandInput.cast(None)

_propGpInfo = ['propGpInfo', 'Property&Methods', False]
_propInfo = ['propInfo', '', '', 20, True]
_propIpt = adsk.core.TextBoxCommandInput.cast(None)

# _idGpInfo = ['idGpInfo', 'EntityID', False]
# _idInfo = ['idpInfo', '', '', 20, True]
# _idIpt = adsk.core.TextBoxCommandInput.cast(None)

# other
_app = None
_ui  = None
_handlers = []

class MouseDownHandler(adsk.core.MouseEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):

        sel = _ui.activeSelections
        sel.clear()

class CommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmd = args.firingEvent.sender
            ipts = cmd.commandInputs

            global _selInfo
            if args.input.id != _selInfo[0]: return

            global _selIpt, _objIpt, _propIpt, _idIpt 
            if _selIpt.selectionCount < 1:
                _objIpt.text = ''
                _propIpt.text = ''
                # _idIpt.text = ''
            else:
                ent = _selIpt.selection(0).entity
                _objIpt.text = '\n'.join(self.getInfos(ent))
                _propIpt.text = '\n'.join(self.getProps(ent))
                # _idIpt.text = '\n'.join(self.getIds(ent))

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

     
    def getInfos(self, ent):
        info = []

        try:
            info.append('name : {}'.format(ent.name))
        except:
            pass

        try:
            info.append('type : {}'.format(ent.objectType.split('::')[-1]))
        except:
            pass

        return info

    def getProps(self, ent):
        info = []

        try:
            props = ['{} : {}'.format(p, type(getattr(ent ,p))) for p in dir(ent) if p[0] != '_']
            info.extend(props)
        except:
            pass

        return info

    # def getIds(self, ent):
    #     info = []

    #     try:
    #         if hasattr(ent, 'faces'):
    #             info.append('--faces--')
    #             info.append(self.getEntityId(ent.faces))
    #     except:
    #         pass

    #     global _selIpt
    #     _selIpt.addSelection(ent)

    #     return info

    def getEntityId(self, lst):

        cmd = u'Selections.List'

        actSels = _ui.activeSelections
        actSels.clear()
        [actSels.add(i) for i in lst]
        ids = _app.executeTextCommand(cmd)
        actSels.clear()

        return ids


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmd = adsk.core.Command.cast(args.command)
            cmd.isOKButtonVisible = False

            # event
            onChange = CommandInputChangedHandler()
            cmd.inputChanged.add(onChange)
            _handlers.append(onChange)

            onMouseDown = MouseDownHandler()
            cmd.mouseUp.add(onMouseDown)
            _handlers.append(onMouseDown)

            onDestroy = CommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # dialog
            ipts = cmd.commandInputs

            global _selInfo, _selIpt
            _selIpt = ipts.addSelectionInput(_selInfo[0], _selInfo[1], _selInfo[2])

            global _objInfo, _objIpt     
            _objIpt = ipts.addTextBoxCommandInput(
                _objInfo[0], _objInfo[1], _objInfo[2], _objInfo[3], _objInfo[4])

            global _propGpInfo, _propInfo, _propIpt
            _propGp = ipts.addGroupCommandInput(_propGpInfo[0], _propGpInfo[1])
            _propGp.isExpanded = _propGpInfo[2]
            _propIpt = _propGp.children.addTextBoxCommandInput(
                _propInfo[0], _propInfo[1], _propInfo[2], _propInfo[3], _propInfo[4])

            # global _idGpInfo, _idInfo, _idIpt 
            # _idGp = ipts.addGroupCommandInput(_idGpInfo[0], _idGpInfo[1])
            # _idGp.isExpanded = _idGpInfo[2]
            # _idIpt = _idGp.children.addTextBoxCommandInput(
            #     _idInfo[0], _idInfo[1], _idInfo[2], _idInfo[3], _idInfo[4])

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            adsk.terminate()
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        global _cmdInfo
        cmdDef = _ui.commandDefinitions.itemById(_cmdInfo[0])
        if cmdDef:
            cmdDef.deleteMe()
        
        cmdDef = _ui.commandDefinitions.addButtonDefinition(_cmdInfo[0], _cmdInfo[1], _cmdInfo[2])
        onCommandCreated = CommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        cmdDef.execute()

        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))