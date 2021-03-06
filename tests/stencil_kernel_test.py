import unittest
from stencil_kernel import *
from asp.util import *

class BasicTests(unittest.TestCase):
	def test_init(self):
		# if no kernel method is defined, it should fail
		self.failUnlessRaises((Exception), StencilKernel)
	
	def test_pure_python(self):
		class MyKernel(StencilKernel):
			def kernel(self, in_grid, out_grid):
				print "Running kernel...\n"
				for x in out_grid.interior_points():
					out_grid[x] = in_grid[x]


		kernel = MyKernel()
		in_grid = StencilGrid([10,10])
		out_grid = StencilGrid([10,10])
		kernel.pure_python = True
		kernel.kernel(in_grid, out_grid)
		self.failIf(in_grid[3,3] != out_grid[3,3])





class StencilProcessASTTests(unittest.TestCase):
	def setUp(self):
		class MyKernel(StencilKernel):
			def kernel(self, in_grid, out_grid):
				for x in out_grid.interior_points():
					for y in in_grid.neighbors(x, 1):
						out_grid[x] += in_grid[y]


		self.kernel = MyKernel()
		self.in_grid = StencilGrid([10,10])
		self.out_grid = StencilGrid([10,10])
	
	def test_get_kernel_body(self):
		self.failIfEqual(self.kernel.kernel_ast, None)


		
	def test_StencilInteriorIter_and_StencilNeighborIter(self):
		import re
		argdict = {'in_grid': self.in_grid, 'out_grid': self.out_grid}
		output_as_string = ast.dump(StencilKernel.StencilProcessAST(argdict).visit(self.kernel.kernel_ast))
		self.assertTrue(re.search("StencilInteriorIter", output_as_string))
		self.assertTrue(re.search("StencilNeighborIter", output_as_string))


class StencilConvertASTTests(unittest.TestCase):
	def setUp(self):
		class MyKernel(StencilKernel):
			def kernel(self, in_grid, out_grid):
				for x in out_grid.interior_points():
					for y in in_grid.neighbors(x, 1):
						out_grid[x] = out_grid[x] + in_grid[y]


		self.kernel = MyKernel()
		self.in_grid = StencilGrid([10,10])
		self.out_grid = StencilGrid([10,10])
		self.argdict = argdict = {'in_grid': self.in_grid, 'out_grid': self.out_grid}


	def test_StencilConvertAST_array_macro(self):
		import re
		
		result = StencilKernel.StencilConvertAST(self.argdict).gen_array_macro_definition('in_grid')

		self.assertTrue(re.search("array_macro", str(result)))
		self.assertTrue(re.search("#define", str(result)))

	def test_StencilConvertAST_array_macro_use(self):
		result = StencilKernel.StencilConvertAST(self.argdict).gen_array_macro('in_grid', [3,4])
		self.assertEqual(result, "_in_grid_array_macro(3,4)")

	def test_StencilConvertAST_array_replacement(self):
		import asp.codegen.python_ast as ast
		return True
		n = ast.Subscript(ast.Name("grid", None), ast.Index(ast.Num(1)), None)
		result = StencilKernel.StencilConvertAST(self.argdict).visit(n)
		self.assertEqual(str(result), "_my_grid[1]")


	def test_StencilConvertAST_array_unpack_to_double(self):
		converter = StencilKernel.StencilConvertAST(self.argdict)
		statements = []
		for variable in self.argdict:
			statements.append(converter.gen_array_unpack(variable))
		code = ''.join(stmt.generate().next() for stmt in statements)
		self.assertEqual(code, ("double *_my_out_grid = (double *) PyArray_DATA(out_grid);"
														"double *_my_in_grid = (double *) PyArray_DATA(in_grid);"))

	def test_visit_StencilInteriorIter(self):
		import asp.codegen.python_ast as ast, re
		
		n = StencilKernel.StencilInteriorIter("in_grid",
						      [ast.Pass()],
						      ast.Name("targ", None))
		result = StencilKernel.StencilConvertAST(self.argdict).visit(n)
		self.assertTrue(re.search("Module", str(type(result))))
	
	def test_visit_StencilNeighborIter(self):
		import asp.codegen.python_ast as ast, re
		n = StencilKernel.StencilNeighborIter("in_grid",
						      [ast.parse("in_grid[x] = in_grid[x] + out_grid[y]").body[0]],
						      ast.Name("y", None),
						      1)
		converter = StencilKernel.StencilConvertAST(self.argdict)
		# visit_StencilNeighborIter expects to have dim vars defined already
		converter.gen_dim_var(0)
		converter.gen_dim_var(1)
		result = converter.visit(n)
		self.assertTrue(re.search("array_macro", str(result)))

	def test_whole_thing(self):

		import numpy
		self.in_grid.data = numpy.ones([10,10])

		print self.in_grid.data
		
		self.kernel.kernel(self.in_grid, self.out_grid)
		
		print self.out_grid.data
		self.assertEqual(self.out_grid[5,5],4.0)


