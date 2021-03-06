"""
Module pieces.  It contains definition for all chess pieces (hybrid variant).
It is also intended to keep compatibility for ortodox variant.
"""

__id__ = "$Id$"
# __all__ = ["Piece", "AtomicPiece"]

from atoms import *

class IllegalMove(Exception):
    pass

class UnspecifiedPromotion(IllegalMove):
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
            if r.__class__ is list:
                for i in r: yield i
            elif r is not None:
                # ignore void results
                yield r
    return lambda x: [y for y in g(x)]

def myassert(v, exc, msg=""):
    if not v:
        if msg == "": raise exc
        else: raise exc, msg

def count_up2(it):
    """
    counts elements in iterator up to 2 (i.e. returns 2 iff there at least 2)
    """
    cnt = 0
    for x in it:
        if cnt >= 2: break
        cnt += 1
    return cnt

_illmove = IllegalMove("FIXME: this is because makeMove() (which performs royality check) \
is called after move_SAN()")

def dropCastle(col, flank):
    def f(board):
        result = []
        if board.castle[col][flank]:
            def old(c): c[col][flank] = True
            def new(c): c[col][flank] = False
            result.append(("castle", (old, new)))
        return result
    return f


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

    def fjoin(self, dst):
        return lambda board: (dst, self.join(board[dst]))

    def fleave(self, src):
        return lambda board: (src, self.leave(board[src]))

    def fturn(self):
        return lambda board: myassert(board.turn == self.col,
                                      IllegalMove, ("it's not %s's turn to move" % self.col))

    corners = {white: {queenside: Loc('a1'), kingside: Loc('h1')},
               black: {queenside: Loc('a8'), kingside: Loc('h8')}}

    def move(self, src, dst, options={}):
        fhunks = [self.move0(src, dst, options)]

        for flank in (queenside, kingside):
            if src == Piece.corners[self.col][flank]:
                do = lambda: fhunks.append(dropCastle(self.col, flank))
                if self.__class__ is HybridPiece:
                    do()
                if self.__class__ is RookPiece:
                    # FIXME: this is wrong (see game rules)
                    do()
            if dst == Piece.corners[self.col.inv()][flank]:
                fhunks.append(dropCastle(self.col.inv(), flank))

        return fiter(*fhunks)

    def move0(self, src, dst, options={}):
        """
        generic move() method is suitable for most pieces
        """
        return fiter(self.fturn(),
                     self.fleave(src),
                     self.reach(src, dst),
                     self.fjoin(dst))

    def move_src_SAN(self, board, src, dst, options={}):
        """
        Returns a string representation of the move's src according to SAN.  Note it depends on 'board'.
        This generic method is suitable for most pieces.
        """

        # try not to show src at all
        cnt = count_up2(board.witerMove(self, WLoc(None), WLoc(dst), options))
        if cnt == 1:
            return ''
        elif cnt == 0:
            raise _illmove
        else:
            # try to fix src file
            cnt = count_up2(board.witerMove(self, WLoc(src.x, None), WLoc(dst), options))
            if cnt == 1:
                return str(src)[0]
            elif cnt == 0:
                raise _illmove
            else:
                # try to fix src rank
                cnt = count_up2(board.witerMove(self, WLoc(None, src.y), WLoc(dst), options))
                assert cnt <> 2 # still ambiguilty: impossible
                if cnt == 0:
                    raise _illmove
                return str(src)[1]

    def move_movesign_SAN(self, board, dst):
        if board[dst] is None:
            return ''
        elif board[dst].col == board.turn:
            return '^'
        else:
            return 'x'

    def move_actor_SAN(self):
        # the only exception is for pawn
        return self.sym

    def move_dst_SAN(self, dst):
        return str(dst)

    def move_promotion_SAN(self, options={}):
        np = options.get('promote')
        if np is None:
            return ''
        else:
            return '=' + np.sym

    def move_checksign_SAN(self, board, src, dst, options={}):
        # not implemented!
        return ''

    def move_SAN(self, board, src, dst, options={}):
        return self.move_actor_SAN() + self.move_src_SAN(board, src, dst, options) \
               + self.move_movesign_SAN(board, dst) + self.move_dst_SAN(dst) \
               + self.move_promotion_SAN(options) + self.move_checksign_SAN(board, src, dst, options={})
    
    

    def attacks(self, board, src, dst):
        """
        returns True iff the piece from 'src' attacks 'dst' no matter what is on 'dst'
        """
        try:
            self.reach(src, dst)(board)
            return True
        except IllegalMove:
            return False

    def show(self):
        """
        a rectangle 2x3 should be filled by these chars
        """
        sp = self.col.show()
        return (sp*3, sp+self.sym[0]+sp)

    def iterMove(self, board, src):
        """
        Returns an iterator which iterates all possible moves of this piece.
        Doesn't care whether any king is under attack.  This is a generic version for all pieces.
        """
        for dst in Loc.iter('*'):
            try:
                # a pawn may require 'options' argument, so this code is incorrect
                patch = self.move(src, dst)(board)
                yield patch
            except IllegalMove:
                pass
        
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
                    for cls in atomic_pieces+prime_pieces:
                        yield cls(col)
                    for cls1 in prime_pieces:
                        for cls2 in prime_pieces:
                            if cls1 <= cls2:
                                yield HybridPiece(cls1(col), cls2(col))
            else:
                raise Exception, "not implemented case"

    iter = staticmethod(iter)

    def ord(self):
        # each subclass should define it's ordinal number
        return self.__class__.ordinal
    
