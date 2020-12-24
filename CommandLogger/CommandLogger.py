#FusionAPI_python addin
#Author-kantoku
#Description-command logger ver0.0.3

import adsk.core, adsk.fusion, adsk.cam, traceback
import adsk.drawing

_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_cmdDefs = adsk.core.CommandDefinitions.cast(None)
_handlers =[]

# -- command --
_cmdInfo = {
    'id' : 'commandlogger',
    'name' : 'CommandLogger',
    'tooltip' : '',
    'resourceFolder' : './resources/CommandLogger',
    'tabId' : 'SolidTab',
    'panelId' : 'SolidScriptsAddinsPanel'
}

# -- dialog --
# commandLog group
_cmdLogInfo = {
    'id' : 'logging',
    'name' : 'Show Command Logging',
    'checkBoxChecked' : False,
    'obj' : adsk.core.GroupCommandInput.cast(None),
    'handler' : None
}

# commandLog Panel info
_cmdPanelInfo = {
    'id' : 'panelInfo',
    'name' : 'Show Panel Information',
    'isCheckBox' : True,
    'resourceFolder' : '',
    'value' : False,
    'obj' : adsk.core.BoolValueCommandInput.cast(None)
}


class ExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):

        # command log
        global _ui, _cmdLogInfo, _handlers
        if _cmdLogInfo['checkBoxChecked'] != _cmdLogInfo['obj'].isEnabledCheckBoxChecked:
            if _cmdLogInfo['obj'].isEnabledCheckBoxChecked:
                # command log on
                dumpMsg('-- start command log --')
                _ui.commandStarting.add(_cmdLogInfo['handler'])
                _handlers.append(_cmdLogInfo['handler'])
            else:
                # command log off
                dumpMsg('-- stop command log --')
                _ui.commandStarting.remove(_cmdLogInfo['handler'])
                _handlers.remove(_cmdLogInfo['handler'])
            _cmdLogInfo['checkBoxChecked'] = _cmdLogInfo['obj'].isEnabledCheckBoxChecked

        #  panel info
        global _cmdPanelInfo
        if _cmdPanelInfo['value'] != _cmdPanelInfo['obj'].value:
            _cmdPanelInfo['value'] = _cmdPanelInfo['obj'].value

