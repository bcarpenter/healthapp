from collections import namedtuple
from itertools import product

from stencil_grid import StencilGrid

import numpy

class WebGraph(object):

    def __init__(self, lines, junctions, boundary_size):
        # Lines are the arrays of nodes (e.g., arteries).
        self.lines = lines
        for line in self.lines:
            if not isinstance(line, Line):
                raise TypeError('graph lines must be of type Line')

        # Junctions are where multiple lines meet (e.g., bifurcations). They
        # specify which lines meet and which sides of those lines are in the
        # junction. No side of a line can be in more than one junction.
        self.junctions = junctions
        for junction in self.junctions:
            if not isinstance(junction, Junction):
                raise TypeError('junctions must be of type Junction')

        # Verify the correctness of the junctions.
        junction_size, line_sides = 0, set()
        for junction in junctions:
            if len(junction.line_sides) < 3:
                raise Exception('junction must have at least three lines')
            for line_side in junction.line_sides.items():
                line, side = line_side
                # Ensure that each line side is in at most one junction.
                if line_side in line_sides:
                    error = '%s side of line %s in multiple junctions'
                    raise Exception(error % (side, line))
                line_sides.add(line_side)

        # Boundaries specify sides of lines that aren't in junctions.
        line_ids = WebGraph.indices(self.lines)
        all_line_sides = set(product(line_ids, (Side.LEFT, Side.RIGHT)))
        boundary_line_sides = all_line_sides - line_sides
        self.boundaries = [Boundary(line_side, boundary_size)
                           for line_side in boundary_line_sides]

        # Fill in the junctions and boundaries with the values in the lines.
        self.fill_junctions()
        self.fill_boundaries()

    def get_line(self, line_id):
        return self.lines[line_id]

    def fill_junctions(self):
        """Fills the junctions with values from the lines."""
        for junction in self.junctions:
            for line_id, side in junction.line_sides.items():
                values = self._get_line_values(line_id, side, junction.size)
                junction.line_values[line_id] = values

    def fill_boundaries(self):
        """Fills the boundaries with values from the lines."""
        for boundary in self.boundaries:
            values = self._get_line_values(boundary.line_id, boundary.side,
                                           boundary.size)
            boundary.set_values(values)

    def fill_lines(self):
        """Fills the peripheries of the lines with values from the junctions
        and boundaries. After calling this method, the lines in the graph will
        reflect the most up-to-date values from computations that wrote to the
        boundary and junctions.
        """
        for junction in self.junctions:
            for line_id, side in junction.line_sides.items():
                self._put_line_values(line_id, side,
                                      junction.line_values[line_id])
        for boundary in self.boundaries:
            self._put_line_values(boundary.line_id, boundary.side,
                                  boundary.values)

    def _get_line_values(self, line_id, side, count):
        line = self.get_line(line_id)
        if side is Side.LEFT:
            return line[:count]
        if side is Side.RIGHT:
            return line[-count:]
        raise Exception('unknown side %s' % (side,))

    def _put_line_values(self, line_id, side, values):
        line = self.get_line(line_id)
        if side is Side.LEFT:
            line[:len(values)] = values
        elif side is Side.RIGHT:
            line[-len(values):] = values
        else:
            raise Exception('unknown side %s' % (side,))

    def __repr__(self):
        return 'WebGraph(lines=%s, junctions=%s)' % \
            (self.lines, self.junctions)

    @staticmethod
    def indices(collection):
        try:
            return collection.keys()
        except AttributeError:
            return range(len(collection))

class Side(object):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        if self is Side.LEFT:
            return 'Side.LEFT'
        if self is Side.RIGHT:
            return 'Side.RIGHT'
        return 'Side(%s)' % (repr(self.name),)

Side.LEFT = Side('left')
Side.RIGHT = Side('right')

class Line(StencilGrid):

    def __init__(self, size, dtype=float):
        # Ensure that 'size' is a single-element sequence since lines must be
        # 1-D stencil grids. Alternatively, it may be a scalar value.
        if isinstance(size, list) or isinstance(size, tuple):
            if len(size) != 1:
                raise Exception('size %s must specify a 1-D stencil' % (size,))
            self.size = size[0]
        elif isinstance(size, int) or isinstance(size, float):
            self.size = size
        else:
            raise Exception('invalid size %s' % (size,))
        StencilGrid.__init__(self, [self.size], dtype)

    def __str__(self):
        values = ('%.5g' % (self[ii],) for ii in range(self.size))
        return '[%s]' % (', '.join(values))

    def __repr__(self):
        return 'Line(%s)' % (self.size,)

    @staticmethod
    def create_from_sequence(seq, dtype=float):
        line = Line([len(seq)], dtype)
        for ii, value in enumerate(seq):
            line[ii] = value
        return line

class Junction(object):

    def __init__(self, line_sides, size, dtype=float):
        self.line_sides = dict(line_sides)
        self.size = size
        self.dtype = numpy.dtype(dtype)
        self.line_values = {}
        for line_id in self.line_sides:
            self.line_values[line_id] = numpy.zeros(self.size, self.dtype)

    def key(self):
        return tuple(sorted(self.line_sides.items()))

    def __repr__(self):
        return 'Junction(%s, %s)' % (self.line_sides, self.size)

class Boundary(Junction):
    
    def __init__(self, line_side, size, dtype=float):
        Junction.__init__(self, (line_side,), size, dtype)
        self.line_id = iter(self.line_sides).next()
        self.side = self.line_sides[self.line_id]
        self.values = self.line_values[self.line_id]

    def key(self):
        return (self.line_id, self.side)

    def set_values(self, values):
        self.values[:] = values 

    def __repr__(self):
        return 'Boundary(%s, %s)' % ((self.line_id, self.side), self.size)
