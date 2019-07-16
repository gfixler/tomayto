# triple-quotes to comment out against select-all->run
# but still allow stream selecting lines between and running

"""
cmds.hotkeySet(query=True, hotkeySetArray=True)
cmds.hotkeySet(query=True, current=True)

cmds.hotkeySet("MyNewKeySet", current=True) # creates if non-existent

cmds.hotkeySet("Maya_Default", edit=True, current=True)
cmds.hotkeySet("MyNewKeySet", edit=True, current=True)
"""

"""
import sys

path = "C:/msys64/home/GFixler/code/py"
if path not in sys.path:
    sys.path = [path] + sys.path
"""

del sys.modules["tomayto"]
del sys.modules["tomayto.core"]
del sys.modules["tomayto.util"]

import tomayto
reload(tomayto)
reload(tomayto.core)
reload(tomayto.util)

# create our instance
tom = tomayto.Tomayto()

"""
# shouldn't need to do these most of the time
tom.clearNameCommands()
tom.createNameCommands()
"""

# tomayto.util.listAllNameCommands()

# hook up the Python callback (called from MEL) to our instance
tomaytoCB = tom.getch

"""
def tomaytoCB (key, alt, ctrl, press):
    print key, "Alt" if alt else "", "Ctrl" if ctrl else "", "DOWN" if press else "UP"
"""

