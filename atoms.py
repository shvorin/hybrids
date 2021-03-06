"""
Module atoms contains several immutable classes:
for pieces colors and locations.  There also defined a useful class 'Immutable'.
"""

__id__ = "$Id$"
__all__ = ["Immutable", "Color", "white", "black", "Flank", "queenside", "kingside", "Loc", "AffLoc", "WLoc", "invalid_init"]

import types

def invalid_init(self, *args):
    raise TypeError, ("it is forbidden to create '%s' instances" % self.__class__.__name__)


class Immutable(object):
    """
    Immutable is a base class for immutable objects.  Any subclasses should define their
    own '__slots__' to keep all (immutable!) data there.
    """
    
    __slots__ = ()

    __init__ = invalid_init
    
# FIXME: 'readonly' property temporary(?) disabled to allow loading by pickle
#     def __setattr__(self, name, value):
#         raise TypeError, "readonly attribute"

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

class Flank(Immutable):
    __slots__ = ('value', )
    __queenside = 0
    __kingside = 1

    def createValues():
        """this static method is to be deleted just after instances created"""
        v1 = object.__new__(Flank)
        v1.init_instance(value=Flank.__queenside)
        v2 = object.__new__(Flank)
        v2.init_instance(value=Flank.__kingside)
        return (v1, v2)

    createValues = staticmethod(createValues)

    # FIXME: is it OK to use __repr__(), not just __str__() ?
    def __repr__(self):
        if   self.value == Flank.__queenside: return 'queenside'
        elif self.value == Flank.__kingside: return 'kingside'

# NB: use classical "queenside", not "guardside"
queenside, kingside = Flank.createValues()
del Flank.createValues # no more Flank values ;)

class Loc(Immutable):
    __slots__ = ('x', 'y')
    
    # let files and ranks be public 'static' fields
    files = list('abcdefgh')
    ranks = list('12345678')
    
    xyrange = range(8)

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

        if x in Loc.files and y in Loc.ranks:
            # algebraic notation given
            try:
                x, y = Loc.files.index(x), Loc.ranks.index(y)
            except ValueError:
                raise ValueError, "invalid algebraic notation"
        else:
            # numeric representation given
            if not (x in Loc.xyrange and y in Loc.xyrange):
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

    def iter(*args):
        """
        returns an iterator of Loc instances; arguments may contains wildcards ('*')
        """
        l = len(args)
        
        if l == 1:
            (a, ) = args
            if isinstance(a, Loc):
                yield a
            elif a == '*':
                for x in Loc.xyrange:
                    for y in Loc.xyrange:
                        yield Loc(x, y)
            else:
                raise ValueError
        elif l == 2:
            (x, y) = args
            if x == '*':
                if y == '*':
                    for res in Loc.iter('*'):
                        yield res
                else:
                    for x in Loc.xyrange:
                        yield Loc(x, y)
            elif y == '*':
                for y in Loc.xyrange:
                    yield Loc(x, y)
            else:
                yield Loc(x, y)
        else:
            raise ValueError
            
    iter = staticmethod(iter)

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

    def __mul__(self, other):
        return AffLoc(self.x*other, self.y*other)

class WLoc(Immutable):
    """
    'wild Loc' may be used to iterate ordinal Locs.
    Values of x and y may be None which stands for wild value.
    """
    __slots__ = ('x', 'y')

    xyrange = Loc.xyrange + [None]

    def __init__(self, *args):
        """
        args may be either:
        Loc, WLoc (copy constructor);
        single string: 'e1', '*1', 'e*', '**', '*' (a single asterisk is not recommended(?));
        pair of strings: ('e', '1'), ('*', '1'), ('e', '*'), ('*', '*');
        pair of (numbers or None): (4, 0), (4, None), (None, 0), (None, None);
        None

        A wrapped pair like (('e', '1')) may be used.
        """

        length = len(args)
        if length == 2:
            x, y = args
        elif length == 1:
            (a, ) = args
            if a in (None, '*'):
                self.init_instance(x=None, y=None)
                return
            elif isinstance(a, self.__class__) or isinstance(a, Loc):
                # copy constructor
                x, y = a.x, a.y
            else:
                x, y = a
        else:
            raise ValueError, "wrong # of args"

        if x.__class__ is types.StringType and y.__class__ is types.StringType:
            try:
                if x == '*':
                    x = None
                else:
                    x = Loc.files.index(x)
                if y == '*':
                    y = None
                else:
                    y = Loc.ranks.index(y)
            except ValueError: # raised by index()
                raise ValueError, "invalid algebraic notation"
        else:
            # numeric representation given
            if not (x in WLoc.xyrange and y in WLoc.xyrange):
                if x.__class__ is types.IntType and y.__class__ is types.IntType:
                    raise ValueError, "numeric representation is out of range"
                else:
                    raise ValueError, "invalid representation"
        
        self.init_instance(x=x, y=y)

    # FIXME: is it OK to use __repr__(), not just __str__() ?
    def __repr__(self):
        res = ''
        if self.x is None:
            res += '*'
        else:
            res += Loc.files[self.x]
        if self.y is None:
            res += '*'
        else:
            res += Loc.ranks[self.y]
        return res

    def __iter__(self):
        """
        returns an iterator of Locs
        """
        if self.x is None:
            xs = Loc.xyrange
        else:
            xs = (self.x, )

        if self.y is None:
            ys = Loc.xyrange
        else:
            ys = (self.y, )

        for x in xs:
            for y in ys:
                yield Loc(x,y) # FIXME: don't use standard Loc constructor; it's not effective
