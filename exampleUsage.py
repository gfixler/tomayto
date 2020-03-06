import maya.cmds as cmds

import core

wspos = lambda tf: cmds.xform(tf, query=True, worldSpace=True, translation=True)

class stateSTART (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {
            ('m', False, False, True): ("PUSH", "move"),
            ('u', False, False, True): ("PUSH", "undo"),
            ('r', False, True, True): ("PUSH", "redo"),
            ('s', False, False, True): ("PUSH", "select"),
            ('w', False, False, True): ("PUSH", "makeWindow")
        }


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


class stateMakeWindow (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        try:
            self.mainInst.winMaker
        except:
            self.mainInst.winMaker = {"windows": {}, "currentWindow": None, "focus": None}
        self.keymap = {
            ("c", False, False, True): ("PUSH", ("stateCreateLayout", ["column"])),
            ("f", False, False, True): ("PUSH", ("stateCreateLayout", ["form"])),
            ("F", False, False, True): ("PUSH", ("stateCreateLayout", ["frame"])),
            ("g", False, False, True): ("PUSH", ("stateCreateLayout", ["grid"])),
            ("p", False, False, True): ("PUSH", ("stateCreateLayout", ["pane"])),
            ("r", False, False, True): ("PUSH", ("stateCreateLayout", ["row"])),
            ("s", False, False, True): ("PUSH", ("stateCreateLayout", ["scroll"])),
            ("t", False, False, True): ("PUSH", ("stateCreateLayout", ["tab"]))
        }

    def onEnter (self):
        win = cmds.window()
        wm = self.mainInst.winMaker
        wm["windows"][win] = {"window": win, "layout": None}
        wm["currentWindow"] = win
        wm["focus"] = "window"
        cmds.showWindow()


class stateCreateLayout (object):

    import pdb

    def __init__ (self, mainInst, layoutType):
        self.mainInst = mainInst
        self.keymap = {}
        self.layoutType = layoutType
        print layoutType

    def onEnter (self):
        wm = self.mainInst.winMaker
        if wm["focus"] == "window":
            if self.layoutType == "frame":
                win = wm["windows"][wm["currentWindow"]]["window"]
                lay = cmds.frameLayout(parent=win)
                wm["windows"]["layout"] = lay
        self.mainInst.popState()


exampleStates = {
    "START": stateSTART,
    "undo": stateUndo,
    "redo": stateRedo,
    "move": stateMove,
    "pickXYZ": statePickXYZ,
    "select": stateSelect,
    "selectMesh": stateSelectMesh,
    "makeWindow": stateMakeWindow,
    "stateCreateLayout": stateCreateLayout
}

def instantiate ():
    cmds.hotkeySet("Tomayto", edit=True, current=True)
    tom = core.Tomayto(exampleStates, "START")
    return tom

