
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

class Board:
    turn = None
    moveCount = 0
    locs = {}
    for x in range(8):
        for y in range(8):
            locs[(x,y)] = E
    
    b_pieces = {}
    for p in pieces:
        b_pieces[p] = []
    w_pieces = b_pieces
    
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
 |...|...|...|...|...|...|...|...| 
-+---+---+---+---+---+---+---+---+-
 |...|...|...|...|...|...|...|...| 
7|.P.|.P.|.P.|.P.|.P.|.P.|.P.|.P.|7
 |...|...|...|...|...|...|...|...| 
-+---+---+---+---+---+---+---+---+-
 |   |   |   |   |   |   |   |   | 
6|   |   |   |   |   |   |   |   |6
 |   |   |   |   |   |   |   |   | 
-+---+---+---+---+---+---+---+---+-
 |   |   |   |   |   |   |   |   | 
5|   |   |   |   |   |   |   |   |5
 |   |   |   |   |   |   |   |   | 
-+---+---+---+---+---+---+---+---+-
 |   |   |   |   |   |   |   |   | 
4|   |   |   |   |   |   |   |   |4
 |   |   |   |   |   |   |   |   | 
-+---+---+---+---+---+---+---+---+-
 |   |   |   |   |   |   |   |   | 
3|   |   |   |   |   |   |   |   |3
 |   |   |   |   |   |   |   |   | 
-+---+---+---+---+---+---+---+---+-
 |   |   |   |   |   |   |   |   | 
2| P | P | P | P | P | P | P | P |2
 |   |   |   |   |   |   |   |   | 
-+---+---+---+---+---+---+---+---+-
 |   |   |   |   |   |   |   |   | 
1| R | N | B | Q | K | B | N | R |1
 |   |   |   |   |   |   |   |   | 
-+---+---+---+---+---+---+---+---+-
 | a | b | c | d | e | f | g | h |
"""
        for x in range(8):
            self.locs[(x,1)] = (P, white)
            self.locs[(x,6)] = (P, black)
        for x, p in zip(range(8), [R, N, B, Q, K, B, N, R]):
            self.locs[x,0] = (p, white)
            self.locs[x,7] = (p, black)

class Piece:
    def __init__(self, sym, col):
        self.sym = sym
        self.col = col
    
    def leave(self, board, pos):
        raise "pure virtual"
    
    def join(self, board, pos):
        raise "pure virtual"
    
    def moveto(self, board, src, dst):
        raise "pure virtual"
    
    def isHybriding(self):
        return False
    
    def isHybrid(self):
        return False
    
    def show(self):
        sp = showColor[self.col]
        p0 = showPiece[self.sym]
        return (sp*3, sp+p0+sp)

# no hybriding ability
class BPiece(Piece):
    def leave(self, board, pos):
        "returns a pos-patch 'the piece leaves position'"
        source = board.getLoc(pos)
        if source == (self.sym, self.col):
            return (source, E)
        else:
            raise "invalid src"
    
    def join(self, board, pos):
        "returns a pos-patch 'the piece joins position'"
        target = board.getLoc(pos)
        if target == E or target[1] != self.col:
            return (target, (self.sym, self.col))
        else:
            raise "invalid dst"

# with hybriding ability
class SPiece(Piece):
    def isHybriding(self):
        return True
    
    def leave(self, board, pos):
        "returns a pos-patch 'the piece leaves position'"
        source = board.getLoc(pos)
        if source == E:
            raise "invalid src"
        (sym, col) = source
        if col != self.col:
            raise "invalid src"
        if sym == self.sym:
            rest = E
        elif sym[0] == self.sym:
            rest = sym[1]
        elif sym[1] == self.sym:
            rest = sym[0]
        else:
            raise "invalid src"
        return (source, rest)
    
    def join(self, board, pos):
        "returns a pos-patch 'the piece leaves position'"
        target = board.getLoc(pos)
        me = (self.sym, self.col)
        if target == E:
            return (target, me)
        (sym, col) = target
        if col != self.col:
            return (target, me)
        # try to make a new hybrid
        if pieceObjects[sym].isHybridable():
            return (target, (sort2(sym, self.sym), self.col))
        else:
            raise "invalid dst"

class Hybrid(Piece):
    def __init__(self, sym, col):
        self.col = col
        self.sym = sort2(sym) # let's keep'em sorted
    
    def isHybrid(self):
        return True
    
    def leave(self, board, pos):
        "returns a pos-patch 'the piece leaves position'"
        source = board.getLoc(pos)
        if source != (self.sym, self.col):
            raise "invalid src"
        return (source, E)
    
    def join(self, board, pos):
        "returns a pos-patch 'the piece joins position'"
        target = board.getLoc(pos)
        if target == E or target[1] != self.col:
            return (target, (self.sym, self.col))
        else:
            raise "invalid dst"
    
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

class King(BPiece):
    pass

class Pawn(BPiece):
    pass

class Rook(SPiece):
    pass

class Queen(SPiece):
    pass

class Bishop(SPiece):
    pass

class Knight(SPiece):
    pass

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

