import numpy as np

class Sample:
    """
    Sample class for parameter sampling.
    """
    def __init__(self, parameters, n=1):
        self.parameters = parameters
        self.n = n
        self.samples = []

    def generate(self):
        """Generate parameter samples."""
        self.samples = []
        for _ in range(self.n):
            sample = {}
            for name, value in self.parameters.items():
                if isinstance(value, dict):
                    if 'range' in value:
                        start, end = value['range']
                        sample[name] = np.random.uniform(start, end)
                    elif 'choices' in value:
                        sample[name] = np.random.choice(value['choices'])
                    elif 'distribution' in value:
                        dist = value['distribution']
                        if dist == 'normal':
                            mu = value.get('mu', 0)
                            sigma = value.get('sigma', 1)
                            sample[name] = np.random.normal(mu, sigma)
                        elif dist == 'uniform':
                            low = value.get('low', 0)
                            high = value.get('high', 1)
                            sample[name] = np.random.uniform(low, high)
                else:
                    sample[name] = value
            self.samples.append(sample)
        return self.samples

def sample(parameters, n=1):
    """Generate parameter samples."""
    sampler = Sample(parameters, n)
    return sampler.generate()