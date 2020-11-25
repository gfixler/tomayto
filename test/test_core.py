import unittest
from nose.plugins.attrib import attr

from .. import core

try:
    import maya.cmds as cmds
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__


class stateExampleSTART (object):

    def __init__ (self, mainInst):
        pass


class stateSecondState (object):

    def __init__ (self, mainInst):
        pass


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

    def test_pushState_secondStatePushedProperly (self):
        self.tom.pushState(stateSecondState)
        [(cls, inst)] = self.tom.stateStack
        self.assertEquals(cls, stateSecondState)
        self.assertTrue(isinstance(inst, stateSecondState))

