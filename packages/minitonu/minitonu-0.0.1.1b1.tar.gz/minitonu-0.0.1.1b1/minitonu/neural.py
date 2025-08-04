# minitonu/neural.py
from .core import Tensor

class Perceptron:
    def __init__(self, weights, bias):
        self.weights = Tensor(weights)
        self.bias = float(bias)

    def forward(self, inputs):
        x = Tensor(inputs)
        weighted_sum = sum(a * b for a, b in zip(self.weights.data, x.data)) + self.bias
        return 1.0 if weighted_sum > 0 else 0.0

    def __repr__(self):
        return f"Perceptron(weights={self.weights}, bias={self.bias})"

