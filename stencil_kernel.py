import numpy
import inspect
from stencil_grid import *
from stencil_struct import *
import asp.codegen.python_ast as ast
import asp.codegen.cpp_ast as cpp_ast
import asp.codegen.ast_tools as ast_tools
from asp.util import *

# may want to make this inherit from something else...
class StencilKernel(object):
	def __init__(self):
		# we want to raise an exception if there is no kernel()
		# method defined.
		try:
			dir(self).index("kernel")
		except ValueError:
			raise Exception("No kernel method defined.")

		# if the method is defined, let us introspect and find
		# its AST
		self.kernel_src = inspect.getsource(self.kernel)
		self.kernel_ast = ast.parse(self.remove_indentation(self.kernel_src))

		self.pure_python = False
		self.pure_python_kernel = self.kernel

		# replace kernel with shadow version
		self.kernel = self.shadow_kernel
		

	def remove_indentation(self, src):
		return src.lstrip()

	def add_libraries(self, mod):
		# these are necessary includes, includedirs, and init statements to use the numpy library
		mod.add_library("numpy",[numpy.get_include()+"/numpy"])
		mod.add_header("arrayobject.h")
		mod.add_to_init([cpp_ast.Statement("import_array();")])
		

	def shadow_kernel(self, *args):
		if self.pure_python:
			return self.pure_python_kernel(*args)

		#FIXME: need to somehow match arg names to args
		argnames = map(lambda x: str(x.id), self.kernel_ast.body[0].args.args)
		argdict = dict(zip(argnames[1:], args))
		#debug_print('Kernel arguments:\n' + str(argdict))

		phase2 = StencilKernel.StencilProcessAST(argdict).visit(self.kernel_ast)
		debug_print('Phase 2 AST:\n' + ast.dump(phase2))
		phase3 = StencilKernel.StencilConvertAST(argdict).visit(phase2)

		from asp.jit import asp_module

		mod = asp_module.ASPModule()
		self.add_libraries(mod)
		mod.add_function(phase3)
#		mod.compile()
#		mod.compiled_module.kernel(argdict['in_grid'].data, argdict['out_grid'].data)
		myargs = [y.data for y in args]
