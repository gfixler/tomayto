import maya.cmds as cmds


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

    def __init__ (self, mainInst):
        self.mainInst = mainInst
        self.keymap = {
            ('m', NOALT, NOCTRL, PRESS): ("PUSH", (stateMap, ("visibleSelectionOfType", ["mesh", True]))),
            ('l', NOALT, NOCTRL, PRESS): ("PUSH", (stateMap, ("visibleSelectionOfType", ["locator", True]))),
            ('c', NOALT, NOCTRL, PRESS): ("PUSH", (stateMap, ("visibleSelectionOfType", ["camera", True]))),
            ('n', NOALT, NOCTRL, PRESS): ("RUN", self.selectNone)
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


class stateVisibleSelectionOfType (object):

    def __init__ (self, mainInst, nodeType, transformIsParent=False):
        self.mainInst = mainInst
        self.transforms = getTransformsOfType(nodeType, transformIsParent)
        self.keymap = { }

    def onEnter (self):
        self.mainInst.pushState((stateMap, ("visiblySelectTransform", [self.transforms])))

    def onPopTo (self, *_):
        self.mainInst.popState()


class stateVisiblySelectTransform (object):

    def __init__ (self, mainInst, transforms):
        self.mainInst = mainInst
        self.transforms = transforms
        self.keymap = {
            ("Return", NOALT, NOCTRL, PRESS): ("POP", self.popSelection)
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

    def toggleSelection (self, name):
        def toggler ():
            cmds.select(name, toggle=True)
        return toggler

    def popSelection (self):
        for ann in self.anns:
            p = cmds.listRelatives(ann, parent=True)[0]
            cmds.delete(p)
        cmds.undoInfo(closeChunk=True)
        sel = cmds.ls(selection=True, flatten=True)
        return sel


stateMap = {
    "pickXYZ": statePickXYZ,
    "select": stateSelect,
    "visibleSelectionOfType": stateVisibleSelectionOfType,
    "visiblySelectTransform": stateVisiblySelectTransform,
}

