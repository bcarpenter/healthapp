from itertools import product
from stencil_struct import StencilStruct
import numpy

class StencilGrid(object):

    def __init__(self, size, dtype=float):
        self.dim = len(size)
        self.shape = size
        self.ghost_depth = 1
        self.dtype = numpy.dtype(dtype)
        self.data = numpy.zeros(size, dtype)

        self.set_grid_variables()
        self.set_interior()
        # add default neighbor definition
        self.set_default_neighbor_definition()

    def __getitem__(self, key):
        """
        Allows the programmer to index into the stencil grid using the []
        notation. If the data type of this stencil grid is a struct type, the
        returned item is a struct with the same fields.
        """
        # For struct types, wrap the data in a proxy object that allows the
        # dot (.) notation to access attributes instead of the [] notation
        # that numpy's dtype objects use.
        if self.dtype.type is numpy.void:
            return StencilStruct(self.dtype, self.data.__getitem__(key))
        return self.data.__getitem__(key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def set_grid_variables(self):
        self.grid_variables = ["DIM"+str(x) for x in range(0,self.dim)]

    def set_interior(self):
        """
        Sets the number of interior points in each dimension
        """
        self.interior = [size - self.ghost_depth * 2 for size in self.shape]
        
    def set_default_neighbor_definition(self):
        """
        Sets the default for neighbors[0] and neighbors[1].  Note that neighbors[1]
        does not include the center point.
        """
        self.neighbor_definition = []

        self.neighbor_definition.append([tuple([0 for x in range(self.dim)])])
        self.neighbor_definition.append([])

        for x in range(self.dim):
            for y in (1, -1):
                tmp = list(self.neighbor_definition[0][0])
                tmp[x] += y
                self.neighbor_definition[1].append(tuple(tmp))

    def interior_points(self):
        """
        Iterator over the interior points of the grid.  Only executed
        in pure Python mode; in SEJITS mode, it should be executed only
        in the translated language/library.
        """
        all_dims = []
        for dimension in range(self.dim):
            # When computing the number of interior points, we assumed that
            # the ghost depth is symmetric on both sides.
            start = (self.shape[dimension] - self.interior[dimension]) / 2
            all_dims.append(range(start, self.shape[dimension] - start))
        return (list(point) for point in product(*all_dims))

    def border_points(self):
        """
        Iterator over the border points of a grid.  Only executed in pure Python
        mode; in SEJITS mode, it should be executed only in the translated
        language/library.
        """
        pass

    def neighbors(self, center, dist):
        """
        Returns a list of neighbors that are at distance dist from the center
        point.  Uses neighbor_definition to determine what the neighbors are.
        """
        # return tuples for each neighbor
        for neighbor in self.neighbor_definition[dist]:
            yield tuple(c + n for c, n in zip(center, neighbor))
