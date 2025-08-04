class Tensor:
    def __init__(self, data):
        self.data = data
        self.shape = self._shape(data)

    def _shape(self, data):
        if not isinstance(data, list): return ()
        if isinstance(data[0], list):
            return (len(data), len(data[0]))
        return (len(data),)

    def add(self, other):
        return Tensor(self._apply_op(self.data, other.data, lambda x, y: x + y))

    def sub(self, other):
        return Tensor(self._apply_op(self.data, other.data, lambda x, y: x - y))

    def mul(self, other):
        return Tensor(self._apply_op(self.data, other.data, lambda x, y: x * y))

    def dot(self, other):
        if len(self.shape) != 2 or len(other.shape) != 2:
            raise ValueError("Dot product only supports 2D tensors")
        result = []
        for row in self.data:
            new_row = []
            for col in zip(*other.data):
                new_row.append(sum([a * b for a, b in zip(row, col)]))
            result.append(new_row)
        return Tensor(result)

    def mean(self):
        flat = self._flatten(self.data)
        return sum(flat) / len(flat)

    def sum(self):
        return sum(self._flatten(self.data))

    def _flatten(self, data):
        if not isinstance(data[0], list): return data
        return [item for sublist in data for item in sublist]

    def _apply_op(self, a, b, op):
        if isinstance(a[0], list):
            return [[op(ai, bi) for ai, bi in zip(ar, br)] for ar, br in zip(a, b)]
        return [op(ai, bi) for ai, bi in zip(a, b)]

    def show(self):
        for row in self.data:
            print(row)
