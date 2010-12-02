from mako.template import *

def indent(code, indentation=''):
    return '\n'.join(indentation + line for line in code.split('\n'))
