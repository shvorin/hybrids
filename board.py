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
        self.turn = None
        self.semimoveCount = 0
        self.locs = {}
        for x in range(8):
            for y in range(8):
                self[(x,y)] = None
    
        self.history = []

        # en-passant may be None either (loc, semimoveCnt);
        # if this value equals to (loc, self.semimoveCount) then en-passant move over this loc is allowed;
        # for obsolete/non-valid semimoveCnt: (loc, semimoveCnt) is assumed to equal None
        self.enpassant = None

        # whether casting is possible (for 'hybrids' variant it is never possible)
        self.castle_white = None
        self.castle_black = None

        # only 2 chess variants are supported: 'ortodox' and 'hybrids'
        self.variant = None

        self.setup(variant)

    def enpassant_possible(self, loc):
        return self.enpassant == (loc, self.semimoveCount)
    
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
        self.enpassant = None

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
        # perform a sanity check
        if(old != self[loc]):
            raise ("hunk (%s: %s -> %s) failed" % (loc, old, new))
        self[loc] = new
        

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
        self.applyPatch(patch)
        # clear history from the future
        self.history[self.semimoveCount:] = []
        self.semimoveCount += 1
        self.turn = self.turn.inv()
        self.history.append(patch)
    
    def undo(self):
        if self.semimoveCount == 0:
            raise "undo: it the first position"
        self.applyPatch(self.history[self.semimoveCount-1], rev=True)
        self.semimoveCount = self.semimoveCount-1
        self.turn = self.turn.inv()

    def redo(self):
        if len(self.history) == self.semimoveCount:
            raise "redo: it the last position"
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
                        # check for checks
                        if self.check_last_move():
                            yield patch
                        # FIXME: check for mate/stalemate
                        self.undo()
                    except IllegalMove:
                        pass
                    except Exception, e:
                        print ("(%s)" % piece, src, dst)
                    
    def check_last_move(self):
        return True # not implemented

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

        
# test suite
b = Board()
# print available moves
# for x in b.iterMove(('*', ), ('*', ) , '*'): print x
