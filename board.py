"""
Module board.  Here defined a mutable class 'board' which represents
the current position and history of the whole game.
"""

__Id__ = "$Id$"
# __all__ = []

from atoms import *
from pieces import *

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
        self.gameover = None
        self.turn = None
        self.semimoveCount = 0
        self.locs = {}
        for x in range(8):
            for y in range(8):
                self[(x,y)] = None
    
        self.history = []
        self.historyEnd = 0

        # en-passant state is a pair (loc_or_None, semimoveCnt);
        # if this value equals to (loc, self.semimoveCount) then en-passant move over this loc is allowed;
        # for obsolete/non-valid semimoveCnt: (loc, semimoveCnt) is assumed to equal (None, _)
        self.enpassant = (None, 0)

        # whether casting is possible (for 'hybrids' variant it is never possible)
        self.castle_white = None
        self.castle_black = None

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
8|.R.|.N.|.B.|.Q.|.K.|.B.|.N.|.R.|8
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
1| R | N | B | Q | K | B | N | R |1
-+---+---+---+---+---+---+---+---+-
 | a | b | c | d | e | f | g | h | 
"""
        if not variant in Board.variants:
            raise Exception, ("variant '%s' is not supported" % variant)

        self.variant = variant
        
        self.semimoveCount = 0
        self.turn = white
        self.history = []
        self.historyEnd = 0
        self.enpassant = (None, 0)

        if variant == 'ortodox':
            raise "ortodox pieces should be set..."
            
            self.castle_white = self.castle_black = True
        elif variant == 'hybrids':
            for x, cls in zip(range(8), [RookPiece, KnightPiece, BishopPiece, QueenPiece,
                                         KingPiece, BishopPiece, KnightPiece, RookPiece]):
                self[(x,0)] = cls(white)
                self[(x,7)] = cls(black)

            # in hybrids no castling allowed at all
            self.castle_white = self.castle_black = False
            
        for x in range(8):
            self[(x,1)] = PawnPiece(white)
            self[(x,6)] = PawnPiece(black)

        for x in range(8):
            for y in range(2, 6):
                self[(x, y)] = None

    def applyHunk(self, loc, (old, new)):
        if loc.__class__ == Loc:
            # perform a sanity check
            if(old != self[loc]):
                raise ("hunk (%s: %s -> %s) failed" % (loc, old, new))
            self[loc] = new
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
        self.history[self.semimoveCount:] = [patch]
        self.semimoveCount += 1
        self.turn = self.turn.inv()
    
    def undo(self):
        assert self.semimoveCount >= 0
        if self.semimoveCount == 0:
            raise "undo: it's the first position"
        self.semimoveCount -= 1
        self.applyPatch(self.history[self.semimoveCount], 'rev')
        self.turn = self.turn.inv()

    def redo(self):
        assert self.semimoveCount <= self.historyEnd
        if self.semimoveCount == self.historyEnd:
            raise "redo: it's the last position"
        self.applyPatch(self.history[self.semimoveCount])
        self.semimoveCount += 1
        self.turn = self.turn.inv()

    def iterMove(self, wpiece, wsrc, wdst, options={}):
        for dst in Loc.iter(*wdst):
            for piece in Piece.iter(*wpiece):
                for src in Loc.iter(*wsrc):
                    try:
                        patch = piece.move(src, dst, options)(self)
                        self.makeMove(patch)
                        self.undo()
                        yield patch
                    except IllegalMove:
                        pass
                    
    def kingAttacked(self, myCol):
        """
        Checks whether our king is under attack (after last move).
        Optional 'patch' is just for efficiency
        """
        
        # FIXME: enhance the position representation to make this search more convenient
        # TODO: use patch
        myKing = KingPiece(myCol)
        for dst in Loc.iter('*'):
            if self[dst] == myKing: break
        # assert self[dst] == myKing # assertion fails if no myKing found on the board
        # FIXME
        if self[dst] != myKing: return False

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
        for x in self.iterMove(('*', ), ('*', ), ('*', )):
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
        promote (None, R, Q, B, N), capture (True, False), hybrid, i.e. 'going to hybrid' (True, False),
        check (None, 'check', 'mate').
        all keys except 'promote' may be ignored"""

        # IllegalMove may be raised
        patch = piece.move(src, dst, options)(self)
        self.makeMove(patch)
        self.historyEnd = self.semimoveCount

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
        return ('enpassant', (self.enpassant, (loc, self.semimoveCount+1)))

    def enpassantLoc(self):
        """
        returns phantom location or None if en-passant is impossible now
        """
        (loc, cnt) = self.enpassant
        if cnt == self.semimoveCount:
            return loc
        else:
            return None
    

# test suite
b = Board()


defs = {}
globs = globals()
prime_pieces = RookPiece, KnightPiece, BishopPiece, QueenPiece
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

del defs, globs, prime_pieces

# print available moves
# for x in b.iterMove(('*', ), ('*', ) , '*'): print x
