from collections import namedtuple
from itertools import product

class Side(namedtuple('Side', 'line side')):

    LEFT = -1
    RIGHT = 1

    def __repr__(self):
        return 'Side(line=%s, side=%s)' % (self.line, self.__side_name())

    def __side_name(self):
        if self.side not in (Side.LEFT, Side.RIGHT):
            return 'UNKNOWN'
        return 'Side.LEFT' if self.side is Side.LEFT else 'Side.RIGHT'


class DeltaGraph(object):

    def __init__(self, lines, junctions):
        # Lines are the arrays of nodes (e.g., arteries).
        self.lines = lines
        # Junctions are where multiple lines meet (e.g., bifurcations). They
        # specify which lines meet and which sides of those lines are in the
        # junction. No side of a line can be in more than one junction.
        self.junctions = junctions

        # Verify the correctness of the junctions.
        line_sides = set()
        for junction in junctions:
            for line_side in junction:
                if line_side in line_sides:
                    line, side = line_side
                    error = '%s side of line %s in multiple junctions'
                    raise Exception(error % (side, line))
                line_sides.add(line_side)

        # Boundaries specify sides of lines that aren't in junctions.
        all_line_sides = product(DeltaGraph.indices(self.lines),
                                 (Side.LEFT, Side.RIGHT))
        all_line_sides = set(Side(line, side) for line, side in all_line_sides)
        self.boundaries = all_line_sides - line_sides

    def __repr__(self):
        return 'DeltaGraph(lines=%s, junctions=%s)' % \
            (self.lines, self.junctions)

    @staticmethod
    def indices(collection):
        try:
            return collection.keys()
        except AttributeError:
            return range(len(collection))


if __name__ == '__main__':
    lines = [(1, 2, 3, 4, 5, 6, 7, 8, 9),
             (11, 12, 13, 14, 15, 16, 17, 18, 19),
             (21, 22, 23, 24, 25, 26, 27, 28, 29)]
    junctions = [[Side(0, Side.RIGHT),
                  Side(1, Side.LEFT),
                  Side(2, Side.LEFT)]]
    graph = DeltaGraph(lines, junctions)
    print graph.boundaries
