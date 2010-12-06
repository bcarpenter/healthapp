import numpy
from codepy.cgen import *

# these are additional classes that, along with codepy's classes, let
# programmers express the C code as a real AST (not the hybrid AST/strings/etc
# that codepy implements.

class CNumber(Generable):
    def __init__(self, num):
        self.num = num

    def __str__(self):
        return str(self.num)

class CName(Generable):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)


class Expression(Generable):
    def __str__(self):
        return ""

    def generate(self):
        yield str(self) + ';'

class BinOp(Expression):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return "(%s %s %s)" % (self.left, self.op, self.right)

class UnaryOp(Expression):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

    def __str__(self):
        return "(%s(%s))" % (self.op, self.operand)

class Subscript(Expression):
    def __init__(self, value, index):
        self.value = value
        self.index = index

    def __str__(self):
        return "%s[%s]" % (self.value, self.index)

class Call(Expression):
    def __init__(self, func, args):
        self.func = func
        self.args = args

    def __str__(self):
        return "%s(%s)" % (self.func, ", ".join(map(str, self.args)))

class Attribute(Expression):
    def __init__(self, attr, value):
        self.attr = attr
        self.value = value

    def __str__(self):
        return '%s.%s' % (self.value, self.attr)

class Sqrt(Expression):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'sqrt(%s)' % self.value

class Pow(Expression):
    def __init__(self, value, pow):
        self.value = value
        self.pow = pow
    def __str__(self):
        return 'pow(%s, %s)' % self.value, self.pow


class Return(Expression):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "return %s" % self.value


# expression types not used in this example:

class PostfixUnaryOp(Expression):
    def __init__(self, operand, op):
        self.operand = operand
        self.op = op

    def __str__(self):
        return "((%s)%s)" % (self.operand, self.op)

class ConditionalExpr(Expression):
    def __init__(self, test, body, orelse):
        self.test = test
        self.body = body
        self.orelse = orelse

    def __str__(self):
        return "(%s ? %s : %s)" % (self.test, self.body, self.orelse)

class TypeCast(Expression):
    # "type" should be a declaration with an empty variable name
    # e.g. TypeCast(Pointer(Value('int', '')), ...)

    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return "((%s)%s)" % (self.type.inline(), self.value)

def cpp_type(dtype):
    """Returns the name and declarator for the C++ version of the specified
    type. If the given type is a C++ primitive, the declarator is None.
    """
    try:
        return dtype_to_ctype(dtype), None
    except ValueError:
        fields = []
        for field in dtype.names:
            subtype, _ = dtype.fields[field]
            subname, subdeclarator = cpp_type(subtype)
            if subdeclarator is not None:
                subname = subdeclarator.inline()
            fields.append(Value(subname, field))
        struct_name = '_void_' + hex(abs(hash(dtype)))[2:]
        return 'struct ' + struct_name, Struct(struct_name, fields)
