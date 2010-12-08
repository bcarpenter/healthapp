from math import sqrt
from webgraph import Side
from webkernel import BoundaryKernel
from newton_kernel import NewtonKernel
from asp import _asp_declare


class InterfaceBoundaryKernel(BoundaryKernel):

    def boundary_values(self, in_boundary, out_boundary):
        inflow = in_boundary.line_sides.values()[0] == Side.LEFT
        if inflow:
            kernel = InflowKernel()
        else:
            kernel = OutflowKernel()
        initialGuesses = [1, 1, 1]
        solution = [0, 0, 0]
        kernel.kernel(initialGuesses, solution, 0.0001, 100)


class InflowKernel(NewtonKernel):

    def kernel(self, initialGuess, solution, epsilon, max_iters):

        def func0(x):
            _asp_declare('double', 'u_inflow')
            u_inflow = 0
            return x[1] - u_inflow

        def func1(x):
            _asp_declare('double', 'rho')
            _asp_declare('double', 'c1star')
            rho = 1050
            c1star = 0.001
            return x[2] - x[1] * rho * c1star

        def func2(x):
            _asp_declare('double', 'A_0star')
            _asp_declare('double', 'b1star')
            A_0star = 1
            b1star = 2                        
            return x[2] - (b1star / A_0star) * x[0]

        functions = [func0, func1, func2]
        self.solve(functions, initialGuess, solution, epsilon, max_iters)


class OutflowKernel(NewtonKernel):

    def kernel(self, initialGuess, solution, epsilon, max_iters):

        def func0(x):
            _asp_declare('double', 'A_0star')
            _asp_declare('double', 'b1star')
            A_0star = 5
            b1star = 2         
            return x[0] - 4 * pow(x[0], 2) - (x[0] - 1)

        def func1(x):
            _asp_declare('double', 'A_0star')
            _asp_declare('double', 'b1star')
            A_0star = 5
            b1star = 2           
            return x[2] - (b1star / A_0star) * (x[0] - sqrt(A_0star))

        def func2(x):
            _asp_declare('double', 'rho')
            _asp_declare('double', 'c1star')
            rho = 1050
            c1star = 2           
            return x[1] - (x[2] - 2) / (rho * c1star)

        functions = [func0, func1, func2]
        self.solve(functions, initialGuess, solution, epsilon, max_iters)
