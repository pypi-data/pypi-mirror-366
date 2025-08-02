import itertools
import numpy as np
from .datadict import DataDict

class Experiment:
    """
    Experiment class for designing and running model experiments.
    """
    def __init__(self, model_class, parameters=None, iterations=1):
        self.model_class = model_class
        self.parameters = parameters or {}
        self.iterations = iterations
        self.results = DataDict()

    def run(self):
        """Run the experiment."""
        param_combinations = self._generate_param_combinations()
        total_runs = len(param_combinations) * self.iterations
        run_count = 0

        for params in param_combinations:
            for i in range(self.iterations):
                run_count += 1
                print(f"Running experiment {run_count}/{total_runs}")
                model = self.model_class(params)
                model_data = model.run()
                self._record_results(model_data, params, i)

        return self.results

    def _generate_param_combinations(self):
        """Generate all parameter combinations."""
        if not self.parameters:
            return [{}]

        # Handle parameter ranges
        param_lists = {}
        for name, value in self.parameters.items():
            if isinstance(value, list):
                param_lists[name] = value
            elif isinstance(value, dict) and 'range' in value:
                start, end, step = value['range']
                param_lists[name] = list(np.arange(start, end, step))
            else:
                param_lists[name] = [value]

        # Generate combinations
        keys = list(param_lists.keys())
        combinations = list(itertools.product(*(param_lists[key] for key in keys)))
        return [{keys[i]: val for i, val in enumerate(comb)} for comb in combinations]

    def _record_results(self, model_data, params, iteration):
        """Record model results."""
        # Record parameters
        for name, value in params.items():
            self.results.record(f'param_{name}', value, iteration)

        # Record model data
        for name in model_data._records:
            steps, values = zip(*model_data.get_record(name))
            for step, value in zip(steps, values):
                self.results.record(f'{name}_step_{step}', value, iteration)

        # Record model reports
        for name in model_data._reports:
            self.results.report(f'report_{name}_iter_{iteration}', model_data.get_report(name))