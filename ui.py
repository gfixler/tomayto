try:
    import maya.cmds as cmds
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__


class SelectionList (object):

    def __init__ (self, values=[], createUI=True):
        self._values = values
        self._entries = []
        if createUI:
            self.createUI()

    def populateUI (self):
        self._entries = []
        labels = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890"
        for label, value in zip(labels, self._values):
            l = cmds.text(label=label, parent=self._form)
            t = cmds.text(label=value, parent=self._form)
            self._entries.append((l, t))
        if self._entries:
            label, text = self._entries[0]
            self.textHeight = cmds.text(text, query=True, height=True)
            for (tlab, top), (blab, bot) in zip(self._entries, self._entries[1:]):
                cmds.formLayout(self._form, edit=True, attachControl=[(top, "top", 0, bot)])
                cmds.formLayout(self._form, edit=True, attachControl=[(blab, "top", 0, tlab)])
            for label, text in self._entries:
                cmds.formLayout(self._form, edit=True, attachControl=[(text, "left", 5, label)])

    def createUI (self):
        self._scroll = cmds.scrollLayout()
        self._form = cmds.formLayout()
        self.populateUI()

