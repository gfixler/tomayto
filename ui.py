try:
    import maya.cmds as cmds
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__

import math


class SelectionList (object):

    def __init__ (self, values=[], createUI=True, font="fixedWidthFont"):
        self._values = values
        self._entries = []
        if createUI:
            self.createUI()

    def populateUI (self):
        self._entries = []
        for value in self._values:
            entry = cmds.text(label=value, parent=self._form)
            self._entries.append(entry)
        if self._entries:
            for top, bot in zip(self._entries, self._entries[1:]):
                cmds.formLayout(self._form, edit=True, attachControl=[(bot, "top", 0, top)])
        cmds.evalDeferred(self.extractTextHeight)

    def extractTextHeight (self):
        text = self._entries[0]
        self.textHeight = cmds.text(text, query=True, height=True)

    def scrollPage (self, direction="down"):
        saHeight = cmds.scrollLayout(self._scroll, query=True, height=True)
        pixels = saHeight / self.textHeight * self.textHeight
        cmds.scrollLayout(self._scroll, edit=True, scrollByPixel=(direction, pixels))

    def scrollHalfPage (self, direction="down"):
        saHeight = cmds.scrollLayout(self._scroll, query=True, height=True)
        pixels = saHeight / self.textHeight / 2 * self.textHeight
        cmds.scrollLayout(self._scroll, edit=True, scrollByPixel=(direction, pixels))

    def createUI (self):
        self._scroll = cmds.scrollLayout()
        self._form = cmds.formLayout()
        self.populateUI()

