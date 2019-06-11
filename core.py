import maya.cmds as cmds

from . import util


class Tomayto (object):

    prefix = "tomayto"

    def getch (self, key, alt, ctrl, press):
        if press:
            print "pressed: " + ("alt + " if alt else "") + ("ctrl + " if ctrl else "") + util.charName(key)
        else:
            print "released: " + ("alt + " if alt else "") + ("ctrl + " if ctrl else "") + util.charName(key)

    def createNameCommands (self):
        """
        Generates the cartesian product of all key characters and modifiers,
        and whether then work on press or release, creates nameCommands for
        each, and hooks them up to hotkeys to call (in a badly hardcoded way)
        to the getch method on a blessed instance of the class.
        """
        for keyChar in util.keyChars :
            for a in [False, True]:
                for c in [False, True]:
                    modTag = ("_alt" if a else "") + ("_ctrl" if c else "")
                    nameCommandName = Tomayto.prefix + (modTag if modTag else "") + "_" + util.charName(keyChar)
                    # print keyChar, modTag, nameCommandName
                    if keyChar == '"':
                        keyChar = '\\\\\\\"' # ugh
                    if keyChar == '\\':
                        keyChar = '\\\\\\\\' # ugh
                    # press nameCommand
                    cmds.nameCommand( nameCommandName + "_press"
                                    , annotation = nameCommandName + "_press"
                                    , command = 'python("tomayto.core.tomayto.getch(\\\"' + keyChar + '\\\", ' + str(a) + ', ' + str(c) + ', True)")'
                                    ) # HACK - tomayto.core.tomayto = gross
                    print "created", nameCommandName + "_press nameCommand"
                    # release nameCommand
                    cmds.nameCommand( nameCommandName + "_release"
                                    , annotation = nameCommandName + "_release"
                                    , command = 'python("tomayto.core.tomayto.getch(\\\"' + keyChar + '\\\", ' + str(a) + ', ' + str(c) + ', False)")'
                                    ) # HACK - tomayto.core.tomayto = gross
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


tomayto = Tomayto()

