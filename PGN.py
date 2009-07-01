__Id__ = "$Id$"

from simpleparse.common import numbers, strings, comments
from simpleparse.parser import Parser
from simpleparse.dispatchprocessor import *
import os.path

def load_ebnf(fname):
    # FIXME: a path to EBNF is hard-coded
    return file(os.path.join('EBNF', fname+'.ebnf')).read()

parser = Parser(load_ebnf('move') + load_ebnf('tags') + load_ebnf('game'))


# a testing function
def parseMove(result_trees):
    tree = result_trees[1]
    actor = tree[0]
    l = len(tree)

    promotion = tree[-1]
    if actor[0] == 'Pawn' and promotion[0] == 'Promotion':
        l -= 1
    else:
        promotion = None

    if l == 3:
        return (actor, tree[1], tree[2], promotion)
    elif l == 2:
        return (actor, None, tree[1], promotion)
    else:
        raise Error, "invalid parsed tree"
