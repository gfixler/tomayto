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
        self.transforms = getTransformsOfType(nodeType, transformIsParent)
        self.keymap = {
            ("l", NOALT, CTRL, PRESS): ("PUSH", (stateVisiblySelectTransform, ["locator", transformIsParent, single])),
            ("m", NOALT, CTRL, PRESS): ("PUSH", (stateVisiblySelectTransform, ["mesh", transformIsParent, single])),
            ("c", NOALT, CTRL, PRESS): ("PUSH", (stateVisiblySelectTransform, ["camera", transformIsParent, single])),
            ("s", ALT, CTRL, PRESS): ("PUSH", (stateVisiblySelectTransform, [nodeType, transformIsParent, not single])),
            ("Return", NOALT, NOCTRL, PRESS): ("POP", self.popSelection),
        }

    def onEnter (self):
        cmds.undoInfo(openChunk=True)
        self.anns = []
        sel = cmds.ls(selection=True, flatten=True)
        for alpha, name in zip("abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", self.transforms):
            print alpha, name
            ann = cmds.annotate(name, tx=alpha, point=wspos(name))
            cmds.color(ann, rgbColor=(1, 1, 1))
            self.anns.append(ann)
            self.keymap[(alpha, NOALT, NOCTRL, PRESS)] = ("RUN", self.toggleSelection(name))
        cmds.select(sel)

    def onPopTo (self, *value):
        self.mainInst.popState(*value)

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
        for ann in self.anns:
            p = cmds.listRelatives(ann, parent=True)[0]
            cmds.delete(p)
        cmds.undoInfo(closeChunk=True)
        sel = cmds.ls(selection=True, flatten=True)
        return sel

