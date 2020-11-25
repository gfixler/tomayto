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


class Test_Tomayto (unittest.TestCase):

    def setUp (self):
        self.tom = core.Tomayto(stateExampleSTART)

    def test__init__stackStartsOutEmpty (self):
        self.assertEquals(self.tom.stateStack, [])

    def test__init__startStateIsCorrect (self):
        self.assertEquals(self.tom.startState, stateExampleSTART)

    def test__init__startStateInstIsCorrect (self):
        self.assertTrue(isinstance(self.tom.startStateInst, stateExampleSTART))

