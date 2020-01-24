import maya.cmds as cmds

from . import util


class Tomayto (object):

    def defaultCB (self, key, alt, ctrl, press):
        """
        This default callback simply prints out the pressed and released keys,
        and modified variants, when assigned to the global callback name. It's
        only intended to check that the nameCommands and hotkeys have been set
        up correctly; normal use is to assign another handler to the global
        callback name.
        """
        if press:
            print "pressed: " + ("alt + " if alt else "") + ("ctrl + " if ctrl else "") + util.charName(key)
        else:
            print "released: " + ("alt + " if alt else "") + ("ctrl + " if ctrl else "") + util.charName(key)

