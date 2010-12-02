from webgraph import WebGraph, Side, Line, Junction, Boundary
from webkernel import LineKernel, JunctionKernel, BoundaryKernel, KernelPass
import numpy
from math import sqrt

class InterfaceKernel(LineKernel):
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
				print inline[y]
				uL_A = inline[y].A + inline[y].A*(0.5*(1-inline[y].A+self.c)*self.delt/self.delx)
				uL_u = inline[y].u + inline[y].u*(0.5*(1-inline[y].u+self.c)*self.delt/self.delx)
				uL_p = inline[y].p + inline[y].p*(0.5*(1-inline[y].p+self.c)*self.delt/self.delx)

				# uR(1,n) = U(1,n) - B(1,1)*U(1,n).*(.5*(1+(U(1,2)-c)*delt./delx(1)))
				uR_A = inline[y].A + inline[y].A*(0.5*(1+inline[y].A-self.c)*self.delt/self.delx)
				uR_u = inline[y].u + inline[y].u*(0.5*(1+inline[y].u-self.c)*self.delt/self.delx)
				uR_p = inline[y].p + inline[y].p*(0.5*(1+inline[y].p-self.c)*self.delt/self.delx)

				# uI(:,1)=(uI(:,3).*Ainitstar./betastar+Ainitstar.^.5).^2;
				outline[x].A = pow(outline[x].p*self.Ainitstar/self.betastar+sqrt(self.Ainitstar),2)

				# uI(:,2)=(1./(2*rho*cstar)).*(uL(:,3)-uR(:,3))+0.5*(uL(:,2)+uR(:,2));
				outline[x].u = (1/(2*self.rho*self.cstar))*(uL_p-uR_p)+0.5*(uL_u+uR_p)

				# uI(:,3)=.5*(uL(:,3)+uR(:,3))+.5*rho*cstar.*(uL(:,2)-uR(:,2));
				outline[x].p = 0.5*(uL_p+uR_p)+0.5*self.rho*self.cstar*(uL_u-uR_u)

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
        lines.append(Line(node_line.shape[0] + 2, node_line.dtype))

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

    class NodeLineKernel(LineKernel):
        def kernel(self, in_grid, out_grid):
            for x in out_grid.interior_points():
                for y in in_grid.neighbors(x, 1):
                    out_grid[x] = out_grid[x] + in_grid[y]

    compute_interfaces = KernelPass(InterfaceKernel(1,2,3,4,5,6,7), None, None)
    compute_nodes = KernelPass(None, None, None)
    compute_interfaces.compute(node_graph, interface_graph)

    print 'Input lines:'
    for line in node_graph.lines:
        print line.data

    print 'Output lines:'
    for line in interface_graph.lines:
        print line.data

