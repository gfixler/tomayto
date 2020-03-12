import maya.cmds as cmds

import util
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
            ('v', False, False, True): ("PUSH", "vimLine"),
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


class stateVimLine (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        try:
            self.mainInst.vimLine
        except:
            self.mainInst.vimLine = {"left": "", "right": ""}
        self.vim = self.mainInst.vimLine
        self.keymap = { }

    def onEnter (self):
        print "entering VimLine"
        self.mainInst.pushState("vimLineNormalMode")

    def onPopTo (self, value):
        print "exiting VimLine"
        self.mainInst.popState()


class stateVimLineNormalMode (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {
            ("i", False, False, True): ("PUSH", ("vimLineInsertMode", ["insert"])),
            ("I", False, False, True): ("PUSH", ("vimLineInsertMode", ["INSERT"])),
            ("a", False, False, True): ("PUSH", ("vimLineInsertMode", ["append"])),
            ("A", False, False, True): ("PUSH", ("vimLineInsertMode", ["APPEND"])),
            ("h", False, False, True): ("RUN", self.cursorLeft),
            ("l", False, False, True): ("RUN", self.cursorRight),
            ("[", False, True, True): ("POP", self.handleEscape)
        }

    def handleEscape (self):
        # TODO: remove visible cursor from text(?)
        print "^["

    def cursorLeft (self):
        vim = self.mainInst.vimLine
        if vim["left"]:
            vim["right"] = vim["left"][-1] + vim["right"]
            vim["left"] = vim["left"][:-1]
            print vim["left"] + "|" + vim["right"]

    def cursorRight (self):
        vim = self.mainInst.vimLine
        if vim["right"]:
            vim["left"] = vim["left"] + vim["right"][0]
            vim["right"] = vim["right"][1:]
            print vim["left"] + "|" + vim["right"]


class stateVimLineInsertMode (object):

    def __init__ (self, mainInst, entryMode):
        self.mainInst = mainInst
        self.vim = self.mainInst.vimLine
        print "entered via", entryMode
        self.keymap = {
            ("h", False, True, True): ("RUN", self.handleBackspace),
            ("[", False, True, True): ("POP", self.handleEscape),
            ("a", False, True, True): ("RUN", self.emacsHome),
            ("e", False, True, True): ("RUN", self.emacsEnd),
            ("Return", False, False, True): ("RUN", self.handleReturn),
            ("Backspace", False, False, True): ("RUN", self.handleBackspace),
        }
        for k in util.keyChars:
            self.keymap[(k, False, False, True)] = ("PUSH", ("vimLineInsertChar", [k]))

    def handleBackspace (self):
        print "^h"
        if self.vim["left"]:
            self.vim["left"] = self.vim["left"][:-1]
        print self.vim["left"] + "|" + self.vim["right"]

    def handleEscape (self):
        print "^["

    def emacsHome (self):
        self.vim["right"] = self.vim["left"] + self.vim["right"]
        self.vim["left"] = ""
        print self.vim["left"] + "|" + self.vim["right"]

    def emacsEnd (self):
        self.vim["left"] = self.vim["left"] + self.vim["right"]
        self.vim["right"] = ""
        print self.vim["left"] + "|" + self.vim["right"]

    def handleReturn (self):
        print "^M"


class stateVimLineInsertChar (object):

    def __init__ (self, mainInst, char):
        self.mainInst = mainInst
        vim = self.mainInst.vimLine
        vim["left"] = vim["left"] + char
        print vim["left"] + "|" + vim["right"]

    def onEnter (self):
        self.mainInst.popState()


exampleStates = {
    "START": stateSTART,
    "undo": stateUndo,
    "redo": stateRedo,
    "move": stateMove,
    "pickXYZ": statePickXYZ,
    "select": stateSelect,
    "selectMesh": stateSelectMesh,
    "vimLine": stateVimLine,
    "vimLineNormalMode": stateVimLineNormalMode,
    "vimLineInsertMode": stateVimLineInsertMode,
    "vimLineInsertChar": stateVimLineInsertChar,
}

def instantiate ():
    cmds.hotkeySet("Tomayto", edit=True, current=True)
    tom = core.Tomayto(exampleStates, "START")
    return tom

