try:
    import maya.cmds as cmds
except ImportError:
    print('WARNING (%s): failed to load maya.cmds module.' % __file__)

from . import selection


class stateMove (object):

    def __init__ (self, mainInst):
        self.mainInst = mainInst

    def onEnter (self):
        self.mainInst.pushState(selection.statePickXYZ)

    def onPopTo (self, value):
        x, y, z = value
        selected = cmds.ls(selection=True)
        map(lambda tf: cmds.move(x, y, z, tf), selected)
        self.mainInst.popState()

