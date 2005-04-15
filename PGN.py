__Id__ = "$Id$"

from simpleparse.common import numbers, strings, comments
from simpleparse.parser import Parser

PGN = r'''# note use of raw string when embedding in python code...
<space>        := [ \t\n\r]+

File           := [a-h]
Rank           := [1-8]
Loc            := File, Rank

Prime          := [GNBR]
Hybrid         := Prime, Prime
King           := [K]
Pawn           := [pP]?
>Piece<        := Hybrid/Piece/King/Pawn
Hybridable     := Prime
NotHybridable  := Hybrid/King

CheckSign      := [+\#]

CaptureSign    := [x:]
JoinSign       := [^]
PassSign       := [-]
>MoveSign<     := PassSign/CaptureSign/JoinSign

Promotion      := Piece

# Full Algebraic notation

>Move_FAN_NotHybridable< := NotHybridable, Loc, (CaptureSign/PassSign)?, Loc, CheckSign?
>Move_FAN_Hybridable<    := Hybridable, Loc, MoveSign?, Loc, CheckSign?
>Move_FAN_Pawn<          := Hybridable, Loc, (CaptureSign/PassSign)?, Loc, Promotion?, CheckSign?

# strict version
Move_FAN       := Move_FAN_NotHybridable/Move_FAN_Hybridable/Move_FAN_Pawn

# relaxed version
# Move_FAN       := Piece, Loc, MoveSign?, Loc, Promotion?, CheckSign?

# Short Algebraic notation
>move_aux<     := MoveSign?, Loc, Promotion?, CheckSign?

Move_SAN       := Piece, (((File/Rank), move_aux)/move_aux)

# Allow any
Move           := Move_SAN/Move_FAN
'''

parser = Parser(PGN)
