from ._cbase import CArray, lib, DType
from ctypes import c_int, c_size_t, c_float
from typing import *
from ._helpers import ShapeHelp, DtypeHelp
from ._core import array

def zeros_like(arr):
  ptr = lib.zeros_like_array(arr.data if isinstance(arr, array) else arr).contents; out = array(ptr)
  return (setattr(out, "shape", arr.shape), setattr(out, "ndim", arr.ndim), setattr(out, "size", arr.size), setattr(out, "strides", arr.strides), out)[4]

def ones_like(arr):
  ptr = lib.ones_like_array(arr.data if isinstance(arr, array) else arr).contents; out = array(ptr)
  return (setattr(out, "shape", arr.shape), setattr(out, "ndim", arr.ndim), setattr(out, "size", arr.size), setattr(out, "strides", arr.strides), out)[4]

def zeros(*shape, dtype="float32"):
  s, sz, nd, sa = ShapeHelp.process_shape(shape)
  out = array(lib.zeros_array(sa, c_size_t(sz), c_size_t(nd), c_int(DtypeHelp._parse_dtype(dtype))).contents, dtype)
  return (setattr(out, "shape", tuple(s)), setattr(out, "ndim", nd), setattr(out, "size", sz), setattr(out, "strides", ShapeHelp.get_strides(s)), out)[4]

def ones(*shape, dtype="float32"):
  s, sz, nd, sa = ShapeHelp.process_shape(shape)
  out = array(lib.ones_array(sa, c_size_t(sz), c_size_t(nd), c_int(DtypeHelp._parse_dtype(dtype))).contents, dtype)
  return (setattr(out, "shape", tuple(s)), setattr(out, "ndim", nd), setattr(out, "size", sz), setattr(out, "strides", ShapeHelp.get_strides(s)), out)[4]

def randn(*shape, dtype="float32"):
  s, sz, nd, sa = ShapeHelp.process_shape(shape)
  out = array(lib.randn_array(sa, c_size_t(sz), c_size_t(nd), c_int(DtypeHelp._parse_dtype(dtype))).contents, dtype)
  return (setattr(out, "shape", tuple(s)), setattr(out, "ndim", nd), setattr(out, "size", sz), setattr(out, "strides", ShapeHelp.get_strides(s)), out)[4]

def randint(low, high, *shape, dtype="int32"):
  s, sz, nd, sa = ShapeHelp.process_shape(shape)
  out = array(lib.randint_array(c_int(low), c_int(high), sa, c_size_t(sz), c_size_t(nd), c_int(DtypeHelp._parse_dtype(dtype))).contents, dtype)
  return (setattr(out, "shape", tuple(s)), setattr(out, "ndim", nd), setattr(out, "size", sz), setattr(out, "strides", ShapeHelp.get_strides(s)), out)[4]

def uniform(low, high, *shape, dtype="float32"):
  s, sz, nd, sa = ShapeHelp.process_shape(shape)
  out = array(lib.uniform_array(c_int(low), c_int(high), sa, c_size_t(sz), c_size_t(nd), c_int(DtypeHelp._parse_dtype(dtype))).contents, dtype)
  return (setattr(out, "shape", tuple(s)), setattr(out, "ndim", nd), setattr(out, "size", sz), setattr(out, "strides", ShapeHelp.get_strides(s)), out)[4]

def fill(fill_val, *shape, dtype="float32"):
  s, sz, nd, sa = ShapeHelp.process_shape(shape)
  out = array(lib.fill_array(c_float(fill_val), sa, c_size_t(sz), c_size_t(nd), c_int(DtypeHelp._parse_dtype(dtype))).contents, dtype)
  return (setattr(out, "shape", tuple(s)), setattr(out, "ndim", nd), setattr(out, "size", sz), setattr(out, "strides", ShapeHelp.get_strides(s)), out)[4]

def linspace(start: float, step: float, end: float, *shape: Union[list, tuple], dtype: int = "float32") -> array:
  s, sz, nd, sa = ShapeHelp.process_shape(shape)
  out = array(lib.linspace_array(c_float(start), c_float(step), c_float(end), sa, c_size_t(sz), c_size_t(nd), c_int(DtypeHelp._parse_dtype(dtype))).contents, dtype)
  return (setattr(out, "shape", tuple(s)), setattr(out, "ndim", nd), setattr(out, "size", sz), setattr(out, "strides", ShapeHelp.get_strides(s)), out)[4]

def arange(start: float, stop: float, step: float = 1.0, dtype: str = "float32") -> array:
  if step == 0.0: raise ValueError("Step cannot be zero")
  if (step > 0 and start >= stop) or (step < 0 and start <= stop): raise ValueError("Invalid arange parameters: no values in range")
  c_array = lib.arange_array(c_float(start), c_float(stop), c_float(step), c_int(DtypeHelp._parse_dtype(dtype)))
  sz = lib.out_size(c_array)
  out = array(c_array.contents, dtype)
  return (setattr(out, "shape", (sz,)), setattr(out, "ndim", 1), setattr(out, "size", sz), setattr(out, "strides", ShapeHelp.get_strides((sz,))), out)[4]