class AtomicPiece(Piece):
    symbols = tuple('KP')

    # subclasses should define class field 'symbol'

    def hybridable(self): return False

    def ishybrid(self): return False

class KingPiece(AtomicPiece):
    symbol = 'K'
    ordinal = 0 # the lowest

    oldKingLoc = {white: Loc(4, 0), black: Loc(4, 7)}

    # relative to oldKingLoc
    oldRookAffLoc = {queenside: AffLoc(-4, 0), kingside: AffLoc(3, 0)}
    #newKingAffLoc = {queenside: AffLoc(-2, 0), kingside: AffLoc(2, 0)}
    newRookAffLoc = {queenside: AffLoc(-1, 0), kingside: AffLoc(1, 0)}

    requiredEmpty = {queenside: [AffLoc(i,0) for i in (-1,-2,-3)],
                     kingside: [AffLoc(i,0) for i in (1,2)] }
    requiredUnattacked = {queenside: [AffLoc(i,0) for i in (0,-1,-2)],
                          kingside: [AffLoc(i,0) for i in (0,1,2)] }
    
    def move0(self, src, dst, options={}):
        fput = lambda board: (dst, (None, self))
        fhunks = [self.fturn(), self.fleave(src)]

        for flank in (queenside, kingside):
            fhunks.append(dropCastle(self.col, flank))

        x, y = (dst-src)()

        # ordinary move or capture
        if x is 0 and y in (-1, 1) or x in (-1, 1) and y in (-1, 0, 1):
            fhunks.append(self.fjoin(dst))
            return fiter(*fhunks)
            
        # castle
        if y is 0 and src == KingPiece.oldKingLoc[self.col]:
            if x is -2:
                flank = queenside
            elif x is 2:
                flank = kingside
            else:
                return fraise(IllegalMove, "invalid king move")

            # 1. check castle is not dropped
            def checkCastleAllowed(board):
                if not board.castle[self.col][flank]:
                    raise IllegalMove, "invalid king move: castle not allowed"

            fhunks.append(checkCastleAllowed)
            
            # 2. check empty squares
            def checkEmpty(board):
                for al in KingPiece.requiredEmpty[flank]:
                    l = src+al
                    if board[l] is not None:
                         raise IllegalMove, ("invalid king move: castle requires an empty square %s" % l)

            fhunks.append(checkEmpty)

            # 3. check unattacked squares
            def checkUnattacked(board):
                for al in KingPiece.requiredUnattacked[flank]:
                    dloc = src+al
                    # TODO: make more efficient search
                    for sloc in Loc.iter('*'):
                        piece = board[sloc]
                        if piece is not None and piece.col != self.col \
                           and piece.attacks(board, sloc, dloc):
                            raise IllegalMove, ("invalid king move: castle requires square %s not attacked" % dloc)

            fhunks.append(checkUnattacked)
            fhunks.append(fput)
            rook_src = src + KingPiece.oldRookAffLoc[flank]
            rook_dst = src + KingPiece.newRookAffLoc[flank]

            def rook_move(board):
                p = board[rook_src]
                if p.__class__ is RookPiece:
                    rook = p
                    leave = (rook, None)
                elif p.__class__ is HybridPiece:
                    if p.p1.__class__ is RookPiece:
                        rook = p.p1
                        leave = (p, p.p2)
                    elif p.p2.__class__ is RookPiece:
                        rook = p.p2
                        leave = (p, p.p1)
                    else:
                        raise IllegalMove, ("invalid king move: castle requires a Rook on %s" % rook_src)
                else:
                    raise IllegalMove, ("invalid king move: castle requires a Rook on %s" % rook_src)
                return [(rook_src, leave), (rook_dst, (None, rook))]

            fhunks.append(rook_move)
            return fiter(*fhunks)
            
        return fraise(IllegalMove, "invalid king move")        

    def attacks(self, board, src, dst):
        x, y = (dst-src)()
        return x is 0 and y in (-1, 1) or x in (-1, 1) and y in (-1, 0, 1)
        

