from .core import dot, transpose, zeros, ones, add
from .neural import Neuron, Layer

def test_core():
    assert dot([[1, 2]], [[3], [4]]) == [[11]]
    assert transpose([[1, 2], [3, 4]]) == [[1, 3], [2, 4]]
    assert zeros(3) == [0, 0, 0]
    assert ones((2, 2)) == [[1, 1], [1, 1]]
    assert add([1, 2], [3, 4]) == [4, 6]

def test_neural():
    n = Neuron([0.5, 1.0], bias=0.1)
    assert round(n.activate([2, 3]), 2) == 4.1

    l = Layer([Neuron([1, 1]), Neuron([0.5, 0.5])])
    out = l.forward([2, 2])
    assert out == [4, 2.0]

if __name__ == "__main__":
    test_core()
    test_neural()
    print("✅ Todos los tests pasaron correctamente.")
