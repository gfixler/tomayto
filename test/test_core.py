import unittest

import core


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


class stateForTestingInfoOutput_noEvents (object):

    def __init__ (self, mainInst):
        self.keymap = { }


class stateForTestingInfoOutput_namedPushEvent (object):

    def __init__ (self, mainInst):
        self.keymap = {
            ('p', False, False, True): ("PUSH", "Simple State", stateSimple),
        }


class stateForTestingInfoOutput_namedPushEventWithArgumentForOnEnter (object):

    def __init__ (self, mainInst):
        self.keymap = {
            ('p', False, False, True): ("PUSH", "State w/ Argument", (stateThatAcceptsAnArgument, [42])),
        }


class stateForTestingInfoOutput_namedPopEvent (object):

    def __init__ (self, mainInst):
        self.keymap = {
            ('P', False, False, True): ("POP", "Pop State", None)
        }


class stateForTestingInfoOutput_namedRunEvent (object):

    def __init__ (self, mainInst):
        self.keymap = {
            ('R', False, False, True): ("RUN", "Run State", self.runMethod)
        }

    def runMethod (self):
        pass


class Test_formatEventInfo (unittest.TestCase):

    def test_simpleKeyPress (self):
        result = core.formatEventInfo(('x', False, False, True))
        expected = "> x    "
        self.assertEqual(result, expected)

    def test_simpleKeyRelease (self):
        result = core.formatEventInfo(('q', False, False, False))
        expected = "< q    "
        self.assertEqual(result, expected)

    def test_altKeyPress (self):
        result = core.formatEventInfo(('j', True, False, True))
        expected = "> M-j  "
        self.assertEqual(result, expected)

    def test_altKeyRelease (self):
        result = core.formatEventInfo(('z', True, False, False))
        expected = "< M-z  "
        self.assertEqual(result, expected)

    def test_ctrlKeyPress (self):
        result = core.formatEventInfo(('p', False, True, True))
        expected = "> C-p  "
        self.assertEqual(result, expected)

    def test_ctrlKeyRelease (self):
        result = core.formatEventInfo(('v', False, True, False))
        expected = "< C-v  "
        self.assertEqual(result, expected)

    def test_altCtrlKeyPress (self):
        result = core.formatEventInfo(('w', True, True, True))
        expected = "> C-M-w"
        self.assertEqual(result, expected)

    def test_altCtrlKeyRelease (self):
        result = core.formatEventInfo(('k', True, True, False))
        expected = "< C-M-k"
        self.assertEqual(result, expected)


