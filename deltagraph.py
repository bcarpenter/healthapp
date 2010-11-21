from collections import namedtuple
from itertools import product

class Side(namedtuple('Side', 'chain side')):

    LEFT = -1
    RIGHT = 1

    def __repr__(self):
        return 'Side(chain=%s, side=%s)' % (self.chain, self.__side_name())

    def __side_name(self):
        if self.side not in (Side.LEFT, Side.RIGHT):
            return 'UNKNOWN'
        return 'Side.LEFT' if self.side is Side.LEFT else 'Side.RIGHT'


class DeltaGraph(object):

    def __init__(self, chains, junctions):
        # Chains are the arrays of nodes (e.g., arteries).
        self.chains = chains
        # Junctions are where multiple chains meet (e.g., bifurcations). They
        # specify which chains meet and which sides of those chains are in the
        # junction. No side of a chain can be in more than one junction.
        self.junctions = junctions

        # Verify the correctness of the junctions.
        chain_sides = set()
        for junction in junctions:
            if len(junction) < 3:
                raise Exception('junction must have at least three chains')
            for chain_side in junction:
                if chain_side in chain_sides:
                    chain, side = chain_side
                    error = '%s side of chain %s in multiple junctions'
                    raise Exception(error % (side, chain))
                chain_sides.add(chain_side)

        # Boundaries specify sides of chains that aren't in junctions.
        chain_ids = DeltaGraph.indices(self.chains)
        all_chain_sides = product(chain_ids, (Side.LEFT, Side.RIGHT))
        all_chain_sides = set(Side(c, s) for c, s in all_chain_sides)
        self.boundaries = all_chain_sides - chain_sides

    def __repr__(self):
        return 'DeltaGraph(chains=%s, junctions=%s)' % \
            (self.chains, self.junctions)

    @staticmethod
    def indices(collection):
        try:
            return collection.keys()
        except AttributeError:
            return range(len(collection))


if __name__ == '__main__':
    chains = [(1, 2, 3, 4, 5, 6, 7, 8, 9),
             (11, 12, 13, 14, 15, 16, 17, 18, 19),
             (21, 22, 23, 24, 25, 26, 27, 28, 29)]
    junctions = [[Side(0, Side.RIGHT),
                  Side(1, Side.LEFT),
                  Side(2, Side.LEFT)]]
    graph = DeltaGraph(chains, junctions)
    print graph.boundaries
