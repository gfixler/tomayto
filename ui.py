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
        self.keyEntries = []
        self.settings = settings
        if createUI:
            self.createUI()

    def clearUI (self):
        for entry in self.entries:
            cmds.deleteUI(entry)
        self.entries = []
        for keyEntry in self.keyEntries:
            cmds.deleteUI(keyEntry)
        self.keyEntries = []

    def populateUI (self):
        self.clearUI()
        for key in self.settings["selectionKeys"]:
            keyEntry = cmds.text(label=key, font = self.settings["font"], parent=self.keyFlow)
            self.keyEntries.append(keyEntry)
        for value in self.values:
            entry = cmds.text( label = value
                             , parent = self.entryFlow
                             , align = self.settings["textAlign"]
                             , font = self.settings["font"]
                             , backgroundColor = self.settings["bgCol"]
                             )
            self.entries.append(entry)
        cmds.intSlider(self.slider, edit=True, minValue=1, maxValue=len(self.entries), value=len(self.entries))

    def scrollDown (self):
        viewHeight = cmds.flowLayout(self.entryFlow, query=True, height=True)
        sldIx = cmds.intSlider(self.slider, query=True, value=True)
        entIx = len(self.entries) - sldIx
        n = 0
        heights = 0
        for i in xrange(entIx, len(self.entries)):
            h = cmds.text(self.entries[i], query=True, height=True)
            if heights + h >= viewHeight:
                break
            heights += h
            n += 1
        self.scrollToIndex(sldIx - n + 1)

    # def scrollHalfPage (self, direction="down"):
    #     saHeight = cmds.scrollLayout(self._scroll, query=True, height=True)
    #     pixels = saHeight / self.textHeight / 2 * self.textHeight
    #     cmds.scrollLayout(self._scroll, edit=True, scrollByPixel=(direction, pixels))

    def scrollToIndex (self, index):
        revValue = len(self.entries) - index
        for e in self.entries[:revValue]:
            cmds.control(e, edit=True, manage=False)
        for e in self.entries[revValue:]:
            cmds.control(e, edit=True, manage=True)
        for e in self.keyEntries[:index]:
            cmds.control(e, edit=True, manage=True)
        for e in self.keyEntries[index:]:
            cmds.control(e, edit=True, manage=False)
        cmds.intSlider(self.slider, edit=True, value=index)

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
        self.slider = cmds.intSlider(horizontal=False, dragCommand=self.scrollToIndex)
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

