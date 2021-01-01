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
    "keyLeftPadding": 5,
    "keyEntryPadding": 15,
    "selectionKeys": "hfgkdurytielsowanvbpqz473857201cx",
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
        for key in self.settings["selectionKeys"]:
            cmds.text(label=key, font = self.settings["font"], parent=self.keyFlow)
        for value in self.values:
            entry = cmds.text( label = value
                             , parent = self.entryFlow
                             , align = self.settings["textAlign"]
                             , font = self.settings["font"]
                             , backgroundColor = self.settings["bgCol"]
                             )
            self.entries.append(entry)

    # def scrollPage (self, direction="down"):
    #     saHeight = cmds.scrollLayout(self._scroll, query=True, height=True)
    #     pixels = saHeight / self.textHeight * self.textHeight
    #     cmds.scrollLayout(self._scroll, edit=True, scrollByPixel=(direction, pixels))

    # def scrollHalfPage (self, direction="down"):
    #     saHeight = cmds.scrollLayout(self._scroll, query=True, height=True)
    #     pixels = saHeight / self.textHeight / 2 * self.textHeight
    #     cmds.scrollLayout(self._scroll, edit=True, scrollByPixel=(direction, pixels))

    def highlightIndex (self, n):
        if n >= 0 and n < len(self.entries):
            cmds.text(self.entries[n], edit=True, backgroundColor=self.settings["hlCol"])

    def clearHighlightIndex (self, n):
        if n >= 0 and n < len(self.entries):
            cmds.text(self.entries[n], edit=True, backgroundColor=self.settings["bgCol"])

    def createUI (self):
        self.form = cmds.formLayout(backgroundColor = self.settings["bgCol"])
        self.keyFlow = cmds.flowLayout( vertical = True
                                      , backgroundColor = self.settings["bgCol"]
                                      )
        cmds.setParent("..")
        self.entryFlow = cmds.flowLayout( vertical = True
                                        , backgroundColor = self.settings["bgCol"]
                                        )
        cmds.setParent("..")
        self.slider = cmds.intSlider(horizontal=False)
        cmds.formLayout(self.form, edit=True, attachForm=[ (self.keyFlow, "top", 0)
                                                         , (self.keyFlow, "bottom", 0)
                                                         , (self.keyFlow, "left", self.settings["keyLeftPadding"])
                                                         , (self.slider, "top", 0)
                                                         , (self.slider, "bottom", 0)
                                                         , (self.slider, "right", 0)
                                                         , (self.entryFlow, "top", 0)
                                                         , (self.entryFlow, "bottom", 0)
                                                         ],
                                              attachControl=[ (self.entryFlow, "left", self.settings["keyEntryPadding"], self.keyFlow)
                                                            , (self.entryFlow, "right", 0, self.slider)] )
        self.populateUI()

