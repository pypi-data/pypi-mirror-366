import networkx as nx
import numpy as np
from _evoke_cpp import evoke_count
from .orbit_converter import OrbitMatrixConverter

class EVOKEOrbitCounter:
    def __init__(self, G: nx.Graph, size: int = 4):
        self.G = G
        self.size = size
        self.counts = None
        self.converter = OrbitMatrixConverter()

    def _nx_to_cpp_graph(self) -> dict[int, list[int]]:
        return {int(n): [int(nbr) for nbr in self.G.neighbors(n)] for n in self.G.nodes}

    def count_orbits(self):
        cpp_graph = self._nx_to_cpp_graph()
        self.counts = evoke_count(cpp_graph, size=self.size, parallel=True)
        return self.counts

    def get_orbits(self, induced: bool = False) -> np.ndarray:
        if self.counts is None:
            self.count_orbits()
        sorted_nodes = sorted(self.counts)
        orbit_matrix = np.array([self.counts[node] for node in sorted_nodes], dtype=int)
        return self.converter.noninduced_to_induced(orbit_matrix) if induced else orbit_matrix