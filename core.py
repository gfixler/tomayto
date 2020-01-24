import maya.cmds as cmds

from . import util


def createTomaytoKeymap (callbackName="tomaytoCB", nameCommandPrefix = "tomayto"):
    """
    Creates Maya nameCommands and hotkeys for the cartesian product of all
    keys, modifiers, and press and release states, pointing them all toward
    a default, global handler. This pointing is done to a default name in
    the global space, as nameCommands are MEL-only, and, as such, are
    difficult (but not impossible) to point to existing Python identifiers.
    This means that a callable of that name must be created in the global space
    to handle the information from the nameCommands.
    """
    cks = cmds.hotkeySet(query=True, current=True)
    for keyChar in util.keyChars :
        for a in [False, True]:
            for c in [False, True]:
                modTag = ("_alt" if a else "") + ("_ctrl" if c else "")
                nameCommandName = nameCommandPrefix + (modTag if modTag else "") + "_" + util.charName(keyChar)

                # Over-escaping required for when callback lines are nested in mel python calls
                if keyChar == '"':
                    keyChar = '\\\\\\\"'
                if keyChar == '\\':
                    keyChar = '\\\\\\\\'

                # press nameCommand
                callback = "python(\"" + callbackName + "(\\\"" + keyChar + "\\\", " + str(a) + ", " + str(c) + ", True)\")"
                cmds.nameCommand( nameCommandName + "_press"
                                , annotation = nameCommandName + "_press"
                                , command = callback
                                )
                print "created", nameCommandName + "_press nameCommand"

                # release nameCommand
                callback = "python(\"" + callbackName + "(\\\"" + keyChar + "\\\", " + str(a) + ", " + str(c) + ", False)\")"
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

def removeTomaytoKeymap (nameCommandPrefix = "tomayto"):
    """
    nameCommands are accessible through Maya's assignCommand, but only by
    index. Deleting one causes all with greater indices to move down to fill
    those indices. This means a group of nameCommands must be deleted from the
    end (the highest indices) to the beginning, which is what this does,
    finding all with the matching prefix, working backwards from the end.
    """
    nameCmdCount = cmds.assignCommand(query=True, numElements=True)
    for i in reversed(xrange(1, nameCmdCount + 1)):
        keyString = cmds.assignCommand(i, query=True, name=True)
        if keyString and keyString.startswith(nameCommandPrefix + "_"):
            cmds.assignCommand(edit=True, delete=i)
            print "deleted", keyString
        else:
            print "preserved", keyString


class Tomayto (object):

    def defaultCB (self, key, alt, ctrl, press):
        """
        This default callback simply prints out the pressed and released keys,
        and modified variants, when assigned to the global callback name. It's
        only intended to check that the nameCommands and hotkeys have been set
        up correctly; normal use is to assign another handler to the global
        callback name.
        """
        if press:
            print "pressed: " + ("alt + " if alt else "") + ("ctrl + " if ctrl else "") + util.charName(key)
        else:
            print "released: " + ("alt + " if alt else "") + ("ctrl + " if ctrl else "") + util.charName(key)

