import networkx as nx

def read_graph_from_file(filepath):
    """
    Reads an undirected, vertex-labeled graph from file.
    Format:
    - Starts with: t N M
    - Then: N lines of 'v VertexID LabelId Degree' (only label is used)
    - Then: M lines of 'e VertexID VertexID'

    Parameters:
    - filepath: str, path to the graph file

    Returns:
    - G: networkx.Graph with node labels in the 'label' attribute
    """
    G = nx.Graph()

    with open(filepath, 'r') as f:
        for line in f:
            tokens = line.strip().split()
            if not tokens:
                continue
            if tokens[0] == 'v':
                node_id = int(tokens[1])
                label = int(tokens[2])
                G.add_node(node_id, label=label)
            elif tokens[0] == 'e':
                u, v = int(tokens[1]), int(tokens[2])
                G.add_edge(u, v)

    return G
