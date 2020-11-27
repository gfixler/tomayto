import unittest
from nose.plugins.attrib import attr

from .. import core


"""
NOTE: SOME RULES I'M FOLLOWING IN TESTING STATE STUFF:

    1. TRY TO ISOLATE PATHWAYS
        Don't reuse test states for a bunch of things; let them all be unique,
        so we don't end up testing, and thus debugging, their interactions.

    2. KEEP EVENTS CONSISTENT
        Don't mix around the ALT/CTRL/PRESS booleans just for the sake of it,
        unless those are the things you're testing. Almost all of the events
        should be like: (<letter>, False, False, True) - i.e. a letter, with no
        mods, that matches/triggers on key press.

    3. TRY TO MAKE EVENT LETTERS MEANINGFUL
        It's a bit easier to follow, and find related bits, while testing the
        run event handler, if the event key is 'r', not a randomly chosen key.
"""

class stateExampleSTART (object):

    def __init__ (self, mainInst):
        self.keymap = {
            ('p', False, False, True): ("PUSH", stateSimple),
            ('e', False, False, True): ("PUSH", stateWithOnEnterCallbackForPushEvent),
            ('a', False, False, True): ("PUSH", (stateThatAcceptsAnArgument, ["Alice"])),
            ('r', True, False, True): ("RUN", self.runFromEvent),
        }

    def runFromEvent (self):
        global varFromRunEvent
        varFromRunEvent = True


class stateSimple (object):

    def __init__ (self, mainInst):
        pass


class stateWithOnEnterCallbackForPushEvent (object):

    def __init__ (self, mainInst):
        pass

    def onEnter (self):
        global varFromOnEnterFromPushEvent
        varFromOnEnterFromPushEvent = True


class stateWithOnEnterCallbackForPush (object):

    def __init__ (self, mainInst):
        pass

    def onEnter (self):
        global varFromOnEnterFromPush
        varFromOnEnterFromPush = True


class stateThatAcceptsAnArgument (object):

    def __init__ (self, mainInst, name):
        global varFromArgument
        varFromArgument = name


class stateWithOnPopToCallback (object):

    def __init__ (self, mainInst):
        pass

    def onPopTo (self):
        global varFromOnPopTo
        varFromOnPopTo = True


class stateWithOnPopToCallbackWithArgument (object):

    def __init__ (self, mainInst):
        pass

    def onPopTo (self, argument):
        global varFromOnPopToWithArgument
        varFromOnPopToWithArgument = argument


class stateWithPopEvents (object):

    def __init__ (self, mainInst):
        self.keymap = {
            ('p', False, False, True): ("POP", None),
            ('P', False, False, True): ("POP", self.popCallback),
        }

    def popCallback (self):
        global varFromPopCallback
        varFromPopCallback = True
        return "popCallbackReturnValue"


class stateForTestingHelpOutput_noEvents (object):

    def __init__ (self, mainInst):
        self.keymap = { }


