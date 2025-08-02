# Axon Library Documentation

Axon is a Python library for numerical computing with arrays, providing functionality similar to NumPy but with its own implementation. It offers basic array operations, linear algebra functions, and various utility functions for scientific computing.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Classes](#core-classes)
- [Array Creation](#array-creation)
- [Array Operations](#array-operations)
- [Linear Algebra](#linear-algebra)
- [Examples](#examples)

## Installation

```python
import axon as ax
```

## Quick Start

```python
import axon as ax

# Create arrays
a = ax.array([1, 2, 3, 4])
b = ax.zeros(3, 3)
c = ax.randn(2, 2)

# Basic operations
result = a + 5
dot_product = a.dot(ax.array([1, 1, 1, 1]))

# Linear algebra
matrix = ax.array([[1, 2], [3, 4]])
inverse = ax.linalg.inv(matrix)
```

## Core Classes

### array

The fundamental data structure in Axon, similar to NumPy's ndarray.

#### Constructor
```python
array(data, dtype="float32")
```

**Parameters:**
- `data`: List, nested list, or scalar value
- `dtype`: Data type string (default: "float32")

**Supported dtypes:**
- Integer types: `"int8"`, `"int16"`, `"int32"`, `"int64"`, `"long"`
- Unsigned integer types: `"uint8"`, `"uint16"`, `"uint32"`, `"uint64"`
- Float types: `"float32"`, `"float64"`, `"double"`
- Boolean: `"bool"`

#### Properties
- `shape`: Tuple representing array dimensions
- `size`: Total number of elements
- `ndim`: Number of dimensions
- `strides`: Tuple of stride values
- `dtype`: Data type of the array

#### Methods
- `astype(dtype)`: Convert array to specified data type
- `tolist()`: Convert array to Python list
- `is_contiguous()`: Check if array is contiguous in memory
- `is_view()`: Check if array is a view of another array
- `contiguous()`: Return a contiguous copy
- `make_contiguous()`: Make array contiguous in-place
- `view()`: Create a view of the array

## Array Creation

### Basic Creation Functions

#### zeros
```python
zeros(*shape, dtype="float32")
```
Create array filled with zeros.

```python
a = ax.zeros(3, 3)          # 3x3 matrix of zeros
b = ax.zeros(2, 3, 4)       # 3D array of zeros
```

#### ones
```python
ones(*shape, dtype="float32")
```
Create array filled with ones.

```python
a = ax.ones(5)              # 1D array of ones
b = ax.ones(2, 2, dtype="int32")  # 2x2 integer matrix of ones
```

#### zeros_like / ones_like
```python
zeros_like(arr)
ones_like(arr)
```
Create arrays with same shape as input array.

```python
a = ax.array([[1, 2], [3, 4]])
b = ax.zeros_like(a)        # Same shape, filled with zeros
c = ax.ones_like(a)         # Same shape, filled with ones
```

#### fill
```python
fill(fill_val, *shape, dtype="float32")
```
Create array filled with specified value.

```python
a = ax.fill(7.5, 3, 3)      # 3x3 matrix filled with 7.5
```

### Random Arrays

#### randn
```python
randn(*shape, dtype="float32")
```
Create array with random values from standard normal distribution.

```python
a = ax.randn(3, 3)          # 3x3 matrix with random values
```

#### randint
```python
randint(low, high, *shape, dtype="int32")
```
Create array with random integers in specified range.

```python
a = ax.randint(0, 10, 5)    # 1D array with random integers 0-9
b = ax.randint(-5, 5, 2, 3) # 2x3 matrix with random integers -5 to 4
```

#### uniform
```python
uniform(low, high, *shape, dtype="float32")
```
Create array with random values from uniform distribution.

```python
a = ax.uniform(0.0, 1.0, 4, 4)  # 4x4 matrix with uniform random values
```

### Sequence Arrays

#### arange
```python
arange(start, stop, step=1.0, dtype="float32")
```
Create array with evenly spaced values.

```python
a = ax.arange(0, 10, 2)     # [0, 2, 4, 6, 8]
b = ax.arange(1.0, 3.0, 0.5)  # [1.0, 1.5, 2.0, 2.5]
```

#### linspace
```python
linspace(start, step, end, *shape, dtype="float32")
```
Create array with linearly spaced values.

```python
a = ax.linspace(0, 0.1, 1, 11)  # 11 values from 0 to 1
```

## Array Operations

### Arithmetic Operations

Arrays support standard arithmetic operations with broadcasting:

```python
a = ax.array([1, 2, 3, 4])
b = ax.array([2, 2, 2, 2])

# Element-wise operations
c = a + b               # Addition
d = a - b               # Subtraction
e = a * b               # Multiplication
f = a / b               # Division
g = a ** 2              # Power

# Operations with scalars
h = a + 5               # Add scalar to all elements
i = a * 2.5             # Multiply all elements by scalar
```

### Mathematical Functions

#### Unary Functions
```python
a = ax.array([1, 4, 9, 16])

# Mathematical functions
b = a.sqrt()            # Square root
c = a.log()             # Natural logarithm
d = a.exp()             # Exponential
e = a.abs()             # Absolute value
f = a.sign()            # Sign function

# Trigonometric functions
g = a.sin()             # Sine
h = a.cos()             # Cosine
i = a.tan()             # Tangent
j = a.sinh()            # Hyperbolic sine
k = a.cosh()            # Hyperbolic cosine
l = a.tanh()            # Hyperbolic tangent
```

### Shape Operations

#### reshape
```python
reshape(new_shape)
```
Change array shape without changing data.

```python
a = ax.array([1, 2, 3, 4, 5, 6])
b = a.reshape([2, 3])   # Reshape to 2x3 matrix
```

#### transpose
```python
transpose()
```
Transpose array (swap dimensions).

```python
a = ax.array([[1, 2, 3], [4, 5, 6]])
b = a.transpose()       # Shape becomes (3, 2)
```

#### flatten
```python
flatten()
```
Return flattened 1D array.

```python
a = ax.array([[1, 2], [3, 4]])
b = a.flatten()         # [1, 2, 3, 4]
```

#### squeeze / expand_dims
```python
squeeze(axis=-1)
expand_dims(axis)
```
Remove or add dimensions.

```python
a = ax.array([[[1], [2]], [[3], [4]]])  # Shape: (2, 2, 1)
b = a.squeeze(axis=2)   # Remove dimension at axis 2
c = b.expand_dims(0)    # Add dimension at axis 0
```

### Reduction Operations

#### sum / mean
```python
sum(axis=-1, keepdims=False)
mean(axis=-1, keepdims=False)
```

```python
a = ax.array([[1, 2, 3], [4, 5, 6]])
b = a.sum()             # Sum all elements
c = a.sum(axis=0)       # Sum along axis 0
d = a.mean(axis=1)      # Mean along axis 1
```

#### min / max
```python
min(axis=-1, keepdims=False)
max(axis=-1, keepdims=False)
```

```python
a = ax.array([[1, 5, 2], [3, 1, 4]])
b = a.min()             # Global minimum
c = a.max(axis=0)       # Maximum along axis 0
```

#### var / std
```python
var(axis=-1, ddof=0)
std(axis=-1, ddof=0)
```
Calculate variance and standard deviation.

```python
a = ax.array([1, 2, 3, 4, 5])
variance = a.var()      # Variance
std_dev = a.std()       # Standard deviation
```

### Comparison Operations

Arrays support comparison operations that return boolean arrays:

```python
a = ax.array([1, 2, 3, 4])
b = ax.array([2, 2, 2, 2])

# Comparison operations
c = a == b              # Element-wise equality
d = a != b              # Element-wise inequality
e = a > b               # Greater than
f = a < b               # Less than
g = a >= b              # Greater than or equal
h = a <= b              # Less than or equal

# Comparison with scalars
i = a > 2               # Compare with scalar
```

## Linear Algebra

The `ax.linalg` module provides linear algebra functions.

### Vector Operations

#### dot
```python
dot(a, b, dtype="float32")
```
Compute dot product of two vectors.

```python
a = ax.array([1, 2, 3])
b = ax.array([4, 5, 6])
result = ax.linalg.dot(a, b)  # Scalar result
```

#### dot_mv
```python
dot_mv(a, b, dtype="float32")
```
Matrix-vector or vector-matrix multiplication.

```python
matrix = ax.array([[1, 2], [3, 4]])
vector = ax.array([1, 2])
result = ax.linalg.dot_mv(matrix, vector)
```

#### inner / outer
```python
inner(a, b, dtype="float32")
outer(a, b, dtype="float32")
```
Inner and outer products.

```python
a = ax.array([1, 2, 3])
b = ax.array([4, 5, 6])
inner_prod = ax.linalg.inner(a, b)  # Scalar
outer_prod = ax.linalg.outer(a, b)  # 3x3 matrix
```

#### cross
```python
cross(a, b, axis=None, dtype="float32")
```
Cross product of vectors.

```python
a = ax.array([1, 2, 3])
b = ax.array([4, 5, 6])
result = ax.linalg.cross(a, b)  # 3D cross product
```

### Matrix Operations

#### inv
```python
inv(a, dtype="float32")
```
Compute matrix inverse.

```python
a = ax.array([[1, 2], [3, 4]], dtype="float64")
inverse = ax.linalg.inv(a)
```

#### solve
```python
solve(a, b, dtype="float32")
```
Solve linear system Ax = b.

```python
A = ax.array([[2, 1], [1, 1]], dtype="float64")
b = ax.array([3, 2], dtype="float64")
x = ax.linalg.solve(A, b)
```

#### lstsq
```python
lstsq(a, b, dtype="float32")
```
Solve linear least-squares problem.

```python
A = ax.array([[1, 1], [1, 2], [1, 3]], dtype="float64")
b = ax.array([6, 8, 10], dtype="float64")
x = ax.linalg.lstsq(A, b)
```

#### rank
```python
rank(a, dtype="float32")
```
Compute matrix rank.

```python
a = ax.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype="float64")
matrix_rank = ax.linalg.rank(a)
```

### Matrix Decompositions

#### LU decomposition
```python
lu(a, dtype="float32")
```
LU decomposition with partial pivoting.

```python
a = ax.array([[2, 1, 1], [4, 3, 3], [8, 7, 9]], dtype="float64")
L, U = ax.linalg.lu(a)
```

#### QR decomposition
```python
qr(a, dtype="float32")
```
QR decomposition.

```python
a = ax.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype="float64")
Q, R = ax.linalg.qr(a)
```

#### SVD
```python
svd(a, dtype="float32")
```
Singular Value Decomposition.

```python
a = ax.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype="float64")
U, S, Vt = ax.linalg.svd(a)
print("U:", U)
print("S:", S)
print("Vt:", Vt)
```

#### Cholesky decomposition
```python
cholesky(a, dtype="float32")
```
Cholesky decomposition for positive definite matrices.

```python
a = ax.array([[4, 12, -16], [12, 37, -43], [-16, -43, 98]], dtype="float64")
L = ax.linalg.cholesky(a)
print("Cholesky factor:", L)
```

#### Determinant
```python
det(a, dtype="float32")
```
Compute matrix determinant.

```python
a = ax.array([[1, 2], [3, 4]], dtype="float64")
determinant = ax.linalg.det(a)
```

### Eigenvalue Problems

#### Standard eigenvalues
```python
eign(a, dtype="float32")        # Eigenvalues only
eignv(a, dtype="float32")       # Eigenvectors only
```

#### Hermitian eigenvalues
```python
eignh(a, dtype="float32")       # Eigenvalues for Hermitian matrices
eignhv(a, dtype="float32")      # Eigenvectors for Hermitian matrices
```

```python
# Symmetric matrix
a = ax.array([[4, -2], [-2, 1]], dtype="float64")
eigenvals = ax.linalg.eignh(a)
eigenvecs = ax.linalg.eignhv(a)
```

### Normalization

#### normalize
```python
normalize(a, mode="mm")
```
Normalize array using different methods.

**Modes:**
- `"mm"`: Min-max normalization
- `"std"`: Standard normalization
- `"rms"`: RMS normalization

```python
a = ax.array([1, 2, 3, 4, 5], dtype="float32")
normalized = ax.linalg.normalize(a, mode="std")
```

#### Norm functions
```python
l1_norm(a, mag=False)
l2_norm(a, mag=False)
unit_norm(a)
robust_norm(a)
```

```python
a = ax.array([3, 4], dtype="float32")
l1_result = ax.linalg.l1_norm(a)        # L1 norm
l2_result = ax.linalg.l2_norm(a)        # L2 norm
unit_result = ax.linalg.unit_norm(a)    # Unit normalization

# Get both normalized array and magnitude
l2_normalized, magnitude = ax.linalg.l2_norm(a, mag=True)
```

## Examples

### Basic Array Operations

```python
import axon as ax

# Create arrays
a = ax.array([1, 2, 3, 4], dtype="float32")
b = ax.array([2, 3, 4, 5], dtype="float32")

# Arithmetic operations
print("Addition:", a + b)
print("Scalar multiplication:", a * 2)
print("Element-wise power:", a ** 2)

# Mathematical functions
print("Square root:", a.sqrt())
print("Exponential:", a.exp())

# Reductions
print("Sum:", a.sum())
print("Mean:", a.mean())
print("Standard deviation:", a.std())
```

### Matrix Operations

```python
import axon as ax

# Create matrices
A = ax.array([[1, 2], [3, 4]], dtype="float64")
B = ax.array([[5, 6], [7, 8]], dtype="float64")

# Matrix operations
print("Matrix multiplication:", A @ B)
print("Matrix inverse:", ax.linalg.inv(A))
print("Determinant:", ax.linalg.det(A))

# Solve linear system
b = ax.array([5, 11], dtype="float64")
x = ax.linalg.solve(A, b)
print("Solution:", x)
```

### Advanced Linear Algebra

```python
import axon as ax

# SVD example
A = ax.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype="float64")
U, S, Vt = ax.linalg.svd(A)
print("Singular values:", S)

# Cholesky decomposition
pos_def = ax.array([[4, 12, -16], [12, 37, -43], [-16, -43, 98]], dtype="float64")
L = ax.linalg.cholesky(pos_def)
print("Cholesky factor:", L)

# Eigenvalue problem
symmetric = ax.array([[4, -2], [-2, 1]], dtype="float64")
eigenvals = ax.linalg.eignh(symmetric)
eigenvecs = ax.linalg.eignhv(symmetric)
print("Eigenvalues:", eigenvals)
print("Eigenvectors:", eigenvecs)
```

### Array Manipulation

```python
import axon as ax

# Create and reshape arrays
a = ax.arange(0, 12)
print("Original:", a)

b = a.reshape([3, 4])
print("Reshaped to 3x4:")
print(b)

c = b.transpose()
print("Transposed:")
print(c)

# Indexing and slicing
print("First row:", b[0])
print("First column:", b[:, 0])
```

This documentation covers the main functionality of the Axon library. The library provides a comprehensive set of tools for numerical computing, with particular strength in linear algebra operations and matrix decompositions.
