import maya.cmds as cmds
import maya.mel as mel

import core


PRESS = True
RELEASE = False

ALT = True
NOALT = False

CTRL = True
NOCTRL = False

wspos = lambda tf: cmds.xform(tf, query=True, worldSpace=True, translation=True)
minTime = lambda: cmds.playbackOptions(query=True, minTime=True)
maxTime = lambda: cmds.playbackOptions(query=True, maxTime=True)


class stateSTART (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {
            ('d', NOALT, NOCTRL, PRESS):   ("RUN", cmds.delete),
            ('f', NOALT, NOCTRL, PRESS):   ("RUN", cmds.viewFit),
            ('F', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.viewFit(allObjects=True)),
            ('m', NOALT, NOCTRL, PRESS):   ("PUSH", (stateMap, "move")),
            ('u', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.evalDeferred(cmds.undo)),
            ('r', NOALT, CTRL,   PRESS):   ("RUN", lambda: cmds.evalDeferred(cmds.redo)),
            ('s', NOALT, NOCTRL, PRESS):   ("PUSH", (stateMap, "select")),
            ('h', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.play(state=True, forward=False)),
            ('h', NOALT, NOCTRL, RELEASE): ("RUN", lambda: cmds.play(state=False, forward=False)),
            ('l', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.play(state=True)),
            ('l', NOALT, NOCTRL, RELEASE): ("RUN", lambda: cmds.play(state=False)),
            ('H', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.currentTime(minTime())),
            ('L', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.currentTime(maxTime())),
            ('M', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.currentTime(round((minTime() + maxTime()) / 2))),
            ('M', ALT, CTRL, PRESS):       ("RUN", self.switchToMayaHotkeys),
            ('t', NOALT, NOCTRL, PRESS):   ("PUSH", (stateMap, "toolSelect")),
        }

    def switchToMayaHotkeys (self):
        cmds.hotkeySet("Maya_Default", edit=True, current=True)


class stateMove (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {}

    def onEnter (self):
        self.mainInst.pushState((stateMap, "pickXYZ"))

    def onPopTo (self, value):
        x, y, z = value
        selected = cmds.ls(selection=True)
        map(lambda tf: cmds.move(x, y, z, tf), selected)
        self.mainInst.popState()


class statePickXYZ (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {
            ('O', NOALT, NOCTRL, PRESS): ("POP", self.popOrigin)
        }

    def popOrigin (self):
        return (0, 0, 0)


class stateSelect (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {
            ('m', NOALT, NOCTRL, PRESS): ("PUSH", (stateMap, "selectMesh")),
            ('n', NOALT, NOCTRL, PRESS): ("RUN", self.selectNone)
        }

    def onPopTo (self, value):
        self.mainInst.popState(value)

    def selectNone (self):
        cmds.select(None)
        self.mainInst.popState(None)


class stateSelectMesh (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {
            ("Return", NOALT, NOCTRL, PRESS): ("POP", self.popSelection)
        }

    def onEnter (self):
        meshes = cmds.ls(type="mesh")
        tfs = map(lambda x: cmds.listRelatives(x, parent=True)[0], meshes)
        self.anns = []
        sel = cmds.ls(selection=True, flatten=True)
        for alpha, name in zip("abcdefghijklmnopqrstuvwxyz0123456789", sorted(list(set(tfs)))):
            print alpha, name
            ann = cmds.annotate(name, tx=alpha, point=wspos(name))
            cmds.color(ann, rgbColor=(1, 1, 1))
            self.anns.append(ann)
            self.keymap[(alpha, False, False, True)] = ("RUN", self.toggleSelection(name))
        cmds.select(sel)

    def toggleSelection (self, name):
        def toggler ():
            cmds.select(name, toggle=True)
        return toggler

    def popSelection (self):
        for ann in self.anns:
            p = cmds.listRelatives(ann, parent=True)[0]
            cmds.delete(p)
        sel = cmds.ls(selection=True, flatten=True)
        return sel


class stateToolSelect (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {
            ('q', NOALT, NOCTRL, PRESS): ("RUN", self.selectSelectTool),
            ('m', NOALT, NOCTRL, PRESS): ("RUN", self.selectMoveTool),
            ('r', NOALT, NOCTRL, PRESS): ("RUN", self.selectRotateTool),
            ('s', NOALT, NOCTRL, PRESS): ("RUN", self.selectScaleTool),
            ('M', NOALT, NOCTRL, PRESS): ("RUN", self.selectManipTool),
            ('t', NOALT, NOCTRL, PRESS): ("POP", None)
        }

    def selectSelectTool (self):
        cmds.setToolTo(mel.eval("$temp = $gSelect"))
        self.mainInst.popState()

    def selectMoveTool (self):
        cmds.setToolTo(mel.eval("$temp = $gMove"))
        self.mainInst.popState()

    def selectRotateTool (self):
        cmds.setToolTo(mel.eval("$temp = $gRotate"))
        self.mainInst.popState()

    def selectScaleTool (self):
        cmds.setToolTo(mel.eval("$temp = $gScale"))
        self.mainInst.popState()

    def selectManipTool (self):
        cmds.setToolTo(mel.eval("$temp = $gshowManip"))
        self.mainInst.popState()


stateMap = {
    "START": stateSTART,
    "move": stateMove,
    "pickXYZ": statePickXYZ,
    "select": stateSelect,
    "selectMesh": stateSelectMesh,
    "toolSelect": stateToolSelect,
}

def initialize ():
    if cmds.hotkeySet(query=True, current=True) != "Tomayto":
        if "Tomayto" in cmds.hotkeySet(query=True, hotkeySetArray=True):
            cmds.hotkeySet("Tomayto", edit=True, current=True)
        else:
            cmds.hotkeySet("Tomayto", current=True)
    core.disable()
    core.enable()
    tom = core.Tomayto(stateMap, "START")
    return tom

