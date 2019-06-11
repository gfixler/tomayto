# from http://help.autodesk.com/cloudhelp/2018/ENU/Maya-Tech-Docs/CommandsPython/assignCommand.html

count = cmds.assignCommand(query=True, numElements=True)
print ('There are ' + str(count) + ' named command objects.')

for index in range(1, count+1):
    keyString = cmds.assignCommand(index, query=True, keyString=True)

    if  0 < len(keyString) and keyString[0] != "NONE":
        displayString = '('

        if "1" == keyString[2]: displayString += 'Ctrl+'
        if "1" == keyString[1]: displayString += 'Alt+'
        if "1" == keyString[5]: displayString += 'Command+'

        displayString += keyString[0]

        if "1" == keyString[3]: displayString += ' Release'
        if "1" == keyString[4]: displayString += ' KeyRepeat'

        displayString += ')'

        print index, cmds.assignCommand(index, query=True, name=True), displayString


delNameCmd = lambda i: cmds.assignCommand(edit=True, delete=i)
delNameCmdAbove = lambda n: [delNameCmd(n) for i in xrange(1000)][0] # useful hack


# how to play with hotkey sets

cmds.hotkeySet(query=True, hotkeySetArray=True)
cmds.hotkeySet(query=True, current=True)

cmds.hotkeySet("MyNewKeySet", current=True) # creates if non-existent

cmds.hotkeySet("Maya_Default", edit=True, current=True)
cmds.hotkeySet("MyNewKeySet", edit=True, current=True)


# the rest of this file sets up a key echoer

puncNames = { ';': "semicolon"
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

charName = lambda c: puncNames[c] if c in puncNames else c

def sayKey (key, nameCmdName):
    print key, nameCmdName

# create all name commands and hook them up to hotkeys
# This just echoes everything typed, with nameCommand names

keys=" abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890# `-=~!@#$%^&*()_+,./<>?;:'\"{[}]|\\"
for key in keys:
    for a in [False, True]:
        for c in [False, True]:
            for s in [False, True]:
                modTag = ("_alt" if a else "") + ("_ctrl" if c else "") + ("_shift" if s else "")
                nameCommandName= "key" + (modTag if modTag else "") + "_" + charName(key)
                print key, modTag, nameCommandName
                if key == '"':
                    key = '\\\\\\\"' #ugh
                cmds.nameCommand(nameCommandName, annotation=nameCommandName, command='python("sayKey(\\\"' + key + '\\\", \\\"' + nameCommandName + '\\\")")')
                cmds.hotkey(keyShortcut=key, name=nameCommandName, altModifier=a, ctrlModifier=c, shiftModifier=s)

