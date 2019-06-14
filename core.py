import maya.cmds as cmds

from . import util


def say (msg):
    print msg

def makeStateSetter (inst):
    def stateSetter (state):
        inst.state = state
    return stateSetter

class Tomayto (object):

    nameCommandPrefix = "tomayto"

    def tempWin (self):
        self.win = cmds.window()
        cmds.showWindow()

    def noTempWin (self):
        cmds.deleteUI(self.win)

    def __init__ (self, callbackName="tomaytoCB"):
        self.callbackName = callbackName
        self.state = "idle"
        toState = makeStateSetter(self)
        self.states = {
            "idle": {
                ("l", False, False, True): lambda: toState("list"),
                ("l", False, True, True): lambda: cmds.scriptEditorInfo(clearHistory=True),
                ("w", False, False, True): lambda: self.tempWin(),
                ("w", False, False, False): lambda: self.noTempWin(),
            },
            "list": {
                ("j", False, False, True): lambda: [say(cmds.ls(type="joint")), toState("idle")],
                ("m", False, False, True): lambda: [say(cmds.ls(type="mesh")), toState("idle")],
                ("l", False, False, True): lambda: [say(cmds.ls(type="locator")), toState("idle")],
                ("c", False, False, True): lambda: [say(cmds.ls(type="nurbsCurve")), toState("idle")],
            },
        }

    def getch (self, key, alt, ctrl, press):
        k = (key, alt, ctrl, press)
        try:
            f = self.states[self.state][k]
            f()
        except:
            pass
        # if press:
        #     print "pressed: " + ("alt + " if alt else "") + ("ctrl + " if ctrl else "") + util.charName(key)
        # else:
        #     print "released: " + ("alt + " if alt else "") + ("ctrl + " if ctrl else "") + util.charName(key)

    def createNameCommands (self):
        """
        Generates cartesian product of all key characters and modifiers,
        for press and release states, creates nameCommands for each that call
        to a passed or default callback name (by string), and creates hotkeys.
        """
        for keyChar in util.keyChars :
            for a in [False, True]:
                for c in [False, True]:
                    modTag = ("_alt" if a else "") + ("_ctrl" if c else "")
                    nameCommandName = Tomayto.nameCommandPrefix + (modTag if modTag else "") + "_" + util.charName(keyChar)

                    # Over-escaping required for when callback lines are nested in mel python calls
                    if keyChar == '"':
                        keyChar = '\\\\\\\"'
                    if keyChar == '\\':
                        keyChar = '\\\\\\\\'

                    # press nameCommand
                    callback = "python(\"" + self.callbackName + "(\\\"" + keyChar + "\\\", " + str(a) + ", " + str(c) + ", True)\")"
                    cmds.nameCommand( nameCommandName + "_press"
                                    , annotation = nameCommandName + "_press"
                                    , command = callback
                                    )
                    print "created", nameCommandName + "_press nameCommand"

                    # release nameCommand
                    callback = "python(\"" + self.callbackName + "(\\\"" + keyChar + "\\\", " + str(a) + ", " + str(c) + ", False)\")"
                    cmds.nameCommand( nameCommandName + "_release"
                                    , annotation = nameCommandName + "_release"
                                    , command = callback
                                    )
                    print "created", nameCommandName + "_release nameCommand"

                    # hotkey for both press and release nameCommands
                    cmds.hotkey( keyShortcut = keyChar
                               , name = nameCommandName + "_press"
                               , releaseName = nameCommandName + "_release"
                               , altModifier = a
                               , ctrlModifier = c
                               )
                    print "created", nameCommandName, " press/release hotkey"

    def clearNameCommands (self):
        """
        nameCommands are accessible through assignCommand, but only by index.
        Deleting one causes all with greater indices to move down to fill those
        indices. This means a group of nameCommands must be deleted from the
        end (the highest indices) to the beginning, which is what this does,
        finding all with the matching prefix, working backwards from the end.
        """
        nameCmdCount = cmds.assignCommand(query=True, numElements=True)
        for i in reversed(xrange(1, nameCmdCount + 1)):
            keyString = cmds.assignCommand(i, query=True, name=True)
            if keyString and keyString.startswith("tomayto_"):
                cmds.assignCommand(edit=True, delete=i)
                print "deleted", keyString
            else:
                print "preserved", keyString

