"""
Module pieces.  It contains definition for all chess pieces (hybrid variant).
It is also intended to keep compatibility for ortodox variant.
"""

__id__ = "$Id$"
# __all__ = ["Piece", "AtomicPiece"]

from atoms import *

class IllegalMove(Exception):
    pass

def fraise(exc, msg=""):
    if msg == "":
        def f(x): raise exc
    else:
        def f(x): raise exc, msg
    return f

def fconst(v):
    return lambda x: v

fconst_None = fconst(None)

def fiter(*fs):
    """
    takes a list of function; result is a function which returns an iterator
    """
    def g(x):
        for f in fs:
            r = f(x)
            # ignore void results
            if r != None: yield r
    return lambda x: [y for y in g(x)]

def myassert(v, exc, msg=""):
    if not v:
        if msg == "": raise exc
        else: raise exc, msg

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

        self.init_instance(sym=sym, col=col)
            

    # FIXME: is it OK to use __repr__(), not just __str__() ?
    def __repr__(self):
        return self.col.showShort() + self.sym

    def leave(self, other):
        """
        generic leave() method suitable for most pieces
        """
        if self == other:
            return (self, None)
        else:
            if other == None: msg = "empty"
            elif other.col != self.col: msg = "enemy piece"
            else: msg = ("not a %s" % self.__class__.__name__)
            raise IllegalMove, msg

    def join(self, other):
        """
        generic join() method suitable for most pieces
        """
        if other == None or other.col != self.col:
            return (other, self)
        else:
            raise IllegalMove, ("%s is not hybridable" % self.__class__.__name__)

    def reach(self, src, dst):
        """
        all subclasses should have reach() method which returns None or raises IllegalMove
        """
        raise Exception, "an abstract method called"

    def fjoin(self, src):
        return lambda board: (src, self.join(board[src]))

    def fleave(self, dst):
        return lambda board: (dst, self.leave(board[dst]))

    def fturn(self):
        return lambda board: myassert(board.turn == self.col,
                                      IllegalMove, ("it's not %s's turn to move" % self.col))

    def freach(self, src, dst):
        return lambda board: self.reach(board, src, dst)

    def move(self, src, dst, options={}):
        """
        generic move() method is suitable for most pieces
        """
        return fiter(self.fturn(),
                     self.fleave(src),
                     self.reach(src, dst),
                     self.fjoin(dst))

    def show(self):
        """
        a rectangle 2x3 should be filled by theese chars
        """
        sp = self.col.show()
        return (sp*3, sp+self.sym[0]+sp)

    def iter(*args):
        l = len(args)
        if l == 1:
            (a, ) = args
            if isinstance(a, Piece):
                yield a
            elif a == '*':
                for col in white, black:
                    for res in Piece.iter('*', col):
                        yield res
            else:
                raise ValueError
        elif l == 2:
            (a, col) = args
            if col == '*':
                cols = [white, black]
            elif isinstance(col, Color):
                cols = [col]
            else:
                raise ValueError, "unknown color"
            
            if a == '*':
                for col in cols:
                    # FIXME: use more generic class iterator
                    for cls in [KingPiece, PawnPiece, RookPiece, BishopPiece, KnightPiece, QueenPiece]:
                        yield cls(col)
                    for cls1 in [RookPiece, BishopPiece, KnightPiece, QueenPiece]:
                        for cls2 in [RookPiece, BishopPiece, KnightPiece, QueenPiece]:
                            if cls1 <= cls2:
                                yield HybridPiece(cls1(col), cls2(col))
            else:
                raise Exception, "not implemented case"

    iter = staticmethod(iter)
    
class AtomicPiece(Piece):
    symbols = tuple('KP')

    # subclasses should define class field 'symbol'

    def hybridable(self): return False

    def ishybrid(self): return False

class KingPiece(AtomicPiece):
    symbol = 'K'

    def reach(self, src, dst):
        x, y = (dst-src)()
        x = abs(x)
        if   x == 0:
            if abs(y) == 1: return fconst_None
        elif x == 1:
            if abs(y) <= 1: return fconst_None

        return fraise(IllegalMove, "invalid king move")

