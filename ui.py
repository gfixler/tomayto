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
        if len(values) != len(set(values)):
            raise ValueError, "duplicate values to SelectionList not allowed"
        self.values = values
        self.entries = []
        self.keyEntries = []
        self.settings = settings
        if createUI:
            self.createUI()

    def clearUI (self):
        for _, entry in self.entries:
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
            self.entries.append((False, entry))
        cmds.intSlider(self.slider, edit=True, minValue=1, maxValue=len(self.entries), value=len(self.entries))

    def scrollDown (self):
        viewHeight = cmds.flowLayout(self.entryFlow, query=True, height=True)
        sldIx = cmds.intSlider(self.slider, query=True, value=True)
        entIx = len(self.entries) - sldIx
        n = 0
        heights = 0
        for i in xrange(entIx, len(self.entries)):
            _, entry = self.entries[i]
            h = cmds.text(entry, query=True, height=True)
            if heights + h >= viewHeight:
                break
            heights += h
            n += 1
        self.scrollToIndex(sldIx - n + 1)

    def scrollUp (self):
        viewHeight = cmds.flowLayout(self.entryFlow, query=True, height=True)
        sldIx = cmds.intSlider(self.slider, query=True, value=True)
        entIx = len(self.entries) - sldIx
        n = 0
        heights = 0
        for i in reversed(xrange(0, entIx)):
            _, entry = self.entries[i]
            h = cmds.text(entry, query=True, height=True)
            heights += h
            n += 1
            if heights + h > viewHeight:
                break
        self.scrollToIndex(sldIx + n)

    def scrollToIndex (self, index):
        revValue = len(self.entries) - index
        for _, e in self.entries[:revValue]:
            cmds.control(e, edit=True, manage=False)
        for _, e in self.entries[revValue:]:
            cmds.control(e, edit=True, manage=True)
        for k in self.keyEntries[:index]:
            cmds.control(k, edit=True, manage=True)
        for k in self.keyEntries[index:]:
            cmds.control(k, edit=True, manage=False)
        cmds.intSlider(self.slider, edit=True, value=index)

    def highlightIndex (self, i):
        if i >= 0 and i < len(self.entries):
            _, entry = self.entries[i]
            cmds.text(entry, edit=True, backgroundColor=self.settings["hlCol"])

    def clearHighlightIndex (self, i):
        if i >= 0 and i < len(self.entries):
            _, entry = self.entries[i]
            cmds.text(entry, edit=True, backgroundColor=self.settings["bgCol"])

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

