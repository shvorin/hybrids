"""
Module board.  Here defined a mutable class 'board' which represents
the current position and history of the whole game.
"""

__Id__ = "$Id$"
# __all__ = []

from atoms import *
from pieces import *
from gamehist import *

# auxillary definitions...

# an iterator
def reverse(data):
    for index in range(len(data)-1, -1, -1):
        yield data[index]

def Const(v):
    return lambda x: v


class Board:

    # supported chess variants
    variants = ('ortodox', 'hybrids')

    def __init__(self, variant='hybrids'):
        """
        NB: all instance values should be defined here
        """
        self.gameover = None

        # turn to move: white either black
        self.turn = None

        # An inner table maps locations to the corresponding pieces (or None if the field is empty).
        # Don't access it directly, use __getitem__, __setitem__ methods instead.
        self.locs = {}
        for x in range(8):
            for y in range(8):
                self[(x,y)] = None

        # Maps pieces to location lists.
        # Don't access it directly, it should be updated in applyHunk only
        self.pieceMap = {}
        self.clearPieceMap()
    
        # en-passant state is a pair (loc_or_None, ply);
        # if this value equals to (loc, self.gamehist.currPly) then en-passant move over this loc is allowed;
        # for obsolete/non-valid ply: (loc, ply) is assumed to equal (None, _)
        self.enpassant = (None, 0)

        # whether casting is possible (for 'hybrids' variant it is never possible)
        self.castle_white = None
        self.castle_black = None

        # history is a stack of patches
        self.gamehist = None

        # only 2 chess variants are supported: 'ortodox' and 'hybrids'
        self.variant = None

        self.setup(variant)

    def __getitem__(self, loc):
        return self.locs[Loc(loc)]

    def __setitem__(self, loc, v):
        self.locs[Loc(loc)] = v
    
    def __str__(self):
        "shows current position in human-readable format"
        s = ''
        s += ' | a | b | c | d | e | f | g | h | \n'
        s += '-+---+---+---+---+---+---+---+---+-\n'
        for y in range(7, -1, -1):
            for i in range(2):
                if i==1:
                    extra = str(y+1)
                else:
                    extra = ' '
                s += extra
                for x in range(8):
                    s += '|'
                    p = self[Loc(x, y)]
                    if p == None:
                        s += ' '*3
                    else:
                        s += p.show()[i]
                s += '|' + extra + '\n'
            s += '-+---+---+---+---+---+---+---+---+-\n'
        s += ' | a | b | c | d | e | f | g | h | \n'
        return s
    
    def setup(self, variant='hybrids'):
        """
        setups initial position; __str__() will show the following:

 | a | b | c | d | e | f | g | h | 
-+---+---+---+---+---+---+---+---+-
 |...|...|...|...|...|...|...|...| 
8|.R.|.N.|.B.|.G.|.K.|.B.|.N.|.R.|8
-+---+---+---+---+---+---+---+---+-
 |...|...|...|...|...|...|...|...| 
7|.P.|.P.|.P.|.P.|.P.|.P.|.P.|.P.|7
-+---+---+---+---+---+---+---+---+-
 |   |   |   |   |   |   |   |   | 
6|   |   |   |   |   |   |   |   |6
-+---+---+---+---+---+---+---+---+-
 |   |   |   |   |   |   |   |   | 
5|   |   |   |   |   |   |   |   |5
-+---+---+---+---+---+---+---+---+-
 |   |   |   |   |   |   |   |   | 
4|   |   |   |   |   |   |   |   |4
-+---+---+---+---+---+---+---+---+-
 |   |   |   |   |   |   |   |   | 
3|   |   |   |   |   |   |   |   |3
-+---+---+---+---+---+---+---+---+-
 |   |   |   |   |   |   |   |   | 
2| P | P | P | P | P | P | P | P |2
-+---+---+---+---+---+---+---+---+-
 |   |   |   |   |   |   |   |   | 
1| R | N | B | G | K | B | N | R |1
-+---+---+---+---+---+---+---+---+-
 | a | b | c | d | e | f | g | h | 
"""
        if not variant in Board.variants:
            raise Exception, ("variant '%s' is not supported" % variant)

        self.variant = variant
        
        self.turn = white
        self.gamehist = GameHist(Variant=self.variant)
        self.gamehist.setup()
        self.enpassant = (None, 0)

        if variant == 'ortodox':
            raise "ortodox pieces should be set..."
            
            self.castle_white = self.castle_black = True
        elif variant == 'hybrids':
            self.clearPieceMap()
            
            for x, cls in zip(range(8), [RookPiece, KnightPiece, BishopPiece, GuardPiece,
                                         KingPiece, BishopPiece, KnightPiece, RookPiece]):
                for col, y in (white, 0), (black, 7):
                    loc = Loc(x, y)
                    p = cls(col)
                    self[loc] = p
                    self.pieceMap[p].append(loc)

            # in hybrids no castling allowed at all
            self.castle_white = self.castle_black = False
            
        for x in range(8):
            for col, y in (white, 1), (black, 6):
                loc = Loc(x, y)
                p = PawnPiece(col)
                self[loc] = p
                self.pieceMap[p].append(loc)

        for x in range(8):
            for y in range(2, 6):
                self[(x, y)] = None

    def applyHunk(self, loc, (old, new)):
        if loc.__class__ == Loc:
            # perform a sanity check
            if(old != self[loc]):
                raise ("hunk (%s: %s -> %s) failed" % (loc, old, new))
            self[loc] = new
            if old:
                self.pieceMap[old].remove(loc)
            if new:
                self.pieceMap[new].append(loc)
        # special case(s) follows
        elif loc == 'enpassant':
            # sanity check
            if old != self.enpassant:
                raise ("special hunk (%s -> %s) failed" % (old, new))
            self.enpassant = new
        else:
            raise 'applyHunk: unknown special case'

    def applyPatch(self, patch, rev=False):
        """Applies a patch (a list of hunks) to the current position.
A single hunk is a triple: location, a piece a this location to be removed
and a new piece to be placed at this location.

It should not be called directly, since it alters the board, but does nothing
with history.
"""
        if rev:
            for (loc, (old, new)) in reverse(patch):
                self.applyHunk(loc, (new, old))
        else:
            for hunk in patch:
                self.applyHunk(*hunk)
    
    def makeMove(self, patch):
        """tries to apply the patch and alters the history"""
        if self.gameover:
            raise IllegalMove, ("game already finished (result is %s)" % self.gameover)
        self.applyPatch(patch)
        # check if we our king is under attack
        if self.kingAttacked(self.turn):
            self.applyPatch(patch, 'rev')
            raise IllegalMove, ("%s king is left under attack" % self.turn)
        self.gamehist.apply(patch)
        self.turn = self.turn.inv()
    
    def undo(self):
        self.applyPatch(self.gamehist.prev(), 'rev')
        self.turn = self.turn.inv()

    def redo(self):
        self.applyPatch(self.gamehist.next())
        self.turn = self.turn.inv()

    def iterMove(self):
        # FIXME: is it better to check more mobile pieces first?
        for p in self.pieceMap.iterkeys():
            # FIXME: do keep white and black apart?
            if p.col != self.turn:
                continue
            for src in self.pieceMap[p]:
                for patch in p.iterMove(self, src):
                    try:
                        # check whether king is under attack
                        self.makeMove(patch)
                        self.undo()
                        yield patch
                    except IllegalMove:
                        pass
                    
    def kingAttacked(self, myCol, patch=None):
        """
        Checks whether our king is under attack (after last move).
        Optional 'patch' is just for efficiency
        """
        
        # FIXME: enhance the position representation to make this search more convenient
        # TODO: use patch
        myKing = KingPiece(myCol)
        try:
            [dst] = self.pieceMap[myKing]
        except Exception, e:
            if e.__class__ == ValueError or e.__class__ == KeyError:
                raise "no %s king found at the board" % myCol
            else:
                raise e

        # TODO: make more efficient search
        for src in Loc.iter('*'):
            piece = self[src]
            if piece and piece.col != myCol:
                if piece.attacks(self, src, dst):
                    return True
        return False

    def detectMate(self):
        """
        says whether current position is check/mate/stalemate
        """
        for x in self.iterMove():
            move_possible = True
            break
        else:
            move_possible = False

        check = self.kingAttacked(self.turn)

        if check:
            if move_possible: return 'check'
            else: return 'mate'
        else:
            if move_possible: return None
            else: return 'stalemate'

    # FIXME: name: it returns a patch (appliable for makeMove())
    def move(self, piece, src, dst, options={}):
        """a (parsed) move is:
        (piece, src, dst, ?options?), where dict options may contain the following keys:
        promote (None, R, G, B, N), capture (True, False), hybrid, i.e. 'going to hybrid' (True, False),
        check (None, 'check', 'mate').
        all keys except 'promote' may be ignored"""

        # IllegalMove may be raised
        patch = piece.move(src, dst, options)(self)
        self.makeMove(patch)
        self.gamehist.commit()

        # check for check/mate/stalemate after the move
        result = self.detectMate()
        if result == 'check':
            print 'check'
        elif result == 'stalemate':
            print 'stalemate:\nResult: 1/2:1/2'
            self.gameover = 'draw'
        elif result == 'mate':
            winner = self.turn.inv()
            if winner == white:
                score = '1:0'
            else:
                score = '0:1'
            print ('mate, %s win:\nResult: %s' % (winner, score))
            self.gameover = score
        else:
            assert result == None

    def enpassantHunk(self, loc):
        """
        returns new en-passant hunk appliable to the current position
        """
        return ('enpassant', (self.enpassant, (loc, self.gamehist.currPly+1)))

    def enpassantLoc(self):
        """
        returns phantom location or None if en-passant is impossible now
        """
        (loc, cnt) = self.enpassant
        if cnt == self.gamehist.currPly:
            return loc
        else:
            return None

    def clearPieceMap(self):
        for col in black, white:
            for cls in atomic_pieces+prime_pieces:
                self.pieceMap[cls(col)] = []

            for cls1 in prime_pieces:
                for cls2 in prime_pieces:
                    # don't care about repetitions
                    self.pieceMap[HybridPiece(cls1(col), cls2(col))] = []

# test suite
b = Board()


defs = {}
globs = globals()
for col in white, black:
    c = col.__str__()[0]
    for cls in prime_pieces:
        name = c+cls.symbol
        assert not globs.has_key(name)
        defs[name] = cls(col)

        for cls2 in prime_pieces:
            name = c+cls.symbol+cls2.symbol
            assert not globs.has_key(name)
            # don't care about redefinitions
            defs[name] = HybridPiece(cls(col), cls2(col))

    for cls in KingPiece, PawnPiece:
        name = c+cls.symbol
        assert not globs.has_key(name)
        defs[name] = cls(col)

for (name, val) in defs.iteritems():
    globs[name] = val

del defs, globs

# print available moves
# for x in b.iterMove(('*', ), ('*', ) , '*'): print x
