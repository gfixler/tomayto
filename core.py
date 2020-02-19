import maya.cmds as cmds

import util


class Tomayto (object):

    def __init__ (self, states, startState):
        """
        Each state must be a class with an init that accepts a handler func.
        "states" is a dict of name:state pairs of state class references.
        "startState" is the (string) key of the starting state in states.
        """
        self.states = states
        self.startState = states[startState](self) # init start state
        self.stateStack = [] # start state doesn't go on stack/can't be popped

    def tester (self, key, alt, ctrl, press):
        """
        When assigned to the global callback name, this callback prints out
        pressed and released keys, and modified variants. It's useful to check
        that the nameCommands and hotkeys have been set up correctly; normal
        use is to assign another handler to the global callback name.
        """
        if press:
            print "pressed: " + ("alt + " if alt else "") + ("ctrl + " if ctrl else "") + util.keyName(key)
        else:
            print "released: " + ("alt + " if alt else "") + ("ctrl + " if ctrl else "") + util.keyName(key)

