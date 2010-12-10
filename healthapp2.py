from webgraph import WebGraph, Side, Line, Junction, Boundary
from webkernel import LineKernel, JunctionKernel, BoundaryKernel, KernelPass
import numpy
from health import (InterfaceLineKernel, InterfaceJunctionKernel,
                    InterfaceBoundaryKernel, create_interface_graph)
from math import sqrt
from random import uniform


def create_node_graph():
    ARTERY_LENGTH = 100
    lines = []

    for i in range(0, 21):
        line = []
        for j in range(0, ARTERY_LENGTH):
            line.append((uniform(0.001, 0.3),uniform(0.001, 0.3),uniform(0.001, 0.3)))
        lines.append(tuple(line))
    #print lines[0]
    line_dtype = numpy.dtype([('A', float), ('u', float), ('p', float)])
    lines = [Line.create_from_sequence(line, line_dtype) for line in lines]

    line_sides = []
    line_sides.append([(0, Side.RIGHT), (1, Side.LEFT), (2, Side.LEFT)])
    line_sides.append([(1, Side.RIGHT), (3, Side.LEFT), (4, Side.LEFT)])
    line_sides.append([(4, Side.RIGHT), (5, Side.LEFT), (6, Side.LEFT)])
    line_sides.append([(6, Side.RIGHT), (7, Side.LEFT), (8, Side.RIGHT)])
    line_sides.append([(8, Side.LEFT), (10, Side.RIGHT), (9, Side.LEFT)])
    line_sides.append([(2, Side.RIGHT), (11, Side.LEFT), (12, Side.RIGHT)])
    line_sides.append([(11, Side.RIGHT), (10, Side.LEFT), (13, Side.RIGHT)])
    line_sides.append([(14, Side.RIGHT), (15, Side.LEFT), (13, Side.LEFT)])
    line_sides.append([(14, Side.LEFT), (16, Side.RIGHT), (17, Side.LEFT)])
    line_sides.append([(17, Side.RIGHT), (19, Side.LEFT), (18, Side.LEFT)])
    line_sides.append([(15, Side.RIGHT), (20, Side.LEFT), (18, Side.RIGHT)])

    junctions = [Junction(line_side, 3) for line_side in line_sides]

    return WebGraph(lines, junctions, boundary_size=3)

if __name__ == '__main__':
    node_graph = create_node_graph()
    interface_graph = create_interface_graph(node_graph, junction_size=1,
                                             boundary_size=1)
    compute_interfaces = KernelPass(InterfaceLineKernel(),
                                    InterfaceJunctionKernel(),
                                    InterfaceBoundaryKernel())
    compute_nodes = KernelPass(InterfaceLineKernel(), None, None)

    compute_interfaces.compute(node_graph, interface_graph)
    compute_nodes.compute(interface_graph, node_graph)

    print 'Input lines:'
    for line in node_graph.lines:
        print line.data

    print 'Output lines:'
    for line in interface_graph.lines:
        print line.data


