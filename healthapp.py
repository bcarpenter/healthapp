from math import sqrt
import numpy
from webgraph import WebGraph, Side, Line, Junction
from webkernel import KernelPass
from health import (InterfaceLineKernel, InterfaceJunctionKernel,
                    InterfaceBoundaryKernel, create_interface_graph)

def create_node_graph():
    lines = [((1,1,1), (2,2,2), (3,3,3), (4,4,4), (5,5,5), (6,6,6), (7,7,7), (8,8,8), (9,9,9)),
             ((11,11,11), (12,12,12), (13,13,13), (14,14,14), (15,15,15), (16,16,16), (17,17,17), (18,18,18), (19,19,19)),
             ((21,21,21), (22,22,22), (23,23,23), (24,24,24), (25,25,25), (26,26,26), (27,27,27), (28,28,28), (29,29,29))]

    line_dtype = numpy.dtype({'A': float, 'u': float, 'p': float}.items())
    lines = [Line.create_from_sequence(line, line_dtype) for line in lines]

    line_sides = [(0, Side.RIGHT), (1, Side.LEFT), (2, Side.LEFT)]
    junctions = [Junction(line_sides, 3)]

    return WebGraph(lines, junctions, boundary_size=3)


if __name__ == '__main__':
    node_graph = create_node_graph()
    interface_graph = create_interface_graph(node_graph, junction_size=1,
                                             boundary_size=1)
    compute_interfaces = KernelPass(InterfaceLineKernel(),
                                    InterfaceJunctionKernel(),
                                    InterfaceBoundaryKernel())
    compute_nodes = KernelPass(InterfaceLineKernel, None, None)
    compute_interfaces.compute(node_graph, interface_graph)

    print 'Input lines:'
    for line in node_graph.lines:
        print line.data

    print 'Output lines:'
    for line in interface_graph.lines:
        print line.data

