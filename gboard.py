#!/usr/bin/env python

__id__ = "$Id$"
# $ URL: http://gh218.keldysh.ru/svn/hybrids/trunk/gboard.py $
# __all__ = []

from Tkinter import *
from FileDialog import *
from board import *
from pieces import *
import os.path
import errno

# Try using cPickle if available.
# try:
#     import cPickle as pickle
# except ImportError:
import pickle


def sub2((x1, y1), (x2, y2)):
    return x1-x2, y1-y2

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
                                (wG, 'queenw.gif'),
                                (bG, 'queenb.gif')):
            GBoard.photoimages[piece] = PhotoImage(file=os.path.join('images', filename))
            
    init_photoimages = staticmethod(init_photoimages)

    raw_suffix = '.raw_pgn'


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

        # may be a tupple (loc, piece, items_tupple) or None;
        # items_tupple is a tupple (1 or 2 values) of (item, shift),
        # where shift is difference between items original coordinates and
        # cursor position at the moment of selecting
        self.selected = None

        # user's option, may be None or some subclass of PrimePiece
        # the pawn will be promoted to that piece without question
        # TODO: this should be _option_
        # self.alwaysPromote = RookPiece
        self.alwaysPromote = None
        
        self.root = Tk()
        if not GBoard.photoimages:
            GBoard.init_photoimages()
        
        # FIXME: show various variants
        self.root.wm_title("chess ('%s' variant)" % self.board.variant)
        self.root.wm_iconname("chess")

        self.xsize = self.ysize = 96

        self.c = Canvas(self.root, background='white',
                        height=10*self.xsize,
                        width=10*self.ysize)
        self.c.create_rectangle(self.xsize-1, self.ysize-1, 9*self.xsize+1, 9*self.ysize+1,
                                fill="white", outline="black")

        for column in range(1,9):
            for row in range(1,9):
                if (column + row) & 0x1:
                    color = "grey60"
                else:
                    color = "grey95"
                    
                self.c.create_rectangle(self.xsize * row, self.ysize * column,
                                        self.xsize * (row+1), self.ysize * (column+1),
                                        fill=color, outline="black")
        
        for column in range(1,9):
            coltxt = repr(9-column)
            self.c.create_text(self.xsize / 2, self.ysize * column + self.ysize / 2, text=coltxt)
    
        for row in range(1,9):
            rowtxt = " abcdefgh "[row]
            self.c.create_text(self.xsize * row + self.xsize / 2, 9 * self.ysize + self.ysize / 2, text=rowtxt)

        self.c.bind('<ButtonPress-1>', self.mouseDown)
        self.c.bind('<B1-Motion>', self.mouseMove)
        self.c.bind('<ButtonRelease-1>', self.mouseUp)
        self.c.bind('<KeyRelease>', self.keyRelease)
        self.c.bind('<KeyPress>', self.keyPress)
        self.c.focus_set()

        self.c.pack(side=LEFT,expand=YES,fill=BOTH)
        self.drawPosition()

        # import os
        # io = os.open('fifo', os.O_RDONLY | os.O_NONBLOCK)
        # self.fifo = os.fdopen(io, 'r')

    def mouseDown(self, event):
        event_coords = event.x, event.y
        xcell, ycell = event.x / self.xsize - 1, 7 - (event.y / self.ysize - 1)
        loc = self.getLoc(event.x, event.y)
        if loc:
            piece = self.board[loc]
            if piece == None:
                self.selected = None
            elif piece.ishybrid():
                img1, img2 = self.boardDrawn[loc]
                # check event.y more precisely
                threshold = (event.y - (7-ycell+1)*self.ysize)
                assert 0 <= threshold <= self.ysize
                threshold *= 3
                if threshold < self.ysize:
                    # upper chosen
                    self.selected = (loc, piece.p2,
                                     ((img2, sub2(self.upperField(loc), event_coords)), ))
                elif threshold > 2*self.ysize:
                    # lower chosen
                    self.selected = (loc, piece.p1,
                                     ((img1, sub2(self.lowerField(loc), event_coords)), ))
                else:
                    # both chosen
                    self.selected = (loc, piece,
                                     ((img1, sub2(self.lowerField(loc), event_coords)),
                                      (img2, sub2(self.upperField(loc), event_coords))))
            else:
                # not hybrid
                (img, ) = self.boardDrawn[loc]
                self.selected = (loc, piece, ((img, sub2(self.centerField(loc), event_coords)), ))
        else:
            self.selected = None
                    
    def mouseMove(self, event):
        if self.selected:
            loc, piece, item_shifts = self.selected
            for item, (x, y) in item_shifts:
                self.c.coords(item, x+event.x, y+event.y)
                self.c.tkraise(item)

    def mouseUp(self, event):
        if self.selected:
            loc, piece, item_shifts = self.selected
            newloc = self.getLoc(event.x, event.y)
            if newloc:
                try:
                    try:
                        self.board.move(piece, loc, newloc)
                    except UnspecifiedPromotion, msg:
                        # Ok, lets ask user to specify promotion
                        options = {}
                        col = self.board.turn
                        if self.alwaysPromote:
                            options['promote'] = self.alwaysPromote(col)
                        else:
                            pd = PromotionDialog(self)
                            selected = pd.go()
                            if selected is not None:
                                options['promote'] = selected(col)
                            else:
                                raise IllegalMove, "cancel promotion"

                        self.board.move(piece, loc, newloc, options)
                except IllegalMove, msg:
                    print IllegalMove, msg
                    
            self.selected = None

        # FIXME: may be too expensive
        self.drawPosition()

    def keyRelease(self, event):
        from string import upper
        key = upper(event.keysym)

        if key == 'BACKSPACE' or key == 'LEFT':
            self.undo()
        elif key == 'RIGHT':
            self.redo()
        elif key == 'D':
            print 'Current position:'
            print self.board
        elif key == 'M':
            print 'All legal moves:'
            for patch in self.board.iterMove():
                print patch
        elif key == 'L':
            self.gload()
        elif key == 'S':
            self.gsave()

    def keyPress(self, event):
        print 'keyPress: ', event.keysym
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

    def getLoc(self, *args):
        """
        for given coordinates x,y returns corresponding location;
        if arguments are out of range None is returned
        """
        l = len(args)
        if l == 1:
            (args, ) = args
        elif l != 2:
            raise ValueError
        x, y = args
        try:
            return Loc(x/self.xsize-1, 7-(y / self.ysize-1))
        except ValueError: # out of range
            return None

    def drawPiece(self, piece, loc):
        for item in self.boardDrawn[loc]:
            self.c.delete(item)

        self.boardDrawn[loc] = ()
        
        if piece == None:
            return
        
        if piece.ishybrid():
            for p, fld_func in (piece.p1, self.lowerField), (piece.p2, self.upperField):
                coords = fld_func(loc)
                item = self.c.create_image(*coords)
                self.c.itemconfigure(item, image=GBoard.photoimages[p])
                self.boardDrawn[loc] += (item, )
        else:
            coords = self.centerField(loc)
            item = self.c.create_image(*coords)
            self.c.itemconfigure(item, image=GBoard.photoimages[piece])
            self.boardDrawn[loc] += (item, )

    def undo(self):
        self.board.undo()
        self.drawPosition()

    def redo(self):
        self.board.redo()
        self.drawPosition()

