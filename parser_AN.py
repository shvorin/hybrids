
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

(K, P, R, Q, B, N) = range(6)

piece_symbols = {}
for sym, name in zip([K, P, R, Q, B, N], "KPRQBN"):
    piece_symbols[name] = sym

def x(sym):
    try:
        return unit(piece_symbols[sym])
    except KeyError:
        return zero

parse_spiece = bind(getChar, x)

parse_piece = pipe(pmap2(lambda r1, r2: (r1, r2), (parse_spiece, parse_spiece)), parse_spiece)
