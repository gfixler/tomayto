try:
    import maya.cmds as cmds
except ImportError:
    print('WARNING (%s): failed to load maya.cmds module.' % __file__)


import math

from . import color as col
from .util import defaultSettings


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
            raise(ValueError, "duplicate values to SelectionList not allowed")
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
        self.scrollLine(False) # HACK to hide extra key letters

    def getScrollIndex (self):
        sliderValue = cmds.intSlider(self.slider, query=True, value=True)
        return len(self.entryVals) - sliderValue

    def getVisibleEntries (self):
        """
        Returns (key, entry val, entry) triple.
        """
        viewHeight = cmds.flowLayout(self.entryFlow, query=True, height=True)
        ix = self.getScrollIndex()
        visVals = self.entryVals[ix:]
        keyPairs = zip(self.settings["selectionKeys"], visVals)
        heights = 0
        n = 0
        results = []
        for k, v in keyPairs:
            entry = self.entries[v]
            h = cmds.text(entry["ui"], query=True, height=True)
            if heights + h > viewHeight:
                break
            results.append((k, v, entry))
            heights = heights + h
            n += 1
        return results

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

    def scrollLine (self, down=True):
        ix = self.getScrollIndex()
        self.scrollToIndex(ix + (1 if down else -1))

    def scrollPage (self, down=True, half=False):
        viewHeight = cmds.flowLayout(self.entryFlow, query=True, height=True)
        ix = self.getScrollIndex()
        n = 0
        heights = 0
        entryVals = self.entryVals[ix:] if down else reversed(self.entryVals[:ix])
        for entryVal in entryVals:
            entry = self.entries[entryVal]
            h = cmds.text(entry["ui"], query=True, height=True)
            if heights + h > (viewHeight / 2 if half else viewHeight):
                break
            heights += h
            n += 1
        self.scrollToIndex(ix + (n if down else -n))

    def scrollToTop (self):
        self.scrollToIndex(0)

    def scrollToBottom (self):
        self.scrollToIndex(len(self.entryVals))

    def highlightEntry (self, entry):
        cmds.text(entry["ui"], edit=True, backgroundColor=self.settings["hlCol"])

    def noHighlightEntry (self, entry):
        cmds.text(entry["ui"], edit=True, backgroundColor=self.settings["bgCol"])

    def toggle (self, key):
        viewHeight = cmds.flowLayout(self.entryFlow, query=True, height=True)
        sldIx = cmds.intSlider(self.slider, query=True, value=True)
        entIx = len(self.entryVals) - sldIx
        visVals = self.entryVals[entIx:]
        keyPairs = zip(self.settings["selectionKeys"], visVals)
        heights = 0
        for k, v in keyPairs:
            entry = self.entries[v]
            h = cmds.text(entry["ui"], query=True, height=True)
            if heights + h > viewHeight:
                break
            heights = heights + h
            if k == key:
                if entry["selected"] == 0:
                    self.highlightEntry(entry)
                    self.selectionIx += 1
                    entry["selected"] = self.selectionIx
                else:
                    self.noHighlightEntry(entry)
                    entry["selected"] = 0

    def toggleVisible (self):
        setToState = False
        for _, _, e in self.getVisibleEntries():
            if e["selected"] == 0:
                setToState = True
                break
        if setToState:
            for k, _, e in self.getVisibleEntries():
                if not e["selected"]:
                    self.toggle(k)
        else:
            for k, _, e in self.getVisibleEntries():
                if e["selected"]:
                    self.toggle(k)

    def showTopPane (self):
        cmds.paneLayout(self.topPane, edit=True, manage=True)

    def hideTopPane (self):
        cmds.paneLayout(self.topPane, edit=True, manage=False)

    def createUI (self):
        self.form = cmds.formLayout(backgroundColor = self.settings["bgCol"])
        self.topPane = cmds.paneLayout()
        self.vimline_form = cmds.formLayout()
        self.vimline_ltxt = cmds.text(label="left")
        self.vimline_ctxt = cmds.text(label="c")
        self.vimline_rtxt = cmds.text(label="right")
        cmds.setParent("..")
        cmds.formLayout(self.vimline_form, edit=True, attachForm=[ (self.vimline_ltxt, "top", 5)
                                                                 , (self.vimline_ltxt, "left", 5)
                                                                 , (self.vimline_ctxt, "top", 5)
                                                                 , (self.vimline_rtxt, "top", 5)
                                                                 , (self.vimline_rtxt, "left", 5)
                                                                 ],
                                                      attachControl=[ (self.vimline_ctxt, "left", 0, self.vimline_ltxt)
                                                                    , (self.vimline_rtxt, "left", 0, self.vimline_ctxt)
                                                                    ] )
        cmds.setParent("..")
        self.keyFlow = cmds.flowLayout( vertical = True
                                      , backgroundColor = self.settings["bgCol"]
                                      )
        cmds.setParent("..")
        self.entryFlow = cmds.flowLayout( vertical = True
                                        , backgroundColor = self.settings["bgCol"]
                                        )
        cmds.setParent("..")
        self.slider = cmds.intSlider(horizontal=False, dragCommand=self.scrollToIndex)
        cmds.formLayout(self.form, edit=True, attachForm=[ (self.keyFlow, "bottom", 0)
                                                         , (self.keyFlow, "left", self.settings["keyLeftPadding"])
                                                         , (self.slider, "bottom", 0)
                                                         , (self.slider, "right", 0)
                                                         , (self.entryFlow, "bottom", 0)
                                                         , (self.topPane, "top", 0)
                                                         , (self.topPane, "left", 0)
                                                         , (self.topPane, "right", 0)
                                                         ],
                                              attachControl=[ (self.entryFlow, "left", self.settings["keyEntryPadding"], self.keyFlow)
                                                            , (self.entryFlow, "right", 0, self.slider)
                                                            , (self.keyFlow, "top", 5, self.topPane)
                                                            , (self.entryFlow, "top", 5, self.topPane)
                                                            , (self.slider, "top", 5, self.topPane)
                                                            ] )
                                                        # , (self.vimline_ltxt, "left", 5)
                                                        # , (self.vimline_ltxt, "top", 5)
                                                        # , (self.vimline_ctxt, "top", 5)
                                                        # , (self.vimline_rtxt, "top", 5)
                                                        # # , (self.vimline_rtxt, "right", 5) # decided not to attach right text to form
                                                        # , (self.vimline_rtxt, "left", 0, self.vimline_ctxt)
                                                        # , (self.vimline_ctxt, "left", 0, self.vimline_ltxt)
        self.hideTopPane()
        self.populateUI()

