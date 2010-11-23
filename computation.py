from stencil_grid import StencilGrid
from stencil_kernel import StencilKernel

class LineComputation(StencilKernel):
    """A line stencil that runs over a line of nodes."""
    pass


class JunctionComputation(object):

    

    def junction_values(in_junction, out_junction):
        pass


class BoundaryComputation(JunctionComputation):
    """A computation over the nodes along the boundary of a line. This is a
    specific instance of a junction computation in that a boundary is a
    junction with only one line (however, such a junction would actually be
    illegal as junctions must comprise three or more lines).
    """

    def boundary_values(in_boundary, out_boundary):
        pass
