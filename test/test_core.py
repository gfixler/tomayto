import unittest
from nose.plugins.attrib import attr

from .. import core

try:
    import maya.cmds as cmds
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__


class stateExampleSTART (object):

    def __init__ (self, mainInst):
        self.keymap = {
            ('x', True, False, True): ("RUN", self.makeBall),
            ('p', False, False, True): ("PUSH", stateSecondState),
            ('o', False, False, True): ("PUSH", stateOnEnterWitness),
            ('a', False, False, True): ("PUSH", (stateFromArgument, ["Alice"])),
        }

    def makeBall (self):
        self.ball = cmds.polySphere()[0]


class stateSecondState (object):

    def __init__ (self, mainInst):
        pass


class stateFromArgument (object):

    def __init__ (self, mainInst, name):
        cmds.spaceLocator(name=name)


class stateOnEnterWitness (object):

    def __init__ (self, mainInst):
        cmds.spaceLocator(name="onEnterWitnessLocator")


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
        self.tom.eventHandler('q', False, False, True)

    @attr("maya")
    def test_eventHandler_handlesRunEvent (self):
        self.assertFalse(hasattr(self.tom.startStateInst, "ball"))
        self.tom.eventHandler('x', True, False, True)
        self.assertTrue(cmds.objExists(self.tom.startStateInst.ball))

    def test_eventHandler_handlesPushEvent (self):
        self.tom.eventHandler('p', False, False, True)
        [(cls, inst)] = self.tom.stateStack
        self.assertEquals(cls, stateSecondState)
        self.assertTrue(isinstance(inst, stateSecondState))

    @attr("maya")
    def test_eventHandler_handlesPushEventWithOnEnterCallback (self):
        self.tom.eventHandler('o', False, False, True)
        [(cls, inst)] = self.tom.stateStack
        self.assertTrue(cmds.objExists("onEnterWitnessLocator"))

    @attr("maya")
    def test_eventHandler_handlesPushEventWithArgument (self):
        self.tom.eventHandler('a', False, False, True)
        self.assertTrue(cmds.objectType("Alice"), "locator")

    def test_pushState_secondStatePushedProperly (self):
        self.tom.pushState(stateSecondState)
        [(cls, inst)] = self.tom.stateStack
        self.assertEquals(cls, stateSecondState)
        self.assertTrue(isinstance(inst, stateSecondState))

    @attr("maya")
    def test_pushState_handlesPushEventWithOnEnterCallback (self):
        self.tom.pushState(stateOnEnterWitness)
        [(cls, inst)] = self.tom.stateStack
        self.assertTrue(cmds.objExists("onEnterWitnessLocator"))

    @attr("maya")
    def test_pushState_handlesPushEventWithArgument (self):
        self.tom.pushState((stateFromArgument, ["Alice"]))
        self.assertTrue(cmds.objectType("Alice"), "locator")

