import numpy
import unittest
from stencil_grid import *
from stencil_struct import *

class BasicTests(unittest.TestCase):
    def test_init(self):
        grid = StencilGrid([10,10])
        self.failIf(grid.dim != 2)
        self.failIf(grid.data.shape != (10,10))
        self.failIf(grid.interior != [8,8])
        self.failIf(grid.grid_variables[0] != "DIM0")

    def test_neighbor_definition_2D(self):
        grid = StencilGrid([10,10])
        # test to make sure default neighbor definition is correct
        self.failIf(grid.neighbor_definition[0] != [(0,0)])
        self.failIf(len(grid.neighbor_definition[1]) != 4)

    def test_neighbor_definition_3D(self):
        # test to make sure default neighbor definition is correct in 3D
        grid = StencilGrid([5,5,5])
        self.failIf(len(grid.neighbor_definition[1]) != 6)

    def test_neighbor_definition_1D(self):
        grid = StencilGrid([10])
        self.assertEquals(len(grid.neighbor_definition[1]), 2)

    def test_interior_iterator_1D(self):
        grid = StencilGrid([10])
        pts = [x for x in grid.interior_points()]
        self.assertEqual(len(pts), 8)


    def test_interior_iterator_2D(self):
        # 2D
        grid = StencilGrid([5,5])
        pts = [x for x in grid.interior_points()]
        self.failIf(pts[0] != [1,1])
        self.failIf(len(pts) != 9)

    def test_interior_iterator_3D(self):
        # 3D
        grid = StencilGrid([5,5,5])
        pts = [x for x in grid.interior_points()]
        self.failIf(pts[0] != [1,1,1])
        self.failIf(len(pts) != 27)
    
    def test_neighbors_iterator(self):
        grid = StencilGrid([10,10])
        self.failIf(len([x for x in grid.neighbors([1,1],1)]) != 4)

        grid = StencilGrid([5,5,5])
        self.failIf(len([x for x in grid.neighbors([1,1,1],1)]) != 6)

        grid = StencilGrid([5])
        self.assertEquals(len([x for x in grid.neighbors([1],1)]), 2)

    def test_struct_type_1D(self):
        dtype = numpy.dtype([('a', float), ('b', float), ('c', float)])
        grid = StencilGrid([10], dtype)
        self.assertEquals(len(tuple(grid.neighbors([1], 1))), 2)

    def test_struct_type_2D(self):
        dtype = numpy.dtype([('a', float), ('b', float), ('c', float)])
        grid = StencilGrid([10, 10], dtype)
        self.assertEquals(len(tuple(grid.neighbors([1, 1], 1))), 4)

    def test_struct_field_access_1D(self):
        # This test should probably be split into smaller tests...
        dtype = numpy.dtype([('a', float), ('b', float),
                             ('c', float), ('d', float)])
        grid = StencilGrid([10], dtype)

        # Test writing to the stencil nodes in various ways.
        counter = 1.0
        for ii in range(grid.shape[0]):
            grid[ii][0] = counter
            grid[ii].b = counter + 1
            struct_object = grid[ii]
            struct_object[2] = counter + 2
            struct_object.d = counter + 3
            counter += 4

        counter = 1.0
        # Test reading from the stencil nodes in various ways.
        for ii in range(grid.shape[0]):
            struct_object = grid[ii]
            self.assertEquals(struct_object.a, counter)
            self.assertEquals(struct_object[1], counter + 1)
            self.assertEquals(grid[ii].c, counter + 2)
            self.assertEquals(grid[ii][3], counter + 3)
            counter += 4

if __name__ == '__main__':
    unittest.main()
