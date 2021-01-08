try:
    import maya.cmds as cmds
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__


import core
from states import START


def initialize (refreshKeymap=True):
    if cmds.hotkeySet(query=True, current=True) != "Tomayto":
        if "Tomayto" in cmds.hotkeySet(query=True, hotkeySetArray=True):
            cmds.hotkeySet("Tomayto", edit=True, current=True)
        else:
            cmds.hotkeySet("Tomayto", current=True)
    if refreshKeymap:
        core.disable()
        core.enable()
    tom = core.Tomayto(START.stateSTART)
    return tom

