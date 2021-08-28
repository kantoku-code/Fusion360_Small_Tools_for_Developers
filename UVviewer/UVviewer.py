# FusionAPI_python Script
# Author-kantoku
# Description-マウスカーソル部分のUVを可視化

import adsk.core
import adsk.fusion
import traceback

_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_handlers = []
_fact = None

# command
_cmdInfo = ['UVviewer', 'UVviewer', 'UVviewer']

# dialog
_selInfo = ['dlgSel', '', '']
_selIpt = adsk.core.SelectionCommandInput.cast(None)

_prmInfo = ['dlgPrm', 'マウス位置の U:V :', '-']
_prmIpt = adsk.core.TextBoxCommandInput.cast(None)

_verInfo = ['verPrm', '頂点の U:V :', '-']
_verIpt = adsk.core.TextBoxCommandInput.cast(None)


class CommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            adsk.terminate()
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class PreSelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            args = adsk.core.SelectionEventArgs.cast(args)
            args.isSelectable = False

            sel = args.selection
            ent = sel.entity
            entType: str = ent.objectType.split('::')[-1]

            global _fact
            if entType == 'BRepFace':
                _fact.setFace(ent)
            else:
                _fact.setFace(None)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class MouseMoveHandler(adsk.core.MouseEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args: adsk.core.MouseEventArgs):
        try:
            global _fact
            _fact.setMouse(
                args.viewport,
                args.viewportPosition)

            prms = _fact.update()

            global _selIpt, _prmIpt, _verIpt
            if prms:
                musPrm = prms[0]
                _prmIpt.text = '{:.3f}:{:.3f}'.format(musPrm[0], musPrm[1])
                verPrms = ['{:.3f}:{:.3f}'.format(
                    p[0], p[1]) for p in prms[1:]]
                _verIpt.text = '\n'.join(verPrms)
            else:
                _prmIpt.text = '-'
                _verIpt.text = '-'

            args.viewport.refresh()

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            # -- Command --
            global _ui, _handlers
            cmd = adsk.core.Command.cast(args.command)
            cmd.isPositionDependent = True
            cmd.isOKButtonVisible = False

            # -- Event --
            onDestroy = CommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # MouseMove
            onMouseMove = MouseMoveHandler()
            cmd.mouseMove.add(onMouseMove)
            _handlers.append(onMouseMove)

            # preSelect
            onPre = PreSelectHandler()
            cmd.preSelect.add(onPre)
            _handlers.append(onPre)

            # -- dialog --
            global _selInfo, _selIpt
            inputs = cmd.commandInputs
            _selIpt = inputs.addSelectionInput(
                _selInfo[0], _selInfo[1], _selInfo[2])
            _selIpt.isVisible = False

            global _prmInfo, _prmIpt
            _prmIpt = inputs.addTextBoxCommandInput(
                _prmInfo[0], _prmInfo[1], _prmInfo[2], 1, True)

            global _verInfo, _verIpt
            _verIpt = inputs.addTextBoxCommandInput(
                _verInfo[0], _verInfo[1], _verInfo[2], 10, True)

            # -- other --
            global _fact
            _fact = DrawUVFactry()

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class DrawUVFactry():
    _vp = adsk.core.Viewport.cast(None)
    _face = adsk.fusion.BRepFace.cast(None)
    _clone = adsk.fusion.BRepFace.cast(None)
    _musPos = adsk.core.Point2D.cast(None)
    _cgGroup = adsk.fusion.CustomGraphicsGroup.cast(None)

    red = adsk.core.Color.create(255, 0, 0, 255)
    _solidRed = adsk.fusion.CustomGraphicsSolidColorEffect.create(red)
    blue = adsk.core.Color.create(0, 0, 255, 255)
    _solidBlue = adsk.fusion.CustomGraphicsSolidColorEffect.create(blue)

    def __init__(self):
        self.refreshCG()
        self.vp = adsk.core.Viewport.cast(None)
        self.face = adsk.fusion.BRepFace.cast(None)
        self.clone = adsk.fusion.BRepFace.cast(None)
        self.musPos = adsk.core.Point2D.cast(None)
        self.cgGroup = adsk.fusion.CustomGraphicsGroup.cast(None)

        self.solidRed = adsk.fusion.CustomGraphicsSolidColorEffect.create(
            adsk.core.Color.create(255, 0, 0, 255))
        self.solidBlue = adsk.fusion.CustomGraphicsSolidColorEffect.create(
            adsk.core.Color.create(0, 0, 255, 255))

    def __del__(self):
        self.removeCG()

    def removeCG(self):
        des: adsk.fusion.Design = _app.activeProduct
        cgs = [cmp.customGraphicsGroups for cmp in des.allComponents]
        cgs = [cg for cg in cgs if cg.count > 0]

        if len(cgs) < 1:
            return

        for cg in cgs:
            gps = [c for c in cg]
            gps.reverse()
            for gp in gps:
                gp.deleteMe()

    def refreshCG(self):
        self.removeCG()
        des: adsk.fusion.Design = _app.activeProduct
        root: adsk.fusion.Component = des.rootComponent
        self.cgGroup = root.customGraphicsGroups.add()

    def setMouse(self, vp: adsk.core.Viewport, musPos: adsk.core.Point2D):
        self.vp = vp
        self.musPos = musPos

    def setFace(self, face: adsk.fusion.BRepFace):
        if self.face == face:
            return

        self.face = face

        if face:
            tmpBrep = adsk.fusion.TemporaryBRepManager.get()
            cloneBody = tmpBrep.copy(face)
            self.clone = cloneBody.faces[0]
        else:
            self.clone = None

    def update(self):
        self.refreshCG()

        if not self.face:
            return

        # mouse
        pos3d = self.vp.viewToModelSpace(self.musPos)
        cam = self.vp.camera
        vec = cam.eye.vectorTo(cam.target)

        musPnt = adsk.core.Point3D.create(
            pos3d.x + vec.x,
            pos3d.y + vec.y,
            pos3d.z + vec.z)

        musInf = adsk.core.Line3D.create(pos3d, musPnt).asInfiniteLine()

        geo: adsk.core.Surface = self.clone.geometry

        ints = musInf.intersectWithSurface(geo)
        if ints.count < 1:
            return

        pnt: adsk.core.Point3D = min(
            ints, key=(lambda p: cam.eye.distanceTo(p)))

        eva: adsk.core.SurfaceEvaluator = self.clone.evaluator
        res, prm = eva.getParameterAtPoint(pnt)

        crvsU = eva.getIsoCurve(prm.x, False)
        crvsV = eva.getIsoCurve(prm.y, True)

        for crv in crvsU:
            crvCg = self.cgGroup.addCurve(crv)
            crvCg.color = self.solidRed
            crvCg.weight = 2

        for crv in crvsV:
            crvCg = self.cgGroup.addCurve(crv)
            crvCg.color = self.solidBlue
            crvCg.weight = 2

        # vertex
        vertices = [p.geometry for p in self.clone.vertices]
        _, pnt2ds = eva.getParametersAtPoints(vertices)

        verPrms = list([(p.x, p.y) for p in pnt2ds])

        res = [(prm.x, prm.y)]
        res.extend(verPrms)
        return res


def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        des: adsk.fusion.Design = _app.activeProduct
        root: adsk.fusion.Component = des.rootComponent

        cmdDefs: adsk.core.CommandDefinitions = _ui.commandDefinitions

        global _cmdInfo
        cmdDef: adsk.core.CommandDefinition = cmdDefs.itemById(_cmdInfo[0])
        if cmdDef:
            cmdDef.deleteMe()

        cmdDef = cmdDefs.addButtonDefinition(
            _cmdInfo[0], _cmdInfo[1], _cmdInfo[2])

        global _handlers
        onCommandCreated = CommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        cmdDef.execute()

        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
