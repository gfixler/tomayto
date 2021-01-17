try:
    import maya.cmds as cmds
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__

try:
    import maya.mel as mel
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__


from .. core import ALT, NOALT, CTRL, NOCTRL, PRESS, RELEASE


wspos = lambda tf: cmds.xform(tf, query=True, worldSpace=True, translation=True)


class statePickXYZ (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {
            ('O', NOALT, NOCTRL, PRESS): ("POP", self.popOrigin)
        }

    def popOrigin (self):
        return (0, 0, 0)


class stateSelect (object):

    def __init__ (self, mainInst, single=False):
        self.mainInst = mainInst
        self.keymap = {
            ('m', NOALT, NOCTRL, PRESS): ("PUSH", (stateVisiblySelectTransform, ["mesh", True, single])),
            ('l', NOALT, NOCTRL, PRESS): ("PUSH", (stateVisiblySelectTransform, ["locator", True, single])),
            ('c', NOALT, NOCTRL, PRESS): ("PUSH", (stateVisiblySelectTransform, ["camera", True, single])),
            ('n', NOALT, NOCTRL, PRESS): ("RUN", self.selectNone),
            ('t', NOALT, NOCTRL, PRESS):   ("PUSH", stateToolSelect),
            ('w', NOALT, NOCTRL, PRESS): ("PUSH", stateSelectWindow),
        }

    def onPopTo (self, *value):
        self.mainInst.popState(*value)

    def selectNone (self):
        cmds.select(None)
        self.mainInst.popState()


def getTransformsOfType (nodeType, transformIsParent=False):
    nodes = cmds.ls(type=nodeType)
    if transformIsParent:
        getParent = lambda n: cmds.listRelatives(n, parent=True)[0]
        nodes = map(getParent, nodes)
    return nodes


class stateVisiblySelectTransform (object):

    def __init__ (self, mainInst, nodeType, transformIsParent=False, single=False):
        self.mainInst = mainInst
        self.nodeType = nodeType
        self.transformIsParent = transformIsParent
        self.single = single
        self.annotations = []
        self.keymap = {
            ("l", NOALT, CTRL, PRESS): ("RUN", lambda: self.updateArgs("locator", self.single)),
            ("m", NOALT, CTRL, PRESS): ("RUN", lambda: self.updateArgs("mesh", self.single)),
            ("c", NOALT, CTRL, PRESS): ("RUN", lambda: self.updateArgs("camera", self.single)),
            ("s", ALT, CTRL, PRESS): ("RUN", lambda: self.updateArgs(self.nodeType, not self.single)),
            ("Return", NOALT, NOCTRL, PRESS): ("POP", self.popSelection),
        }

    def clearAnnotations (self):
        for ann in self.annotations:
            p = cmds.listRelatives(ann, parent=True)[0]
            cmds.delete(p)
        self.annotations = []

    def updateAnnotations (self):
        self.clearAnnotations()
        sel = cmds.ls(selection=True, flatten=True)
        transforms = getTransformsOfType(self.nodeType, self.transformIsParent)
        for alpha, name in zip("abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", transforms):
            ann = cmds.annotate(name, tx=alpha, point=wspos(name))
            cmds.color(ann, rgbColor=(1, 1, 1))
            self.annotations.append(ann)
            self.keymap[(alpha, NOALT, NOCTRL, PRESS)] = ("RUN", self.toggleSelection(name))
        cmds.select(sel)

    def updateArgs (self, nodeType, single):
        if nodeType != self.nodeType:
            self.nodeType = nodeType
            self.updateAnnotations()
        self.single = single

    def onEnter (self):
        cmds.undoInfo(openChunk=True)
        self.updateAnnotations()

    def toggleSelection (self, name):
        def toggler ():
            if self.single:
                if name in cmds.ls(selection=True):
                    cmds.select(None)
                else:
                    cmds.select(name, replace=True)
            else:
                cmds.select(name, toggle=True)
        return toggler

    def popSelection (self):
        self.clearAnnotations()
        cmds.undoInfo(closeChunk=True)
        sel = cmds.ls(selection=True, flatten=True)
        # return sel


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


class stateSelectWindow (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {
            ('h', NOALT, NOCTRL, PRESS): ("RUN", self.prevWin),
            ('l', NOALT, NOCTRL, PRESS): ("RUN", self.nextWin),
            ("Return", NOALT, NOCTRL, PRESS): ("POP", self.cleanup),
        }
        self.wins = cmds.lsUI(type="window")
        self.ix = 0
        self.filterWins()
        self.selectWin()

    def filterWins (self):
        winExists = lambda w: cmds.window(w, query=True, exists=True)
        existingWins = filter(winExists, self.wins)
        self.wins = filter(lambda x: x != "MayaWindow", existingWins)

    def selectWin (self):
        print self.wins[self.ix]
        print cmds.window(self.wins[self.ix], query=True, topLeftCorner=True)
        cmds.window(self.wins[self.ix], edit=True, visible=True)
        cmds.setFocus(self.wins[self.ix])

    def prevWin (self):
        self.filterWins()
        self.ix = self.ix - 1
        if self.ix < 0:
            self.ix = len(self.wins) - 1
        self.selectWin()

    def nextWin (self):
        self.filterWins()
        self.ix = self.ix + 1
        if self.ix >= len(self.wins):
            self.ix = 0
        self.selectWin()

    def cleanup (self):
        cmds.setFocus("MayaWindow")

