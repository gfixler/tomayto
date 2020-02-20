import maya.cmds as cmds

import util


class Tomayto (object):

    def __init__ (self, statesMap, startStateName):
        """
        Each state must be a class with an init that accepts a reference to the
        instance of this class that instantiates it. Each instance should store
        the ref for use in communicating with it later.
        "statesMap" is a dict of name:state pairs of state class references.
        "startStateName" is the string key of the starting state in statesMap.
        """
        self.statesMap = statesMap
        self.startStateName = startStateName
        self.startState = statesMap[startStateName](self) # init start state
        self.stateStack = [] # start state doesn't go on stack/can't be popped
        self.overrides = {}
        self.state = None

    def currentState (self):
        if self.stateStack:
            return self.stateStack[-1]
        return (self.startStateName, self.startState)

    def eventHandler (self, key, alt, ctrl, press):
        stateName, state = self.currentState()
        event = (key, alt, ctrl, press)
        overrideKey = (stateName, event)
        if overrideKey in self.overrides:
            self.eventHandler(self.overrides[overrideKey])
            return
        if self.state == "REBIND1":
            if press:
                return
            self.rebindSource = event
            self.state = "REBIND2"
        elif self.state == "REBIND2":
            if press:
                return
            self.rebindTarget = event
            self.overrides[(stateName, self.rebindSource)] = self.rebindTarget
            self.state = None
        # rebind
        elif event == ('K', True, True, False):
            self.state = "REBIND1"
        # help
        elif event == ('?', False, False, True):
            self.helpOnCurrentState()
            return
        #everything else
        elif event in state.keymap.keys():
            eventAction, eventActionData = state.keymap[event]
            if eventAction == "PUSH":
                self.pushState(eventActionData)
            elif eventAction == "POP":
                self.popState(eventActionData)
            elif eventAction == "RUN":
                self.runMethod(eventActionData)

    def pushState (self, stateName):
        if stateName in self.statesMap:
            stateClass = self.statesMap[stateName]
            newState = stateClass(self)
            self.stateStack.append((stateName, newState))
            try:
                newState.onEnter() # may not exist
            except:
                pass

    def popState (self, valueAction=None):
        if self.stateStack:
            popStateName, popState = self.stateStack.pop()
            stateName, state = self.currentState()
            try:
                if valueAction:
                    value = valueAction()
                    state.onPopTo(value)
                else:
                    state.onPopTo()
            except:
                pass

    def runMethod (self, methodName):
        methodName()

    def helpOnCurrentState (self):
        stateName, state = self.currentState()
        print "HELP (" + stateName + ")"
        for k, v in state.keymap.items():
            print k, v

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

