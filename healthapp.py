from webgraph import WebGraph, Side, Line, Junction, Boundary
from webkernel import LineKernel, JunctionKernel, BoundaryKernel, KernelPass

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
        lines.append(Line(node_line.shape[0] + 2))

    junctions = []
    for junction in node_graph.junctions:
        # We don't ncessarily use the same junction size as the original graph
        # since there is no constraint between junction sizes of different
        # graphs.
        junctions.append(Junction(junction.line_sides, junction_size))

    return WebGraph(lines, junctions, boundary_size)

if __name__ == '__main__':
    lines = [(1, 2, 3, 4, 5, 6, 7, 8, 9),
             (11, 12, 13, 14, 15, 16, 17, 18, 19),
             (21, 22, 23, 24, 25, 26, 27, 28, 29)]
    lines = [Line.create_from_sequence(line) for line in lines]

    line_sides = [(0, Side.RIGHT), (1, Side.LEFT), (2, Side.LEFT)]
    junctions = [Junction(line_sides, 2)]
    node_graph = WebGraph(lines, junctions, boundary_size=2)
    interface_graph = create_interface_graph(node_graph, junction_size=1,
                                             boundary_size=1)
    print interface_graph.lines
    for junction in interface_graph.junctions:
        print junction, junction.line_values
    for boundary in interface_graph.boundaries:
        print boundary, boundary.values

    compute_interfaces = KernelPass(None, None, None)
    compute_nodes = KernelPass(None, None, None)
