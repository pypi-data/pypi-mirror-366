# Axon

![axonlogo.png](https://github.com/delveopers/Axon/blob/main/logo.png)

Lightweight multi-dimensional array manipulation library powered by GPU, similar to NumPy, but trying to be better.

## Features

- Custom `array` class with Pythonic syntax
- Element-wise arithmetic: `+`, `-`, `-`, `/`
- Scalar operations (e.g., `array + 5`)
- Trigonometric functions: `sin`, `cos`, `tan`, etc.
- Auto handling of `CArray`, scalars, and lists
- Simple `__str__`/`__repr__` for pretty printing
- Reshape, transpose, flatten
- Data type conversion

## Requirements

- Python 3.7+
- C compiler (for building the C backend)
- ctypes module (standard in Python)

## Getting Started

### Build

To use Axon, make sure you have compiled the C backend to a shared library (`.dll`, `.so`, or `.dylib`) and exposed the C functions via `ctypes`.

Place the compiled `.dll` (on Windows) or `.so` (Linux/macOS) in your `axon/` folder.

## Example

Here's a quick demo of how Axon works:

```python
import axon
from axon import array

# Create two 2D arrays
a = array([[1, 2], [3, 4]], dtype=axon.int32)
b = array([[5, 6], [7, 8]], dtype=axon.int32)

# Addition
c = a + b
print("Addition:\n", c)

# Multiplication
d = a * b
print("Multiplication:\n", d)

# Matrix Multiplication
e = a @ b
print("Matrix Multiplication:\n", e)
```

### Output

```
Addition:
 array([6, 8], [10, 12], dtype=int32)
Multiplication:
 array([5, 12], [21, 32], dtype=int32)
Matrix Multiplication:
 array([19, 22], [43, 50], dtype=int32)
```

anyway, prefer documentation for detailed usage guide:

1. [usage.md](https://github.com/delveopers/Axon/blob/main/docs/Usage.md): for user guide & documentation
2. [technical.md](https://github.com/delveopers/Axon/blob/main/docs/Technical.md): for contirbutors & contirbution related guide

## License

This project is under the [Apache-2.0](LICENSE) License.
