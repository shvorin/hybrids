__Id__ = "$Id$"

class Immutable(object):
    __slots__ = ()

    def __init__(self, *args):
        raise TypeError, ("it is forbidden to create '%s' instances" % self.__class__.__name__)
    
    def __setattr__(self, name, value):
        raise TypeError, "readonly attribute"

    def __delattr__(self, name):
        raise TypeError, "readonly attribute"

    def __cmp__(self, other):
        return cmp(self(), other())

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
            (x, y) = args
        elif length == 1:
            ((x, y), ) = args
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

class Piece(Immutable):
    __slots__ = ('sym', 'col')

    # FIXME: is it OK to use __repr__(), not just __str__() ?
    def __repr__(self):
        return self.col.showShort() + self.sym

    def newPiece(sym, col):
        pass
        
    newPiece = staticmethod(newPiece)

def metaclass(name, bases, dict):
    newclass = type(name, bases, dict)
    # FIXME
    if name != 'AtomicPiece':
        AtomicPiece.pieces[newclass.symbol] = newclass
    return newclass


class AtomicPiece(Piece):
    symbols = tuple('KP')
    pieces = {}

    # subclasses should define class field 'symbol'

    __metaclass__ = metaclass
    
    def __init__(self, col):
        if self.__class__ == AtomicPiece:
            raise TypeError, ("it is forbidden to create '%s' instances" % self.__class__.__name__)
        self.init_instance(sym=self.__class__.symbol, col=col)

    def hybridable(self): return False

    def ishybrid(self): return False

    def leave(self, other):
        if self == other:
            return (self, None)
        else:
            if other == None: msg = "empty"
            elif other.col != self.col: msg = "enemy piece"
            else: msg = ("not a %s" % self.__class__.__name__)
            raise IllegalMove, msg

    def join(self, other):
        if other == None or other.col != self.col:
            return (other, self)
        else:
            raise IllegalMove, ("%s is not hybridable" % self.__class__.__name__)

class PrimePiece(Piece):
    symbols = tuple('RBNQ')
    pieces = {}

    def new(sym):
        if sym in symbols:
            return pieces[sym]
        else:
            raise ValueError, "unknown symbol"
        
    new = staticmethod(new)
    
    def hybridable(self): return True

    def ishybrid(self): return False

    def __add__(self, other):
        assert isinstance(other, PrimePiece)
        return HybridPiece.new(self.sym, other.sym)

    def leave(self, other):
        "returns a pos-hunk 'the piece leaves position'"
        if other == None:
            raise IllegalMove, "attempt to move from empty position"
        if other.col != self.col:
            raise IllegalMove, "attempt to move evemy's piece"
#         if other.sym == self.sym:
#             rest = None ...
#         else:
#             (sym0, sym1) = sym
            
#             if sym0 == self.sym:
#                 rest = sym1
#             elif sym1 == self.sym:
#                 rest = sym0
#             else:
#                 raise IllegalMove, "no such piece on this position"
#         return (other, rest)

class QueenPiece(PrimePiece):
    symbol = 'Q'
    
    def isReachable(self, src, dst):
        """Note, in hybrids the queen moves in the same manner as the king!"""
        x, y = (dst-src)()
        if abs(x) == 0: return abs(y) == 1
        else:           return abs(y) <= 1


class KingPiece(AtomicPiece):
    symbol = 'K'

    __metaclass__ = metaclass
    
    def isReachable(self, src, dst):
        x, y = (dst-src)()
        if abs(x) == 0: return abs(y) == 1
        else:           return abs(y) <= 1

    def move(self, src, dst):
        def f(board):
            hunk1 = self.leave(board[src])

            if not self.isReachable(src, dst):
                raise IllegalMove, "invalid king move"

            hunk2 = self.join(board[dst])

            return [hunk1, hunk2]
        return f
