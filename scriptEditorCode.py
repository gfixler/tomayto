# triple-quotes to comment out against select-all->run
# but still allow stream selecting lines between and running

"""
import sys

path = "C:/msys64/home/GFixler/code/py"
if path not in sys.path:
    sys.path = [path] + sys.path
"""

try:
    del tomayto
except:
    pass
mods = sys.modules.keys()
for mod in mods:
    if mod.startswith("tomayto"):
        del sys.modules[mod]
        print "deleted", mod

import tomayto

try:
    reload(tomayto)
    reload(tomayto.core)
    reload(tomayto.util)
    reload(tomayto.exampleUsage)
except:
    pass

# create our instance
tom = tomayto.exampleUsage.instantiate()
# hook up the Python callback (called from MEL) to our instance
tomaytoCB = tom.eventHandler

