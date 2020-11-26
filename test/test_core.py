import unittest
from nose.plugins.attrib import attr

from .. import core

try:
    import maya.cmds as cmds
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__


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
            ('u', False, False, True): ("PUSH", stateSimple),
            ('e', False, False, True): ("PUSH", stateWithOnEnterCallbackForPushEvent),
            ('a', False, False, True): ("PUSH", (stateFromPushWithArgument, ["Alice"])),
            ('r', True, False, True): ("RUN", self.makeBall),
        }

    def makeBall (self):
        self.ball = cmds.polySphere()


class stateSimple (object):

    def __init__ (self, mainInst):
        pass


class stateFromPushWithArgument (object):

    def __init__ (self, mainInst, name):
        cmds.spaceLocator(name=name)


class stateWithOnEnterCallbackForPushEvent (object):

    def __init__ (self, mainInst):
        pass

    def onEnter (self):
        cmds.spaceLocator(name="onEnterFromPushEventWitnessLocator")


class stateWithOnEnterCallbackForPush (object):

    def __init__ (self, mainInst):
        pass

    def onEnter (self):
        cmds.spaceLocator(name="onEnterFromPushWitnessLocator")


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
        self.tom.eventHandler('u', False, False, True)
        [(cls, inst)] = self.tom.stateStack
        self.assertEquals(cls, stateSimple)
        self.assertTrue(isinstance(inst, stateSimple))

    @attr("maya")
    def test_eventHandler_handlesPushEventWithOnEnterCallback (self):
        self.assertFalse(cmds.objExists("onEnterFromPushEventWitnessLocator"))
        self.tom.eventHandler('e', False, False, True)
        self.assertTrue(cmds.objExists("onEnterFromPushEventWitnessLocator"))

    @attr("maya")
    def test_eventHandler_handlesPushEventWithArgument (self):
        self.assertFalse(cmds.objExists("Alice"))
        self.tom.eventHandler('a', False, False, True)
        self.assertTrue(cmds.objExists("Alice"))

    def test_pushState_secondStatePushedProperly (self):
        self.tom.pushState(stateSimple)
        [(cls, inst)] = self.tom.stateStack
        self.assertEquals(cls, stateSimple)
        self.assertTrue(isinstance(inst, stateSimple))

    @attr("maya")
    def test_pushState_handlesPushWithOnEnterCallback (self):
        self.assertFalse(cmds.objExists("onEnterFromPushWitnessLocator"))
        self.tom.pushState(stateWithOnEnterCallbackForPush)
        [(cls, inst)] = self.tom.stateStack
        self.assertTrue(cmds.objExists("onEnterFromPushWitnessLocator"))

    @attr("maya")
    def test_pushState_handlesPushWithArgument (self):
        self.assertFalse(cmds.objExists("Bob"))
        self.tom.pushState((stateFromPushWithArgument, ["Bob"]))
        self.assertTrue(cmds.objExists("Bob"))

    @attr("maya")
    def test_eventHandler_handlesRunEvent (self):
        self.assertFalse(hasattr(self.tom.startStateInst, "ball"))
        self.tom.eventHandler('r', True, False, True)
        [transform, shape] = self.tom.startStateInst.ball
        self.assertEquals(cmds.objectType(shape), "polySphere")

