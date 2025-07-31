import networkx as nx
from collections import defaultdict, Counter

class FilterEngine:
    def __init__(self, data_graph, pattern_graph, orbit_counter_class, graphlet_size=4):
        self.data_graph = data_graph
        self.pattern_graph = pattern_graph
        self.graphlet_size = graphlet_size
        self.orbit_counter_class = orbit_counter_class
        self.data_labels = nx.get_node_attributes(data_graph, "label")
        self.pattern_labels = nx.get_node_attributes(pattern_graph, "label")


        self.label_index = defaultdict(list)
        for node, label in self.data_labels.items():
            self.label_index[label].append(node)

        # Orbit counters
        self.pattern_orbits = self._compute_orbits(pattern_graph, orbit_counter_class)

    def _compute_orbits(self, graph, counter_class):
        counter = counter_class(graph, size=self.graphlet_size)
        orbit_matrix = counter.get_orbits(induced=False)
        return {node: orbit_matrix[i].tolist() for i, node in enumerate(graph.nodes())}

    def run(self):
        candidate_sets = self.ldf_filter()
        if not candidate_sets:
            return {}, {}, None
        candidate_sets = self.nlf_filter(candidate_sets)
        if not candidate_sets:
            return {}, {}, None

        candidate_sets, subgraph = self.orbit_filter(candidate_sets)
        if not candidate_sets:
            return {}, {}, None

        return self.pattern_orbits, candidate_sets, subgraph

    def ldf_filter(self):
        candidate_sets = {}
        data_degrees = dict(self.data_graph.degree)

        for u in self.pattern_graph.nodes:
            label_u = self.pattern_labels[u]
            deg_u = self.pattern_graph.degree[u]

            labeled_nodes = self.label_index.get(label_u, [])
            candidates = [
                v for v in labeled_nodes
                if data_degrees[v] >= deg_u
            ]

            if not candidates:
                return {}
            candidate_sets[u] = candidates

        return candidate_sets

    def nlf_filter(self, candidate_sets):
        refined_sets = {}

        pattern_nlf = {
            u: Counter(self.pattern_labels[nbr] for nbr in self.pattern_graph.neighbors(u))
            for u in self.pattern_graph.nodes
        }

        # Compute only NLFs for candidate vertices actually used
        used_data_nodes = set(v for cset in candidate_sets.values() for v in cset)
        data_nlf = {
            v: Counter(self.data_labels[nbr] for nbr in self.data_graph.neighbors(v))
            for v in used_data_nodes
        }

        for u, candidates in candidate_sets.items():
            u_nlf = pattern_nlf[u]
            filtered = [
                v for v in candidates
                if all(data_nlf[v].get(lbl, 0) >= cnt for lbl, cnt in u_nlf.items())
            ]

            if not filtered:
                return {}
            refined_sets[u] = filtered

        return refined_sets

    def orbit_filter(self, candidate_sets):
        candidate_nodes = set(v for candidates in candidate_sets.values() for v in candidates)
        original_subgraph = self.data_graph.subgraph(candidate_nodes).copy()
        mapping = {node: i for i, node in enumerate(original_subgraph.nodes())}
        reverse_mapping = {i: node for node, i in mapping.items()}
        relabeled_subgraph = nx.relabel_nodes(original_subgraph, mapping)
        counter = self.orbit_counter_class(relabeled_subgraph, size=self.graphlet_size)
        data_orbit_matrix = counter.get_orbits(induced=False)
        data_orbits = {
            reverse_mapping[i]: data_orbit_matrix[i].tolist()
            for i in range(len(data_orbit_matrix))
        }
        refined_sets = {}
        for u, candidates in candidate_sets.items():
            orbit_u = self.pattern_orbits[u]
            filtered = []

            for v in candidates:
                orbit_v = data_orbits.get(v)
                if orbit_v is None:
                    continue
                if all(ov >= ou for ov, ou in zip(orbit_v, orbit_u)):
                    filtered.append(v)

            if not filtered:
                return {}, original_subgraph

            refined_sets[u] = filtered

        return refined_sets, original_subgraph


    def orbit_filter_full(self, candidate_sets):
        # Compute data graph orbits directly on full graph
        counter = self.orbit_counter_class(self.data_graph, size=self.graphlet_size)
        data_orbit_matrix = counter.get_orbits(induced=False)

        # Map orbit vectors to nodes
        data_orbits = {
            node: data_orbit_matrix[i].tolist()
            for i, node in enumerate(self.data_graph.nodes())
        }

        # Filter candidates using orbit comparison
        refined_sets = {}
        for u, candidates in candidate_sets.items():
            orbit_u = self.pattern_orbits[u]
            filtered = []

            for v in candidates:
                orbit_v = data_orbits[v]
                # All elements of v's orbit vector must be ≥ pattern's orbit vector
                if all(ov >= ou for ov, ou in zip(orbit_v, orbit_u)):
                    filtered.append(v)

            if not filtered:
                return {}

            refined_sets[u] = filtered

        return refined_sets

    def printCandidateSets(self, candidate_sets):
        # Display results
        if not candidate_sets:
            print("No match possible after filtering.")
        else:
            print("\n=== Candidate Sets ===")
            for u, cands in candidate_sets.items():
                print(f"Pattern Node {u} → Candidates: {cands}")