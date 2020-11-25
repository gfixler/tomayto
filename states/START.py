try:
    import maya.cmds as cmds
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__

try:
    import maya.mel as mel
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__

from .. core import ALT, NOALT, CTRL, NOCTRL, PRESS, RELEASE

import selection
import transform
import vimline


minTime = lambda: cmds.playbackOptions(query=True, minTime=True)
maxTime = lambda: cmds.playbackOptions(query=True, maxTime=True)


class stateSTART (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {
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
        }

    def switchToMayaHotkeys (self):
        cmds.hotkeySet("Maya_Default", edit=True, current=True)


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

