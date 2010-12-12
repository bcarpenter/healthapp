from webgraph import WebGraph, Line, Junction


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
