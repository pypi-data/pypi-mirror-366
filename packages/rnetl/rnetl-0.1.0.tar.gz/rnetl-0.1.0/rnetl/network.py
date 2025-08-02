from .node import Node
from .edge import Edge

class Network:
    """
    Network class for managing nodes and edges.
    """
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.node_id_counter = 0

    def add_node(self, model, **kwargs):
        """Add a node to the network."""
        node = Node(model, self.node_id_counter, **kwargs)
        self.nodes.append(node)
        self.node_id_counter += 1
        return node

    def remove_node(self, node):
        """Remove a node from the network."""
        if node in self.nodes:
            # Remove all edges connected to this node
            edges_to_remove = [e for e in self.edges if node in e.get_nodes()]
            for edge in edges_to_remove:
                self.remove_edge(edge)
            # Remove the node
            self.nodes.remove(node)
            return True
        return False

    def add_edge(self, model, node1, node2, weight=1, **kwargs):
        """Add an edge between two nodes."""
        if node1 in self.nodes and node2 in self.nodes:
            edge = Edge(model, node1, node2, weight, **kwargs)
            self.edges.append(edge)
            node1.add_neighbor(node2)
            node2.add_neighbor(node1)
            return edge
        return None

    def remove_edge(self, edge):
        """Remove an edge from the network."""
        if edge in self.edges:
            node1, node2 = edge.get_nodes()
            node1.remove_neighbor(node2)
            node2.remove_neighbor(node1)
            self.edges.remove(edge)
            return True
        return False

    def get_node(self, node_id):
        """Get a node by its ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_nodes(self):
        """Get all nodes in the network."""
        return self.nodes

    def get_edges(self):
        """Get all edges in the network."""
        return self.edges

    def node_count(self):
        """Get the number of nodes in the network."""
        return len(self.nodes)

    def edge_count(self):
        """Get the number of edges in the network."""
        return len(self.edges)