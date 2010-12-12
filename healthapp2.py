from webgraph import WebGraph, Side, Line, Junction, Boundary
from webkernel import LineKernel, JunctionKernel, BoundaryKernel, KernelPass
import numpy
from math import sqrt,pow
from random import uniform

class InterfaceJunctionKernel(JunctionKernel):
    def __init__(self):
        JunctionKernel.__init__(self)
    def kernel(self, in_junction, out_junction):
        self.junction_values(in_junction, out_junction)

class InterfaceBoundaryKernel(BoundaryKernel):
    def __init__(self):
        BoundaryKernel.__init__(self)
    def kernel(self, in_junction, out_junction):
        self.boundary_values(in_junction, out_junction)

class InterfaceKernel(LineKernel):
    """A line stencil that runs over a line of nodes."""
    def __init__(self):
        LineKernel.__init__(self)

    def kernel(self, in_grid, out_grid):
        # must declare the variables before using them. should eventually analyze code statically and automatically do this.
        _asp_declare('double', 'delt')
        _asp_declare('double', 'delx')
        _asp_declare('double', 'Ainitstar')
        _asp_declare('double', 'betastar')
        _asp_declare('double', 'rho')
        _asp_declare('double', 'c')
        _asp_declare('double', 'cstar')
        delt = 1.0
        delx = 2.0
        Ainitstar = 3.0
        betastar = 4.0
        rho = 5.0
        c = 6.0
        cstar = 7.0
        
        
        # declare the temporary uL/uR values
        _asp_declare('double', 'uL_A')
        _asp_declare('double', 'uL_u')
        _asp_declare('double', 'uL_p')
        _asp_declare('double', 'uR_A')
        _asp_declare('double', 'uR_u')
        _asp_declare('double', 'uR_p')
        # lambda1=U(:,2)+c;
        # lambda2=U(:,2)-c;
        for x in out_grid.interior_points():
            for y in in_grid.neighbors(x,1):
                # Strategy: calculate all uL,uR values, and use them to calculate the uI output values

                # uL(2,n) = U(1,n) + B(1,1)*U(1,n).*(.5*(1-(U(1,2)+c)*delt./delx(1)))
                # Shift the point over by 1 since the output interface line has
                # a ghost depth of 2.
                # FIXME: ASP doesn't like this...yet.
                # y = tuple(i - 1 for i in y)
                
                uL_A = in_grid[y].A + in_grid[y].A*(0.5*(1-in_grid[y].A+c)*delt/delx)
                uL_u = in_grid[y].u + in_grid[y].u*(0.5*(1-in_grid[y].u+c)*delt/delx)
                uL_p = in_grid[y].p + in_grid[y].p*(0.5*(1-in_grid[y].p+c)*delt/delx)
                
                # uR(1,n) = U(1,n) - B(1,1)*U(1,n).*(.5*(1+(U(1,2)-c)*delt./delx(1)))
                uR_A = in_grid[y].A + in_grid[y].A*(0.5*(1+in_grid[y].A-c)*delt/delx)
                uR_u = in_grid[y].u + in_grid[y].u*(0.5*(1+in_grid[y].u-c)*delt/delx)
                uR_p = in_grid[y].p + in_grid[y].p*(0.5*(1+in_grid[y].p-c)*delt/delx)
                
                # uI(:,1)=(uI(:,3).*Ainitstar./betastar+Ainitstar.^.5).^2;
                out_grid[x].A = pow(out_grid[x].p*Ainitstar/betastar+sqrt(Ainitstar),2)
                
                # uI(:,2)=(1./(2*rho*cstar)).*(uL(:,3)-uR(:,3))+0.5*(uL(:,2)+uR(:,2));
                out_grid[x].u = (1/(2*rho*cstar))*(uL_p-uR_p)+0.5*(uL_u+uR_p)
                
                # uI(:,3)=.5*(uL(:,3)+uR(:,3))+.5*rho*cstar.*(uL(:,2)-uR(:,2));
                out_grid[x].p = 0.5*(uL_p+uR_p)+0.5*rho*cstar*(uL_u-uR_u)

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
    node_graph = WebGraph(lines, junctions, boundary_size=3)
    interface_graph = create_interface_graph(node_graph, junction_size=1,
                                                 boundary_size=1)
    class NodeLineKernel(LineKernel):
        def kernel(self, in_grid, out_grid):
            for x in out_grid.interior_points():
                for y in in_grid.neighbors(x, 1):
                    out_grid[x] = out_grid[x] + in_grid[y]

    compute_interfaces = KernelPass(InterfaceKernel(),  InterfaceJunctionKernel(), InterfaceBoundaryKernel())
    compute_nodes = KernelPass(None, None, None)
    compute_interfaces.compute(node_graph, interface_graph)

    print 'Input lines:'
    for line in node_graph.lines:
        print line.data

    print 'Output lines:'
    for line in interface_graph.lines:
        print line.data