# Raw save (instead of PGN)
    def save(self, fname):
        pickle.dump(self.board, file(fname, 'w'), pickle.HIGHEST_PROTOCOL)

# Raw load (instead of PGN)
    def load(self, fname):
        self.board = pickle.load(file(fname))
        self.drawPosition()

    def gload(self):
        fd = LoadFileDialog(self.root)
        fname = fd.go(pattern='*'+GBoard.raw_suffix, key='gboard')

        if fname is None:
            return

        self.load(fname)

    def gsave(self):
        fd = SaveFileDialog(self.root)
        fname = fd.go(pattern='*'+GBoard.raw_suffix, key='gboard')
        
        if fname is None:
            return

        # TODO: append raw_suffix if file does not contains it already
        
        self.save(fname)

    def poll(self):
        print "poll"
        try:
            line = self.fifo.readline()
        except OSError, err:
            if err.errno == errno.EAGAIN or err.errno == errno.EWOULDBLOCK:
                line = None
            else:
                raise
        self.command(line)
        self.root.after(1000, self.poll)

    def command(self, line):
        if not line:
            return
        line = line[:-1] # drop final '\n'
        if line == 'backward':
            self.undo()
            return
        if line == 'forward':
            self.redo()
            return
        raise ("unknown command %s" % line)

class PromotionDialog:
    title = "Promotion Dialog"

    key_bindigns = {'G': GuardPiece,
                    'R': RookPiece,
                    'B': BishopPiece,
                    'N': KnightPiece,
                    '<ESCAPE>': None}

    def keyPress(self, event):
        from string import upper
        key = upper(event.keysym)

        print 'PromotionDialog.keyPress: %s' % key
        
        if self.key_bindigns.has_key(key):
            self.quit(self.key_bindigns[key])
        # otherwise unknown event ignored

    def quit(self, selected):
        self.selected = selected
        self.top.destroy()
        self.master.quit()

    def handler(self, selected):
        return lambda event=None: self.quit(selected)

    def go(self):
        self.master.mainloop()          # Exited by self.quit()
        return self.selected
        
    def __init__(self, gboard, title=None):
        from string import lower
        
        if title is None: title = self.title
        self.master = gboard.root

        self.top = Toplevel(self.master)
        self.top.title(title)
        self.top.iconname(title)

        self.sel = Canvas(self.top)
        for cls in RookPiece, KnightPiece, BishopPiece, GuardPiece:
            piece = cls(gboard.board.turn)

            Button(self.sel,
                   image=GBoard.photoimages[piece],
                   command=self.handler(cls)).pack(side=LEFT)

        self.sel.pack()
        self.top.bind('<KeyPress>', self.keyPress)

        self.selected = None
        self.top.protocol('WM_DELETE_WINDOW', self.handler(None))


if __name__ == '__main__':
    try:
        g = GBoard()
        # g.poll()
        g.root.mainloop()
    except Exception, e:
        print ("an exception caught:\n%s" % e)

