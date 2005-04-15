__Id__ = "$Id$"

from simpleparse.common import numbers, strings, comments
from simpleparse.parser import Parser

PGN = r'''# note use of raw string when embedding in python code...
<space>        := [ \t\n\r]+

File           := [a-h]
Rank           := [1-8]
Loc            := File, Rank

PrimePiece     := [GNBR]
HybridPiece    := PrimePiece, PrimePiece
King           := [K]
Pawn           := [p]?
>Piece<        := HybridPiece/PrimePiece/King/Pawn

CheckSign      := [+\#]

CaptureSign    := [x:]
JoinSign       := [^]
PassSign       := [-]
>MoveSign<     := PassSign/CaptureSign/JoinSign

Promotion      := PrimePiece

# Full Algebraic notation
Move_FAN       := Piece, Loc, MoveSign?, Loc, Promotion?, CheckSign?

>move_aux<     := MoveSign?, Loc, Promotion?, CheckSign?
# Short Algebraic notation
Move_SAN       := Piece, (((File/Rank), move_aux)/move_aux)
'''

parser = Parser(PGN)
