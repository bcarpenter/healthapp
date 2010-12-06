from asp.jit.asp_module import ASPModule
from asp.jit.parallel_executor import ParallelExecutor
from stencil_grid import StencilGrid
from stencil_kernel import StencilKernel
from webgraph import WebGraph, Side
from newton_kernel import NewtonKernel
from math import sqrt, pow

def _asp_declare(val, dtype):
    pass
class LineKernel(StencilKernel):
    """A line stencil that runs over a line of nodes."""
    pass
class JunctionKernel(object):
    def __init__(self, asp_module_factory=None):
        if asp_module_factory is None:
            self.asp_module_factory = ASPModule
        else:
            self.asp_module_factory = asp_module_factory
    def junction_values(self, in_junction, out_junction):
        leftSide = []
        rightSide = []
        for num, side in in_junction.line_sides.items():
            if side == Side.LEFT:
                leftSide.append(num)
            elif side == Side.RIGHT:
                rightSide.append(num)

        assert( (len(leftSide) == 1 and len(rightSide) == 2) or
                (len(leftSide) == 2 and len(rightSide) == 1) )
        
        input_side_name = None
        input_side = []
        output_side = []
        if (len(leftSide) == 1):
            input_side = leftSide
            output_side = rightSide
            input_side_name = Side.LEFT
        else:
            input_side_name = Side.RIGHT
            input_side = rightSide
            output_side = leftSide

        # do calculation
        input_nodes = in_junction.line_values[input_side[0]]
        output_nodes0 = in_junction.line_values[output_side[0]]
        output_nodes1 = in_junction.line_values[output_side[1]]

        junction_input_nodes = input_nodes[1:]
        junction_output_nodes0 = output_nodes0[:-1]
        junction_output_nodes1 = output_nodes1[:-1]
        
        class JunctionNewtonKernel(NewtonKernel):
            def kernel(self, initialGuess, solution, epsilon, max_iters):
                # x:
                # - x[0] = a1_star
                # - x[1] = a2_star
                # - x[2] = a3_star
                # - x[3] = u1_star
                # - x[4] = u2_star
                # - x[5] = u3_star
                
                def func0(x):
                    return x[3]*x[0] - (x[4]*x[1] + x[5]*x[2])
                def func1(x):
                    _asp_declare('double', 'rho')
                    _asp_declare('double', 'b1_1')
                    _asp_declare('double', 'b1_2')
                    _asp_declare('double', 'b1_3')
                    _asp_declare('double', 'A_0_1')
                    _asp_declare('double', 'A_0_2')
                    _asp_declare('double', 'A_0_3')
                    rho = 1
                    b1_1 = 2
                    b1_2 = 3            
                    b1_3 = 4      
                    A_0_1 = 5
                    A_0_2 = 6
                    A_0_3 = 7
                    return b1_1/A_0_1*x[0] - b1_2/A_0_2*x[1] * .5*rho*(pow(x[3],2) - pow(x[4],2))
                def func2(x):
                    _asp_declare('double', 'rho')
                    _asp_declare('double', 'b1_1')
                    _asp_declare('double', 'b1_2')
                    _asp_declare('double', 'b1_3')
                    _asp_declare('double', 'A_0_1')
                    _asp_declare('double', 'A_0_2')
                    _asp_declare('double', 'A_0_3')
                    rho = 1
                    b1_1 = 2
                    b1_2 = 3           
                    b1_3 = 4      
                    A_0_1 = 5
                    A_0_2 = 6
                    A_0_3 = 7
                    return b1_1/A_0_1*x[0] - b1_3/A_0_2*x[2] * .5*rho*(pow(x[3],2) - pow(x[5],2))
                def func3(x):
                    _asp_declare('double', 'rho')
                    _asp_declare('double', 'b1_1')
                    _asp_declare('double', 'b1_2')
                    _asp_declare('double', 'b1_3')
                    _asp_declare('double', 'A_0_1')
                    _asp_declare('double', 'A_0_2')
                    _asp_declare('double', 'A_0_3')
                    rho = 1
                    b1_1 = 2
                    b1_2 = 3            
                    b1_3 = 4      
                    A_0_1 = 5
                    A_0_2 = 6
                    A_0_3 = 7
                    
                    return x[3]+ pow(4*x[0], 2) * b1_1/(2*rho*A_0_1)
                def func4(x):
                    _asp_declare('double', 'rho')
                    _asp_declare('double', 'b1_1')
                    _asp_declare('double', 'b1_2')
                    _asp_declare('double', 'b1_3')
                    _asp_declare('double', 'A_0_1')
                    _asp_declare('double', 'A_0_2')
                    _asp_declare('double', 'A_0_3')
                    rho = 1
                    b1_1 = 2
                    b1_2 = 3            
                    b1_3 = 4      
                    A_0_1 = 5
                    A_0_2 = 6
                    A_0_3 = 7
                    return x[4] + pow(4*x[1], 2) * b1_2/(2*rho*A_0_2)
                def func5(x):
                    _asp_declare('double', 'rho')
                    _asp_declare('double', 'b1_1')
                    _asp_declare('double', 'b1_2')
                    _asp_declare('double', 'b1_3')
                    _asp_declare('double', 'A_0_1')
                    _asp_declare('double', 'A_0_2')
                    _asp_declare('double', 'A_0_3')
                    rho = 1
                    b1_1 = 2
                    b1_2 = 3            
                    b1_3 = 4      
                    A_0_1 = 5
                    A_0_2 = 6
                    A_0_3 = 7
                    return x[5] + pow(4*x[2],2) * b1_3/(2*rho*A_0_3)

                self.solve([func0,func1,func2, func3, func4,func5], initialGuess, solution, epsilon, max_iters)
        guess = [1, 2, 3, 4, 5, 6]
        solution = [0,0,0,0,0,0]
        kernel = JunctionNewtonKernel()
        kernel.pure_python = False
        kernel.kernel(guess, solution, 0.00001, 1000)
        
        # populate solutions into out_junction
        count = 0
        for num in out_junction.line_sides.keys():
            if out_junction.line_sides[num] == Side.LEFT:
                if input_side_name == Side.LEFT:
                    out_junction.line_values[num][0].A = abs(solution[0])
                    out_junction.line_values[num][0].u = abs(solution[3])
                    out_junction.line_values[num][0].p = abs(solution[0]*solution[3]/2)# = leftSide.pop()#StencilStruct(1,2,3)
                else:
                    out_junction.line_values[num][0].A = abs(solution[1+count])
                    out_junction.line_values[num][0].u = abs(solution[4+count])
                    out_junction.line_values[num][0].p = abs(solution[0+count]*solution[3+count]/2)# = leftSide.pop()#StencilStruct(1,2,3)              
                    count+=1              
            elif out_junction.line_sides[num] == Side.RIGHT:
                if input_side_name == Side.RIGHT:
                    out_junction.line_values[num][0].A = abs(solution[0])
                    out_junction.line_values[num][0].u = abs(solution[3])
                    out_junction.line_values[num][0].p = abs(solution[0]*solution[3]/2)# = leftSide.pop()#StencilStruct(1,2,3)
                else:
                    out_junction.line_values[num][0].A = abs(solution[1+count])
                    out_junction.line_values[num][0].u = abs(solution[4+count])
                    out_junction.line_values[num][0].p = abs(solution[1+count]*solution[4+count]/2)# = leftSide.pop()#StencilStruct(1,2,3)
                    count+=1
            else:
                raise Exception("unknown side")


