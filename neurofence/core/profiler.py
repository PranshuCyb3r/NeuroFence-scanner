import numpy as np

class NeuronProfiler:
    def __init__(self):
        self.count = 0
        self.sum_values = None
        self.sum_squares = None
        self.peak_values = None
        self.fire_count = None

    def observe(self, activations, spike_gate=None):
        activations = np.array(activations, dtype=float)

        if self.sum_values is None:
            n_neurons = len(activations)
            self.sum_values = np.zeros(n_neurons)
            self.sum_squares = np.zeros(n_neurons)
            self.peak_values = np.full(n_neurons, -np.inf)
            self.fire_count = np.zeros(n_neurons)

        self.count += 1
        self.sum_values += activations
        self.sum_squares += activations ** 2
        self.peak_values = np.maximum(self.peak_values, activations)

        if spike_gate is not None:
            self.fire_count += (activations > spike_gate).astype(float)

    @property
    def average(self):
        return self.sum_values / self.count

    @property
    def std(self):
        mean = self.average
        variance = (self.sum_squares / self.count) - (mean ** 2)
        variance = np.maximum(variance, 0)
        return np.sqrt(variance)

    @property
    def peak(self):
        return self.peak_values

    @property
    def fire_rate(self):
        if self.fire_count is None:
            return None
        return self.fire_count / self.count