try:
    import maya.cmds as cmds
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__


import math

import color as col
from util import defaultSettings


SelectionListDefaults = {
    "font": "fixedWidthFont",
    "textAlign": "left",
    "bgCol": col.MayaControlBG,
    "hlCol": col.TextHLBright,
    "fullWidthSelection": False,
}


@defaultSettings(SelectionListDefaults)
class SelectionList (object):

    def __init__ (self, values=[], createUI=True, settings={}):
        self._values = values
        self._entries = []
        self._settings = settings
        if createUI:
            self.createUI()

    def clearUI (self):
        for entry in self._entries:
            cmds.deleteUI(entry)
        self._entries = []

    def populateUI (self):
        self.clearUI()
        for value in self._values:
            entry = cmds.text( label = value
                             , parent = self._form
                             , align = self._settings["textAlign"]
                             , font = self._settings["font"]
                             , backgroundColor = self._settings["bgCol"]
                             )
            if self._settings["fullWidthSelection"]:
                cmds.formLayout(self._form, edit=True, attachForm=[(entry, "left", 0), (entry, "right", 0)])
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

    def highlightIndex (self, n):
        if n >= 0 and n < len(self._entries):
            cmds.text(self._entries[n], edit=True, backgroundColor=self._settings["hlCol"])

    def clearHighlightIndex (self, n):
        if n >= 0 and n < len(self._entries):
            cmds.text(self._entries[n], edit=True, backgroundColor=self._settings["bgCol"])

    def createUI (self):
        self._scroll = cmds.scrollLayout( childResizable = self._settings["fullWidthSelection"]
                                        , backgroundColor = self._settings["bgCol"]
                                        )
        self._form = cmds.formLayout()
        self.populateUI()

