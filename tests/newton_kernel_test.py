from math import *
from newton_kernel import NewtonKernel
import numpy

class MyKernel(NewtonKernel):
    ten = -14
    test = ten
    def kernel(self, initialGuess, solution, epsilon, max_iters):
        # this calls either the C or the python, depending on what is wanted
        def func0(x):
            _asp_declare('double', 'test')
            test = -14
            return sqrt(pow(10-x[0],2) + pow(10-x[1], 2) ) + test
        def func1(x):
            return sqrt(pow(10-x[0],2) + pow(-10-x[1], 2) ) - 16
        self.solve([func0,func1], initialGuess, solution, epsilon, max_iters)

solution = [0,0]
kernel = MyKernel()
kernel.pure_python = False
kernel.kernel([1,1], solution, 0.0001,100)
print solution
