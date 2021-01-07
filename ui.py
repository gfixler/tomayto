try:
    import maya.cmds as cmds
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__


import math

import color as col
from util import defaultSettings


ident = lambda x: x


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

    def __init__ (self, values=[], createUI=True, filtF=ident, sortF=ident, settings={}):
        if len(values) != len(set(values)):
            raise ValueError, "duplicate values to SelectionList not allowed"
        self.values = values
        self.entries = dict([(value, {"selected": 0}) for value in values])
        self.keyEntries = []
        self.filtF = filtF
        self.sortF = sortF
        self.settings = settings
        self.selectionIx = 0
        if createUI:
            self.createUI()

    def clearUI (self):
        for entry in self.entries.values():
            if "ui" in entry:
                cmds.deleteUI(entry["ui"])
                del entry["ui"]
        for keyEntry in self.keyEntries:
            cmds.deleteUI(keyEntry)
        self.keyEntries = []

    def populateUI (self):
        self.clearUI()
        self.entryVals = sorted(filter(self.filtF, self.values), key=self.sortF)
        for key in self.settings["selectionKeys"]:
            keyEntry = cmds.text(label=key, font = self.settings["font"], parent=self.keyFlow)
            self.keyEntries.append(keyEntry)
        for entryVal in self.entryVals:
            ui = cmds.text( label = entryVal
                          , parent = self.entryFlow
                          , align = self.settings["textAlign"]
                          , font = self.settings["font"]
                          , backgroundColor = self.settings["bgCol"]
                          )
            entry = self.entries[entryVal]
            entry["ui"] = ui
            if entry["selected"] > 0:
                self.highlightEntry(entry)
        cmds.intSlider(self.slider, edit=True, minValue=1, maxValue=len(self.entryVals), value=len(self.entryVals))
        self.scrollLineUp() # HACK to hide extra key letters

    def toggle (self, key):
        sldIx = cmds.intSlider(self.slider, query=True, value=True)
        entIx = len(self.entryVals) - sldIx
        visVals = self.entryVals[entIx:]
        keyPairs = zip(self.settings["selectionKeys"], visVals)
        for k, v in keyPairs:
            if k == key:
                e = self.entries[v]
                if e["selected"] == 0:
                    self.highlightEntry(e)
                    self.selectionIx += 1
                    e["selected"] = self.selectionIx
                else:
                    self.noHighlightEntry(e)
                    e["selected"] = 0

    def getScrollIndex (self):
        sliderValue = cmds.intSlider(self.slider, query=True, value=True)
        return len(self.entryVals) - sliderValue

    def scrollPageDown (self):
        viewHeight = cmds.flowLayout(self.entryFlow, query=True, height=True)
        ix = self.getScrollIndex()
        n = 0
        heights = 0
        for entryVal in self.entryVals[ix:]:
            entry = self.entries[entryVal]
            h = cmds.text(entry["ui"], query=True, height=True)
            if heights + h > viewHeight:
                break
            heights += h
            n += 1
        self.scrollToIndex(ix + n)

    def scrollPageUp (self):
        viewHeight = cmds.flowLayout(self.entryFlow, query=True, height=True)
        ix = self.getScrollIndex()
        n = 0
        heights = 0
        for entryVal in reversed(self.entryVals[:ix]):
            entry = self.entries[entryVal]
            h = cmds.text(entry["ui"], query=True, height=True)
            heights += h
            n += 1
            if heights + h > viewHeight:
                break
        self.scrollToIndex(ix - n)

    def scrollToIndex (self, index):
        n = cmds.intSlider(self.slider, query=True, maxValue=True)
        index = max(0, min(index, n-1))
        for v in self.entryVals[:index]:
            cmds.control(self.entries[v]["ui"], edit=True, manage=False)
        for v in self.entryVals[index:]:
            cmds.control(self.entries[v]["ui"], edit=True, manage=True)
        revValue = len(self.entryVals) - index
        for k in self.keyEntries[:revValue]:
            cmds.control(k, edit=True, manage=True)
        for k in self.keyEntries[revValue:]:
            cmds.control(k, edit=True, manage=False)
        cmds.intSlider(self.slider, edit=True, value=revValue)

    def highlightEntry (self, entry):
        cmds.text(entry["ui"], edit=True, backgroundColor=self.settings["hlCol"])

    def noHighlightEntry (self, entry):
        cmds.text(entry["ui"], edit=True, backgroundColor=self.settings["bgCol"])

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

