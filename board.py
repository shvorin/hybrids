
__Id__ = "$Id$"

#from Tkinter import *

# Atoms
(E, K, P, R, Q, B, N) = range(7)
(white, black) = (0, 1)

bpieces = [K, P]
spieces = [R, Q, B, N]
pieces  = bpieces + spieces

showColor = {white: ' ', black: '.'}
showPiece = {K: 'K', P: 'P', R: 'R', Q: 'Q', B: 'B', N: 'N'}

# forward declaration
pieceObjects = {}

def sort2((p1, p2)):
    if p1 > p2:
        return (p2, p1)
    else:
        return (p1, p2)

def aff_sub((x1, x2), (y1, y2)):
    "affinity subtraction"
    return (x1-y1, x2-y2)

def aff_add((x1, x2), (y1, y2)):
    "affinity addition"
    return (x1+y1, x2+y2)

# an iterator
def reverse(data):
    for index in range(len(data)-1, -1, -1):
        yield data[index]

# do not rely on representation (i.e. don't use "not color")
def invColor(col):
    if col == black: return white
    else: return black

letters = {}
for letter, num in zip("abcdefgh", range(8)):
    letters[letter] = num

def scanPos(s):
    return (letters[s[0]], int(s[1])-1)

class IllegalMove(Exception):
    pass

class Board:
    turn = None
    semimoveCount = 0
    locs = {}
    for x in range(8):
        for y in range(8):
            locs[(x,y)] = E
    
    b_pieces = {}
    w_pieces = {}
    for p in pieces:
        b_pieces[p] = []
        w_pieces[p] = []
    
    history = []
    
    def getLoc(self, pos):
        return self.locs[pos]
    
    def dump(self):
        s = ''
        s = s + ' | a | b | c | d | e | f | g | h | \n'
        s = s + '-+---+---+---+---+---+---+---+---+-\n'
        for y in range(7, -1, -1):
            for i in range(2):
                if i==1:
                    extra = str(y+1)
                else:
                    extra = ' '
                s = s + extra
                for x in range(8):
                    s = s + '|'
                    loc = self.getLoc((x, y))
                    if loc == E:
                        s = s + ' '*3
                    else:
                        s = s + pieceObjects[loc].show()[i]
                s = s + '|' + extra + '\n'
            s = s + '-+---+---+---+---+---+---+---+---+-\n'
        s = s + ' | a | b | c | d | e | f | g | h | \n'
        return s
    
    def setup(self):
        """setups initial position; dump() will show the following:

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
        self.semimoveCount = 0
        self.turn = white
        history = []
        
        for p, xs in zip([R, N, B, Q, K], [[0,7], [1,6], [2,5], [3], [4]]):
            self.w_pieces[p] = [(x, 0) for x in xs]
            self.b_pieces[p] = [(x, 7) for x in xs]
        
        self.w_pieces[P] = [(x, 1) for x in range(8)]
        self.b_pieces[P] = [(x, 6) for x in range(8)]
        
        for p, poses in self.w_pieces.iteritems():
            for pos in poses:
                self.locs[pos] = (p, white)
        
        for p, poses in self.b_pieces.iteritems():
            for pos in poses:
                self.locs[pos] = (p, black)

    def applyPatch(self, patch, rev=False):
        """Applies a patch (a list of hunks) to the current position.
A single hunk is a triple: location, a piece a this location to be removed
and a new piece to be placed at this location.

