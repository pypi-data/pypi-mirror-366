# minitonu/core.py
class Tensor:
    def __init__(self, data):
        self.data = [float(x) for x in data]

    def __add__(self, other):
        return Tensor([a + b for a, b in zip(self.data, other.data)])

    def __sub__(self, other):
        return Tensor([a - b for a, b in zip(self.data, other.data)])

    def __mul__(self, other):
        return Tensor([a * b for a, b in zip(self.data, other.data)])

    def sum(self):
        return sum(self.data)

    def mean(self):
        return self.sum() / len(self.data)

    def __repr__(self):
        return f"Tensor({self.data})"
