class Edge:
    """
    Edge class for network models.
    """
    def __init__(self, model, node1, node2, weight=1, **kwargs):
        self.model = model
        self.node1 = node1
        self.node2 = node2
        self.weight = weight
        self.properties = kwargs

    def __repr__(self):
        return f"Edge({self.node1.id}-{self.node2.id}, weight={self.weight})"

    def get_property(self, name, default=None):
        """Get an edge property."""
        return self.properties.get(name, default)

    def set_property(self, name, value):
        """Set an edge property."""
        self.properties[name] = value

    def get_nodes(self):
        """Get the nodes connected by this edge."""
        return (self.node1, self.node2)