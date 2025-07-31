import networkx as nx
import numpy as np

class OrderEngine:
    def __init__(self, pattern_graph, pattern_orbits=None, method='auto'):
        self.pattern_graph = pattern_graph
        self.pattern_orbits = pattern_orbits
        self.num_nodes = pattern_graph.number_of_nodes()

        if method == 'auto':
            self.use_orbit = pattern_orbits is not None
        elif method == 'orbit':
            if pattern_orbits is None:
                raise ValueError("Orbit method selected but no orbit data provided.")
            self.use_orbit = True
        elif method == 'degree':
            self.use_orbit = False
        else:
            raise ValueError("Invalid method: choose from 'auto', 'orbit', or 'degree'")

    def compute_score(self, node):
        if self.use_orbit:
            return sum(x * x for x in self.pattern_orbits[node])
        else:
            return self.pattern_graph.degree[node]

    def run(self):
        order = []
        pivot = {}
        visited = set()

        orbit_strength = {
            u: self.compute_score(u)
            for u in self.pattern_graph.nodes
        }

        start_node = max(orbit_strength, key=orbit_strength.get)
        order.append(start_node)
        visited.add(start_node)
        pivot[start_node] = None  # root has no pivot

        for _ in range(1, self.num_nodes):
            max_bn = -1
            selected = None

            for u in self.pattern_graph.nodes:
                if u in visited:
                    continue

                backward_neighbors = sum(
                    1 for v in order if self.pattern_graph.has_edge(u, v)
                )

                if backward_neighbors > max_bn or (
                    backward_neighbors == max_bn and
                    orbit_strength[u] > orbit_strength.get(selected, -1)
                ):
                    max_bn = backward_neighbors
                    selected = u

            # Find pivot among previously ordered nodes
            pivot_node = next(
                (v for v in order if self.pattern_graph.has_edge(selected, v)), None
            )
            pivot[selected] = pivot_node

            visited.add(selected)
            order.append(selected)

        return order, pivot