
__Id__ = "$Id$"

class Atoms:
    def __init__(self, scope, count=0):
        self.scope = scope
        self.count = count

    def newAtom(self, name):
        if getattr(self.scope, name, None) != None:
            # FIXME: is it OK to use standard exception 'AttributeError' ?
            raise AttributeError, ("symbol '%s' already defined" % name)
        setattr(self.scope, name, self.count)
        self.count = self.count+1

    def newAtoms(self, names):
        for name in names: self.newAtom(name)

    def getCount(self):
        return self.count
