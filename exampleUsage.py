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
            ('V', False, False, True): ("PUSH", "vimLineTestWin"),
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

    def __init__ (self, mainInst, onChange=lambda _: None):
        self.mainInst = mainInst
        try:
            self.mainInst.vimLine
        except:
            # TODO: better handling of VimLine state, e.g. per 'client'
            self.mainInst.vimLine = { "left": ""
                                    , "right": ""
                                    , "onChange": onChange
                                    , "mode": "START"
                                    }
        self.vim = self.mainInst.vimLine
        self.keymap = { }

    def onEnter (self):
        print "entering VimLine"
        self.mainInst.pushState("vimLineNormalMode")

    def onPopTo (self, _):
        print "exiting VimLine"
        self.mainInst.popState()


class stateVimLineTestWin (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        try:
            self.mainInst.vimLineTestWin
        except:
            self.mainInst.vimLineTestWin = {}

        self.win = cmds.window()
        cmds.showWindow()
        self.fl = cmds.formLayout()
        # NO DIAGNOSE COLORS MODE
        self.ltext = cmds.text(label=" ", font="fixedWidthFont")
        self.itext = cmds.text(label=" ", font="fixedWidthFont")
        self.rtext = cmds.text(label=" ", font="fixedWidthFont")
        # DIAGNOSE COLORS MODE
        # self.ltext = cmds.text(label=" ", font="fixedWidthFont", backgroundColor=(1.0, 0.0, 0.0))
        # self.itext = cmds.text(label=" ", font="fixedWidthFont", backgroundColor=(0.0, 1.0, 0.0))
        # self.rtext = cmds.text(label=" ", font="fixedWidthFont", backgroundColor=(0.0, 0.0, 1.0))
        # HACK: must create text with " ", then edit to "" to shrink to 0 width
        cmds.text(self.ltext, edit=True, label="")
        cmds.text(self.itext, edit=True, label="")
        cmds.text(self.rtext, edit=True, label="")
        cmds.formLayout(self.fl, edit=True, attachForm=[ (self.ltext, "left", 0)
                                                       ],
                                            attachControl=[ (self.itext, "left", 0, self.ltext)
                                                          , (self.rtext, "left", 0, self.itext)
                                                          ])

        self.mainInst.vimLineTestWin = { "win": self.win
                                       , "ltext": self.ltext
                                       , "itext": self.itext
                                       , "rtext": self.rtext
                                       }

    def testWinOnChange (self, vimState):
        vim = self.mainInst.vimLine
        vimtw = self.mainInst.vimLineTestWin

        if vim["mode"] in ["insert", "INSERT", "append", "APPEND"]:
            cmds.text(vimtw["itext"], edit=True, backgroundColor=(0.3, 0.3, 0.3))
        elif vim["mode"] == "NORMAL":
            cmds.text(vimtw["itext"], edit=True, backgroundColor=(0.6, 0.6, 0.6))
            if not vim["right"]:
                if vim["left"]:
                    vim["right"] = vim["left"][-1]
                    vim["left"] = vim["left"][:-1]

        if vim["right"]:
            cmds.text(vimtw["rtext"], edit=True, label=vim["right"][1:])
            cmds.text(vimtw["itext"], edit=True, label=vim["right"][0])
        else:
            cmds.text(vimtw["rtext"], edit=True, label="")
            cmds.text(vimtw["itext"], edit=True, label=" ")

        if vim["left"]:
            cmds.text(vimtw["ltext"], edit=True, label=vim["left"])
        else:
            cmds.text(vimtw["ltext"], edit=True, label="")


    def onEnter (self):
        self.mainInst.pushState(("vimLine", [self.testWinOnChange]))

    def onPopTo (self):
        cmds.deleteUI(self.mainInst.vimLineTestWin["win"])
        self.mainInst.popState()



class stateVimLineNormalMode (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.mainInst.vimLine["mode"] = "NORMAL"
        self.handleChange()
        self.keymap = {
            ("i", False, False, True): ("PUSH", ("vimLineEnterInsertMode", ["insert"])),
            ("I", False, False, True): ("PUSH", ("vimLineEnterInsertMode", ["INSERT"])),
            ("a", False, False, True): ("PUSH", ("vimLineEnterInsertMode", ["append"])),
            ("A", False, False, True): ("PUSH", ("vimLineEnterInsertMode", ["APPEND"])),
            ("h", False, False, True): ("RUN", self.cursorLeft),
            ("l", False, False, True): ("RUN", self.cursorRight),
            ("0", False, False, True): ("RUN", self.toFirstColumn),
            ("$", False, False, True): ("RUN", self.toLastColumn), # TODO: $ should go to last non-whitespace column
            ("[", False, True, True): ("POP", self.handleEscape),
        }

    def onEnter (self):
        print "Entering vimLine Normal Mode"

    def onPopTo (self, _):
        self.mainInst.vimLine["mode"] = "NORMAL"
        self.handleChange()

    def handleChange (self):
        vim = self.mainInst.vimLine
        if "onChange" in vim:
            if callable(vim["onChange"]):
                vim["onChange"](vim)

    def handleEscape (self):
        # TODO: remove visible cursor from text(?)
        # print "^["
        pass

    def cursorLeft (self):
        vim = self.mainInst.vimLine
        if vim["left"]:
            vim["right"] = vim["left"][-1] + vim["right"]
            vim["left"] = vim["left"][:-1]
        self.handleChange()

    def cursorRight (self):
        vim = self.mainInst.vimLine
        if vim["right"]:
            vim["left"] = vim["left"] + vim["right"][0]
            vim["right"] = vim["right"][1:]
        self.handleChange()

    def toFirstColumn (self):
        vim = self.mainInst.vimLine
        vim["right"] = vim["left"] + vim["right"]
        vim["left"] = ""
        self.handleChange()

    def toLastColumn (self):
        vim = self.mainInst.vimLine
        if vim["right"]:
            vim["left"] = vim["left"] + vim["right"][:-1]
            vim["right"] = vim["right"][-1]
        elif vim["left"]:
            vim["right"] = vim["left"][-1]
            vim["left"] = vim["left"][:-1]
        self.handleChange()


class stateVimLineEnterInsertMode (object):

    def __init__ (self, mainInst, entryMode):
        self.mainInst = mainInst
        self.vim = self.mainInst.vimLine
        # TODO: handle cursor position based on entry mode
        print "entered via", entryMode
        if entryMode == "insert":
            self.mainInst.vimLine["mode"] = "insert"
        elif entryMode == "INSERT":
            self.mainInst.vimLine["mode"] = "INSERT"
            self.vim["right"] = self.vim["left"] + self.vim["right"]
            self.vim["left"] = ""
            self.handleChange()
        elif entryMode == "append":
            self.mainInst.vimLine["mode"] = "append"
            if self.vim["right"]:
                self.vim["left"] += self.vim["right"][0]
                self.vim["right"] = self.vim["right"][1:]
        elif entryMode == "APPEND":
            self.mainInst.vimLine["mode"] = "APPEND"
            self.vim["left"] = self.vim["left"] + self.vim["right"]
            self.vim["right"] = ""
        else:
            raise keyError, 'insert mode entry mode "' + entryMode + '" unknown'
        self.keymap = {
            ("h", False, True, True): ("RUN", self.handleBackspace),
            ("a", False, True, True): ("RUN", self.emacsHome),
            ("e", False, True, True): ("RUN", self.emacsEnd),
            ("Return", False, False, True): ("RUN", self.handleReturn),
            ("Backspace", False, False, True): ("RUN", self.handleBackspace),
            ("[", False, True, True): ("POP", self.handleEscape),
        }
        for k in util.keyChars:
            self.keymap[(k, False, False, True)] = ("PUSH", ("vimLineInsertMode", [k]))

    def onEnter (self):
        self.handleChange()

    def handleChange (self):
        self.vim = self.mainInst.vimLine
        if "onChange" in self.vim:
            if callable(self.vim["onChange"]):
                self.vim["onChange"](self.vim)

    def handleBackspace (self):
        # print "^h"
        vim = self.vim
        if vim["left"]:
            vim["left"] = vim["left"][:-1]
        self.handleChange()

    def handleEscape (self):
        # print "^["
        self.mainInst.vimLine["lastInsertMode"] = self.mainInst.vimLine["mode"]
        self.mainInst.vimLine["mode"] = "NORMAL"
        print "popping back from insert mode"

    def emacsHome (self):
        vim = self.vim
        vim["right"] = vim["left"] + vim["right"]
        vim["left"] = ""
        self.handleChange()

    def emacsEnd (self):
        vim = self.vim
        vim["left"] = vim["left"] + vim["right"]
        vim["right"] = ""
        self.handleChange()

    def handleReturn (self):
        print "^M"


class stateVimLineInsertMode (object):

    def __init__ (self, mainInst, char):
        self.mainInst = mainInst
        vim = self.mainInst.vimLine
        vim["left"] += char
        if "onChange" in vim:
            if callable(vim["onChange"]):
                vim["onChange"](vim)

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
    "vimLineEnterInsertMode": stateVimLineEnterInsertMode,
    "vimLineInsertMode": stateVimLineInsertMode,
    "vimLineTestWin": stateVimLineTestWin,
}

def instantiate ():
    cmds.hotkeySet("Tomayto", edit=True, current=True)
    tom = core.Tomayto(exampleStates, "START")
    return tom

