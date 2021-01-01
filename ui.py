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
        self.values = values
        self.entries = []
        self.settings = settings
        if createUI:
            self.createUI()

    def clearUI (self):
        for entry in self.entries:
            cmds.deleteUI(entry)
        self.entries = []

    def populateUI (self):
        self.clearUI()
        for value in self.values:
            entry = cmds.text( label = value
                             , parent = self.form
                             , align = self.settings["textAlign"]
                             , font = self.settings["font"]
                             , backgroundColor = self.settings["bgCol"]
                             )
            if self.settings["fullWidthSelection"]:
                cmds.formLayout(self.form, edit=True, attachForm=[(entry, "left", 0), (entry, "right", 0)])
            self.entries.append(entry)
        if self.entries:
            for top, bot in zip(self.entries, self.entries[1:]):
                cmds.formLayout(self.form, edit=True, attachControl=[(bot, "top", 0, top)])
        cmds.evalDeferred(self.extractTextHeight)

    def extractTextHeight (self):
        text = self.entries[0]
        self.textHeight = cmds.text(text, query=True, height=True)

    def scrollPage (self, direction="down"):
        saHeight = cmds.scrollLayout(self.scroll, query=True, height=True)
        pixels = saHeight / self.textHeight * self.textHeight
        cmds.scrollLayout(self.scroll, edit=True, scrollByPixel=(direction, pixels))

    def scrollHalfPage (self, direction="down"):
        saHeight = cmds.scrollLayout(self.scroll, query=True, height=True)
        pixels = saHeight / self.textHeight / 2 * self.textHeight
        cmds.scrollLayout(self.scroll, edit=True, scrollByPixel=(direction, pixels))

    def highlightIndex (self, n):
        if n >= 0 and n < len(self.entries):
            cmds.text(self.entries[n], edit=True, backgroundColor=self.settings["hlCol"])

    def clearHighlightIndex (self, n):
        if n >= 0 and n < len(self.entries):
            cmds.text(self.entries[n], edit=True, backgroundColor=self.settings["bgCol"])

    def createUI (self):
        self.scroll = cmds.scrollLayout( childResizable = self.settings["fullWidthSelection"]
                                        , backgroundColor = self.settings["bgCol"]
                                        )
        self.form = cmds.formLayout()
        self.populateUI()

