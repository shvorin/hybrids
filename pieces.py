"""
Module pieces.  It contains definition for all chess pieces (hybrid variant).
It is also intended to keep compatibility for ortodox variant.
"""

__id__ = "$Id$"
# __all__ = ["Piece", "AtomicPiece"]

from atoms import *

class IllegalMove(Exception):
    pass

AbstractMethodError = Exception, "an abstract method called"

class Piece(Immutable):
    __slots__ = ('sym', 'col')

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

    def isReachable(self, src, dst):
        raise AbstractMethodError

    def leave(self, src, dst):
        raise AbstractMethodError

    def join(self, src, dst):
        raise AbstractMethodError

    def move(self, src, dst, options={}):
        """
        generic move() method is suitable for most pieces
        """
        def f(brd):
            #            assert isinstance(brd, board.Board)
            if brd.turn != self.col:
                raise IllegalMove, ("it's not %s's turn to move" % self.col)
            hunk1 = (src, self.leave(brd[src]))

            if not self.isReachable(src, dst):
                raise IllegalMove, ("invalid %s move" % self.__class__.name)

            hunk2 = (dst, self.join(brd[dst]))

            return [hunk1, hunk2]
        return f

    def show(self):
        """
        a rectangle 2x3 should be filled by theese chars
        """
        sp = self.col.show()
        return (sp*3, sp+self.sym[0]+sp)
    
class AtomicPiece(Piece):
    symbols = tuple('KP')

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

class KingPiece(AtomicPiece):
    symbol = 'K'

    def isReachable(self, src, dst):
        x, y = (dst-src)()
        if abs(x) == 0: return abs(y) == 1
        else:           return abs(y) <= 1


class PawnPiece(AtomicPiece):
    symbol = 'P'

    def move(self, src, dst, options={}):
        x, y = (dst-src)()
        assert src.y != 0 and src.y != 7
        
        if self.col == black:
            y = -y
            is_moved = src.y - 6
            do_promote = dst.y
        else:
            is_moved = src.x - 1
            do_promote = 7 - dst.y

        def check_src(board):
            if board[src] != self: raise IllegalMove, "this is not a pawn"

        checks = [check_src]
        
        if x == 0:
            if y == 2:
                def check_double(board):
                    if not is_moved:
                        raise IllegalMove, "cannot make double move"
                    if board[src+AffLoc(0, 1)] != None:
                        raise IllegalMove, "this pawn is blocked"
                checks.append[check_double]
            elif y != 1:
                return fraise(IllegalMove, "invalid pawn move")
            def check_simple(board):
                if board[dst] != None:
                    raise IllegalMove, "this pawn is blocked"
            checks.append[check_simple]
        elif abs(x) == 1 and y == 1:
            # capture move
            pass
        else:
            return fraise(IllegalMove, "invalid pawn move")

class RangedPiece:
    """
    common class for ranged pieces: Rook and Bishop
    """
    def move(self, src, dst, options={}):
        """
        generic move() method is suitable for most pieces
        """
        def f(board):
            # assert isinstance(board, Board)
            if board.turn != self.col:
                raise IllegalMove, ("it's not %s's turn to move" % self.col)
            hunk1 = (src, self.leave(board[src]))

            # only check for IllegalMove exception
            self.reach(board, src, dst)

            hunk2 = (dst, self.join(board[dst]))

            return [hunk1, hunk2]
        return f

class PrimePiece(Piece):
    symbols = tuple('RBNQ')

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


class RookPiece(RangedPiece, PrimePiece):
    symbol = 'R'

    def reach(self, board, src, dst):
        "returns nothing or raises IllegalMove"
        x, y = (dst-src)()
        if x == 0:
            if y == 0: raise IllegalMove, "cannot skip move"
            sign = cmp(y, 0)
            for i in range(sign, y, sign):
                if board[src+AffLoc(0, i)] != None:
                    raise IllegalMove, "rook can't jump over pieces"
        elif y == 0:
            sign = cmp(x, 0)
            for i in range(sign, x, sign):
                if board[aff_add(src, (i, 0))] != None:
                    IllegalMove, "rook can't jump over pieces"
        else:
            raise IllegalMove, "impossible rook move"

class BishopPiece(RangedPiece, PrimePiece):
    symbol = 'B'

    def reach(self, board, src, dst):
        "returns nothing or raises IllegalMove"
        x, y = (dst-src)()
        raise 'not implemented'

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
        
    def show(self):
        sp = self.col.show()
        return (sp+self.p2.sym[0]+sp, sp+self.p1.sym[0]+sp)
    