class PawnPiece(AtomicPiece):
    symbol = 'P'
    ordinal = 1000 # the highest

    secondRank  = {white: 1, black: 6}
    seventhRank = {white: 6, black: 1}
    eighthRank  = {white: 7, black: 0}

    simpleMove = {white: AffLoc(0, 1), black: AffLoc(0, -1)}
    doubleMove = {white: AffLoc(0, 2), black: AffLoc(0, -2)}
    captureMoves = {white: (AffLoc(-1, 1), AffLoc(1, 1)), black: (AffLoc(1, -1), AffLoc(-1, -1))}

    def move0(self, src, dst, options={}):
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
            fhunks.append(lambda board: myassert(board[dst] == None,
                                                 IllegalMove, "this pawn is blocked"))
            if y == 2:
                # double move
                if not untouched:
                    return fraise(IllegalMove, "cannot make double move")
                nextfld = src+fwd
                fhunks.append(lambda board: myassert(board[nextfld] == None,
                                                     IllegalMove, "this pawn is blocked"))
                fhunks.append(lambda board: board.enpassantHunk(nextfld))
            elif y == 1:
                # simple move
                pass # nothigh to do
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
                return fraise(UnspecifiedPromotion)
        else:
            # FIXME: asesertion remove since it may fail due to witerMove()
            # assert not options.has_key('promote')
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
            if board.enpassantLoc() == dst:
                # remove enemy pawn
                # FIXME: extra checks...
                if self.col == white:
                    target_loc = dst+AffLoc(0,-1)
                else:
                    target_loc = dst+AffLoc(0,1)
                target = board[target_loc]
                # requre target is enemy pawn
                assert target.col != self.col and target.__class__ == self.__class__
                return (target_loc, (target, None))
            raise IllegalMove, "invalid pawn's capture move"
        return f

    def attacks(self, board, src, dst):
        """
        the pawn really attacks 'dst', i.e. pawn on e2 does not attack neither e3 nor e4
        """
        x, y = (dst-src)()
        return abs(x) == 1 and ((self.col, y) in ((white, 1), (black, -1)))

    def iterMove(self, board, src):
        """
        returns an iterator of all possible pawn moves
        """
        # FIXME: too many extra cases are checked if move() is used,
        # it may lead to error...
        def iterDst():
            try:
                for shift in PawnPiece.captureMoves[self.col]:
                    yield src+shift
            except ValueError:
                # out of range
                pass
            yield src + PawnPiece.simpleMove[self.col]
            if src.y == PawnPiece.secondRank[self.col]:
                yield src + PawnPiece.doubleMove[self.col]

        if src.y == PawnPiece.seventhRank[self.col]:
            for dst in iterDst():
                for cls in RookPiece, BishopPiece, KnightPiece, GuardPiece:
                    try:
                        yield self.move(src, dst, {'promote': cls(self.col)})(board)
                    except IllegalMove:
                        # do not try other promotions
                        # FIXME: it is more reilable to say 'pass' instead of 'break'
                        break
        else:
            for dst in iterDst():
                try:
                    yield self.move(src, dst)(board)
                except IllegalMove:
                    pass

    def move_actor_SAN(self):
        # the only exception is for pawn
        return ''

    def move_SAN(self, board, src, dst, options={}):
        if board[dst] is None and not board.enpassantLoc() == dst:
            res = str(dst)
        else:
            # capture
            cnt = count_up2(board.witerMove(self, WLoc(src.x, None), WLoc(dst.x, None), options))
            if cnt == 1:
                res = str(src)[0] + 'x' + str(dst)[0]
            elif cnt == 0:
                raise _illmove
            else:
                cnt = count_up2(board.witerMove(self, WLoc(src.x, None), WLoc(dst), options))
                assert cnt <> 2 # still ambiguilty: impossible
                if cnt == 1:
                    res = str(src)[0] + 'x' + str(dst)
                elif cnt == 0:
                    raise _illmove
            
        np = options.get('promote')
        if np is not None:
            res += ('=' + np.sym)
        return res
            

class RangedPiece(object):
    """
    common class for ranged pieces: Rook and Bishop
    """

    def reach(self, src, dst):
        return lambda board: self.reach0(board, src, dst)
    
class PrimePiece(Piece):
    symbols = tuple('RBNG')

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
        if self.ord() < other.ord():
            return self, other
        else:
            return other, self


class RookPiece(RangedPiece, PrimePiece):
    symbol = 'R'
    ordinal = 1

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
    ordinal = 2
    
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
    ordinal = 3

    def reach(self, src, dst):
        x, y = (dst-src)()
        x, y = abs(x), abs(y)
        if (x==1 and y==2) or (x==2 and y==1):
            return fconst_None

        return fraise(IllegalMove, "invalid knight move")


class GuardPiece(PrimePiece):
    """Guard moves like a (nonroyal) king"""
    symbol = 'G'
    ordinal = 4

    def reach(self, src, dst):
        x, y = (dst-src)()
        x = abs(x)
        if   x == 0:
            if abs(y) == 1: return fconst_None
        elif x == 1:
            if abs(y) <= 1: return fconst_None

        return fraise(IllegalMove, "invalid guard move")

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
    
    def ord(self):
        raise TypeError, "ord() not supported for hybrids"

atomic_pieces = PawnPiece, KingPiece
prime_pieces = RookPiece, BishopPiece, KnightPiece, GuardPiece
