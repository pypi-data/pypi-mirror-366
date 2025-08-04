"""
Módulo matemático básico sin dependencias externas.
Inspirado en funciones simples de NumPy.
"""

def dot(a, b):
    if len(a[0]) != len(b):
        raise ValueError("Las dimensiones no coinciden para el producto punto")
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]

def transpose(matrix):
    return list(map(list, zip(*matrix)))

def zeros(shape):
    if isinstance(shape, int):
        return [0] * shape
    elif isinstance(shape, tuple) and len(shape) == 2:
        return [[0 for _ in range(shape[1])] for _ in range(shape[0])]
    else:
        raise ValueError("Forma inválida. Usa un entero o tupla de dos enteros.")

def ones(shape):
    if isinstance(shape, int):
        return [1] * shape
    elif isinstance(shape, tuple) and len(shape) == 2:
        return [[1 for _ in range(shape[1])] for _ in range(shape[0])]
    else:
        raise ValueError("Forma inválida. Usa un entero o tupla de dos enteros.")

def add(a, b):
    return [x + y for x, y in zip(a, b)]

def basic_tokenizer(text):
    """
    Tokeniza texto separando por espacios.
    Ejemplo: 'Hola mundo' => ['Hola', 'mundo']
    """
    return text.strip().split()
