try:
    import maya.cmds as cmds
except ImportError:
    print('WARNING (%s): failed to load maya.cmds module.' % __file__)


from .. core import ALT, NOALT, CTRL, NOCTRL, PRESS, RELEASE
from .. import util


def getVimlineParts (state):
    if state["right"]:
        return (state["left"], state["right"][0], state["right"][1:])
    else:
        return (state["left"], " ", "")


class stateVimline (object):

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

    def onEnter (self):
        print("entering Vimline")
        self.mainInst.pushState(stateVimlineNormalMode)

    def onPopTo (self, *_):
        print("exiting Vimline")
        self.mainInst.popState()


class stateVimlineTestWin (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        try:
            self.mainInst.vimlineTestWin
        except:
            self.mainInst.vimlineTestWin = {}

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

    def testWinOnChange (self, state):
        vimtw = self.mainInst.vimlineTestWin

        if state["mode"] in ["insert", "INSERT", "append", "APPEND"]:
            cmds.text(vimtw["itext"], edit=True, backgroundColor=(0.3, 0.3, 0.3))
        elif state["mode"] == "NORMAL":
            cmds.text(vimtw["itext"], edit=True, backgroundColor=(0.6, 0.6, 0.6))

        l, c, r = getVimlineParts(state)
        cmds.text(vimtw["ltext"], edit=True, label=l)
        cmds.text(vimtw["itext"], edit=True, label=c)
        cmds.text(vimtw["rtext"], edit=True, label=r)


    def onEnter (self):
        self.mainInst.pushState((stateVimline, [self.testWinOnChange]))

    def onPopTo (self, *_):
        cmds.deleteUI(self.mainInst.vimlineTestWin["win"])
        self.mainInst.popState()


class stateVimlineNormalMode (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.mainInst.vimline["mode"] = "NORMAL"
        self.handleChange()
        self.keymap = {
            ("i", NOALT, NOCTRL, PRESS): ("PUSH", (stateVimlineEnterInsertMode, ["insert"])),
            ("I", NOALT, NOCTRL, PRESS): ("PUSH", (stateVimlineEnterInsertMode, ["INSERT"])),
            ("a", NOALT, NOCTRL, PRESS): ("PUSH", (stateVimlineEnterInsertMode, ["append"])),
            ("A", NOALT, NOCTRL, PRESS): ("PUSH", (stateVimlineEnterInsertMode, ["APPEND"])),
            ("h", NOALT, NOCTRL, PRESS): ("RUN", self.cursorLeft),
            ("l", NOALT, NOCTRL, PRESS): ("RUN", self.cursorRight),
            ("0", NOALT, NOCTRL, PRESS): ("RUN", self.toFirstColumn),
            ("$", NOALT, NOCTRL, PRESS): ("RUN", self.toLastColumn), # TODO: $ should go to last non-whitespace column
            ("[", NOALT, CTRL, PRESS): ("POP", self.handleEscape),
            ("Return", NOALT, NOCTRL, PRESS): ("POP", self.handleEscape),
        }

    def onEnter (self):
        print("Entering vimline Normal Mode")

    def onPopTo (self, *_):
        self.mainInst.vimline["mode"] = "NORMAL"
        self.handleChange()

    def handleChange (self):
        vim = self.mainInst.vimline
        # don't allow cursor off right end in normal mode
        if not vim["right"]:
            if vim["left"]:
                vim["right"] = vim["left"][-1]
                vim["left"] = vim["left"][:-1]
        if "onChange" in vim:
            if callable(vim["onChange"]):
                vim["onChange"](vim)

    def handleEscape (self):
        # TODO: remove visible cursor from text(?)
        # print("^[")
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


class stateVimlineEnterInsertMode (object):

    def __init__ (self, mainInst, entryMode):
        self.mainInst = mainInst
        self.vim = self.mainInst.vimline
        # TODO: handle cursor position based on entry mode
        print("entered via", entryMode)
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
            raise(keyError, 'insert mode entry mode "' + entryMode + '" unknown')
        self.keymap = {
            ("h", NOALT, CTRL, PRESS): ("RUN", self.handleBackspace),
            ("a", NOALT, CTRL, PRESS): ("RUN", self.emacsHome),
            ("e", NOALT, CTRL, PRESS): ("RUN", self.emacsEnd),
            ("Return", NOALT, NOCTRL, PRESS): ("RUN", self.handleReturn),
            ("Backspace", NOALT, NOCTRL, PRESS): ("RUN", self.handleBackspace),
            ("[", NOALT, CTRL, PRESS): ("POP", self.handleEscape),
        }
        for k in util.keyChars:
            self.keymap[(k, NOALT, NOCTRL, PRESS)] = ("PUSH", (stateVimlineInsertMode, [k]))

    def onEnter (self):
        self.handleChange()

    def handleChange (self):
        self.vim = self.mainInst.vimline
        if "onChange" in self.vim:
            if callable(self.vim["onChange"]):
                self.vim["onChange"](self.vim)

    def handleBackspace (self):
        # print("^h")
        vim = self.vim
        if vim["left"]:
            vim["left"] = vim["left"][:-1]
        self.handleChange()

    def handleEscape (self):
        # print("^[")
        self.mainInst.vimline["lastInsertMode"] = self.mainInst.vimline["mode"]
        self.mainInst.vimline["mode"] = "NORMAL"
        print("popping back from insert mode")

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
        print("^M")
        self.mainInst.popState(self.handleEscape)


class stateVimlineInsertMode (object):

    def __init__ (self, mainInst, char):
        self.mainInst = mainInst
        vim = self.mainInst.vimline
        vim["left"] += char
        if "onChange" in vim:
            if callable(vim["onChange"]):
                vim["onChange"](vim)

    def onEnter (self):
        self.mainInst.popState()

