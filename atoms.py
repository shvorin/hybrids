"""
Module atoms contains several immutable classes:
for pieces colors and locations.  There also defined a useful class 'Immutable'.
"""

__id__ = "$Id$"
__all__ = ["Immutable", "Color", "white", "black", "Loc", "AffLoc"]

class Immutable(object):
    __slots__ = ()

    def __init__(self, *args):
        raise TypeError, ("it is forbidden to create '%s' instances" % self.__class__.__name__)
    
    def __setattr__(self, name, value):
        raise TypeError, "readonly attribute"

    def __delattr__(self, name):
        raise TypeError, "readonly attribute"

    def __cmp__(self, other):
        return cmp(self(), other)

    def __hash__(self):
        return hash(self())

    def __call__(self):
        return tuple(map((lambda name: object.__getattribute__(self, name)), self.__slots__))

    def init_instance(self, **slots):
        """
        initializes all __slots__ fields of the instance;
        this should be called in '__init__' method (or any other "creation" method) of any subclass
        """
        for name in self.__class__.__slots__:
            try:
                object.__setattr__(self, name, slots[name])
            except KeyError:
                raise ValueError, ("all __slots__ field must be defined, while '%s' is not" % name)
        # del self.init_instance # no re-initialization allowed
    

class Color(Immutable):
    __slots__ = ('value', )
    __white = 0
    __black = 1
    
    # FIXME: is it OK to use __repr__(), not just __str__() ?
    def __repr__(self):
        if   self.value == Color.__white: return 'white'
        elif self.value == Color.__black: return 'black'
        else : raise ValueError, "oops, unknown color"

    def showShort(self):
        return self.__repr__()[0]
        
    def createValues():
        """this static method is to be deleted just after instances created"""
        v1 = object.__new__(Color)
        v1.init_instance(value=Color.__white)
        v2 = object.__new__(Color)
        v2.init_instance(value=Color.__black)
        return (v1, v2)

    createValues = staticmethod(createValues)

    def inv(self):
        if self == white: return black
        else: return white

    def show(self):
        if self == white: return ' '
        else: return '.'

white, black = Color.createValues()
del Color.createValues # no more Color values ;)
# FIXME: it is still allowed to modify __slots__ fields by calling init_instance


class Loc(Immutable):
    __slots__ = ('x', 'y')
    
    # let files and ranks be public 'static' fields
    files = 'abcdefgh'
    ranks = '12345678'

    def __init__(self, *args):
        length = len(args)
        if length == 2:
            x, y = args
        elif length == 1:
            (a, ) = args
            if isinstance(a, self.__class__):
                # copy constructor
                x, y = a.x, a.y
            else:
                x, y = a
        else:
            raise ValueError, "wrong # of args"

        if x in list(Loc.files) and y in list(Loc.ranks):
            # algebraic notation given
            try:
                x, y = Loc.files.index(x), Loc.ranks.index(y)
            except ValueError:
                raise ValueError, "invalid algebraic notation"
        else:
            # numeric representation given
            if not (x in range(8) and y in range(8)):
                raise ValueError, "numeric representation is out of range"
        
        self.init_instance(x=x, y=y)
            

    # FIXME: is it OK to use __repr__(), not just __str__() ?
    def __repr__(self):
        return Loc.files[self.x] + Loc.ranks[self.y]
    
    def flip(self):
        return Loc(self.x, 7-self.y)

    def __sub__(self, other):
        if Loc == other.__class__:
            return AffLoc(self.x-other.x, self.y-other.y)
        elif AffLoc == other.__class__:
            return self+(-other)
        else:
            raise TypeError, "Loc of AffLoc expected as 2nd argument"
    
    def __add__(self, other):
        assert AffLoc == other.__class__
        return Loc(self.x+other.x, self.y+other.y)

class AffLoc(Immutable):
    """
    defines vectors of the affinity space where points represented by Loc
    """
    __slots__ = ('x', 'y')

    def __init__(self, *args):
        length = len(args)
        if length == 2:
            (x, y) = args
        elif length == 1:
            ((x, y), ) = args
        else:
            raise ValueError, "wrong # of args"
        self.init_instance(x=x, y=y)

    # FIXME: is it OK to use __repr__(), not just __str__() ?
    def __repr__(self): return str(self())

    def __neg__(self):
        return AffLoc(-self.x, -self.y)
    
    def __add__(self, other):
        assert AffLoc == other.__class__
        return AffLoc(self.x+other.x, self.y+other.y)
    
    def __sub__(self, other):
        assert AffLoc == other.__class__
        return AffLoc(self.x-other.x, self.y-other.y)
