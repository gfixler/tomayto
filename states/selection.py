try:
    import maya.cmds as cmds
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
            ('t', NOALT, NOCTRL, PRESS): ("PUSH", (stateSelect, [True])),
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
        return sel

