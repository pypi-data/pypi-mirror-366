import networkx as nx
import numpy as np
from _orca_cpp import orca_count
from .orbit_converter import OrbitMatrixConverter

class ORCAOrbitCounter:
    def __init__(self, G: nx.Graph, size: int = 4):
        self.G = G
        self.size = size
        self.counts = None
        self.converter = OrbitMatrixConverter()

    def _nx_to_cpp_adjlist(self) -> tuple[list[list[int]], dict]:
        n = self.G.number_of_nodes()
        adj = [[] for _ in range(n)]
        mapping = {node: i for i, node in enumerate(sorted(self.G.nodes()))}
        for u, v in self.G.edges():
            adj[mapping[u]].append(mapping[v])
            adj[mapping[v]].append(mapping[u])
        return adj, mapping

    def count_orbits(self) -> dict[int, list[int]]:
        adj, mapping = self._nx_to_cpp_adjlist()
        orbit_matrix = orca_count(adj, self.size)
        reverse_mapping = {v: k for k, v in mapping.items()}
        self.counts = {reverse_mapping[i]: row for i, row in enumerate(orbit_matrix)}
        return self.counts

    def get_orbits(self, induced: bool = False) -> np.ndarray:
        if self.counts is None:
            self.count_orbits()
        sorted_nodes = sorted(self.counts)
        orbit_matrix = np.array([self.counts[node] for node in sorted_nodes], dtype=int)
        return orbit_matrix if induced else self.converter.induced_to_noninduced(orbit_matrix)
