"""
Module pieces.  It contains definition for all chess pieces (hybrid variant).
It is also intended to keep compatibility for ortodox variant.
"""

__id__ = "$Id$"
# __all__ = ["Piece", "AtomicPiece"]

from atoms import *

AbstractMethodError = Exception, "an abstract method called"

class Piece(Immutable):
    __slots__ = ('sym', 'col')

    pieces = {}

    def __init__(self, arg1, arg2=None):
        """
        Usage: ClassName(col) or ClassName(sym, col).
        Some classes does not need 'sym' argument, since they have 'symbol' attribute;
        the others require.
        """
        if self.__class__ in (Piece, AtomicPiece, PrimePiece):
            raise TypeError, ("it is forbidden to create '%s' instances" % self.__class__.__name__)

        if self.__class__.__dict__.has_key('symbol'):
            col = arg1
            sym = self.__class__.symbol
            assert arg2 == None
        else:
            sym = arg1
            col = arg2
            assert arg2 != None
            assert sym in self.__class__.symbols

        self.init_instance(sym=self.__class__.symbol, col=col)
            

    # FIXME: is it OK to use __repr__(), not just __str__() ?
    def __repr__(self):
        return self.col.showShort() + self.sym

    def newPiece(sym, col):
        if pieces.has_key(sym):
            return pieces[sym](col)
        else:
            raise ValueError, "unknown symbol"
        
    newPiece = staticmethod(newPiece)
    
    def isReachable(self, src, dst):
        raise AbstractMethodError

    def move(self, src, dst):
        raise AbstractMethodError

    def leave(self, src, dst):
        raise AbstractMethodError

    def join(self, src, dst):
        raise AbstractMethodError
        
class AtomicPiece(Piece):
    symbols = tuple('KP')
    pieces = {}

    # subclasses should define class field 'symbol'

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

# FIXME: have to add __metaclass__ attribute to *all* subclasses of AtomicPiece
def metaclass(name, bases, dict):
    newclass = type(name, bases, dict)
    AtomicPiece.pieces[newclass.symbol] = newclass
    Piece.pieces[newclass.symbol] = newclass
    return newclass

class KingPiece(AtomicPiece):
    symbol = 'K'

    __metaclass__ = metaclass
    
    def isReachable(self, src, dst):
        x, y = (dst-src)()
        if abs(x) == 0: return abs(y) == 1
        else:           return abs(y) <= 1

    def move(self, src, dst):
        def f(board):
            assert isinstance(board, Board)
            hunk1 = self.leave(board[src])

            if not self.isReachable(src, dst):
                raise IllegalMove, "invalid king move"

            hunk2 = self.join(board[dst])

            return [hunk1, hunk2]
        return f


class PawnPiece(AtomicPiece):
    symbol = 'P'

    __metaclass__ = metaclass

    def isReachable(self, src, dst):
        NotImplemented

class PrimePiece(Piece):
    symbols = tuple('RBNQ')
    pieces = {}

    # subclasses should define class field 'symbol'

    def hybridable(self): return True

    def ishybrid(self): return False

    def __add__(self, other):
        assert isinstance(other, PrimePiece)
        return HybridPiece(self, other)

    def leave(self, other):
        "returns a loc-hunk 'the piece leaves location'"
        if other == None:
            raise IllegalMove, "attempt to move from empty location"
        if other.col != self.col:
            raise IllegalMove, "attempt to move evemy's piece"

        if other == self:
            rest = None
        else:
            assert isinstance(other, HybridPiece)
            rest = other-self

        return (other, rest)

    def join(self, other):
        "returns a loc-hunk 'the piece joins location'"        
        if other == None or other.col != self.col:
            return (other, self)
        assert isinstance(other, PrimePiece)
        return (other, self+other)

    def sort2(self, other):
        # FIXME: use custom order
        if self.sym < other.sym:
            return self, other
        else:
            return other, self


class RookPiece(PrimePiece):
    symbol = 'R'

class BishopPiece(PrimePiece):
    symbol = 'B'

class KnightPiece(PrimePiece):
    symbol = 'N'

    def isReachable(self, src, dst):
        x, y = (dst-src)()
        x, y = abs(x), abs(y)
        return (x==1 and y==2) or (x==2 or y==1)


class QueenPiece(PrimePiece):
    """Note, in hybrids the queen moves in the same manner as the king!"""
    symbol = 'Q'

    # FIXME: does not work
    isReachable = KingPiece.isReachable
    move = KingPiece.move


class HybridPiece(Piece):
    __slots__ = ('sym', 'col', 'p1', 'p2')
    
    #symbols = ('RR', 'RB') ...
    def isReachable(self, src, dst):
        NotImplemented

    def __init__(self, p1, p2):
        assert isinstance(p1, PrimePiece)
        assert isinstance(p2, PrimePiece)
        assert p1.col == p2.col

        p1, p2 = p1.sort2(p2)
        self.init_instance(sym=p1.sym+p2.sym,
                           col=p1.col,
                           p1=p1,
                           p2=p2)
        
    def __sub__(self, other):
        assert isinstance(other, PrimePiece)
        if self.p1 == other:
            return self.p2
        elif self.p2 == other:
            return self.p1
        else:
            raise ValueError, ("this hybrid does not contain prime piece %s" % other)
        
