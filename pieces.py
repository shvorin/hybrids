"""
Module pieces.  It contains definition for all chess pieces (hybrid variant).
It is also intended to keep compatibility for ortodox variant.
"""

__id__ = "$Id$"
# __all__ = ["Piece", "AtomicPiece"]

from atoms import *

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
