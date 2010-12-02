from asp.jit.asp_module import ASPModule
from asp.jit.parallel_executor import ParallelExecutor
from stencil_grid import StencilGrid
from stencil_kernel import StencilKernel
from webgraph import WebGraph

class LineKernel(StencilKernel):
	"""A line stencil that runs over a line of nodes."""
	def __init__(self, delt, delx, Ainitstar, betastar, rho, c, cstar):
		self.delt = delt
		self.delx = delx
		self.Ainitstar = Ainitstar
		self.betastar = betastar
		self.rho = rho
		self.c = c
		self.cstar = cstar

	def kernel(self, inline, outline):
		# lambda1=U(:,2)+c;
		# lambda2=U(:,2)-c;
	    for x in outline.interior_points():
			for y in inline.neighbors(x,1):
				# Strategy: calculate all uL,uR values, and use them to calculate the uI output values

				# uL(2,n) = U(1,n) + B(1,1)*U(1,n).*(.5*(1-(U(1,2)+c)*delt./delx(1)))
				uL_A = inline[y].A + inline[y].A*(0.5*(1-inline[y].A+c)*delt/delx)
				uL_u = inline[y].u + inline[y].u*(0.5*(1-inline[y].u+c)*delt/delx)
				uL_p = inline[y].p + inline[y].p*(0.5*(1-inline[y].p+c)*delt/delx)

				# uR(1,n) = U(1,n) - B(1,1)*U(1,n).*(.5*(1+(U(1,2)-c)*delt./delx(1)))
				uR_A = inline[y].A + inline[y].A*(0.5*(1+inline[y].A-c)*delt/delx)
				uR_u = inline[y].u + inline[y].u*(0.5*(1+inline[y].u-c)*delt/delx)
				uR_p = inline[y].p + inline[y].p*(0.5*(1+inline[y].p-c)*delt/delx)

				# uI(:,1)=(uI(:,3).*Ainitstar./betastar+Ainitstar.^.5).^2;
				outline[x].A = pow(outline[x].p*Ainitstar/betastar+sqrt(Ainitstar),2)

				# uI(:,2)=(1./(2*rho*cstar)).*(uL(:,3)-uR(:,3))+0.5*(uL(:,2)+uR(:,2));
				outline[x].u = (1/(2*rho*cstar))*(uL_p-uR_p)+0.5*(uL_u+uR_p)

				# uI(:,3)=.5*(uL(:,3)+uR(:,3))+.5*rho*cstar.*(uL(:,2)-uR(:,2));
				outline[x].p = 0.5*(uL_p+uR_p)+0.5*rho*cstar*(uL_u-uR_u)


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
