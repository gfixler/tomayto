import maya.cmds as cmds

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
            ('m', NOALT, NOCTRL, PRESS):   ("PUSH", "move"),
            ('u', NOALT, NOCTRL, PRESS):   ("PUSH", "undo"),
            ('r', NOALT, CTRL,   PRESS):   ("PUSH", "redo"),
            ('s', NOALT, NOCTRL, PRESS):   ("PUSH", "select"),
            ('h', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.play(state=True, forward=False)),
            ('h', NOALT, NOCTRL, RELEASE): ("RUN", lambda: cmds.play(state=False, forward=False)),
            ('l', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.play(state=True)),
            ('l', NOALT, NOCTRL, RELEASE): ("RUN", lambda: cmds.play(state=False)),
            ('H', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.currentTime(minTime())),
            ('L', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.currentTime(maxTime())),
            ('M', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.currentTime(round((minTime() + maxTime()) / 2))),
            ('M', ALT, CTRL, PRESS):       ("RUN", self.switchToMayaHotkeys),
        }

    def switchToMayaHotkeys (self):
        cmds.hotkeySet("Maya_Default", edit=True, current=True)

class stateUndo (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {}

    def onEnter (self):
        cmds.evalDeferred(cmds.undo)
        self.mainInst.popState()


class stateRedo (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {}

    def onEnter (self):
        cmds.evalDeferred(cmds.redo)
        self.mainInst.popState()


class stateMove (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {}

    def onEnter (self):
        self.mainInst.pushState("pickXYZ")

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
            ('m', NOALT, NOCTRL, PRESS): ("PUSH", "selectMesh"),
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


exampleStates = {
    "START": stateSTART,
    "undo": stateUndo,
    "redo": stateRedo,
    "move": stateMove,
    "pickXYZ": statePickXYZ,
    "select": stateSelect,
    "selectMesh": stateSelectMesh
}

def initialize ():
    if cmds.hotkeySet(query=True, current=True) != "Tomayto":
        if "Tomayto" in cmds.hotkeySet(query=True, hotkeySetArray=True):
            cmds.hotkeySet("Tomayto", edit=True, current=True)
        else:
            cmds.hotkeySet("Tomayto", current=True)
    core.disable()
    core.enable()
    tom = core.Tomayto(exampleStates, "START")
    return tom

