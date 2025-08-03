from functools import reduce
from operator import mul
from quantecon import cartesian
import numpy as np
from numpy import linspace

def prod(l): 
	return reduce(mul, l, 1.0)


def mlinspace(a,b,orders,out=None):

    sl = [linspace(a[i],b[i],orders[i]) for i in range(len(a))]
    
    if out is None:
        out = cartesian(sl)
    else:
        cartesian(sl, out)

    return out
	
	
class Grid:
    """
    Grid class is a parent class of EmptyGrid, PointGrid, UnstructuredGrid, 
    CartesianGrid, NonUniformCartesianGrid, and SmolyakGrid sub-classes.
    
    .. currentmodule: numeric.grids
    """

    def nodes(self):
        return self.__nodes__

    def n_nodes(self):
        return self.__nodes__.shape[0]

    def node(self, i):
        return self.__nodes__[i,:]

class EmptyGrid(Grid):
    """
    EmptyGrid is a sub-class of Grid class.
    
    .. currentmodule: numeric.grids
    """

    type = 'empty'

    def nodes(self):
        return None
    def n_nodes(self):
        return 0
    def node(self, i):
        return None

class PointGrid(Grid):
    """
    PointGrid is a sub-class of Grid class.
    
    .. currentmodule: numeric.grids
    """

    type = 'point'

    def __init__(self, point):
        self.point = np.array(point)

    def nodes(self):
        return None
    def n_nodes(self):
        return 1
    def node(self, i):
        return None

class UnstructuredGrid(Grid):
    """
    UnstructuredGrid is a sub-class of Grid class.
    
    .. currentmodule: numeric.grids
    """

    type = 'unstructured'

    def __init__(self, nodes):
        nodes = np.array(nodes, dtype=float)
        self.min = nodes.min(axis=0)
        self.max = nodes.max(axis=0)
        self.__nodes__ = nodes

class CartesianGrid(Grid):
    """
    CartesianGrid is a sub-class of Grid class.
    
    .. currentmodule: numeric.grids
    """

    type = 'cartesian'

    def __init__(self, min, max, n=[]):

        self.min = np.array(min, dtype=float)
        self.max = np.array(max, dtype=float)
        if len(n) == 0:
            self.n = np.zeros(n, dtype=int) + 20
        else:
            self.n = np.array(n, dtype=int)
        self.__nodes__ = mlinspace(self.min, self.max, self.n)

class NonUniformCartesianGrid(Grid):
    """
    NonUniformCartesianGrid is a sub-class of Grid class.
    
    .. currentmodule: numeric.grids
    """

    type = "NonUniformCartesian"

    def __init__(self, list_of_nodes):
        list_of_nodes = [np.array(l) for l in list_of_nodes]
        self.min = [min(l) for l in list_of_nodes]
        self.max = [max(l) for l in list_of_nodes]
        self.__nodes__ = cartesian(list_of_nodes)

class SmolyakGrid(Grid):
    """
    SmolyakGrid is a sub-class of Grid class.
    
    .. currentmodule: numeric.grids
    """

    type = "Smolyak"

    def __init__(self, min, max, mu=2):

        print(min, max, mu)
        from interpolation.smolyak import SmolyakGrid as ISmolyakGrid
        min = np.array(min)
        max = np.array(max)
        self.min = min
        self.max = max
        self.mu = mu
        d = len(min)
        print(mu)
        sg = ISmolyakGrid(d, mu, lb=min, ub=max)
        self.sg = sg
        self.__nodes__ = sg.grid

def cat_grids(grid_1, grid_2):

    if isinstance(grid_1, EmptyGrid):
        return grid_2
    if isinstance(grid_1, CartesianGrid) and isinstance(grid_2, CartesianGrid):
        min = np.concatenate([grid_1.min, grid_2.min])
        max = np.concatenate([grid_1.max, grid_2.max])
        n = np.concatenate([grid_1.n, grid_2.n])
        return CartesianGrid(min, max, n)
    else:
        raise Exception("Not Implemented.")

# compat
def node(grid, i): return grid.node(i)
def nodes(grid): return grid.nodes()
def n_nodes(grid): return grid.n_nodes()

if __name__ == "__main__":
    """
    Main entry point
    """

    print("Cartesian Grid")
    grid = CartesianGrid([0.1, 0.3], [9, 0.4], [50, 10])
    print(grid.nodes())
    print(nodes(grid))

    print("UnstructuredGrid")
    ugrid = UnstructuredGrid([[0.1, 0.3], [9, 0.4], [50, 10]])
    print(nodes(ugrid))
    print(node(ugrid,0))
    print(n_nodes(ugrid))


    print("Non Uniform CartesianGrid")
    ugrid = NonUniformCartesianGrid([[0.1, 0.3], [9, 0.4], [50, 10]])
    print(nodes(ugrid))
    print(node(ugrid,0))
    print(n_nodes(ugrid))

    print("Smolyak Grid")
    sg = SmolyakGrid([0.1, 0.2], [1.0, 2.0], 2)
    print(nodes(sg))
    print(node(sg, 1))
    print(n_nodes(sg))
