import unittest

import ui


class Test_SelectionList (unittest.TestCase):

    def test_canInstantiateWithNothing (self):
        sl = ui.SelectionList(createUI=False)
        self.assertEqual(sl.values, [])

    def test_canInstantiateWithList (self):
        testList = ["one", "two", "three", "four", "five"]
        sl = ui.SelectionList(testList, createUI=False)
        self.assertEqual(sl.values, testList)