class CommandStartingHandler(adsk.core.ApplicationCommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global _cmdLogInfo
            # if not _cmdLogInfo['checkBoxChecked']:
            #     return

            # command
            cmdId :str = args.commandId
            cmdDef :adsk.core.CommandDefinition = _cmdDefs.itemById(cmdId)
            cmdName :str = cmdDef.name if cmdDef else '(unknown)'

            dumpMsg('{} : {}'.format(cmdName, cmdId))

            # panel
            global _cmdPanelInfo
            if _cmdPanelInfo['value']:
                # workspace
                try:
                    ws :adsk.core.Workspace = _ui.activeWorkspace
                except:
                    return

                # Toolbar panel
                global _app
                panelId :str = ''
                try:
                    actEditObj = adsk.fusion.Sketch.cast(_app.activeEditObject)
                    if actEditObj:
                        # sketch
                        tpIds = [
                            'SketchCreatePanel',
                            'SketchModifyPanel',
                            'SketchConstraintsPanel',
                            # 'PCB3DSketchCreatePanel'
                        ]

                        panels = _ui.allToolbarPanels
                        tpLst = [panels.itemById(tpId) for tpId in tpIds]
                    else:
                        # other Design
                        tpLst = _ui.toolbarPanelsByProductType(ws.productType)
                except:
                    # other non Design
                    tpLst = _ui.toolbarPanelsByProductType(ws.productType)

                for tp in tpLst:
                    tc :adsk.core.ToolbarControl = tp.controls.itemById(cmdId)
                    if tc:
                        panelId = tp.id
                        break

                    # DropDownControl
                    for dd in tp.controls:
                        if adsk.core.DropDownControl.cast(dd):
                            tc = dd.controls.itemById(cmdId)
                            if tc:
                                panelId = tp.id
                                break

                # Toolbar tab
                tabId = ''
                if len(panelId) < 1:
                    panelId = tabId ='(unknown)'
                else:
                    ttLst = _ui.toolbarTabsByProductType(ws.productType)
                    for tt in ttLst:
                        try:
                            tp  = tt.toolbarPanels.itemById(panelId)
                        except:
                            continue
                        
                        if tp:
                            tabId = tt.id
                            break
                
                    if len(tabId) < 1:
                        tabId ='(unknown)'


                dumpMsg('  Workspace_ID:{}\n  Tab_ID:{}\n  Panel_ID:{}'.format(
                    ws.id, tabId, panelId))

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global _ui
        try:
            cmd = adsk.core.Command.cast(args.command)
            
            # event
            global _handlers
            onExecute = ExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)

            # inputs
            inputs = cmd.commandInputs

            # -- command Log --
            # group
            # global _cmdLogInfo
            # _cmdLogInfo['handler'] = CommandStartingHandler()
            # _ui.commandStarting.add(_cmdLogInfo['handler'])
            # _handlers.append(_cmdLogInfo['handler'])

            _cmdLogInfo['obj'] = inputs.addGroupCommandInput(
                _cmdLogInfo['id'],
                _cmdLogInfo['name'])
            _cmdLogInfo['obj'].isEnabledCheckBoxDisplayed = True
            _cmdLogInfo['obj'].isEnabledCheckBoxChecked = _cmdLogInfo['checkBoxChecked']

            # panel info
            global _cmdPanelInfo
            _cmdPanelInfo['obj'] = _cmdLogInfo['obj'].children.addBoolValueInput(
                _cmdPanelInfo['id'],
                _cmdPanelInfo['name'],
                _cmdPanelInfo['isCheckBox'],
                _cmdPanelInfo['resourceFolder'],
                _cmdPanelInfo['value']
                )

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def dumpMsg(msg :str):
    _ui.palettes.itemById('TextCommands').writeText(str(msg))

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # cmdDef 
        global _cmdInfo, _cmdDefs   
        _cmdDefs = _ui.commandDefinitions

        cmdDef :adsk.core.CommandDefinition = _cmdDefs.itemById(_cmdInfo['id'])
        if cmdDef:
            cmdDef.deleteMe()

        cmdDef = _cmdDefs.addButtonDefinition(
            _cmdInfo['id'], 
            _cmdInfo['name'],
            _cmdInfo['tooltip'],
            _cmdInfo['resourceFolder'])

        # event
        global _handlers
        onCommandCreated = CommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        global _cmdLogInfo
        _cmdLogInfo['handler'] = CommandStartingHandler()
        # _ui.commandStarting.add(_cmdLogInfo['handler'])
        # _handlers.append(_cmdLogInfo['handler'])

        # TextCommands palette
        _ui.palettes.itemById('TextCommands').isVisible = True

        # panel
        global _panelId
        targetpanel :adsk.core.ToolbarPanel = _ui.allToolbarPanels.itemById(_cmdInfo['panelId'])

        if not targetpanel:
            _ui.messageBox('Unsupported ID(panel)')
            return

        controls :adsk.core.ToolbarControls = targetpanel.controls

        cmdControl :adsk.core.ToolbarControl = controls.itemById(cmdDef.id)
        if cmdControl:
            cmdControl.deleteMe()

        cmdControl = controls.addCommand(cmdDef)

        cmdControl.isVisible = True
        cmdControl.isPromoted = False
        cmdControl.isPromotedByDefault = False




        dumpMsg('-- start add-ins command logger --')

    except:
        _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        dumpMsg('-- stop add-ins command logger --')

        global _handlers
        for h in _handlers:
            try:
                _ui.commandStarting.remove(h)
            except:
                pass

        # global _ui, _cmdInfo
        panel :adsk.core.ToolbarPanel = _ui.allToolbarPanels.itemById(_cmdInfo['panelId'])
        panel.controls.itemById(_cmdInfo['id']).deleteMe()

        cmdDef = _ui.commandDefinitions.itemById(_cmdInfo['id'])
        if cmdDef:
            cmdDef.deleteMe()

    except:
        _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))