class PawnPiece(AtomicPiece):
    symbol = 'P'

    def move(self, src, dst, options={}):
        x, y = (dst-src)()
        # assert 1 <= src.y <= 6
        
        if self.col == black:
            y = -y
            untouched = src.y == 6
            do_promote = dst.y == 0
            fwd = AffLoc(0, -1)
        else:
            untouched = src.y == 1
            do_promote = 7 == dst.y
            fwd = AffLoc(0, 1)

        fhunks = [self.fturn(), self.fleave(src)]
        
        if x == 0:
            # non-capture move
            if y == 2:
                # double move
                if not untouched:
                    return fraise(IllegalMove, "cannot make double move")
                fhunks.append(lambda board: myassert(board[src+fwd] == None,
                                                     IllegalMove, "this pawn is blocked (case double)"))
                # FIXME: leave "en-passant allowed" hunk here
            elif y == 1:
                # simple move
                fhunks.append(lambda board: myassert(board[dst] == None,
                                                     IllegalMove, "this pawn is blocked (case simple)"))
            else:
                return fraise(IllegalMove, "invalid pawn move (case 1)")
                
        elif abs(x) == 1 and y == 1:
            # capture move
            fhunks.append(self.capture(dst))
        else:
            return fraise(IllegalMove, "invalid pawn move (case 2)")

        if do_promote:
            try:
                newPiece = options['promote']
                if (isinstance(newPiece, PrimePiece)
                    and not isinstance(newPiece, HybridPiece)
                    and newPiece.col == self.col):
                    pass
                else:
                    fraise(IllegalMove, "only prime piece of the same color promotion allowed")
                # don't care about what dst is occupied by
                fhunks.append(self.fput(dst, newPiece))
            except KeyError:
                return fraise(IllegalMove, "promotion not specified")
        else:
            assert not options.has_key('promote')
            fhunks.append(self.fput(dst, self))

        return fiter(*fhunks)

    def fput(self, dst, newPiece):
        # similar to fjoin(), but does not care about what dst is occupied by
        return lambda board: (dst, (board[dst], newPiece))

    def capture(self, dst):
        def f(board):
            target = board[dst]
            if target != None and target.col != self.col:
                # do not generate a hunk here, it will be done later
                return None
            # FIXME: check en-passant
            raise IllegalMove, "invalid pawn's capture move"
        return f

class RangedPiece(object):
    """
    common class for ranged pieces: Rook and Bishop
    """

    def reach(self, src, dst):
        return lambda board: self.reach0(board, src, dst)
    
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
            if not isinstance(other, HybridPiece):
                raise IllegalMove, "this is not a hybrid"
            try:
                rest = other-self
            except ValueError, e:
                raise IllegalMove, e

        return (other, rest)

    def join(self, other):
        "returns a loc-hunk 'the piece joins location'"        
        if other == None or other.col != self.col:
            return (other, self)
        if isinstance(other, PrimePiece):
            return (other, self+other)
        raise IllegalMove, "target expected to be a prime piece"

    def sort2(self, other):
        # FIXME: use custom order
        if self.sym < other.sym:
            return self, other
        else:
            return other, self


class RookPiece(RangedPiece, PrimePiece):
    symbol = 'R'

    def reach0(self, board, src, dst):
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
                if board[src+AffLoc(i, 0)] != None:
                    raise IllegalMove, "rook can't jump over pieces"
        else:
            raise IllegalMove, "impossible rook move"

class BishopPiece(RangedPiece, PrimePiece):
    symbol = 'B'

    def reach0(self, board, src, dst):
        "returns nothing or raises IllegalMove"
        x, y = (dst-src)()
        
        if x == 0:
            raise IllegalMove, "cannot skip move"
        dist = abs(x)
        if dist != abs(y):
            raise IllegalMove, "impossible bishop move"

        step = AffLoc(cmp(x, 0), cmp(y, 0))

        for i in range(1, dist):
            if board[src+step*i] != None:
                raise IllegalMove, "Bishop can't jump over pieces"


class KnightPiece(PrimePiece):
    symbol = 'N'

    def reach(self, src, dst):
        x, y = (dst-src)()
        x, y = abs(x), abs(y)
        if (x==1 and y==2) or (x==2 and y==1):
            return fconst_None

        return fraise(IllegalMove, "invalid knight move")


class QueenPiece(PrimePiece):
    """Note, in hybrids the queen moves in the same manner as the king!"""
    symbol = 'Q'

    def reach(self, src, dst):
        x, y = (dst-src)()
        x = abs(x)
        if   x == 0:
            if abs(y) == 1: return fconst_None
        elif x == 1:
            if abs(y) <= 1: return fconst_None

        return fraise(IllegalMove, "invalid queen move")

class HybridPiece(Piece):
    __slots__ = ('sym', 'col', 'p1', 'p2')
    
    def hybridable(self): return False

    def ishybrid(self): return True

    def reach(self, src, dst):
        def g(board):
            try:
                self.p1.reach(src, dst)(board)
            except IllegalMove, e1:
                if self.p2 != self.p1:
                    try:
                        self.p2.reach(src, dst)(board)
                    except IllegalMove, e2:
                        raise IllegalMove, ("invalid hybrid move: '%s' / '%s'" % (e1, e2))
                else:
                    raise IllegalMove, ("invalid hybrid move: '%s'" % e1)
        return g

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
    