class BoundaryKernel(JunctionKernel):
    """A computation over the nodes along the boundary of a line. This is a
    specific instance of a junction kernel in that a boundary is a
    junction with only one line (however, such a junction would actually be
    illegal as junctions must comprise three or more lines).
    """
    def boundary_values(self, in_boundary, out_boundary):
        inflow = in_boundary.line_sides.values()[0] == Side.LEFT
        if inflow:
            class TempKernel(NewtonKernel):
                def kernel(self, initialGuess, solution, epsilon, max_iters):
                    # x[0] = pL_half
                    # x[1] = pR_half
                    # x[2] = uR_half
                    def func0(x):
                        _asp_declare("double", "u_inflow")
                        u_inflow = 0
                        return x[1] - u_inflow
                    def func1(x):
                        _asp_declare("double", "rho")
                        _asp_declare("double", "c1star")
                        rho = 1050
                        c1star = 0.001
                        return x[2]-x[1]*rho*c1star
                    def func2(x):
                        _asp_declare("double", "A_0star")
                        _asp_declare("double", "b1star")
                        A_0star = 1
                        b1star = 2                        
                        return x[2]-(b1star/A_0star)*x[0]
                    self.solve([func0,func1,func2], initialGuess, solution, epsilon, max_iters)
        else:
            # outflow
            class TempKernel(NewtonKernel):
                def kernel(self, initialGuess, solution, epsilon, max_iters):
                    def func0(x):
                        _asp_declare("double", "A_0star")
                        _asp_declare("double", "b1star")
                        A_0star = 5
                        b1star = 2         
                        return x[0] - 4*pow(x[0], 2) -  (x[0] - 1)
                    def func1(x):
                        _asp_declare("double", "A_0star")
                        _asp_declare("double", "b1star")
                        A_0star = 5
                        b1star = 2           
                        return x[2] - (b1star/A_0star)*(x[0] - sqrt(A_0star))
                    def func2(x):
                        _asp_declare("double", "rho")
                        _asp_declare("double", "c1star")
                        rho = 1050
                        c1star = 2           
                        return x[1] - (x[2] - 2)/(rho*c1star)
                    self.solve([func0,func1,func2], initialGuess, solution, epsilon, max_iters)
        kernel = TempKernel()
        #kernel.pure_python= True
        initialGuesses = [1,1,1]
        solution = [0,0,0]
        kernel.kernel(initialGuesses, solution, 0.0001, 100)
        #import numpy
        #out_boundary.values = numpy.zeros(3, float)
        """
        for num in out_boundary.line_sides.keys():# = abs(solution[1+count])
            print dir(out_boundary.line_values[num])
            out_boundary.line_values[num][0].A = solution[0]
            out_boundary.line_values[num][0].u = solution[1]
            out_boundary.line_values[num][0].p = solution[2]

        for _, value in out_boundary.line_values.items():
            for i in range(len(value)):
                print value
                value[i] = (solution[i])
        """ 

class KernelPass(object):

    def __init__(self, line_kernel, junction_kernel, boundary_kernel):
        self.line_kernel = line_kernel
        self.junction_kernel = junction_kernel
        self.boundary_kernel = boundary_kernel

        # Create a kernel executor that can help run the kernels in parallel.
        self.executor = ParallelExecutor()#line_kernel, junction_kernel,
                                         #boundary_kernel)

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
            yield in_junctions[junction.key()], junction

    @staticmethod
    def boundary_pairs(in_graph, out_graph):
        in_boundaries = {}
        for boundary in in_graph.boundaries:
            in_boundaries[boundary.key()] = boundary
        for boundary in out_graph.boundaries:
            yield in_boundaries[boundary.key()], boundary