class Test_Tomayto (unittest.TestCase):

    def setUp (self):
        self.tom = core.Tomayto(stateExampleSTART)

    def test__init__stackStartsOutEmpty (self):
        self.assertEqual(self.tom.stateStack, [])

    def test__init__startStateIsCorrect (self):
        self.assertEqual(self.tom.startState, stateExampleSTART)

    def test__init__startStateInstIsCorrect (self):
        self.assertTrue(isinstance(self.tom.startStateInst, stateExampleSTART))

    def test_getCurrentState_startStateIsCorrect (self):
        result = self.tom.getCurrentState()
        self.assertEqual(result, (self.tom.startState, self.tom.startStateInst))

    def test_eventHandler_stateDoesNotRequireKeymap (self):
        if hasattr(self.tom.startStateInst, 'keymap'):
            delattr(self.tom.startStateInst, 'keymap')
        assert not hasattr(self.tom.startStateInst, 'keymap')
        self.tom.eventHandler('k', False, False, True)

    def test_eventHandler_handlesPushEvent (self):
        self.tom.eventHandler('p', False, False, True)
        [(cls, inst)] = self.tom.stateStack
        self.assertEqual(cls, stateSimple)
        self.assertTrue(isinstance(inst, stateSimple))

    def test_eventHandler_handlesPushEventWithOnEnterCallback (self):
        self.assertRaises(NameError, lambda: varFromOnEnterFromPushEvent)
        self.tom.eventHandler('e', False, False, True)
        self.assertTrue(varFromOnEnterFromPushEvent)

    def test_eventHandler_handlesPushEventWithArgument (self):
        global varFromArgument
        if "varFromArgument" in globals():
            self.assertNotEqual(varFromArgument, "Alice")
        else:
            self.assertRaises(NameError, lambda: varFromArgument)
        self.tom.eventHandler('a', False, False, True)
        self.assertEqual(varFromArgument, "Alice")

    def test_eventHandler_handlesPopEvent (self):
        self.tom.pushState(stateWithPopEvents)
        [(cls, inst)] = self.tom.stateStack
        self.assertEqual(cls, stateWithPopEvents)
        self.tom.eventHandler('p', False, False, True)
        self.assertEqual(self.tom.stateStack, [])

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
        self.assertEqual(cls, stateSimple)
        self.assertTrue(isinstance(inst, stateSimple))

    def test_pushState_handlesPushWithOnEnterCallback (self):
        self.assertRaises(NameError, lambda: varFromOnEnterFromPush)
        self.tom.pushState(stateWithOnEnterCallbackForPush)
        [(cls, inst)] = self.tom.stateStack
        self.assertTrue(varFromOnEnterFromPush)

    def test_pushState_handlesPushWithArgument (self):
        global varFromArgument
        if "varFromArgument" in globals():
            self.assertNotEqual(varFromArgument, "Bob")
        else:
            self.assertRaises(NameError, lambda: varFromArgument)
        self.tom.pushState((stateThatAcceptsAnArgument, ["Bob"]))
        self.assertEqual(varFromArgument, "Bob")

    def test_popState_stateIsPopped (self):
        self.tom.pushState(stateSimple)
        [(cls, inst)] = self.tom.stateStack
        self.assertEqual(cls, stateSimple)
        self.tom.popState()
        self.assertEqual(self.tom.stateStack, [])

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
        self.assertEqual(varFromOnPopToWithArgument, "popCallbackReturnValue")

    def test_getCurrentStateInfo_noEvents (self):
        self.tom.pushState(stateSimple)
        result = self.tom.getCurrentStateInfo()
        expected = \
"""State stack:
    stateSimple
    stateExampleSTART
"""
        self.assertEqual(result, expected)

    def test_getCurrentStateInfo_namedPushEvent (self):
        self.tom.pushState(stateForTestingInfoOutput_namedPushEvent)
        result = self.tom.getCurrentStateInfo()
        expected = \
"""State stack:
    stateForTestingInfoOutput_namedPushEvent
    stateExampleSTART

Current state events:
    > p     - PUSH - Simple State
"""
        self.assertEqual(result, expected)

    def test_getCurrentStateInfo_namedPushEventWithArgumentForOnEnter (self):
        self.tom.pushState(stateForTestingInfoOutput_namedPushEventWithArgumentForOnEnter)
        result = self.tom.getCurrentStateInfo()
        expected = \
"""State stack:
    stateForTestingInfoOutput_namedPushEventWithArgumentForOnEnter
    stateExampleSTART

Current state events:
    > p     - PUSH - State w/ Argument
"""
        self.assertEqual(result, expected)

    def test_getCurrentStateInfo_namedPopEvent (self):
        self.tom.pushState(stateForTestingInfoOutput_namedPopEvent)
        result = self.tom.getCurrentStateInfo()
        expected = \
"""State stack:
    stateForTestingInfoOutput_namedPopEvent
    stateExampleSTART

Current state events:
    > P     - POP  - Pop State
"""
        self.assertEqual(result, expected)

    def test_getCurrentStateInfo_namedRunEvent (self):
        self.tom.pushState(stateForTestingInfoOutput_namedRunEvent)
        result = self.tom.getCurrentStateInfo()
        expected = \
"""State stack:
    stateForTestingInfoOutput_namedRunEvent
    stateExampleSTART

Current state events:
    > R     - RUN  - Run State
"""
        self.assertEqual(result, expected)

