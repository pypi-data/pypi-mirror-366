# Contributing to Axon

Hey there! 👋  
Thanks for your interest in contributing to **Axon** — a lightweight C-backed Python array manipulation library. This guide will help you get started with contributing and outlines the best practices for working on this project.

## Project Structure

```text
build/
│── \librarry.dll
└── \libarray.so       # compiled c/c++ codebase
axon/
├── \csrc         # core c/cpp++ backend lies here
│   │── \core.cpp         # core functions & logics of array goes here
│   │── \core.h
│   │── \array.cpp         # array function handling file
│   └── \array.h
├── helpers/
│   └── \shape.py     # shape/flatten utilities
├── \_core.py         # Python array class logic
└── \_cbase.py        # ctypes interface to C library
```

## Prerequisites

- Python 3.7+
- Basic knowledge of `ctypes`, Python OOP, and C
- A working C compiler (`gcc`, `clang`, or MSVC)
- Make sure you can compile and load the shared library successfully!

## How to Contribute

### 1. Fork the Repository

Click the **Fork** button at the top right of this repo.

### 2. Clone Your Fork

```bash
git clone https://github.com/delveopers/Axon.git
cd axon
```

### 3. Create a Branch

```bash
git checkout -b fix/your-feature-name
```

### 4. Make Your Changes

- Add your feature/fix in Python or the C backend
- Update or add new tests in `test.py` or `tests/`
- Run your code and verify everything works

### 5. Run the Test File

```bash
python test.py
```

If you added new features, update `test.py` to include usage examples.

## Guidelines

### Do

- Keep indentation to **2 spaces** in both Python and C files
- Use **pure C** (`stdio.h`, `stdlib.h`) — no external dependencies
- Make sure `lib.print_tensor()` works for your output
- Add examples to `test.py` if your feature is user-facing
- Write clean, readable, and consistent code

### Don’t

- Don’t use `numpy`, `math`, or other Python math libraries
- Don’t modify the `__init__` method logic for internal tensors unless necessary
- Don’t commit `.dll` / `.so` files to Git

## Reporting Bugs

Found a bug?
Open an issue with:

- What you did
- What you expected
- What went wrong
- A small code snippet to reproduce it

## Support & Questions

If you're stuck or have ideas, open a discussion or issue. You can also ping Harsh directly.

## License

By contributing, you agree that your code will be licensed under the [Apache-2.0](./LICENSE).

Thanks for helping make Axon better! 🚀
