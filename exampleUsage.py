import maya.cmds as cmds

import core

wspos = lambda tf: cmds.xform(tf, query=True, worldSpace=True, translation=True)
minTime = lambda: cmds.playbackOptions(query=True, minTime=True)
maxTime = lambda: cmds.playbackOptions(query=True, maxTime=True)

class stateSTART (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {
            ('m', False, False, True): ("PUSH", "move"),
            ('u', False, False, True): ("PUSH", "undo"),
            ('r', False, True, True): ("PUSH", "redo"),
            ('s', False, False, True): ("PUSH", "select"),
            ('v', False, False, True): ("PUSH", "vimLine"),
            ('V', False, False, True): ("PUSH", "vimLineTestWin"),
            ('h', False, False, True): ("RUN", lambda: cmds.play(state=True, forward=False)),
            ('h', False, False, False): ("RUN", lambda: cmds.play(state=False, forward=False)),
            ('l', False, False, True): ("RUN", lambda: cmds.play(state=True)),
            ('l', False, False, False): ("RUN", lambda: cmds.play(state=False)),
            ('H', False, False, True): ("RUN", lambda: cmds.currentTime(minTime())),
            ('L', False, False, True): ("RUN", lambda: cmds.currentTime(maxTime())),
            ('M', False, False, True): ("RUN", lambda: cmds.currentTime(round((minTime() + maxTime()) / 2))),
            ('M', True, True, True): ("RUN", self.switchToMayaHotkeys),
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
            ('O', False, False, True): ("POP", self.popOrigin)
        }

    def popOrigin (self):
        return (0, 0, 0)


class stateSelect (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {
            ('m', False, False, True): ("PUSH", "selectMesh"),
            ('n', False, False, True): ("RUN", self.selectNone)
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
            ("Return", False, False, True): ("POP", self.popSelection)
        }

    def onEnter (self):
        meshes = cmds.ls(type="mesh")
        tfs = map(lambda x: cmds.listRelatives(x, parent=True)[0], meshes)
        self.anns = []
        sel = cmds.ls(selection=True, flatten=True)
        for alpha, name in zip("abcdefghijklmnopqrstuvwxyz0123456789", tfs):
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

def instantiate ():
    cmds.hotkeySet("Tomayto", edit=True, current=True)
    tom = core.Tomayto(exampleStates, "START")
    return tom

