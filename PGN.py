__Id__ = "$Id$"

from simpleparse.common import numbers, strings, comments
from simpleparse.parser import Parser
from simpleparse.dispatchprocessor import *
import os.path

def load_ebnf(fname):
    # FIXME: a path to EBNF is hard-coded
    return file(os.path.join('EBNF', fname+'.ebnf')).read()

parser = Parser(load_ebnf('move') + load_ebnf('tags') + load_ebnf('game'))
