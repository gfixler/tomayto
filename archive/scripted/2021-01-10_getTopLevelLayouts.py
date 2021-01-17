def getTopLevelLayouts ():
    """
    Returns a dict, with window-parented layouts as the keys, and with their
    associated values being the windows in which they reside.
    """
    topLays = {}
    for lay in cmds.lsUI(type="layout"):
        par = cmds.layout(lay, query=True, parent=True)
        if cmds.window(par, exists=True):
            topLays[lay] = par
    return dict(topLays)


# getTopLevelLayouts(False)["window1"]


# to get the inverse
swap = lambda (x, y): (y, x)
flipdict = lambda d: dict(map(swap, d.items()))

flipdict(getTopLevelLayouts())

