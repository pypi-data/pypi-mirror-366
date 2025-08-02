# Axon Technical Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Build System](#build-system)
5. [Development Guidelines](#development-guidelines)
6. [Testing](#testing)
7. [Contributing](#contributing)
8. [Performance Considerations](#performance-considerations)
9. [Memory Management](#memory-management)
10. [Error Handling](#error-handling)

## Project Overview

Axon is a high-performance numerical computing library designed for multi-dimensional array operations. The library provides a C/C++ backend with Python bindings, offering NumPy-like functionality with optimized CPU operations and potential CUDA acceleration.

### Key Features
- Multi-dimensional array operations with broadcasting support
- Multiple data type support (float32, float64, int8-64, uint8-64, bool)
- Memory-efficient view operations and strided arrays
- Comprehensive mathematical operations (unary, binary, reduction)
- Matrix multiplication with batch and broadcast support
- Random number generation with statistical distributions
- Progress tracking utilities

## Architecture

### Directory Structure
```
axon/
├── csrc/                    # C/C++ source code
│   ├── core/               # Core array functionality
│   │   ├── core.cpp/.h     # Main array struct and operations
│   │   ├── dtype.cpp/.h    # Data type system
│   │   └── contiguous.cpp/.h # Memory layout management
│   ├── cpu/                # CPU-optimized operations
│   │   ├── binary_ops.cpp/.h    # Binary operations (add, mul, matmul)
│   │   ├── maths_ops.cpp/.h     # Mathematical functions
│   │   ├── red_ops.cpp/.h       # Reduction operations
│   │   ├── helpers.cpp/.h       # Array creation utilities
│   │   └── utils.cpp/.h         # General utilities
│   ├── cuda/               # CUDA acceleration (GPU operations)
│   └── inc/                # Additional headers
│       ├── random.h        # Random number generation
│       └── tqdm.h          # Progress tracking
└── helpers/                # Python helper modules
build/                  # Compiled libraries
docs/                   # Documentation
tests/                  # Test suites
```

## Core Components

### 1. Array Structure (`core/core.h`)

The central `Array` struct represents multi-dimensional arrays:

```c
typedef struct Array {
    void* data;           // Raw data pointer (dtype-agnostic)
    int* strides;         // Memory strides for each dimension
    int* backstrides;     // Reverse strides for efficient indexing
    int* shape;           // Dimensions of the array
    size_t size;          // Total number of elements
    size_t ndim;          // Number of dimensions
    dtype_t dtype;        // Data type identifier
    int is_view;          // View flag (0 = owns data, 1 = view)
} Array;
```

#### Key Design Principles:
- **Type-agnostic storage**: Uses `void*` with dtype information for generic operations
- **Stride-based indexing**: Enables efficient slicing, transposition, and broadcasting
- **View semantics**: Supports zero-copy operations where possible
- **Memory ownership tracking**: Distinguishes between owned arrays and views

### 2. Data Type System (`core/dtype.h`)

Supports comprehensive type system with automatic promotion:

```c
typedef enum {
    DTYPE_FLOAT32, DTYPE_FLOAT64,
    DTYPE_INT8, DTYPE_INT16, DTYPE_INT32, DTYPE_INT64,
    DTYPE_UINT8, DTYPE_UINT16, DTYPE_UINT32, DTYPE_UINT64,
    DTYPE_BOOL
} dtype_t;
```

#### Type Operations:
- **Automatic promotion**: `promote_dtypes()` follows NumPy-like promotion rules
- **Safe casting**: Includes overflow protection for integer types
- **Efficient conversion**: Batch conversion functions for operation pipelines

### 3. Memory Management (`core/contiguous.h`)

#### Contiguity Management:
- **Contiguity checking**: `is_contiguous()` verifies C-contiguous memory layout
- **In-place conversion**: `make_contiguous_inplace()` reorganizes memory when needed
- **View operations**: Maintains stride information for efficient slicing

#### Memory Layout:
```c
// C-contiguous: rightmost index varies fastest
// Array[2,3,4] -> strides[12, 4, 1]
size_t calculate_flat_index(int* indices, int* strides, size_t ndim);
void flat_to_multi_index(size_t flat_idx, int* shape, size_t ndim, int* indices);
```

## Build System

### Compilation Targets

The library can be built as a shared library for different platforms:

#### Linux (.so)
```bash
g++ -shared -fPIC -o libarray.so \
    core/core.cpp core/contiguous.cpp core/dtype.cpp array.cpp \
    cpu/maths_ops.cpp cpu/helpers.cpp cpu/utils.cpp \
    cpu/red_ops.cpp cpu/binary_ops.cpp
```

#### Windows (.dll)
```bash
g++ -shared -o libarray.dll \
    core/core.cpp core/contiguous.cpp core/dtype.cpp array.cpp \
    cpu/maths_ops.cpp cpu/helpers.cpp cpu/utils.cpp \
    cpu/red_ops.cpp cpu/binary_ops.cpp
```

#### macOS (.dylib)
```bash
g++ -dynamiclib -o libarray.dylib \
    core/core.cpp core/contiguous.cpp core/dtype.cpp array.cpp \
    cpu/maths_ops.cpp cpu/helpers.cpp cpu/utils.cpp \
    cpu/red_ops.cpp cpu/binary_ops.cpp
```

### Build Flags

#### Recommended Optimization Flags:
```bash
-O3 -march=native -ffast-math -DNDEBUG
```

#### Debug Flags:
```bash
-g -O0 -Wall -Wextra -fsanitize=address
```

#### CUDA Support (when available):
```bash
nvcc -shared -Xcompiler -fPIC -o libarray_cuda.so \
     cuda/*.cu cpu/*.cpp core/*.cpp
```

## Development Guidelines

### Code Style

#### Naming Conventions:
- **Functions**: `snake_case` (e.g., `create_array`, `matmul_array`)
- **Structs**: `PascalCase` (e.g., `Array`, `RNG`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DTYPE_FLOAT32`)
- **File extensions**: `.h` for headers, `.cpp` for implementation

#### Function Patterns:
```c
// High-level API (array.h)
Array* operation_array(Array* input, ...);

// Low-level operations (cpu/*.h)
void operation_ops(float* in, float* out, size_t size, ...);
```

### Memory Safety

#### Resource Management:
```c
// Always pair create/delete
Array* arr = create_array(...);
// ... use array
delete_array(arr);  // Handles data, shape, strides cleanup

// Views don't own data
Array* view = view_array(arr);
delete_array(view);  // Only frees view metadata, not data
```

#### Buffer Overflow Prevention:
- All array operations check bounds using `size` and `shape` information
- Stride calculations validate against allocated memory regions
- Type conversions include overflow checking for integer types

### Error Handling

#### Return Value Conventions:
- **Array functions**: Return `NULL` on failure
- **Operation functions**: Use `void` returns with pre-allocated output buffers
- **Utility functions**: Return error codes or use assertions for preconditions

#### Common Error Scenarios:
```c
// Check for NULL inputs
if (!array || !array->data) return NULL;

// Validate dimensions for operations
if (a->ndim != b->ndim) return NULL;

// Ensure compatible shapes for broadcasting
if (!can_broadcast(a->shape, b->shape, ndim)) return NULL;
```

## Testing

### Test Structure

#### Unit Tests (`tests/test_array.cpp`):
- Core array creation and deletion
- Data type conversions and promotions
- Memory layout and contiguity operations
- View creation and manipulation

#### Mathematical Operations (`tests/matmul_test.cpp`):
- Binary operations (add, subtract, multiply, divide)
- Unary functions (trigonometric, exponential, logarithmic)
- Matrix multiplication variants (standard, batch, broadcast)
- Reduction operations (sum, mean, min, max, variance, std)

#### Python Integration (`tests/test_array.py`):
- Python binding functionality
- NumPy compatibility validation
- Performance benchmarking against NumPy
- Memory leak detection

### Running Tests

```bash
# Compile test suite
g++ -o test_suite tests/*.cpp -L./build -larray

# Run specific test categories
./test_suite --category=core
./test_suite --category=operations
./test_suite --category=performance

# Python tests
python -m pytest tests/ -v
```

## Performance Considerations

### CPU Optimizations

#### Vectorization:
- Operations use compiler auto-vectorization hints
- Inner loops designed for SIMD instruction utilization
- Memory access patterns optimized for cache efficiency

#### Broadcasting Strategy:
```c
// Efficient broadcasting avoids temporary array creation
void add_broadcasted_array_ops(
    float* a, float* b, float* out,
    int* broadcasted_shape, int broadcasted_size,
    int a_ndim, int b_ndim, int* a_shape, int* b_shape
);
```

#### Matrix Multiplication:
- **Standard**: Optimized for cache-friendly access patterns
- **Batch**: Parallelized across batch dimension
- **Broadcast**: Combines broadcasting with efficient GEMM operations

### Memory Optimization

#### Stride-based Operations:
- Avoid unnecessary memory copies through view operations
- Transpose operations modify strides rather than moving data
- Reshape operations reuse memory when possible

#### Contiguity Management:
```c
// Only make contiguous when necessary for performance
if (!is_contiguous(array) && requires_contiguous_layout(operation)) {
    make_contiguous_inplace(array);
}
```

## Memory Management

### Reference Counting and Views

#### Array Ownership:
- **Owned arrays**: `is_view = 0`, responsible for freeing `data`
- **View arrays**: `is_view = 1`, only free metadata (`shape`, `strides`)

#### Safe View Creation:
```c
Array* create_safe_view(Array* parent) {
    Array* view = view_array(parent);
    if (!view) return NULL;
    
    // Views share data pointer but have independent metadata
    view->is_view = 1;
    return view;
}
```

### Memory Layout Patterns

#### C-Contiguous (Row-Major):
```
Array[2,3] = [[a,b,c], [d,e,f]]
Memory: [a,b,c,d,e,f]
Strides: [3,1]
```

#### Transposed View:
```
Transpose Array[3,2] = [[a,d], [b,e], [c,f]]
Memory: [a,b,c,d,e,f]  (unchanged)
Strides: [1,3]         (modified)
```

## Error Handling

### Comprehensive Error Checking

#### Input Validation:
```c
Array* safe_operation(Array* a, Array* b) {
    // Null pointer checks
    if (!a || !b || !a->data || !b->data) {
        return NULL;
    }
    
    // Shape compatibility
    if (!shapes_compatible(a, b)) {
        return NULL;
    }
    
    // Data type validation
    if (!dtype_supports_operation(a->dtype, b->dtype)) {
        return NULL;
    }
    
    return perform_operation(a, b);
}
```

#### Memory Allocation Failures:
```c
Array* create_array_safe(...) {
    Array* arr = malloc(sizeof(Array));
    if (!arr) return NULL;
    
    arr->data = allocate_dtype_array(dtype, size);
    if (!arr->data) {
        free(arr);
        return NULL;
    }
    
    // Continue initialization...
    return arr;
}
```

### Debugging Support

#### Debug Builds:
- Enable with `-DDEBUG` compile flag
- Includes bounds checking and memory tracking
- Provides detailed error messages and stack traces

#### Memory Leak Detection:
- All allocations tracked in debug mode
- Automatic leak reporting on program exit
- Integration with AddressSanitizer and Valgrind

## Contributing

### Development Workflow

1. **Fork and Clone**: Create personal fork of the repository
2. **Feature Branch**: Create descriptive branch name (`feature/new-reduction-ops`)
3. **Implementation**: Follow coding standards and include tests
4. **Testing**: Ensure all existing tests pass and new tests cover edge cases
5. **Documentation**: Update relevant documentation and comments
6. **Pull Request**: Submit with detailed description and performance impact

### Performance Testing

#### Benchmark Requirements:
- Include performance comparisons with NumPy equivalent operations
- Test on multiple array sizes and shapes
- Measure memory usage alongside execution time
- Verify numerical accuracy within acceptable tolerances

#### Example Benchmark:
```python
import time
import numpy as np
from axon import array

def benchmark_matmul(size):
    # AXON implementation
    a_axon = array.randn([size, size])
    b_axon = array.randn([size, size])
    
    start = time.time()
    c_axon = array.matmul(a_axon, b_axon)
    axon_time = time.time() - start
    
    # NumPy comparison
    a_numpy = np.random.randn(size, size)
    b_numpy = np.random.randn(size, size)
    
    start = time.time()
    c_numpy = np.matmul(a_numpy, b_numpy)
    numpy_time = time.time() - start
    
    return axon_time, numpy_time
```

### Code Review Checklist

- [ ] Memory safety: No leaks, proper cleanup, bounds checking
- [ ] Performance: Efficient algorithms, minimal memory allocation
- [ ] Testing: Comprehensive test coverage including edge cases
- [ ] Documentation: Clear comments and updated technical docs
- [ ] Compatibility: Maintains API consistency and NumPy compatibility
- [ ] Standards: Follows project coding conventions and style

## Additional Resources

- **API Reference**: See `array.h` for complete function signatures
- **Performance Tuning**: Refer to CPU-specific optimization guides
- **CUDA Development**: Guidelines for GPU acceleration implementation
- **Python Bindings**: Documentation for Python integration layer

For questions or clarifications, please refer to the project's issue tracker or contribute to the documentation improvements.