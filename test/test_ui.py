import unittest
from nose.plugins.attrib import attr

from .. import ui


class Test_SelectionList (unittest.TestCase):

    def test_canInstantiateWithNothing (self):
        sl = ui.SelectionList()
        self.assertEquals(sl.entries, [])

    def test_canInstantiateWithList (self):
        testList = ["one", "two", "three", "four", "five"]
        sl = ui.SelectionList(testList)
        self.assertEquals(sl.entries, testList)

