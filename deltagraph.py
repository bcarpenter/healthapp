from collections import namedtuple
from itertools import product

from stencil_grid import StencilGrid

class DeltaGraph(object):

    def __init__(self, lines, junctions):
        # Lines are the arrays of nodes (e.g., arteries).
        self.lines = lines
        # Junctions are where multiple lines meet (e.g., bifurcations). They
        # specify which lines meet and which sides of those lines are in the
        # junction. No side of a line can be in more than one junction.
        self.junctions = junctions

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
                # Copy the line values into the junction.
                values = self._get_line_values(line, side, junction.size)
                junction.line_values[line] = values
            # As a temporary heuristic, find the maximum junction size to
            # determine the boundary size.
            junction_size = max(junction.size, junction_size)

        # Boundaries specify sides of lines that aren't in junctions.
        line_ids = DeltaGraph.indices(self.lines)
        all_line_sides = set(product(line_ids, (Side.LEFT, Side.RIGHT)))
        boundary_line_sides = all_line_sides - line_sides
        self.boundaries = [Boundary(line_side, junction_size)
                           for line_side in boundary_line_sides]
        for boundary in self.boundaries:
            values = self._get_line_values(boundary.line_id, boundary.side,
                                           junction_size)
            boundary.set_line_value(values)

    def get_line(self, line_id):
        return self.lines[line_id]

    def _get_line_values(self, line_id, side, count):
        line = self.get_line(line_id)
        if side is Side.LEFT:
            return line[:count]
        if side is Side.RIGHT:
            return line[-count:]
        raise Exception('unknown side %s' % (side,))

    def __repr__(self):
        return 'DeltaGraph(lines=%s, junctions=%s)' % \
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
    pass

class Junction(object):

    def __init__(self, line_sides, size):
        self.line_sides = dict(line_sides)
        self.size = size
        self.line_values = self.initialize_line_values()

    def initialize_line_values(self):
        return dict(zip(self.line_sides, [0] * self.size))

    def __repr__(self):
        return 'Junction(%s, %s)' % (self.line_sides, self.size)

class Boundary(Junction):
    
    def __init__(self, line_side, size):
        Junction.__init__(self, (line_side,), size)
        self.line_id = iter(self.line_sides).next()
        self.side = self.line_sides[self.line_id]
        self.line_value = self.line_values[self.line_id]

    def set_line_value(self, values):
        self.line_value[:] = values 

    def __repr__(self):
        return 'Boundary(%s, %s)' % ((self.line_id, self.side), self.size)

if __name__ == '__main__':
    lines = [(1, 2, 3, 4, 5, 6, 7, 8, 9),
             (11, 12, 13, 14, 15, 16, 17, 18, 19),
             (21, 22, 23, 24, 25, 26, 27, 28, 29)]
    line_sides = [(0, Side.RIGHT), (1, Side.LEFT), (2, Side.LEFT)]
    junctions = [Junction(line_sides, 2)]
    graph = DeltaGraph(lines, junctions)
    print graph.boundaries
