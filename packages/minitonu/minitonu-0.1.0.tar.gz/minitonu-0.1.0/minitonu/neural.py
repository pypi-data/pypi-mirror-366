import math
import random

class Neuron:
    def __init__(self, input_size):
        self.weights = [random.uniform(-1, 1) for _ in range(input_size)]
        self.bias = random.uniform(-1, 1)

    def forward(self, inputs):
        total = sum(w * i for w, i in zip(self.weights, inputs)) + self.bias
        return self._sigmoid(total)

    def _sigmoid(self, x):
        return 1 / (1 + math.exp(-x))

class Layer:
    def __init__(self, input_size, output_size):
        self.neurons = [Neuron(input_size) for _ in range(output_size)]

    def forward(self, inputs):
        return [neuron.forward(inputs) for neuron in self.neurons]

class Network:
    def __init__(self, sizes):
        self.layers = []
        for i in range(len(sizes) - 1):
            self.layers.append(Layer(sizes[i], sizes[i + 1]))

    def forward(self, inputs):
        for layer in self.layers:
            inputs = layer.forward(inputs)
        return inputs
