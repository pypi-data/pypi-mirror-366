import matplotlib.pyplot as plt
import networkx as nx

def visualize(network, figsize=(10, 10), node_size=300, node_color='skyblue',
              edge_color='gray', with_labels=True, font_size=10):
    """
    Visualize a network.
    """
    # Create a networkx graph
    g = nx.Graph()

    # Add nodes
    for node in network.get_nodes():
        g.add_node(node.id, **node.properties)

    # Add edges
    for edge in network.get_edges():
        g.add_edge(edge.node1.id, edge.node2.id, weight=edge.weight, **edge.properties)

    # Draw the graph
    plt.figure(figsize=figsize)
    pos = nx.spring_layout(g)

    # Draw nodes
    nx.draw_networkx_nodes(g, pos, node_size=node_size, node_color=node_color)

    # Draw edges
    nx.draw_networkx_edges(g, pos, edge_color=edge_color)

    # Draw labels
    if with_labels:
        nx.draw_networkx_labels(g, pos, font_size=font_size)

    plt.axis('off')
    plt.tight_layout()
    return plt

def plot_time_series(data, xlabel='Step', ylabel='Value', title='Time Series',
                     figsize=(10, 6), grid=True):
    """
    Plot time series data.
    """
    plt.figure(figsize=figsize)
    for name, values in data.items():
        steps, vals = zip(*values)
        plt.plot(steps, vals, label=name)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    if grid:
        plt.grid(True)
    plt.legend()
    plt.tight_layout()
    return plt