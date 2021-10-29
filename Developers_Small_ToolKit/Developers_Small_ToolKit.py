# Fusion360API Python Addin
import adsk.core
import adsk.fusion
import traceback
import json
import math

handlers = []
_app: adsk.core.Application = None
_ui: adsk.core.UserInterface = None
_handlers =[]

_cmdInfo = {
    'id': 'Developers_Small_ToolKit_Cmd',
    'name': 'Developers Small ToolKit',
    'tooltip': 'A small ToolKit for developers of the Fusion360 API.',
    'resources': ''
}

_paletteInfo = {
    'id': 'Developers_Small_ToolKit',
    'name': 'Developers Small ToolKit',
    'htmlFileURL': 'index.html',
    'isVisible': True,
    'showCloseButton': True,
    'isResizable': True,
    'width': 300,
    'height': 350,
    'useNewWebBrowser': False, #True,#
    'dockingState': None
    # 'dockingState': adsk.core.PaletteDockingStates.PaletteDockStateRight
}

# commandLog group
_cmdLogInfo = {
    'id' : 'logging',
    'name' : 'Show Command Logging',
    'obj' : adsk.core.GroupCommandInput.cast(None),
    'handler' : None
}

# commandLog Panel info
_cmdPanelInfo = {
    'id' : 'panelInfo',
    'name' : 'Show Panel Information',
    'value' : False,
    'obj' : adsk.core.BoolValueCommandInput.cast(None)
}

