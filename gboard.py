

__id__ = "$Id$"
# __all__ = []

from Tkinter import *
from board import *
from pieces import *

class GBoard:

    def __init__(self, board=None):
        if board:
            self.board = board
        else:
            self.board = Board()
            self.board.setup()

        self.root = Tk()
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

        self.drawPosition()

        self.c.pack(side=LEFT,expand=YES,fill=BOTH)


    def mouseDown(self, event):
        pass

    def mouseMove(self, event):
        pass

    def mouseUp(self, event):
        pass

    def keyRelease(self, event):
        pass

    def keyPress(self, event):
        pass

    def drawPosition(self):
        pass