It should not be called directly, since it alters the board, but does nothing
with history.
"""
        if rev:
            for (pos, old, new) in reverse(patch):
                # perform a sanity check
                if(new != self.getLoc(pos)):
                    raise "hunk failed"
                self.locs[pos] = old
        else:
            for (pos, old, new) in patch:
                # perform a sanity check
                if(old != self.getLoc(pos)):
                    raise "hunk failed"
                self.locs[pos] = new
    
    def makeMove(self, patch):
        self.applyPatch(patch)
        # clear history from the future
        self.history[self.semimoveCount:] = []
        self.semimoveCount = self.semimoveCount+1
        self.turn = invColor(self.turn)
        self.history.append(patch)
    
    def undo(self):
        if self.semimoveCount == 0:
            raise "undo: it the first position"
        self.applyPatch(self.history[self.semimoveCount-1], rev=True)
        self.semimoveCount = self.semimoveCount-1

    def redo(self):
        if len(self.history) == self.semimoveCount:
            raise "redo: it the last position"
        self.applyPatch(self.history[self.semimoveCount])
        self.semimoveCount = self.semimoveCount+1

    # FIXME: name: it returns a patch (appliable for makeMove())
    def move(self, sym, src, dst, options):
        """(parsed) move is:
        (piece, src, dst, options), where dict options may contain the following keys:
        promote (None, R, Q, B, N), capture (True, False), hybrid (True, False), check (None, check, mate).
        all keys except 'promote' may be ignored"""
        src_piece = self.locs[src]
        if src_piece == E:
            raise IllegalMove, ("source position %s is empty" % str(src))
        (src_sym, src_col) = src_piece
        if src_col != self.turn:
            raise IllegalMove, "attempt to move ememy's piece"
        
        movingPiece = pieceObjects[sym]
        NotImplemented
        

class Piece:
    def __init__(self, sym, col):
        self.sym = sym
        self.col = col
    
    def leave(self, src):
        "returns a pos-patch 'the piece leaves position'.  non-hybriding"
        if src == (self.sym, self.col):
            return (E, src)
        else:
            raise IllegalMove, "no such piece on this position"
    
    def join(self, dst):
        "returns a pos-patch 'the piece joins position'.  non-hybriding"
        if dst == E or dst[1] != self.col:
            return (dst, (self.sym, self.col))
        else:
            raise IllegalMove, "target position is occupied by a piece of the same color"
    
    def moveto(self, board, src, dst):
        raise "pure virtual"
    
    def isReachable(self, src, dst):
        "returns True iff dst is reachable from src for some board position"
        raise "pure virtual"
        
    def isHybriding(self):
        return False
    
    def isHybrid(self):
        return False
    
    def show(self):
        sp = showColor[self.col]
        p0 = showPiece[self.sym]
        return (sp*3, sp+p0+sp)


# with hybriding ability
class SPiece(Piece):
    def isHybriding(self):
        return True
    
    def leave(self, src):
        "returns a pos-patch 'the piece leaves position'. hybriding"
        if src == E:
            raise IllegalMove, "attempt to move from empty position"
        (sym, col) = src
        if col != self.col:
            raise IllegalMove, "attempt to move evemy's piece"
        if sym == self.sym:
            rest = E
        elif sym[0] == self.sym:
            rest = sym[1]
        elif sym[1] == self.sym:
            rest = sym[0]
        else:
            raise IllegalMove, "no such piece on this position"
        return (source, rest)
    
    def join(self, dst):
        "returns a pos-patch 'the piece joins position'. hybriding"
        me = (self.sym, self.col)
        if dst == E:
            return (dst, me)
        (sym, col) = dst
        if col != self.col:
            return (dst, me)
        # try to make a new hybrid
        if pieceObjects[sym].isHybridable():
            return (dst, (sort2(sym, self.sym), self.col))
        else:
            raise IllegalMove, "non-hybridable piece on the target position"

class Hybrid(Piece):
    def __init__(self, sym, col):
        self.col = col
        self.sym = sort2(sym) # let's keep'em sorted
    
    def isHybrid(self):
        return True
    
    def leave(self, src):
        "returns a pos-patch 'the piece leaves position'"
        if src != (self.sym, self.col):
            raise IllegalMove, "no such hybrid piece on this position"
        return (src, E)
    
    def join(self, dst):
        "returns a pos-patch 'the piece joins position'"
        if dst == E or dst[1] != self.col:
            return (target, (self.sym, self.col))
        else:
            raise IllegalMove, "target position is occupied"
    
    def show(self):
        """returns a pair like this:
.N.
.R.
"""
        sp = showColor[self.col]
        (sym1, sym2) = self.sym
        p1 = showPiece[sym1]
        p2 = showPiece[sym2]
        return (sp+p2+sp, sp+p1+sp)
    
    def isReachable(self, src, dst):
        (sym1, sym2) = self.sym
        col = self.col
        return pieceObjects[(sym1, col)].isReachable(src, dst) or \
               (sym1 != sym2 and pieceObjects[(sym2, col)].isReachable(src, dst))

class King(Piece):
    def isReachable(self, src, dst):
        (x, y) = aff_sub(dst, src)
        if abs(x) == 0: return abs(y) == 1
        else:           return abs(y) <= 1
        
class Pawn(Piece):
    def isReachable(self, src, dst):
        (x, y) = aff_sub(dst, src)
        if self.col == black:
            y = -y
            is_moved = src[1] - 6
        else:
            is_moved = src[1] - 1
        return (y == 1 and abs(x) <= 1) or (y == 2 and not is_moved)

class Rook(SPiece):
    def isReachable(self, src, dst):
        (x, y) = aff_sub(dst, src)
        # FIXME: I'd like to have xor in python
        if x==0: return y != 0
        else:    return y == 0

class Queen(SPiece):
    "Note, in hybrids the queen moves in the same manner as the king!"
    isReachable = King.isReachable

class Bishop(SPiece):
    def isReachable(self, src, dst):
        (x, y) = aff_sub(dst, src)
        if x==0: return False
        else:    return abs(x) == abs(y)

class Knight(SPiece):
    def isReachable(self, src, dst):
        (x, y) = aff_sub(dst, src)
        (x, y) = (abs(x), abs(y))
        return (x==1 and y==2) or (x==2 or y==1)

def init_pieceObjects():
    map = {K: King, P: Pawn, Q: Queen, R: Rook, B: Bishop, N: Knight}
    
    # init pieceObjects                
    for col in [black, white]:
        for sym in pieces:
            pieceObjects[(sym, col)] = map[sym](sym, col)
            # hybrids
            for sym1 in spieces:
                for sym2 in spieces:
                    if sym1 <= sym2:
                        pieceObjects[((sym1, sym2), col)] = Hybrid((sym1, sym2), col)

init_pieceObjects()


    


# test suite
b = Board()
b.setup()

