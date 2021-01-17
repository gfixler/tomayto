try:
    import maya.cmds as cmds
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__

try:
    import maya.mel as mel
except ImportError:
    print 'WARNING (%s): failed to load maya.mel module.' % __file__


import os


# for use in naming nameCommands (they can't have punctuation in their names)
keyNames = { ';': "semicolon"
           , ':': "colon"
           , "'": "singleQuote"
           , '"': "doubleQuote"
           , '`': "graveAccent"
           , '~': "tilde"
           , '!': "exclamationMark"
           , '@': "atSign"
           , '#': "octothorpe"
           , '$': "dollarSign"
           , '%': "percentSign"
           , '^': "caret"
           , '&': "ampersand"
           , '*': "asterisk"
           , '(': "leftParen"
           , ')': "rightParen"
           , '[': "openSquareBracket"
           , ']': "closeSquareBracket"
           , '{': "openCurlyBrace"
           , '}': "closeCurlyBrace"
           , '<': "lessThanSymbol"
           , '>': "greaterThanSymbol"
           , '-': "minusSign"
           , '_': "underscore"
           , '=': "equalsSign"
           , '+': "plusSign"
           , ',': "comma"
           , '.': "period"
           , '\\': "backslash"
           , '/': "slash"
           , '?': "questionMark"
           , '|': "pipe"
           , ' ': "space"
           }

keyChars = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
specialKeys = ["Up", "Down", "Left", "Right", "Home", "End", "Page_Down", "Page_Up", "Insert", "Return", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]

keys = list(keyChars) # break char string into individual strings, one per key
allKeys = keys + specialKeys

# convert single character into usable key name for naming purposes
keyName = lambda c: keyNames[c] if c in keyNames else c


def listNameCommands ():
    # from code example at bottom of this page:
    # from http://help.autodesk.com/cloudhelp/2018/ENU/Maya-Tech-Docs/CommandsPython/assignCommand.html
    count = cmds.assignCommand(query=True, numElements=True)

    print ('There are ' + str(count) + ' named command objects.')

    for index in range(1, count+1):

        keyString = cmds.assignCommand(index, query=True, keyString=True)

        if  0 < len(keyString) and keyString[0] != "NONE":
            output = '('

            if "1" == keyString[2]: output += 'Ctrl+'
            if "1" == keyString[1]: output += 'Alt+'
            if "1" == keyString[5]: output += 'Command+'

            output += keyString[0]

            if "1" == keyString[3]: output += ' Release'
            if "1" == keyString[4]: output += ' KeyRepeat'

            output += ')'

            print index, cmds.assignCommand(index, query=True, name=True), output


def listHotkeySets ():
    print cmds.hotkeySet(query=True, hotkeySetArray=True)

def currentHotkeySet ():
    return cmds.hotkeySet(query=True, current=True)

def createTomaytoKeymap (callbackName="tomaytoCB", nameCommandPrefix="tomayto", **kwargs):
    """
    Creates Maya nameCommands and hotkeys for the cartesian product of all
    keys, modifiers, and press and release states, pointing them all toward
    a default, global handler. This pointing is done to a default name in
    the global space, as nameCommands are MEL-only, and, as such, are
    difficult (but not impossible) to point to existing Python identifiers.
    This means that a callable of that name must be created in the global space
    to handle the information from the nameCommands.
    """
    for key in allKeys:
        for a in [False, True]:
            for c in [False, True]:
                modTag = ("_alt" if a else "") + ("_ctrl" if c else "")
                nameCommandName = nameCommandPrefix + (modTag if modTag else "") + "_" + keyName(key)

                # Over-escaping required when callback commands are created by mel python calls
                if key == '"':
                    key = '\\\\\\\"'
                if key == '\\':
                    key = '\\\\\\\\'

                # press nameCommand
                callback = "python(\"" + callbackName + "(\\\"" + key + "\\\", " + str(a) + ", " + str(c) + ", True)\")"
                cmds.nameCommand( nameCommandName + "_press"
                                , annotation = nameCommandName + "_press"
                                , command = callback
                                )
                print "created", nameCommandName + "_press nameCommand"

                # release nameCommand
                callback = "python(\"" + callbackName + "(\\\"" + key + "\\\", " + str(a) + ", " + str(c) + ", False)\")"
                cmds.nameCommand( nameCommandName + "_release"
                                , annotation = nameCommandName + "_release"
                                , command = callback
                                )
                print "created", nameCommandName + "_release nameCommand"

                # hotkey for both press and release nameCommands for current key + mods
                cmds.hotkey( keyShortcut = key
                            , name = nameCommandName + "_press"
                            , releaseName = nameCommandName + "_release"
                            , altModifier = a
                            , ctrlModifier = c
                            )
                print "created", nameCommandName, " press/release hotkey"


def removeTomaytoKeymap (nameCommandPrefix="tomayto", **kwargs):
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


def backupDoDeleteScriptPath ():
    print "Begin doDelete script path discovery..."
    opvar = "scriptPath_doDelete"
    if cmds.optionVar(exists=opvar):
        print "  Found option var:", opvar
        storedPath = str(cmds.optionVar(query=opvar))
        print "  Stored path:", storedPath
        if os.path.exists(storedPath):
            print "  Path exists."
        else:
            print "  Path does not exist."
            print "  Querying location of doDelete..."
            locMsg = mel.eval("whatIs doDelete;")
            print "    Result: ", locMsg
            melHeader = "Mel procedure found in: " # Linux, Maya 2017
            scriptHeader = "Script found in: " # Windows, Mayas 2016 and 2018
            scriptPath = ""
            if locMsg.startswith(melHeader):
                print "  Found prefix: ", melHeader
                scriptPath = locMsg[len(melHeader):]
            elif locMsg.startswith(scriptHeader):
                print "  Found prefix: ", scriptHeader
                scriptPath = locMsg[len(scriptHeader):]
            else:
                print "  Could not find doDelete path via whatIs."
            if os.path.exists(scriptPath):
                print "  Path found at:", scriptPath
                cmds.optionVar(stringValue=(opvar, scriptPath))
                print "  Stored in optionVar."
            else:
                print "  Found path does not exist."
        print ("End doDelete script path discovery.")

def hackDeleteKeys (callbackName="tomaytoCB", nameCommandPrefix="tomayto"):
    """
    Maya doesn't allow using Backspace or Delete as hotkeys, but we can
    override the MEL function that they both call. Both keys will fire off the
    same event(s), and we'll only have access to press, not release, and none
    of the modifier keys will work with them, but it's something, at least.
    """
    backupDoDeleteScriptPath()
    print "Overriding doDelete (this session only) with:"
    override = 'global proc doDelete () { python("' + callbackName + '(\\"Backspace\\", False, False, True)"); };'
    print(override)
    mel.eval(override)

def restoreDeleteKeys ():
    """
    Source doDelete.mel, the file that builds the doDelete MEL procedure
    called by Backspace/Delete. This should restore Backspace functionality.
    """
    opvar = "scriptPath_doDelete"
    scriptPath = str(cmds.optionVar(query=opvar))
    if os.path.exists(scriptPath):
        print "Restoring doDelete function"
        print "Sourcing:", scriptPath
        mel.eval('source "' + scriptPath + '";')
    else:
        print "Unable to locate original doDelete script path, but"
        print "functionality should be restored on program restart."

