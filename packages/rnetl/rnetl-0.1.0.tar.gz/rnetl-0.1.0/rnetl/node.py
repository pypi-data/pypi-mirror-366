class Node:
    """
    Node class for network models.
    """
    def __init__(self, model, node_id, **kwargs):
        self.model = model
        self.id = node_id
        self.neighbors = []
        self.properties = kwargs

    def __repr__(self):
        return f"Node(id={self.id})"

    def add_neighbor(self, node):
        """Add a neighbor to this node."""
        if node not in self.neighbors:
            self.neighbors.append(node)
            return True
        return False

    def remove_neighbor(self, node):
        """Remove a neighbor from this node."""
        if node in self.neighbors:
            self.neighbors.remove(node)
            return True
        return False

    def get_property(self, name, default=None):
        """Get a node property."""
        return self.properties.get(name, default)

    def set_property(self, name, value):
        """Set a node property."""
        self.properties[name] = value