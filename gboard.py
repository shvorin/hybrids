

__id__ = "$Id$"
# __all__ = []

from Tkinter import *
from board import *
from pieces import *

class GBoard:
    photoimages = {}

    def init_photoimages():
        for piece, filename in ((wP, 'pawnw.gif'),
                                (bP, 'pawnb.gif'),
                                (wK, 'kingw.gif'),
                                (bK, 'kingb.gif'),
                                (wR, 'rookw.gif'),
                                (bR, 'rookb.gif'),
                                (wB, 'bishopw.gif'),
                                (bB, 'bishopb.gif'),
                                (wN, 'knightw.gif'),
                                (bN, 'knightb.gif'),
                                (wQ, 'queenw.gif'),
                                (bQ, 'queenb.gif')):
            GBoard.photoimages[piece] = PhotoImage(file=filename)
            
    init_photoimages = staticmethod(init_photoimages)


    def __init__(self, board=None):
        if board:
            self.board = board
        else:
            self.board = Board()
            self.board.setup()

        # maps locs to all drawn pieces
        self.boardDrawn = {}
        for x in range(8):
            for y in range(8):
                self.boardDrawn[Loc(x,y)] = ()

        self.selectedItems = ()
        
        self.root = Tk()
        if not GBoard.photoimages:
            GBoard.init_photoimages()
        
        # FIXME: show various variants
        self.root.wm_title("chess ('%s' variant)" % self.board.variant)
        self.root.wm_iconname("chess")

        self.xsize = self.ysize = 48

        self.c = Canvas()
        self.c.config(background='white',
                 height=10*self.xsize,
                 width=10*self.ysize)
        self.c.create_rectangle(self.xsize-1, self.ysize-1, 9*self.xsize+1, 9*self.ysize+1,
                                fill="white", outline="black")
        for i in range(self.xsize, 9 * self.xsize, 4):
            self.c.create_line(i+1, self.ysize-1, self.xsize-1, i+1, fill="black")
            self.c.create_line(9 * self.xsize+1, i-1, i-1, 9 * self.ysize+1, fill="black")

        for column in range(1,9):
            coltxt = repr(9-column)
            self.c.create_text(self.xsize / 2, self.ysize * column + self.ysize / 2, text=coltxt)
    
        for row in range(1,9):
            rowtxt = " abcdefgh "[row]
            self.c.create_text(self.xsize * row + self.xsize / 2, 9 * self.ysize + self.ysize / 2, text=rowtxt)

        for column in range(10):
            for row in range(10):
                color = "white"
                margin = None
                if column == 0 or column == 9:
                    margin = "column"
                    margintext = " abcdefgh "[row]
                if row == 0 or row == 9:
                    if margin == "column":
                        margin = "corner"
                        margintext = " "
                    else:
                        margin = "row"
                        margintext = repr(column)
          
                if not margin and not (column + row) & 0x1:
                    rect = self.c.create_rectangle(
                        column * self.xsize, row * self.ysize,
                        column * self.xsize + self.xsize, row * self.ysize + self.xsize)
                    self.c.itemconfigure(rect, fill="white", outline="white")
                    if margin:
                        self.c.itemconfigure(rect, outline=color)

        self.c.bind('<ButtonPress-1>', self.mouseDown)
        self.c.bind('<B1-Motion>', self.mouseMove)
        self.c.bind('<ButtonRelease-1>', self.mouseUp)
        self.c.bind('<KeyRelease>', self.keyRelease)
        self.c.bind('<KeyPress>', self.keyPress)

#         self.drawPosition()

        self.c.pack(side=LEFT,expand=YES,fill=BOTH)


    def mouseDown(self, event):
        xcell, ycell = event.x / self.xsize - 1, 7 - (event.y / self.ysize - 1)
        if xcell in range(8) and ycell in range(8):
            loc = Loc(xcell, ycell)
            piece = self.board[loc]
            print loc, piece
            if piece == None:
                print 'mouseDown: empty'
                self.selectedItems = ()
            elif piece.ishybrid():
                # check event.y more precisely
                threshold = (event.y - (7-ycell+1)*self.ysize)
                assert 0 <= threshold <= self.ysize
                threshold *= 3
                if threshold < self.ysize:
                    # upper chosen
                    print 'mouseDown: upper'
                    self.selectedItems = (piece.p1, )
                elif threshold > 2*self.ysize:
                    # lower chosen
                    print 'mouseDown: lower'
                    self.selectedItems = (piece.p2, )
                else:
                    # both chosen
                    print 'mouseDown: both'
                    self.selectedItems = (piece.p1, piece.p1)
            else:
                # not hybrid
                print 'mouseDown: not hybrid'
                self.selectedItems = (piece, )
        else:
            print 'mouseDown: out of range'
            self.selectedItems = ()
                    
    def mouseMove(self, event):
        pass

    def mouseUp(self, event):
        pass

    def keyRelease(self, event):
        pass

    def keyPress(self, event):
        pass

    def drawPosition(self):
        for x in range(8):
            for y in range(8):
                loc = Loc(x, y)
                self.drawPiece(self.board[loc], loc)

    def centerField(self, loc):
        x, y = loc()
        
        return (x+1.5)*self.xsize, (7-y+1.5)*self.ysize

    def upperField(self, loc):
        x, y = loc()
        
        return (x+1.5)*self.xsize, (7-y+1+1./3.)*self.ysize

    def lowerField(self, loc):
        x, y = loc()
        
        return (x+1.5)*self.xsize, (7-y+1+2./3.)*self.ysize

    def drawPiece(self, piece, loc):
        for item in self.boardDrawn[loc]:
                self.c.delete(item)

        self.boardDrawn[loc] = ()
        
        if piece == None:
            return
        
        if piece.ishybrid():
            for p, fld_func in (piece.p2, self.lowerField), (piece.p1, self.upperField):
                item = self.c.create_image(*fld_func(loc))
                self.c.itemconfigure(item, image=GBoard.photoimages[p])
                self.boardDrawn[loc] += (item, )
        else:
            item = self.c.create_image(*self.centerField(loc))
            self.c.itemconfigure(item, image=GBoard.photoimages[piece])
            self.boardDrawn[loc] += (item, )
