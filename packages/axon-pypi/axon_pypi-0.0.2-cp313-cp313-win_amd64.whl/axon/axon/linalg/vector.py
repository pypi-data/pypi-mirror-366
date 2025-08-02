from typing import *
from ctypes import c_int, c_float, c_double
from .._cbase import CArray, lib, DType
from .._core import array
from .._helpers import DtypeHelp, ShapeHelp

def dot(a: array, b: array, dtype: DType = 'float32') -> array:
  a, b = a if isinstance(a, array) else array(a, 'float32'), b if isinstance(b, array) else array(b, 'float32')
  ptr = lib.vector_dot(a.data, b.data).contents
  out = array(ptr, dtype if dtype is not None else a.dtype)
  return (setattr(out, "shape", ()), setattr(out, "ndim", 0), setattr(out, "size", 1), setattr(out, "strides", ()), out)[4]

def dot_mv(a: array, b: array, dtype: DType = 'float32') -> array:
  a, b = a if isinstance(a, array) else array(a, 'float32'), b if isinstance(b, array) else array(b, 'float32')
  ptr = lib.vector_matrix_dot(a.data, b.data).contents
  out = array(ptr, dtype if dtype is not None else a.dtype)
  if a.ndim == 1 and b.ndim == 2: out_shape, out_size = (b.shape[1],), b.shape[1]   # vector @ matrix: output shape = (matrix_cols,)
  elif a.ndim == 2 and b.ndim == 1: out_shape, out_size = (a.shape[0],), a.shape[0]   # matrix @ vector: output shape = (matrix_rows,)
  else: out_shape, out_size = (max(a.shape[0] if a.ndim >= 1 else 1, b.shape[0] if b.ndim >= 1 else 1),), out_shape[0] # fallback
  out_ndim, out_strides = len(out_shape), ShapeHelp.get_strides(out_shape)
  return (setattr(out, "shape", out_shape), setattr(out, "ndim", out_ndim), setattr(out, "size", out_size), setattr(out, "strides", out_strides), out)[4]

def inner(a: array, b: array, dtype: DType = 'float32') -> array:
  a, b = a if isinstance(a, array) else array(a, 'float32'), b if isinstance(b, array) else array(b, 'float32')
  ptr = lib.vector_inner(a.data, b.data).contents
  out = array(ptr, dtype if dtype is not None else a.dtype)
  return (setattr(out, "shape", ()), setattr(out, "ndim", 0), setattr(out, "size", 1), setattr(out, "strides", ()), out)[4]

def outer(a: array, b: array, dtype: DType = 'float32') -> array:
  a, b = a if isinstance(a, array) else array(a, 'float32'), b if isinstance(b, array) else array(b, 'float32')
  ptr = lib.vector_outer(a.data, b.data).contents
  out = array(ptr, dtype if dtype is not None else a.dtype)
  out_shape, out_size, out_ndim, out_strides = (a.shape[0], b.shape[0]), a.shape[0] * b.shape[0], 2, ShapeHelp.get_strides((a.shape[0], b.shape[0]))
  return (setattr(out, "shape", out_shape), setattr(out, "ndim", out_ndim), setattr(out, "size", out_size), setattr(out, "strides", out_strides), out)[4]

def cross(a: array, b: array, axis: int=None, dtype: DType = 'float32') -> array:
  a, b = a if isinstance(a, array) else array(a, 'float32'), b if isinstance(b, array) else array(b, 'float32')
  if a.ndim == 1 and b.ndim == 1:
    ptr = lib.vector_cross(a.data, b.data).contents
  elif a.ndim == 2 and b.ndim == 2 or a.ndim == 3 and b.ndim == 3:
    if axis == None: raise ValueError("Axis value can't be NULL, need an axis value")
    if axis > a.ndim or axis > b.ndim: raise IndexError(f"Can't exceed the ndim. Axis >= ndim in this case: {axis} >= {a.ndim}")
    ptr = lib.vector_cross_axis(a.data, b.data, c_int(axis)).contents
  else:
    raise ValueError(".cross() only supported for 1D, 2D, and 3D vectors")
  out = array(ptr, dtype if dtype is not None else a.dtype)
  out_shape, out_size, out_ndim, out_strides = a.shape, a.size, a.ndim, a.strides
  return (setattr(out, "shape", out_shape), setattr(out, "ndim", out_ndim), setattr(out, "size", out_size), setattr(out, "strides", out_strides), out)[4]

def inv(a: array, dtype: DType = 'float32') -> array:
  a = a if isinstance(a, array) else array(a, 'float32')
  ptr = lib.inv_array(a.data).contents
  out = array(ptr, dtype if dtype is not None else a.dtype)
  out.shape, out.size, out.ndim, out.strides = a.shape, a.size, a.ndim, a.strides
  return out

def rank(a: array, dtype: DType = 'float32') -> array:
  a = a if isinstance(a, array) else array(a, 'float32')
  ptr = lib.matrix_rank_array(a.data).contents
  out = array(ptr, dtype if dtype is not None else a.dtype)
  return (setattr(out, "shape", ()), setattr(out, "ndim", 0), setattr(out, "size", 1), setattr(out, "strides", ()), out)[4]

def solve(a: array, b: array, dtype: DType = 'float32') -> array:
  a, b = a if isinstance(a, array) else array(a, 'float32'), b if isinstance(b, array) else array(b, 'float32')
  ptr = lib.solve_array(a.data, b.data).contents
  out = array(ptr, dtype if dtype is not None else a.dtype)
  if b.ndim == 1:
    out_shape, out_size, out_ndim, out_strides = (a.shape[1],), a.shape[1], 1, (1,)
  else:
    out_shape, out_size, out_ndim, out_strides = (a.shape[1], b.shape[1]), a.shape[1] * b.shape[1], 2, ShapeHelp.get_strides((a.shape[1], b.shape[1]))
  return (setattr(out, "shape", out_shape), setattr(out, "ndim", out_ndim), setattr(out, "size", out_size), setattr(out, "strides", out_strides), out)[4]

def lstsq(a: array, b: array, dtype: DType = 'float32') -> array:
  a, b = a if isinstance(a, array) else array(a, 'float32'), b if isinstance(b, array) else array(b, 'float32')
  ptr = lib.lstsq_array(a.data, b.data).contents
  out = array(ptr, dtype if dtype is not None else a.dtype)
  if b.ndim == 1:
    out_shape, out_size, out_ndim, out_strides = (a.shape[1],), a.shape[1], 1, (1,)
  else:
    out_shape, out_size, out_ndim, out_strides = (a.shape[1], b.shape[1]), a.shape[1] * b.shape[1], 2, ShapeHelp.get_strides((a.shape[1], b.shape[1]))
  return (setattr(out, "shape", out_shape), setattr(out, "ndim", out_ndim), setattr(out, "size", out_size), setattr(out, "strides", out_strides), out)[4]