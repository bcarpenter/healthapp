from stencil_grid import StencilGrid
from stencil_kernel import StencilKernel

class LineKernel(StencilKernel):
    """A line stencil that runs over a line of nodes."""
    pass

class JunctionKernel(object):

    def junction_values(in_junction, out_junction):
        pass

class BoundaryKernel(JunctionKernel):
    """A computation over the nodes along the boundary of a line. This is a
    specific instance of a junction kernel in that a boundary is a
    junction with only one line (however, such a junction would actually be
    illegal as junctions must comprise three or more lines).
    """

    def boundary_values(in_boundary, out_boundary):
        pass

class KernelPass(object):

    def __init__(self, line_kernel, junction_kernel, boundary_kernel):
        self.line_kernel = line_kernel
        self.junction_kernel = junction_kernel
        self.boundary_kernel = boundary_kernel

    def compute(self, in_graph, out_graph):
        line_pairs = KernelPass.line_pairs(in_graph, out_graph)
        junction_pairs = KernelPass.junction_pairs(in_graph, out_graph)
        boundary_pairs = KernelPass.boundary_pairs(in_graph, out_graph)

        # START-PARALLEL
        # The junctions and boundaries should be filled with the line values,
        # so there is no need to copy them into the junctions and boundaries.
        if self.line_kernel is not None:
            for in_line, out_line in line_pairs:
                self.line_kernel.kernel(in_line, out_line)
        if self.junction_kernel is not None:
            for in_junction, out_junction in junction_pairs:
                self.junction_kernel.kernel(in_junction, out_junction)
        if self.boundary_kernel is not None:
            for in_boundary, out_boundary in boundary_pairs:
                self.boundary_kernel.kernel(in_boundary, out_boundary)
        # END-PARALLEL

        # Consolidate the values in the output junctions and boundaries into
        # the output lines.
        out_graph.fill_lines()

    @staticmethod
    def line_pairs(in_graph, out_graph):
        for line_id in DeltaGraph.indices(in_graph.lines):
            yield in_graph.get_line(line_id), out_graph.get_line(line_id)

    @staticmethod
    def junction_pairs(in_graph, out_graph):
        in_junctions = {}
        for junction in in_graph.junctions:
            in_junctions[junction.key()] = junction
        for junction in out_graph.junctions:
            return in_junctions[junction.key()], junction

    @staticmethod
    def boundary_pairs(in_graph, out_graph):
        in_boundaries = {}
        for boundary in in_graph.boundaries:
            in_boundaries[boundary.key()] = boundary
        for boundary in out_graph.boundaries:
            return in_boundaries[boundary.key()], boundary
