
__Id__ = "$Id$"

from pmonad import *

parse_file = bind(getChar, mkFilter(contains("abcdefgh")))
parse_rank = bind(getChar, mkFilter(contains(map(str, range(8)))))

letters = {}
for letter, num in zip("abcdefgh", range(8)):
    letters[letter] = num

def scanPos(x,y):
    return (letters[x], int(y)-1)


parse_pos = pmap2(scanPos, (parse_file, parse_rank))

# [K, P, R, Q, B, N] = list("KPRQBN")

piece_symbols = {}
for sym in "KPRQBN":
    piece_symbols[sym] = sym

def x(sym):
    if piece_symbols.has_key(sym):
        return unit(sym)
    else:
        return zero

parse_spiece = bind(getChar, x)

parse_piece = pipe(pmap2(lambda r1, r2: (r1, r2), (parse_spiece, parse_spiece)), parse_spiece)

parse_pos = pmap2(scanPos, (parse_file, parse_rank))

def check_sign(c):
    if c == '+': return unit ({'check': '+'})
    elif c == '#': return unit ({'check': '#'})
    else: return zero
    
parse_Check_sign = pipe(bind(getChar, check_sign), unit ({}))

def capture_sign(c):
    if c == 'x': return unit ({'capture': True})
    elif c == '^': return unit ({'join': True})
    else: return zero

parse_Capture_sign = pipe(bind(getChar, capture_sign), unit ({}))

# parse_SAN = 
# parse_SAN.__doc__ =
"""
SAN ::= Piece [File | Rank] [Capture_sign | Join_sign] Pos [Promotion] [Check_sign]
      | File [Capture_sign] File [Rank] [Promotion]
      | File Rank [Promotion]

"""

