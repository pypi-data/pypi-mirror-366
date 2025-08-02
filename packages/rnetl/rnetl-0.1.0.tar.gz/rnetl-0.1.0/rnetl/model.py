import numpy as np
from .datadict import DataDict
from .network import Network

class NetworkModel:
    """
    Base class for network models.
    """
    def __init__(self, parameters=None):
        self.p = parameters or {}
        self.network = Network()
        self.data = DataDict()
        self._seed = self.p.get('seed', None)
        self._rng = np.random.default_rng(self._seed)
        self._step = 0
        self._running = False

    def setup(self):
        """Initialize the model. To be overridden by subclasses."""
        pass

    def step(self):
        """Define the model's step. To be overridden by subclasses."""
        pass

    def update(self):
        """Update model data. To be overridden by subclasses."""
        pass

    def end(self):
        """Finalize the model. To be overridden by subclasses."""
        pass

    def run(self, steps=None):
        """Run the model for a given number of steps."""
        self._running = True
        self.setup()
        self.update()

        steps = steps or self.p.get('steps', 100)
        for _ in range(steps):
            if not self._running:
                break
            self._step += 1
            self.step()
            self.update()

        self.end()
        return self.data

    def stop(self):
        """Stop the model."""
        self._running = False

    def record(self, name, value):
        """Record a value."""
        self.data.record(name, value, self._step)

    def report(self, name, value):
        """Report a final value."""
        self.data.report(name, value)