#		mod.kernel(argdict['in_grid'].data, argdict['out_grid'].data)
		mod.kernel(*myargs)

	# the actual Stencil AST Node
	class StencilInteriorIter(ast.AST):
		def __init__(self, grid, body, target):
		  self.grid = grid
		  self.body = body
		  self.target = target
		  self._fields = ('grid', 'body', 'target')

		  super(StencilKernel.StencilInteriorIter, self).__init__()
			
	class StencilNeighborIter(ast.AST):
		def __init__(self, grid, body, target, dist):
			self.grid = grid
			self.body = body
			self.target = target
			self.dist = dist
			self._fields = ('grid', 'body', 'target', 'dist')
			super (StencilKernel.StencilNeighborIter, self).__init__()


	# separate files for different architectures
	# class to convert from Python AST to an AST with special Stencil node
	class StencilProcessAST(ast.NodeTransformer):
		def __init__(self, argdict):
			self.argdict = argdict
			super(StencilKernel.StencilProcessAST, self).__init__()

		
		def visit_For(self, node):
			debug_print("visiting a For...\n")
			# check if this is the right kind of For loop
			if (node.iter.__class__.__name__ == "Call" and
				node.iter.func.__class__.__name__ == "Attribute"):
				
				debug_print("Found something to change...\n")

				if (node.iter.func.attr == "interior_points"):
					grid = self.visit(node.iter.func.value).id	   # do we need the name of the grid, or the obj itself?
					target = self.visit(node.target)
					body = map(self.visit, node.body)
					newnode = StencilKernel.StencilInteriorIter(grid, body, target)
					return newnode

				elif (node.iter.func.attr == "neighbors"):
					debug_print(ast.dump(node) + "\n")
					target = self.visit(node.target)
					body = map(self.visit, node.body)
					grid = self.visit(node.iter.func.value).id
					dist = self.visit(node.iter.args[1]).n
					newnode = StencilKernel.StencilNeighborIter(grid, body, target, dist)
					return newnode

				else:
					return node
			else:
				return node

	class StencilConvertAST(ast_tools.ConvertAST):
		
		def __init__(self, argdict):
			self.argdict = argdict
			self.dim_vars = []
			super(StencilKernel.StencilConvertAST, self).__init__()

		def gen_array_macro_definition(self, arg):
			try:
				array = self.argdict[arg]
				defname = "_"+arg+"_array_macro"
				params = "(" + ','.join(["_d"+str(x) for x in xrange(array.dim)]) + ")"
				calc = "(_d%s)" % str(array.dim-1)
				for x in range(1,array.dim):
					calc = "(%s + %s * (_d%s))" % (calc, str(array.shape[x-1]), str(array.dim-x-1))
				return cpp_ast.Define(defname+params, calc)

			except KeyError:
				return cpp_ast.Comment("Not found argument: " + arg)

		def gen_array_macro(self, arg, point):
			macro = "_%s_array_macro(%s)" % (arg, ",".join(map(str, point)))
			return macro

		def gen_dim_var(self, dim):
			"""
			Deterministically generates free variable names for loops over the given
			dimension of the stencil grid. This method generates names like '_i',
			'_j', and so on, wrapping around to '_ia', '_ib', etc... if necessary.
			"""
			characters, offset, dim = [], ord('i') - 1, int(dim + 1)
			while dim > 0:
				quotient, remainder = divmod(dim, ord('z') - offset + 1)
				characters.append(chr(offset + remainder))
				dim = quotient
				offset = ord('a') - 1
			variable = '_' + ''.join(characters)
			self.dim_vars.append(variable)
			return variable

		def gen_array_unpack(self, grid_name, type_name=None):
			type_name = 'double' if type_name is None else type_name
			array_decl = "{0} *_my_{1} = ({0} *) PyArray_DATA({1})"
			return cpp_ast.Statement(array_decl.format(type_name, grid_name))

		def python_to_cpp_type(self, dtype):
			"""Returns the name and declarator for the C++ version of the
			specified type. If the given type is a C++ primitive, the
			declarator is None.
			"""
			if dtype.type is numpy.void:
				fields = []
				for field in dtype.names:
					subtype, _ = dtype.fields[field]
					subname, subdeclarator = self.python_to_cpp_type(subtype)
					if subdeclarator is not None:
						subname = subdeclarator.inline()
					fields.append(cpp_ast.Value(subname, field))
				struct_name = '_void_' + hex(abs(hash(dtype)))[2:]
				return ('struct ' + struct_name,
						cpp_ast.Struct(struct_name, fields))

			if dtype.type is numpy.float32:
				name = 'float'
			elif dtype.type is numpy.float64:
				name = 'double'
			elif dtype.type is numpy.int8:
				name = 'char'
			elif dtype.type is numpy.int16:
				name = 'short'
			elif dtype.type is numpy.int32:
				name = 'int'
			elif dtype.type is numpy.int64:
				name = 'long'
			else:
				raise TypeError('unknown data type: %s' % (dtype,))
			return name, None

		# all arguments are PyObjects
		def visit_arguments(self, node):
			return [cpp_ast.Pointer(cpp_ast.Value("PyObject", self.visit(x))) for x in node.args[1:]]

		def visit_StencilInteriorIter(self, node):
			# should catch KeyError here
			array = self.argdict[node.grid]
			dim = len(array.shape)
			# if dim == 2:
			# 	dim1_var = self.gen_dim_var(0)
			# 	dim2_var = self.gen_dim_var(1)
			# 	start1 = "int %s = %s" % (dim1_var, str(array.ghost_depth))
			# 	condition1 = "%s < %s" % (dim1_var,  str(array.shape[0]-array.ghost_depth))
			# 	update1 = "%s++" % dim1_var
			# 	start2 = "int %s = %s" % (dim2_var, str(array.ghost_depth))
			# 	condition2 = "%s < %s" % (dim2_var, str(array.shape[1]-array.ghost_depth))
			# 	update2 = "%s++" % dim2_var

			definitions = cpp_ast.Module()
			# Define macros for linearizing n-D array indices.
			definitions.extend(self.gen_array_macro_definition(v)
												 for v in self.argdict)
			# If the programmer is using structs as stencil node values, generate
			# struct definitions. Map data types to their names.
			type_names, stencil_types = {}, {}
			for variable, grid in self.argdict.items():
				if grid.dtype not in type_names:
					type_name, declarator = self.python_to_cpp_type(grid.dtype)
					type_names[grid.dtype] = type_name
					if declarator is not None:
						definitions.append(declarator)
				stencil_types[variable] = type_names[grid.dtype]

			# Add the array declarations.
			for variable in self.argdict:
				type_name = stencil_types[variable]
				definitions.append(self.gen_array_unpack(variable, type_name))

			# Iteratively generate the contents of the top-level loop.
			loop_node = None
			for d in xrange(dim):
				dim_var = self.gen_dim_var(d)
				start = "int %s = %s" % (dim_var, str(array.ghost_depth))
			 	condition = "%s < %s" % (dim_var,  str(array.shape[d]-array.ghost_depth))
				update = "%s++" % dim_var
				if d == 0:
					loop_node = cpp_ast.For(start, condition, update, cpp_ast.Block())
					cur_node = loop_node
				else:
					cur_node.body = cpp_ast.For(start, condition, update, cpp_ast.Block())
					cur_node = cur_node.body
		
			body = cpp_ast.Block()
			body.append(cpp_ast.Value("int", self.visit(node.target)))
			body.append(cpp_ast.Assign(self.visit(node.target),
									   self.gen_array_macro(node.grid, self.dim_vars)))

			replaced_body = None
			for gridname in self.argdict:
				replacer = ast_tools.ASTNodeReplacer(ast.Name(gridname, None),
																						 ast.Name('_my_' + gridname, None))
				replaced_body = [replacer.visit(n) for n in node.body]
			body.extend(self.visit(n) for n in replaced_body)

			cur_node.body = body

			ret_node = definitions
			ret_node.append(loop_node)
			return ret_node

		def visit_StencilNeighborIter(self, node):

			block = cpp_ast.Block()
			target = self.visit(node.target)
			block.append(cpp_ast.Value("int", target))
				     
			grid = self.argdict[node.grid]
			debug_print(node.dist)
			for neighbor in grid.neighbor_definition[node.dist]:
				point = ['(%s + %d)' % (v, n) for v, n in zip(self.dim_vars, neighbor)]
				array_index = self.gen_array_macro(node.grid, point)
				block.append(cpp_ast.Assign(target, array_index))
				block.extend([self.visit(z) for z in node.body])

			debug_print('StencilNeighborIter block:\n' + str(block))
			return block
