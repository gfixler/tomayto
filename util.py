import maya.cmds as cmds


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
           , '(': "lParen"
           , ')': "rParen"
           , '[': "openSquareBracket"
           , ']': "closedSquareBracket"
           , '{': "openCurlyBrace"
           , '}': "closedCurlyBrace"
           , '<': "lessThanSymbol"
           , '>': "greaterThanSymbol"
           , '-': "minusSign"
           , '_': "underscore"
           , '=': "equalsSign"
           , '+': "plusSign"
           , ',': "comma"
           , '.': "period"
           , '\\': "backslash"
           , '/': "forwardSlash"
           , '?': "questionMark"
           , '|': "verticalBar"
           , ' ': "space"
           }

keyChars = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
specialKeys = ["Up", "Down", "Left", "Right", "Home", "End", "Page_Down", "Page_Up", "Insert", "Return", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]

keys = list(keyChars) # break char string into individual strings, one per key
allKeys = keys + specialKeys

# convert single character into usable key name for naming purposes
keyName = lambda c: keyNames[c] if c in keyNames else c


def listAllNameCommands ():
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

