A word on naming...

automata + maya
automaya (like a contraction of Autodesk Maya)
automayta ("automater?")
tomayta
tomayto
mayta - nah, sounds like "mater"


# how to play with hotkey sets

cmds.hotkeySet(query=True, hotkeySetArray=True)
cmds.hotkeySet(query=True, current=True)

cmds.hotkeySet("MyNewKeySet", current=True) # creates if non-existent

cmds.hotkeySet("Maya_Default", edit=True, current=True)
cmds.hotkeySet("MyNewKeySet", edit=True, current=True)

