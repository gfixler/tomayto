import maya.cmds as cmds


keyChars = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"

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

