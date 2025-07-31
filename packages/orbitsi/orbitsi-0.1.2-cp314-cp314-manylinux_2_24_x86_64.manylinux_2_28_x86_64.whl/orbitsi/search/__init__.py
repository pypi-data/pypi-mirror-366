from .filtering import FilterEngine
from .ordering import OrderEngine
from .searching import SearchEngine

class OrbitSIEngine:
    def __init__(self, data_graph, orbit_counter_class, graphlet_size=4):
        self.data_graph = data_graph
        self.orbit_counter_class = orbit_counter_class
        self.graphlet_size = graphlet_size

    def run(self, pattern_graph):
        try:
            filter_engine = FilterEngine(
                data_graph=self.data_graph,
                pattern_graph=pattern_graph,
                orbit_counter_class=self.orbit_counter_class,
                graphlet_size=self.graphlet_size
            )
            pattern_orbits, candidate_sets, subgraph = filter_engine.run()
        except ValueError:
            candidate_sets = None

        if not candidate_sets:
            matches = []
        else:
            order_engine = OrderEngine(pattern_graph, pattern_orbits)
            order, pivot = order_engine.run()
            search_engine = SearchEngine(subgraph, pattern_graph, candidate_sets, order, pivot)
            matches = search_engine.run()

        return matches
