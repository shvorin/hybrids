
__Id__ = "$Id$"


class Atoms:
    count = 0
    
    def __init__(self, scope):
        self.scope = scope

    def newAtom(self, name):
        if getattr(self.scope, name, None) != None:
            # FIXME: is it OK to use standard exception 'AttributeError' ?
            raise AttributeError, ("symbol '%s.%s' already defined" % (self.scope, name))
        setattr(self.scope, name, Atoms.count)
        Atoms.count = Atoms.count+1

    def newAtoms(self, names):
        for name in names: self.newAtom(name)


def getCount():
        return Atoms.count

def newAtom(name):
    "updates globals"
    g = globals()
    if g.has_key(name):
        raise ("global symbol '%s' already defined" % name)
    g[name] = Atoms.count
    Atoms.count = Atoms.count + 1

def newAtoms(names):
    "updates globals"
    for name in names: newAtom(name)
