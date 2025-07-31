# orbitsi/main.py
import argparse
from orbitsi.utils import read_graph_from_file
from orbitsi.orbit import EVOKEOrbitCounter, ORCAOrbitCounter
from orbitsi.search import FilterEngine, OrderEngine, SearchEngine

def run_search(args):
    data_graph = read_graph_from_file(args.data)
    pattern_graph = read_graph_from_file(args.pattern)

    counter_cls = EVOKEOrbitCounter if args.orbit_counter == "evoke" else ORCAOrbitCounter

    filter_engine = FilterEngine(
        data_graph=data_graph,
        pattern_graph=pattern_graph,
        orbit_counter_class=counter_cls,
        graphlet_size=args.graphlet_size
    )
    pattern_orbits, candidate_sets = filter_engine.run()
    order_engine = OrderEngine(pattern_graph, pattern_orbits)
    order, pivot = order_engine.run()
    search_engine = SearchEngine(data_graph, pattern_graph, candidate_sets, order, pivot)
    matches = search_engine.run()

    print(f"✅ Matches found: {len(matches)}")
    for match in matches:
        print(match)


def run_orbit_count(args):
    G = read_graph_from_file(args.graph)
    counter_cls = EVOKEOrbitCounter if args.orbit_counter == "evoke" else ORCAOrbitCounter
    counter = counter_cls(G, size=args.graphlet_size)
    orbits = counter.get_orbits(induced=args.induced)
    print(orbits)


def cli_entrypoint():
    parser = argparse.ArgumentParser(prog="orbitsi")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- search ---
    search_parser = subparsers.add_parser("search", help="Subgraph isomorphism search")
    search_parser.add_argument("--data", required=True, help="Path to data graph")
    search_parser.add_argument("--pattern", required=True, help="Path to pattern graph")
    search_parser.add_argument("--orbit-counter", choices=["evoke", "orca"], default="evoke")
    search_parser.add_argument("--graphlet-size", type=int, choices=[4, 5], default=4)
    search_parser.set_defaults(func=run_search)

    # --- count-orbits ---
    count_parser = subparsers.add_parser("count-orbits", help="Count node orbits in a graph")
    count_parser.add_argument("--graph", required=True, help="Path to graph")
    count_parser.add_argument("--orbit-counter", choices=["evoke", "orca"], default="evoke")
    count_parser.add_argument("--graphlet-size", type=int, choices=[4, 5], default=4)
    count_parser.add_argument("--induced", action="store_true", help="Compute induced orbits")
    count_parser.set_defaults(func=run_orbit_count)

    args = parser.parse_args()
    args.func(args)
