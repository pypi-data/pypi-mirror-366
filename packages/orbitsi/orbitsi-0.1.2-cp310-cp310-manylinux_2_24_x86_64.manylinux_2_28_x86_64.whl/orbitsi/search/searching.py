import networkx as nx

class SearchEngine:
    def __init__(self, data_graph, pattern_graph, candidate_sets, order, pivot):
        self.data_graph = data_graph
        self.pattern_graph = pattern_graph
        self.candidate_sets = candidate_sets
        self.order = order
        self.pivot = pivot
        self.mapping = {}  # pattern_node -> data_node
        self.inverse_mapping = {}  # data_node -> pattern_node
        self.matches = []

    def is_valid(self, u, v):
        if v in self.inverse_mapping:
            return False

        pivot_u = self.pivot.get(u)
        if pivot_u is not None:
            mapped_pivot = self.mapping.get(pivot_u)
            if mapped_pivot is not None and not self.data_graph.has_edge(v, mapped_pivot):
                return False

        # Enforce adjacency constraints to previously mapped nodes
        for u_prev in self.mapping:
            if self.pattern_graph.has_edge(u, u_prev):
                v_prev = self.mapping[u_prev]
                if not self.data_graph.has_edge(v, v_prev):
                    return False

        return True


    def backtrack(self, depth=0):
        if depth == len(self.order):
            # Full match found
            self.matches.append(self.mapping.copy())
            return

        u = self.order[depth]
        for v in self.candidate_sets[u]:
            if self.is_valid(u, v):
                # Assign
                self.mapping[u] = v
                self.inverse_mapping[v] = u
                self.backtrack(depth + 1)
                # Undo
                del self.mapping[u]
                del self.inverse_mapping[v]


    def run(self, return_all=True):
        self.matches = []
        self.backtrack()
        return self.matches if return_all else self.matches[:1]
