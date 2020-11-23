import maya.cmds as cmds

import util


class Tomayto (object):

    def __init__ (self, stateMap, startStateName):
        """
        Each state must be a class with an init that accepts a reference to the
        instance of this class that instantiates it. Each instance should store
        the ref for use in communicating with it later.
        "stateMap" is a dict of name:state pairs of state class references.
        "startStateName" is the string key of the starting state in stateMap.
        """
        self.stateMap = stateMap
        self.startStateName = startStateName
        self.startState = stateMap[startStateName](self) # init start state
        self.stateStack = [] # start state doesn't go on stack/can't be popped

    def getCurrentState (self):
        if self.stateStack:
            return self.stateStack[-1]
        return (self.startStateName, self.startState)

    def eventHandler (self, key, alt, ctrl, press):
        stateName, state = self.getCurrentState()
        event = (key, alt, ctrl, press)
        if event == ('?', True, True, True):
            self.helpOnCurrentState()
            return
        elif event in state.keymap.keys():
            eventAction, eventActionData = state.keymap[event]
            if eventAction == "PUSH":
                self.pushState(eventActionData)
            elif eventAction == "POP":
                self.popState(eventActionData)
            elif eventAction == "RUN":
                self.runMethod(eventActionData)

    def pushState (self, stateName):
        if stateName in self.stateMap:
            stateClass = self.stateMap[stateName]
            newStateInst = stateClass(self)
            self.stateStack.append((stateName, newStateInst))
            try:
                newStateInst.onEnter() # may not exist
            except:
                pass

    def popState (self, valueAction=None):
        if self.stateStack:
            popStateName, popStateInst = self.stateStack.pop()
            stateName, stateInst = self.getCurrentState()
            try:
                if valueAction:
                    value = valueAction()
                    stateInst.onPopTo(value)
                else:
                    stateInst.onPopTo()
            except:
                pass

    def runMethod (self, method):
        method()

    def helpOnCurrentState (self):
        stateName, stateInst = self.getCurrentState()
        print "HELP (" + stateName + ")"
        for k, v in stateInst.keymap.items():
            print "\t", k, v
        print "STATE STACK:"
        for s in self.stateStack:
            print "\t", s

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



def enable (hotkeySetName="Tomayto", **kwargs):
    try:
        cmds.hotkeySet(hotkeySetName, current=True) # create, fail on existing
    except:
        cmds.hotkeySet(hotkeySetName, edit=True, current=True)
    util.createTomaytoKeymap(**kwargs)


def disable (removeHotkeySet=False, hotkeySetName="Tomayto", **kwargs):
    util.removeTomaytoKeymap(**kwargs)
    cmds.hotkeySet("Maya_Default", edit=True, current=True)

