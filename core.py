try:
    import maya.cmds as cmds
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__


import util


PRESS = True
RELEASE = False

ALT = True
NOALT = False

CTRL = True
NOCTRL = False


fst = lambda (x, _): x
getName = lambda x: x.__name__


def formatEventInfo (event):
    key, alt, ctrl, action = event
    eventStr = ("> " if action else "< ") \
             + ("C-" if ctrl else "") \
             + ("M-" if alt else "") \
             + key
    padToMaxEventLength = lambda x: (x + "    ")[:7] # longest e.g. "> C-M-x"
    return padToMaxEventLength(eventStr)


class Tomayto (object):

    def __init__ (self, startState):
        self.startState = startState
        self.startStateInst = startState(self)
        self.stateStack = [] # start state doesn't go on stack/can't be popped

    def getCurrentState (self):
        if self.stateStack:
            return self.stateStack[-1]
        return (self.startState, self.startStateInst)

    def eventHandler (self, key, alt, ctrl, press):
        state, stateInst = self.getCurrentState()
        event = (key, alt, ctrl, press)
        if event == ('?', True, True, True):
            self.helpOnCurrentState()
            return
        elif hasattr(stateInst, 'keymap'):
            if event in stateInst.keymap.keys():
                eventAction, eventActionData = stateInst.keymap[event]
                if eventAction == "PUSH":
                    self.pushState(eventActionData)
                elif eventAction == "POP":
                    self.popState(eventActionData)
                elif eventAction == "RUN":
                    self.runMethod(eventActionData)

    def pushState (self, stateData):
        try:
            state, stateArgs = stateData
        except:
            stateArgs = []
            state = stateData
        stateInst = state(self, *stateArgs)
        self.stateStack.append((state, stateInst))
        try:
            stateInst.onEnter()
        except:
            pass

    def popState (self, valueAction=None):
        if self.stateStack:
            self.stateStack.pop()
            state, stateInst = self.getCurrentState()
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

    def getCurrentStateInfo (self):
        nltab = "\n    "
        stackLine = "State stack:"
        stackStates = [self.startState] + map(fst, self.stateStack)
        stackStateNames = map(getName, stackStates)
        stackStateLines = nltab + nltab.join(reversed(stackStateNames))
        infoStr = stackLine + stackStateLines + "\n"
        _, inst = self.getCurrentState()
        try:
            eventInfoStr = ""
            for k, v in inst.keymap.items():
                eventStr = "    " + formatEventInfo(k)
                try:
                    action, data = v
                    name = None
                except:
                    action, name, data = v
                actionStr = (action + " ")[:4]
                nameStr = (name if name else str(data))
                eventInfoStr += " - ".join([eventStr, actionStr, nameStr])
            if eventInfoStr:
                infoStr += "\nCurrent state events:\n" + eventInfoStr + "\n"
        except:
            pass
        return infoStr

    def helpOnCurrentState (self):
        state, stateInst = self.getCurrentState()
        print "HELP (" + state.__name__ + ")"
        for k, v in stateInst.keymap.items():
            print "\t", k, v
        print "STATE STACK:"
        for c, i in self.stateStack:
            print "\t", c.__name__, i


def enable (hotkeySetName="Tomayto", **kwargs):
    try:
        cmds.hotkeySet(hotkeySetName, current=True) # create, fail on existing
    except:
        cmds.hotkeySet(hotkeySetName, edit=True, current=True)
    util.createTomaytoKeymap(**kwargs)

def disable (removeHotkeySet=False, hotkeySetName="Tomayto", **kwargs):
    util.removeTomaytoKeymap(**kwargs)
    cmds.hotkeySet("Maya_Default", edit=True, current=True)

