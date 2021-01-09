try:
    import maya.cmds as cmds
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__

try:
    import maya.mel as mel
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__

from .. ui import SelectionList
from .. core import ALT, NOALT, CTRL, NOCTRL, PRESS, RELEASE

import selection
import transform
import vimline


fst = lambda (x, _) :  x

minTime = lambda: cmds.playbackOptions(query=True, minTime=True)
maxTime = lambda: cmds.playbackOptions(query=True, maxTime=True)


class stateSTART (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {
            ('I', NOALT, NOCTRL, PRESS):   ("PUSH", stateSelectionListDemo),
            ('d', NOALT, NOCTRL, PRESS):   ("RUN", cmds.delete),
            ('f', NOALT, NOCTRL, PRESS):   ("RUN", cmds.viewFit),
            ('F', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.viewFit(allObjects=True)),
            ('u', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.evalDeferred(cmds.undo)),
            ('r', NOALT, CTRL,   PRESS):   ("RUN", lambda: cmds.evalDeferred(cmds.redo)),
            ('h', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.play(state=True, forward=False)),
            ('h', NOALT, NOCTRL, RELEASE): ("RUN", lambda: cmds.play(state=False, forward=False)),
            ('l', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.play(state=True)),
            ('l', NOALT, NOCTRL, RELEASE): ("RUN", lambda: cmds.play(state=False)),
            ('H', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.currentTime(minTime())),
            ('L', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.currentTime(maxTime())),
            ('M', NOALT, NOCTRL, PRESS):   ("RUN", lambda: cmds.currentTime(round((minTime() + maxTime()) / 2))),
            ('M', ALT, CTRL, PRESS):       ("RUN", self.switchToMayaHotkeys),
            ('t', NOALT, NOCTRL, PRESS):   ("PUSH", stateToolSelect),

            ('m', NOALT, NOCTRL, PRESS):   ("PUSH", transform.stateMove),

            ('s', NOALT, NOCTRL, PRESS):   ("PUSH", selection.stateSelect),

            ('v', NOALT, NOCTRL, PRESS):   ("PUSH", vimline.stateVimline),
            ('V', NOALT, NOCTRL, PRESS):   ("PUSH", vimline.stateVimlineTestWin),
            ('v', NOALT, CTRL, PRESS):     ("PUSH", stateRetitleWindowDemo),
        }

    def switchToMayaHotkeys (self):
        cmds.hotkeySet("Maya_Default", edit=True, current=True)


class stateRetitleWindowDemo (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {
            ("Return", NOALT, NOCTRL, PRESS):    ("POP", self.cleanup)
        }
        self._win = cmds.window()
        cmds.showWindow(self._win)

    def callback (self, state):
        l, c, r = vimline.getVimlineParts(state)
        cmds.window(self._win, edit=True, title=l + c + r)

    def onEnter (self):
        self.mainInst.pushState((vimline.stateVimline, [self.callback]))

    def cleanup (self):
        cmds.evalDeferred(lambda: cmds.deleteUI(self._win))
        self.mainInst.popState()


class stateSelectionListDemo (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.win = cmds.window(topLeftCorner=(400, 270))
        values = cmds.ls(allPaths=True)
        self.sl = SelectionList(values, filtF=lambda x: "Manager" not in x, sortF=lambda x: x[1])
        cmds.showWindow(self.win)
        cmds.evalDeferred(self.sizeWindow)
        self.keymap = {
            ('j', NOALT, CTRL, PRESS): ("RUN", self.sl.scrollLine),
            ('k', NOALT, CTRL, PRESS): ("RUN", (self.sl.scrollLine, [False])),
            ('d', NOALT, CTRL, PRESS): ("RUN", (self.sl.scrollPage, [True, True])),
            ('u', NOALT, CTRL, PRESS): ("RUN", (self.sl.scrollPage, [False, True])),
            ('f', NOALT, CTRL, PRESS): ("RUN", self.sl.scrollPage),
            ('b', NOALT, CTRL, PRESS): ("RUN", (self.sl.scrollPage, [False, False])),
            ('6', NOALT, CTRL, PRESS): ("RUN", self.sl.scrollToTop), # ^ - gg is no good
            ('4', NOALT, CTRL, PRESS): ("RUN", self.sl.scrollToBottom), # $ - G is no good
            ('o', NOALT, CTRL, PRESS): ("POP", self.returnOrderedSelected),
            ('a', NOALT, CTRL, PRESS): ("RUN", self.sl.toggleVisible),
            ('Return', NOALT, CTRL, PRESS): ("POP", self.returnUnselected),
            ('Return', NOALT, NOCTRL, PRESS): ("RUN", self.returnUnorderedSelected),
        }
        eventKeys = self.sl.settings["selectionKeys"]
        for key in eventKeys:
            keyMaker = lambda k: lambda: self.toggleSelection(k)
            self.keymap[(key, NOALT, NOCTRL, PRESS)] = ("RUN", keyMaker(key))

    def sizeWindow (self):
        sfEntries = map(lambda v: self.sl.entries[v], self.sl.entryVals)
        getUIWidth = lambda x: cmds.text(x["ui"], query=True, width=True)
        w = max(map(getUIWidth, sfEntries)) * 1.3
        h = min(350, w * 1.5)
        cmds.window(self.win, edit=True, widthHeight=(w, h))

    def toggleSelection (self, key):
        self.sl.toggle(key)

    def returnValues (self, selOrder, selected):
        if selected:
            seld = filter(lambda (_, v): v["selected"] > 0, self.sl.entries.items())
            if selOrder:
                vals = map(fst, sorted(seld, key=lambda (_, v): v["selected"]))
            else:
                vals = [v for v in self.sl.values if self.sl.entries[v]["selected"] > 0]
        else:
            vals = [v for v in self.sl.values if self.sl.entries[v]["selected"] == 0]
        try:
            cmds.deleteUI(self.win)
        except:
            pass
        print
        for val in vals:
            print val
        self.mainInst.popState(vals)

    def returnOrderedSelected (self):
        self.returnValues(True, True)

    def returnUnorderedSelected (self):
        self.returnValues(False, True)

    def returnUnselected (self):
        self.returnValues(False, False)


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

