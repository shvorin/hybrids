
__Id__ = "$Id$"

# parser: src -> (result, src) Option

def bind(parser, f_parser):
    "classical monadic bind"
    def bind_hlp(src):
        x = parser(src)
        if x == None:
            return None
        else:
            (res, src1) = x
            return f_parser(res)(src1)
    
    return bind_hlp
    
def pipe(parser1, parser2):
    "pipe for parser-monads"
    def pipe_hlp(src):
        x = parser1(src)
        if x == None:
            return parser2(src)
        else:
            return x
    
    return pipe_hlp

zero = lambda src: None
zero.__doc__ = "parser-monad 'zero'"

# dangerous monad: the state never degrades
unit = lambda x: lambda src: (x, src)
unit.__doc__ = "classial monadic unit"

def getChar(src):
    "a parser-monad.  gets one char from a string"
    if len(src) == 0:
        return None
    else:
        return (src[0], src[1:])

# this may be (right-)binded with some pmonad
def mkFilter(filt):
    def hlp(r):
        if filt(r): return unit(r)
        else      : return zero
    return hlp

def map(f, parser):
    "classical monadic map"
    return bind(parser, lambda r: unit(f(r)))

def map2(f, (parser1, parser2)):
    "monadic map for 2-tupple"
    return bind(parser1, lambda r1: bind(parser2, lambda r2: unit(f(r1, r2))))

def list_cons(x, xs):
    y = []
    y.insert(0, x)
    y.extend(xs)
    return y

def iterate(parser):
    # return pipe(map2(list_cons, (parser, iterate(parser))), unit(result))
    # Note, have to use lambda to avoid infinite recursion
    return pipe(bind(parser, lambda v: bind(iterate(parser), lambda vs: unit(list_cons(v, vs)))), unit([]))

# TODO: implementation may much better (create a table for the given str...)
def contains(str):
    def hlp(ch):
        for char in str:
            if ch == char: return True
        else:
            return False
    return hlp

