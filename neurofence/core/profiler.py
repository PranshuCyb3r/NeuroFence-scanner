import numpy as np

class NeuronProfiler:
    def __init__(self):
        self.count = 0
        self.sum_values = None
        self.sum_squares = None
        self.peak_values = None

    def observe(self, activations):
        activations = np.array(activations, dtype=float)

        if self.sum_values is None:
            n_neurons = len(activations)
            self.sum_values = np.zeros(n_neurons)
            self.sum_squares = np.zeros(n_neurons)
            self.peak_values = np.full(n_neurons, -np.inf)

        self.count += 1
        self.sum_values += activations
        self.sum_squares += activations ** 2
        self.peak_values = np.maximum(self.peak_values, activations)

    @property
    def average(self):
        return self.sum_values / self.count

    @property
    def std(self):
        """Standard deviation - 'normal variation kitna hota hai' iska measure."""
        mean = self.average
        variance = (self.sum_squares / self.count) - (mean ** 2)
        variance = np.maximum(variance, 0)  # floating-point rounding se negative na ho jaye
        return np.sqrt(variance)

    @property
    def peak(self):
        return self.peak_values