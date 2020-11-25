import maya.cmds as cmds

from .. core import ALT, NOALT, CTRL, NOCTRL, PRESS, RELEASE
from .. import util


class State_Vimline (object):

    def __init__ (self, mainInst, onChange=lambda _: None):
        self.mainInst = mainInst
        try:
            self.mainInst.vimline
        except:
            # TODO: better handling of Vimline state, e.g. per 'client'
            self.mainInst.vimline = { "left": ""
                                    , "right": ""
                                    , "onChange": onChange
                                    , "mode": "START"
                                    }
        self.vim = self.mainInst.vimline
        self.keymap = { }

    def onEnter (self):
        print "entering Vimline"
        self.mainInst.pushState(State_VimlineNormalMode)

    def onPopTo (self, *_):
        print "exiting Vimline"
        self.mainInst.popState()


class State_VimlineTestWin (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        try:
            self.mainInst.vimlineTestWin
        except:
            self.mainInst.vimlineTestWin = {}
        self.keymap = { }

        self.win = cmds.window(widthHeight=(300,100), topLeftCorner=(332, 680))
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

        self.mainInst.vimlineTestWin = { "win": self.win
                                       , "ltext": self.ltext
                                       , "itext": self.itext
                                       , "rtext": self.rtext
                                       }

    def testWinOnChange (self, vimState):
        vim = self.mainInst.vimline
        vimtw = self.mainInst.vimlineTestWin

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
        self.mainInst.pushState((State_Vimline, [self.testWinOnChange]))

    def onPopTo (self, *_):
        cmds.deleteUI(self.mainInst.vimlineTestWin["win"])
        self.mainInst.popState()


class State_VimlineNormalMode (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.mainInst.vimline["mode"] = "NORMAL"
        self.handleChange()
        self.keymap = {
            ("i", NOALT, NOCTRL, PRESS): ("PUSH", (State_VimlineEnterInsertMode, ["insert"])),
            ("I", NOALT, NOCTRL, PRESS): ("PUSH", (State_VimlineEnterInsertMode, ["INSERT"])),
            ("a", NOALT, NOCTRL, PRESS): ("PUSH", (State_VimlineEnterInsertMode, ["append"])),
            ("A", NOALT, NOCTRL, PRESS): ("PUSH", (State_VimlineEnterInsertMode, ["APPEND"])),
            ("h", NOALT, NOCTRL, PRESS): ("RUN", self.cursorLeft),
            ("l", NOALT, NOCTRL, PRESS): ("RUN", self.cursorRight),
            ("0", NOALT, NOCTRL, PRESS): ("RUN", self.toFirstColumn),
            ("$", NOALT, NOCTRL, PRESS): ("RUN", self.toLastColumn), # TODO: $ should go to last non-whitespace column
            ("[", NOALT, CTRL, PRESS): ("POP", self.handleEscape),
            ("Return", NOALT, NOCTRL, PRESS): ("POP", self.handleEscape),
        }

    def onEnter (self):
        print "Entering vimline Normal Mode"

    def onPopTo (self, *_):
        self.mainInst.vimline["mode"] = "NORMAL"
        self.handleChange()

    def handleChange (self):
        vim = self.mainInst.vimline
        if "onChange" in vim:
            if callable(vim["onChange"]):
                vim["onChange"](vim)

    def handleEscape (self):
        # TODO: remove visible cursor from text(?)
        # print "^["
        pass

    def cursorLeft (self):
        vim = self.mainInst.vimline
        if vim["left"]:
            vim["right"] = vim["left"][-1] + vim["right"]
            vim["left"] = vim["left"][:-1]
        self.handleChange()

    def cursorRight (self):
        vim = self.mainInst.vimline
        if vim["right"]:
            vim["left"] = vim["left"] + vim["right"][0]
            vim["right"] = vim["right"][1:]
        self.handleChange()

    def toFirstColumn (self):
        vim = self.mainInst.vimline
        vim["right"] = vim["left"] + vim["right"]
        vim["left"] = ""
        self.handleChange()

    def toLastColumn (self):
        vim = self.mainInst.vimline
        if vim["right"]:
            vim["left"] = vim["left"] + vim["right"][:-1]
            vim["right"] = vim["right"][-1]
        elif vim["left"]:
            vim["right"] = vim["left"][-1]
            vim["left"] = vim["left"][:-1]
        self.handleChange()


class State_VimlineEnterInsertMode (object):

    def __init__ (self, mainInst, entryMode):
        self.mainInst = mainInst
        self.keymap = { }
        self.vim = self.mainInst.vimline
        # TODO: handle cursor position based on entry mode
        print "entered via", entryMode
        if entryMode == "insert":
            self.mainInst.vimline["mode"] = "insert"
        elif entryMode == "INSERT":
            self.mainInst.vimline["mode"] = "INSERT"
            self.vim["right"] = self.vim["left"] + self.vim["right"]
            self.vim["left"] = ""
            self.handleChange()
        elif entryMode == "append":
            self.mainInst.vimline["mode"] = "append"
            if self.vim["right"]:
                self.vim["left"] += self.vim["right"][0]
                self.vim["right"] = self.vim["right"][1:]
        elif entryMode == "APPEND":
            self.mainInst.vimline["mode"] = "APPEND"
            self.vim["left"] = self.vim["left"] + self.vim["right"]
            self.vim["right"] = ""
        else:
            raise keyError, 'insert mode entry mode "' + entryMode + '" unknown'
        self.keymap = {
            ("h", NOALT, CTRL, PRESS): ("RUN", self.handleBackspace),
            ("a", NOALT, CTRL, PRESS): ("RUN", self.emacsHome),
            ("e", NOALT, CTRL, PRESS): ("RUN", self.emacsEnd),
            ("Return", NOALT, NOCTRL, PRESS): ("RUN", self.handleReturn),
            ("Backspace", NOALT, NOCTRL, PRESS): ("RUN", self.handleBackspace),
            ("[", NOALT, CTRL, PRESS): ("POP", self.handleEscape),
            ("Return", NOALT, NOCTRL, PRESS): ("POP", self.handleEscape),
        }
        for k in util.keyChars:
            self.keymap[(k, NOALT, NOCTRL, PRESS)] = ("PUSH", (State_VimlineInsertMode, [k]))

    def onEnter (self):
        self.handleChange()

    def handleChange (self):
        self.vim = self.mainInst.vimline
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
        self.mainInst.vimline["lastInsertMode"] = self.mainInst.vimline["mode"]
        self.mainInst.vimline["mode"] = "NORMAL"
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


class State_VimlineInsertMode (object):

    def __init__ (self, mainInst, char):
        self.mainInst = mainInst
        self.keymap = { }
        vim = self.mainInst.vimline
        vim["left"] += char
        if "onChange" in vim:
            if callable(vim["onChange"]):
                vim["onChange"](vim)

    def onEnter (self):
        self.mainInst.popState()

