__Id__ = "$Id$"

from simpleparse.common import numbers, strings, comments
from simpleparse.parser import Parser
from simpleparse.dispatchprocessor import *

move = r'''# note use of raw string when embedding in python code...
<space>        := [ \t\n\r]+
<sspace>        := [ \t]+

File           := [a-h]
Rank           := [1-8]
Loc            := File, Rank

Prime          := [GNBR]
Hybrid         := Prime, Prime
King           := [K]
Pawn           := [pP]?
>Piece<        := Hybrid/Prime/King
Hybridable     := Prime
NotHybridable  := Hybrid/King

CheckSign      := [+#]

CaptureSign    := [x:]
JoinSign       := [^]
PassSign       := [-]
>MoveSign<     := PassSign/CaptureSign/JoinSign

Promotion      := [=]?, Prime

# Full Algebraic notation

>Move_FAN_NotHybridable< := NotHybridable, Loc, (CaptureSign/PassSign)?, Loc
>Move_FAN_Hybridable<    := Hybridable, Loc, MoveSign?, Loc
>Move_FAN_Pawn<          := Pawn, Loc, (CaptureSign/PassSign)?, Loc, Promotion?

# strict version
Move_FAN       := (Move_FAN_NotHybridable/Move_FAN_Hybridable/Move_FAN_Pawn), CheckSign?


# Short Algebraic notation

>Move_SAN_Pawn_capture<  := Pawn, (File, CaptureSign?, Loc)/(File, CaptureSign?, File)
>Move_SAN_Pawn<          := (Pawn, Loc)/Move_SAN_Pawn_capture, Promotion?
>Move_SAN_NotHybridable< := NotHybridable, (File/Rank, MoveSign?, Loc) / (MoveSign?, Loc)
>Move_SAN_Hybridable<    := Hybridable, (File/Rank, (PassSign/CaptureSign)?, Loc) / ((PassSign/CaptureSign)?, Loc)

Move_SAN                 := (Move_SAN_NotHybridable/Move_SAN_Hybridable/Move_SAN_Pawn), CheckSign?

# Allow any
Move           := Move_FAN/Move_SAN
'''

parser = Parser(move)

tags = r'''
<space>        := [ \t\n\r]+
<sspace>       := [ \t]+
Symbol         := [a-zA-Z0-9_]+
StringToken    := '"', -('"')*, '"'
#Tag            := ("[", Symbol, sspace, StringToken, "]") !
Tag            := ("[", Symbol, sspace, StringToken, "]")
>Tags<         := (Tag, space+)*
'''

p1 = Parser(tags)
