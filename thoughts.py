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


# how to play with hotkey sets

cmds.hotkeySet(query=True, hotkeySetArray=True)
cmds.hotkeySet(query=True, current=True)

cmds.hotkeySet("MyNewKeySet", current=True) # creates if non-existent

cmds.hotkeySet("Maya_Default", edit=True, current=True)
cmds.hotkeySet("MyNewKeySet", edit=True, current=True)

