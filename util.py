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

bools = [False, True]
modKeyGroups = [(charName(k), a, c, s, pr) for k in keyChars for a in bools for c in bools for s in bools for pr in bools]

def sayKey (key, nameCmdName):
    print key, nameCmdName

