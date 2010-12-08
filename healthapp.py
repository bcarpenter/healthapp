from math import sqrt
import numpy
from webgraph import WebGraph, Side, Line, Junction, Boundary
from webkernel import KernelPass
from health import (InterfaceLineKernel, InterfaceJunctionKernel,
                    InterfaceBoundaryKernel)

class InterfaceLine(Line):

    def __init__(self, size, dtype=float):
        Line.__init__(self, size, dtype)
        self.ghost_depth = 2
        self.set_grid_variables()
        self.set_interior()
        self.set_default_neighbor_definition()

def create_interface_graph(node_graph, junction_size, boundary_size):
    """Creates a graph whose nodes store the interface values of the original
    graph. This is similar to creating the dual of the original graph, in
    which vertices and edges are swapped, except junctions are treated slightly
    differently and the vertices in the junctions of the interface graph still
    form a delta.
    """
    lines = []
    for line_id in WebGraph.indices(node_graph.lines):
        node_line = node_graph.get_line(line_id)
        # Add 2 to each line length since we are adding a vertex on each end.
        lines.append(InterfaceLine(node_line.shape[0] + 2, node_line.dtype))

    junctions = []
    for junction in node_graph.junctions:
        # We don't necessarily use the same junction size as the original graph
        # since there is no constraint between junction sizes of different
        # graphs.
        junctions.append(Junction(junction.line_sides, junction_size,
				  junction.dtype))

    return WebGraph(lines, junctions, boundary_size)

if __name__ == '__main__':
    lines = [((1,1,1), (2,2,2), (3,3,3), (4,4,4), (5,5,5), (6,6,6), (7,7,7), (8,8,8), (9,9,9)),
             ((11,11,11), (12,12,12), (13,13,13), (14,14,14), (15,15,15), (16,16,16), (17,17,17), (18,18,18), (19,19,19)),
             ((21,21,21), (22,22,22), (23,23,23), (24,24,24), (25,25,25), (26,26,26), (27,27,27), (28,28,28), (29,29,29))]
    line_dtype = numpy.dtype([('A', float), ('u', float), ('p', float)])
    lines = [Line.create_from_sequence(line, line_dtype) for line in lines]
    
    line_sides = [(0, Side.RIGHT), (1, Side.LEFT), (2, Side.LEFT)]
    junctions = [Junction(line_sides, 3)]
    node_graph = WebGraph(lines, junctions, boundary_size=3)
    interface_graph = create_interface_graph(node_graph, junction_size=1,
                                             boundary_size=1)

    compute_interfaces = KernelPass(InterfaceLineKernel(),
                                    InterfaceJunctionKernel(),
                                    InterfaceBoundaryKernel())
    compute_nodes = KernelPass(None, None, None)
    compute_interfaces.compute(node_graph, interface_graph)

    print 'Input lines:'
    for line in node_graph.lines:
        print line.data

    print 'Output lines:'
    for line in interface_graph.lines:
        print line.data