class Test_Tomayto (unittest.TestCase):

    def setUp (self):
        self.tom = core.Tomayto(stateExampleSTART)

    def test__init__stackStartsOutEmpty (self):
        self.assertEquals(self.tom.stateStack, [])

    def test__init__startStateIsCorrect (self):
        self.assertEquals(self.tom.startState, stateExampleSTART)

    def test__init__startStateInstIsCorrect (self):
        self.assertTrue(isinstance(self.tom.startStateInst, stateExampleSTART))

    def test_getCurrentState_startStateIsCorrect (self):
        result = self.tom.getCurrentState()
        self.assertEquals(result, (self.tom.startState, self.tom.startStateInst))

    def test_eventHandler_stateDoesNotRequireKeymap (self):
        if hasattr(self.tom.startStateInst, 'keymap'):
            delattr(self.tom.startStateInst, 'keymap')
        assert not hasattr(self.tom.startStateInst, 'keymap')
        self.tom.eventHandler('k', False, False, True)

    def test_eventHandler_handlesPushEvent (self):
        self.tom.eventHandler('p', False, False, True)
        [(cls, inst)] = self.tom.stateStack
        self.assertEquals(cls, stateSimple)
        self.assertTrue(isinstance(inst, stateSimple))

    def test_eventHandler_handlesPushEventWithOnEnterCallback (self):
        self.assertRaises(NameError, lambda: varFromOnEnterFromPushEvent)
        self.tom.eventHandler('e', False, False, True)
        self.assertTrue(varFromOnEnterFromPushEvent)

    def test_eventHandler_handlesPushEventWithArgument (self):
        global varFromArgument
        if "varFromArgument" in globals():
            self.assertNotEquals(varFromArgument, "Alice")
        else:
            self.assertRaises(NameError, lambda: varFromArgument)
        self.tom.eventHandler('a', False, False, True)
        self.assertEquals(varFromArgument, "Alice")

    def test_eventHandler_handlesPopEvent (self):
        self.tom.pushState(stateWithPopEvents)
        [(cls, inst)] = self.tom.stateStack
        self.assertEquals(cls, stateWithPopEvents)
        self.tom.eventHandler('p', False, False, True)
        self.assertEquals(self.tom.stateStack, [])

    def test_eventHandler_handlesLocalPopCallback (self):
        self.tom.pushState(stateWithPopEvents)
        self.assertRaises(NameError, lambda: varFromPopCallback)
        self.tom.eventHandler('P', False, False, True)
        self.assertTrue(varFromPopCallback)

    def test_eventHandler_handlesRunEvent (self):
        global varFromRunEvent
        self.assertRaises(NameError, lambda: varFromRunEvent)
        self.tom.eventHandler('r', True, False, True)
        self.assertTrue(varFromRunEvent)

    def test_pushState_stateIsPushedProperly (self):
        self.tom.pushState(stateSimple)
        [(cls, inst)] = self.tom.stateStack
        self.assertEquals(cls, stateSimple)
        self.assertTrue(isinstance(inst, stateSimple))

    def test_pushState_handlesPushWithOnEnterCallback (self):
        self.assertRaises(NameError, lambda: varFromOnEnterFromPush)
        self.tom.pushState(stateWithOnEnterCallbackForPush)
        [(cls, inst)] = self.tom.stateStack
        self.assertTrue(varFromOnEnterFromPush)

    def test_pushState_handlesPushWithArgument (self):
        global varFromArgument
        if "varFromArgument" in globals():
            self.assertNotEquals(varFromArgument, "Bob")
        else:
            self.assertRaises(NameError, lambda: varFromArgument)
        self.tom.pushState((stateThatAcceptsAnArgument, ["Bob"]))
        self.assertEquals(varFromArgument, "Bob")

    def test_popState_stateIsPopped (self):
        self.tom.pushState(stateSimple)
        [(cls, inst)] = self.tom.stateStack
        self.assertEquals(cls, stateSimple)
        self.tom.popState()
        self.assertEquals(self.tom.stateStack, [])

    def test_popState_onPopToCallbackIsCalled (self):
        self.tom.pushState(stateWithOnPopToCallback)
        self.tom.pushState(stateWithPopEvents)
        global varFromOnPopTo
        self.assertRaises(NameError, lambda: varFromOnPopTo)
        self.tom.popState()
        self.assertTrue(varFromOnPopTo)

    def test_popState_onPopToCallbackCanReceiveArgument (self):
        self.tom.pushState(stateWithOnPopToCallbackWithArgument)
        self.tom.pushState(stateWithPopEvents)
        global varFromOnPopToWithArgument
        self.assertRaises(NameError, lambda: varFromOnPopToWithArgument)
        [_, (__, inst)] = self.tom.stateStack
        self.tom.popState(inst.popCallback)
        self.assertEquals(varFromOnPopToWithArgument, "popCallbackReturnValue")

    def test_getCurrentStateInfo_noEvents (self):
        self.tom.pushState(stateSimple)
        result = self.tom.getCurrentStateInfo()
        expected = \
"""State stack:
    stateSimple
    stateExampleSTART
"""
        self.assertEquals(result, expected)

