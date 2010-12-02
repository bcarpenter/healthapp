from asp.jit.asp_module import ASPModule
from asp.jit.parallel_executor import ParallelExecutor
from stencil_grid import StencilGrid
from stencil_kernel import StencilKernel
from webgraph import WebGraph

class LineKernel(StencilKernel):
    """A line stencil that runs over a line of nodes."""
    pass

class JunctionKernel(object):

    def __init__(self, asp_module_factory=None):
        if asp_module_factory is None:
            self.asp_module_factory = ASPModule
        else:
            self.asp_module_factory = asp_module_factory

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

        # Create a kernel executor that can help run the kernels in parallel.
        self.executor = ParallelExecutor(line_kernel, junction_kernel,
                                         boundary_kernel)

    def compute(self, in_graph, out_graph):
        line_pairs = KernelPass.line_pairs(in_graph, out_graph)
        junction_pairs = KernelPass.junction_pairs(in_graph, out_graph)
        boundary_pairs = KernelPass.boundary_pairs(in_graph, out_graph)
        # The junctions and boundaries should be filled with the line values,
        # so there is no need to copy them into the junctions and boundaries.

        # Invoke the kernel computations -- they must all be able to run in
        # parallel since the parallel executor just captures a trace. If the
        # JIT compilation is not enabled for some kernels (i.e., they are in
        # pure-Python mode), they will run at this point, and the executor will
        # only run those that can be compiled.
        if self.line_kernel is not None:
            for in_line, out_line in line_pairs:
                self.line_kernel.kernel(in_line, out_line)
        if self.junction_kernel is not None:
            for in_junction, out_junction in junction_pairs:
                self.junction_kernel.kernel(in_junction, out_junction)
        if self.boundary_kernel is not None:
            for in_boundary, out_boundary in boundary_pairs:
                self.boundary_kernel.kernel(in_boundary, out_boundary)
        # Actually run all of the kernels in parallel if the JIT is enabled.
        self.executor.execute()

        # Consolidate the values in the output junctions and boundaries into
        # the output lines.
        out_graph.fill_lines()

    @staticmethod
    def line_pairs(in_graph, out_graph):
        for line_id in WebGraph.indices(in_graph.lines):
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
