# RNetL

A Python package for network logic operations.

## Installation

You can install RNetL using pip:

```bash
pip install rnetl
```

## Usage

Here's a simple example of how to use RNetL:

```python
import rnetl as rl

# Create a network model
model = rl.NetworkModel({
    'nodes': 10,
    'edges': 15,
    'steps': 50
})

# Define setup method
def setup(self):
    # Add nodes
    for _ in range(self.p['nodes']):
        self.network.add_node(self)

    # Add random edges
    nodes = self.network.get_nodes()
    for _ in range(self.p['edges']):
        node1 = self.model._rng.choice(nodes)
        node2 = self.model._rng.choice(nodes)
        if node1 != node2:
            self.network.add_edge(self, node1, node2)

# Attach setup method to model
model.setup = setup.__get__(model)

# Run the model
results = model.run()

# Visualize the network
plt = rl.visualize(model.network)
plt.show()
```

## Features

- Network model creation and management
- Node and edge properties
- Experiment design and execution
- Data recording and analysis
- Network visualization
- Parameter sampling

## Documentation

Full documentation is available at [https://rnetl.readthedocs.io/](https://rnetl.readthedocs.io/).

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License - see the LICENSE file for details.