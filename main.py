import maya.cmds as cmds

import core
from states import START


def initialize ():
    if cmds.hotkeySet(query=True, current=True) != "Tomayto":
        if "Tomayto" in cmds.hotkeySet(query=True, hotkeySetArray=True):
            cmds.hotkeySet("Tomayto", edit=True, current=True)
        else:
            cmds.hotkeySet("Tomayto", current=True)
    core.disable()
    core.enable()
    tom = core.Tomayto(START.stateMap, "START")
    return tom