class Stencil1dAnd3dTests(unittest.TestCase):
	def setUp(self):
		class My1DKernel(StencilKernel):
			def kernel(self, in_grid_1d, out_grid_1d):
				for x in out_grid_1d.interior_points():
					for y in in_grid_1d.neighbors(x, 1):
						out_grid_1d[x] = out_grid_1d[x] + in_grid_1d[y]


		self.kernel = My1DKernel()
		self.in_grid = StencilGrid([10])
		self.out_grid = StencilGrid([10])
		self.argdict =  {'in_grid_1d': self.in_grid, 'out_grid_1d': self.out_grid}
		
	def test_1d_gen_array_macro_definition(self):
		result = StencilKernel.StencilConvertAST(self.argdict).gen_array_macro_definition('in_grid_1d')
		self.assertEqual(result.__str__(), "#define _in_grid_1d_array_macro(_d0) (_d0)")


	def test_1d_visit_StencilInteriorIter(self):

		import asp.codegen.python_ast as ast, re
		n = StencilKernel.StencilInteriorIter("in_grid_1d",
						      [ast.Pass()],
						      ast.Name("targ", None))
		result = StencilKernel.StencilConvertAST(self.argdict).visit(n)
		self.assertTrue(re.search("Module", str(type(result))))

	def test_whole_thing(self):
		import numpy
		self.in_grid.data = numpy.ones([10])
		self.kernel.kernel(self.in_grid, self.out_grid)
		print self.out_grid.data
		self.assertEqual(self.out_grid[4], 2.0)


class StencilStructConvertASTTests(unittest.TestCase):
    def setUp(self):
        import numpy
        class MyKernel(StencilKernel):
            def kernel(self, in_grid, out_grid):
                for x in out_grid.interior_points():
                    for y in in_grid.neighbors(x, 1):
                        out_grid[x].out_a = (out_grid[x].out_a +
					     in_grid[y].in_a * in_grid[y].in_b)
			out_grid[x].out_b = (out_grid[x].out_b +
					     in_grid[y].in_a + in_grid[y].in_b)
			out_grid[x].out_c = 42

        self.kernel = MyKernel()
        self.in_type = numpy.dtype([('in_a', float), ('in_b', int)])
        self.out_type = numpy.dtype([('out_a', float),
				     ('out_b', float),
				     ('out_c', float)])
        self.in_grid = StencilGrid([5, 5], self.in_type)
        self.out_grid = StencilGrid([5, 5], self.out_type)
        self.argdict = {'in_grid': self.in_grid, 'out_grid': self.out_grid}

    def test_whole_thing(self):
        import numpy
	self.in_grid.data = numpy.ones(self.in_grid.data.shape,
				       self.in_grid.data.dtype)
        self.kernel.kernel(self.in_grid, self.out_grid)
        self.assertEqual(self.out_grid[3,3].out_a, 4.0)
        self.assertEqual(self.out_grid[3,3].out_b, 8.0)
        self.assertEqual(self.out_grid[3,3].out_c, 42.0)

class InterfaceKernelTests(unittest.TestCase):
        def setUp(self):
                import numpy
                from webgraph import Line
                from healthapp import InterfaceKernel
                
                self.kernel = InterfaceKernel()
                self.in_type = numpy.dtype([('A', float), ('u', float), ('p', float)])
                self.out_type = numpy.dtype([('A', float), ('u', float), ('p', float)])
                self.inline = Line([5], self.in_type)
                self.outline = Line([5], self.out_type)
                self.argdict = {'in_grid': self.inline, 'out_grid': self.outline}
        def test_line_kernel(self):
                import numpy
                self.inline.data = numpy.ones(self.inline.data.shape, self.inline.data.dtype)
                self.kernel.kernel(self.inline,self.outline)
                self.assertEqual(self.outline[2].p, 45.0)
        
                
if __name__ == '__main__':
	unittest.main()
