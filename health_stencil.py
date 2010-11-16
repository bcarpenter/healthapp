from stencil_kernel import *
from stencil_grid import *
	
def main():
	class MyKernel(StencilKernel):
		def kernel(self, in_grid, out_grid):
			for x in out_grid.interior_points():
				for y in in_grid.neighbors(x, 1):
						out_grid[x] = out_grid[x] + in_grid[y]



	kernel = MyKernel()
	
	# using 1D grids
	in_grid = StencilGrid([10])
	out_grid = StencilGrid([10])
	
	# fill in_grid interior points with ones	
	for x in in_grid.interior_points():
		print x
		in_grid[x] = in_grid[x] + 1
		

	
	kernel.pure_python = True
	
	print in_grid.data
	for i in range(10):
		kernel.kernel(in_grid, out_grid)
		print out_grid.data

	
	

if __name__ == '__main__':
	main()