class CommandStartingHandler(adsk.core.ApplicationCommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # command
            global _app, _ui
            cmdDefs: adsk.core.CommandDefinitions = _ui.commandDefinitions

            cmdId :str = args.commandId
            cmdDef :adsk.core.CommandDefinition =  cmdDefs.itemById(cmdId)
            cmdName :str = cmdDef.name if cmdDef else '(unknown)'

            _app.log('{} : {}'.format(cmdName, cmdId))

            # panel
            global _cmdPanelInfo
            if _cmdPanelInfo['value']:
                # workspace
                try:
                    ws :adsk.core.Workspace = _ui.activeWorkspace
                except:
                    return

                # Toolbar panel
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

                _app.log(' Workspace_ID:{}\n  Tab_ID:{}\n  Panel_ID:{}'.format(
                    ws.id, tabId, panelId))

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class MyHTMLEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            htmlArgs = adsk.core.HTMLEventArgs.cast(args)

            app: adsk.core.Application = adsk.core.Application.get()

            global _ui, _cmdLogInfo, _handlers, _cmdPanelInfo
            if htmlArgs.action == 'cmdLog':
                # command log
                data = json.loads(htmlArgs.data)
                if data['value']:
                    app.log('-- start command log --')
                    _ui.commandStarting.add(_cmdLogInfo['handler'])
                    _handlers.append(_cmdLogInfo['handler'])
                else:
                    app.log('-- stop command log --')
                    _ui.commandStarting.remove(_cmdLogInfo['handler'])
                    _handlers.remove(_cmdLogInfo['handler'])

            elif htmlArgs.action == 'panelInfo':
                # panel info
                data = json.loads(htmlArgs.data)
                _cmdPanelInfo['value'] = data['value']

            elif htmlArgs.action == 'closeDocs':
                data = json.loads(htmlArgs.data)
                if data['value']:
                    closeAllDocs()

            elif htmlArgs.action == 'windowClear':
                data = json.loads(htmlArgs.data)
                if data['value']:
                    windowClear()

            elif htmlArgs.action == 'dumpCommandDialog':
                data = json.loads(htmlArgs.data)
                if data['value']:
                    dumpCommandDialog()

            elif htmlArgs.action == 'dumpEntityPaths':
                data = json.loads(htmlArgs.data)
                if data['value']:
                    dumpEntityPaths()

            elif htmlArgs.action == 'resourceFolder':
                data = json.loads(htmlArgs.data)
                if data['value']:
                    dumpResourceFolder()

            elif htmlArgs.action == 'removeCG':
                data = json.loads(htmlArgs.data)
                if data['value']:
                    removeCG()
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def removeCG():
    global _app, _ui
    des :adsk.fusion.Design = _app.activeProduct
    cgs = [cmp.customGraphicsGroups for cmp in des.allComponents]
    cgs = [cg for cg in cgs if cg.count > 0]
    
    if len(cgs) < 1: return

    for cg in cgs:
        gps = [c for c in cg]
        gps.reverse()
        for gp in gps:
            gp.deleteMe()

def dumpResourceFolder():
    global _app, _ui
    cmdDef = _ui.commandDefinitions.itemById(_ui.activeCommand)
    if cmdDef:
        try:
            _app.log(cmdDef.resourceFolder)
        except:
            pass

def dumpEntityPaths():
    global _app
    try:
        res = _app.executeTextCommand(u'Selections.List')
        _app.log(res)
    except:
        pass

def dumpCommandDialog():
    global _app
    res = _app.executeTextCommand(u'Toolkit.cmdDialog')
    _app.log(res)

def windowClear():
    global _app
    res = _app.executeTextCommand(u'window.Clear')
    _app.log(res)

def closeAllDocs():
    global _app, _ui
    docs = [doc for doc in _app.documents]
    msg =[
        f'The number of open documents is {len(docs)}.',
        'Would you like me to close them all without saving them?'
    ]

    if not _ui.messageBox(
        '\n'.join(msg),
        '',
        adsk.core.MessageBoxButtonTypes.OKCancelButtonType,
        adsk.core.MessageBoxIconTypes.QuestionIconType
    ) == adsk.core.DialogResults.DialogOK:
        return

    [doc.close(False) for doc in docs[::-1]]



class ShowPaletteCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global _ui, _paletteInfo

            palette = _ui.palettes.itemById(_paletteInfo['id'])
            if palette:
                palette.deleteMe()

            palette: adsk.core.Palette = _ui.palettes.add(
                _paletteInfo['id'],
                _paletteInfo['name'],
                _paletteInfo['htmlFileURL'],
                _paletteInfo['isVisible'],
                _paletteInfo['showCloseButton'],
                _paletteInfo['isResizable'],
                _paletteInfo['width'],
                _paletteInfo['height'],
                _paletteInfo['useNewWebBrowser'],
            )

            if _paletteInfo['dockingState']:
                palette.dockingState = _paletteInfo['dockingState']
            else:
                palette.setPosition(800, 400)

            onHTMLEvent = MyHTMLEventHandler()
            palette.incomingFromHTML.add(onHTMLEvent)
            handlers.append(onHTMLEvent)

            onClosed = MyCloseEventHandler()
            palette.closed.add(onClosed)
            handlers.append(onClosed)

        except:
            _ui.messageBox('Command executed failed: {}'.format(traceback.format_exc()))


class MyCloseEventHandler(adsk.core.UserInterfaceGeneralEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global _app
            _app.log('-- stop command log --')
            try:
                _ui.commandStarting.remove(_cmdLogInfo['handler'])
                _handlers.remove(_cmdLogInfo['handler'])
            except:
                pass
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class ShowPaletteCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            command = args.command
            onExecute = ShowPaletteCommandExecuteHandler()
            command.execute.add(onExecute)
            handlers.append(onExecute)
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def run(context):
    try:
        global _ui, _app
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface
        
        global _cmdInfo
        showPaletteCmdDef = _ui.commandDefinitions.itemById(_cmdInfo['id'])
        if showPaletteCmdDef:
            showPaletteCmdDef.deleteMe()

        showPaletteCmdDef = _ui.commandDefinitions.addButtonDefinition(
            _cmdInfo['id'],
            _cmdInfo['name'],
            _cmdInfo['tooltip'],
            _cmdInfo['resources']
        )

        onCommandCreated = ShowPaletteCommandCreatedHandler()
        showPaletteCmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)
        
        panel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cntrl = panel.controls.itemById('showPalette')
        if not cntrl:
            panel.controls.addCommand(showPaletteCmdDef)

        global _cmdLogInfo
        _cmdLogInfo['handler'] = CommandStartingHandler()

        _app.log(f'Start addin: {_cmdInfo["name"]}')

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        global _ui, _paletteInfo, _handlers
        palette = _ui.palettes.itemById(_paletteInfo['id'])
        if palette:
            palette.deleteMe()

        global _cmdInfo
        panel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cmd = panel.controls.itemById(_cmdInfo['id'])
        if cmd:
            cmd.deleteMe()
        cmdDef = _ui.commandDefinitions.itemById(_cmdInfo['id'])
        if cmdDef:
            cmdDef.deleteMe()

        try:
            _ui.commandStarting.remove(_cmdLogInfo['handler'])
            _handlers.remove(_cmdLogInfo['handler'])
        except:
            pass

        _app.log(f'Stop addin: {_cmdInfo["name"]}')
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))