__Id__ = "$Id$"

import new

class Immutable(object):
    __slots__ = ()

    def __init__(self, *args):
        raise TypeError, "cannot create 'Immutable' instances, this is an abstract class"
    
    def __setattr__(self, name, value):
        raise TypeError, "readonly attribute"

    def __delattr__(self, name):
        raise TypeError, "readonly attribute"

    def __cmp__(self, other):
        return cmp(self(), other())

    def __hash__(self):
        return hash(self())

    def __call__(self):
        return tuple(map((lambda name: object.__getattribute__(self, name)), self.__slots__))
 

class Color(Immutable):
    __slots__ = ('value', )
    __white = 0
    __black = 1
    
    def __init__(self, *args):
        raise TypeError, "cannot create 'Color' instances"

    # FIXME: is it OK to use __repr__(), not just __str__() ?
    def __repr__(self):
        if   self.value == Color.__white: return 'white'
        elif self.value == Color.__black: return 'black'
        else : raise Exception, "oops, unknown color"


    # to be deleted
    def createValues(self):
        v1 = object.__new__(Color)
        object.__setattr__(v1, 'value', Color.__white)
        v2 = object.__new__(Color)
        object.__setattr__(v2, 'value', Color.__black)
        return (v1, v2)

    def inv(self):
        if self == white: return black
        else: return white

(white, black) = Color.createValues(object.__new__(Color))
del Color.createValues # no more Color values ;)

class Loc(Immutable):
    __slots__ = (x, y)
    
    __files = 'abcdefgh'
    __ranks = '12345678'

    def __init__(self, *args):
        length = len(args)
        if length == 2:
            (x, y) = args
        elif length == 1:
            ((x, y), ) = args
        else:
            raise ValueError, "wrong # of args"

        if x in list(Loc.__files) and y in list(Loc.__ranks):
            # algebraic notation given
            try:
                x, y = Loc.__files.index(x), Loc.__ranks.index(y)
            except ValueError:
                raise ValueError, "invalid algebraic notation"
        else:
            # numeric representation given
            if not (x in range(8) and y in range(8)):
                raise ValueError, "numeric representation is out of range"
        
        # explicit assignment forbidden
        self.__dict__['x'] = x
        self.__dict__['y'] = y
            

    # FIXME: is it OK to use __repr__(), not just __str__() ?
    def __repr__(self):
        return Loc.__files[self.x] + Loc.__ranks[self.y]
    
#     def __call__(self):
#         return self.x, self.y

    def flip(self):
        return Loc(self.x, 7-self.y)
    
del new
