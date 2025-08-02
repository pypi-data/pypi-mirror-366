from .._cbase import CArray, lib, DType
from .._helpers import ShapeHelp, DtypeHelp
from ctypes import c_float, c_int, c_bool

def sum_array_ops(self, axis: int=-1, keepdims: bool=False):
  from .._core import array
  out = array(lib.sum_array(self.data, c_int(axis), c_bool(keepdims)).contents, self.dtype)
  if axis == -1: out.shape, out.size, out.ndim = (1,) if keepdims else (), 1, 1 if keepdims else 0
  else:
    new_shape = list(self.shape)
    if keepdims: new_shape[axis] = 1
    else: new_shape.pop(axis)
    out.shape = tuple(new_shape)
    out.size, out.ndim, out.strides = 1 if not new_shape else eval('*'.join(map(str, new_shape))), len(new_shape), ShapeHelp.get_strides(out.shape) if out.shape else []
  return out

def mean_array_ops(self, axis: int=-1, keepdims: bool=False):
  from .._core import array
  out = array(lib.mean_array(self.data, c_int(axis), c_bool(keepdims)).contents, self.dtype)
  if axis == -1: out.shape, out.size, out.ndim = (1,) if keepdims else (), 1, 1 if keepdims else 0
  else:
    new_shape = list(self.shape)
    if keepdims: new_shape[axis] = 1
    else: new_shape.pop(axis)
    out.shape = tuple(new_shape)
    out.size, out.ndim, out.strides = 1 if not new_shape else eval('*'.join(map(str, new_shape))), len(new_shape), ShapeHelp.get_strides(out.shape) if out.shape else []
  return out

def min_array_ops(self, axis: int=-1, keepdims: bool=False):
  from .._core import array
  out = array(lib.min_array(self.data, c_int(axis), c_bool(keepdims)).contents, self.dtype)
  if axis == -1: out.shape, out.size, out.ndim = (1,) if keepdims else (), 1, 1 if keepdims else 0
  else:
    new_shape = list(self.shape)
    if keepdims: new_shape[axis] = 1
    else: new_shape.pop(axis)
    out.shape = tuple(new_shape)
    out.size, out.ndim, out.strides = 1 if not new_shape else eval('*'.join(map(str, new_shape))), len(new_shape), ShapeHelp.get_strides(out.shape) if out.shape else []
  return out

def max_array_ops(self, axis: int=-1, keepdims: bool=False):
  from .._core import array
  out = array(lib.max_array(self.data, c_int(axis), c_bool(keepdims)).contents, self.dtype)
  if axis == -1: out.shape, out.size, out.ndim = (1,) if keepdims else (), 1, 1 if keepdims else 0
  else:
    new_shape = list(self.shape)
    if keepdims: new_shape[axis] = 1
    else: new_shape.pop(axis)
    out.shape = tuple(new_shape)
    out.size, out.ndim, out.strides = 1 if not new_shape else eval('*'.join(map(str, new_shape))), len(new_shape), ShapeHelp.get_strides(out.shape) if out.shape else []
  return out

def var_array_ops(self, axis: int=-1, ddof: int=0):
  from .._core import array
  out = array(lib.var_array(self.data, c_int(axis), c_int(ddof)).contents, self.dtype)
  if axis == -1: out.shape, out.size, out.ndim = (), 1, 0
  else:
    new_shape = list(self.shape)
    new_shape.pop(axis)
    out.shape = tuple(new_shape)
    out.size, out.ndim, out.strides = 1 if not new_shape else eval('*'.join(map(str, new_shape))), len(new_shape), ShapeHelp.get_strides(out.shape) if out.shape else []
  return out

def std_array_ops(self, axis: int=-1, ddof: int=0):
  from .._core import array
  out = array(lib.std_array(self.data, c_int(axis), c_int(ddof)).contents, self.dtype)
  if axis == -1: out.shape, out.size, out.ndim = (), 1, 0
  else:
    new_shape = list(self.shape)
    new_shape.pop(axis)
    out.shape = tuple(new_shape)
    out.size, out.ndim, out.strides = 1 if not new_shape else eval('*'.join(map(str, new_shape))), len(new_shape), ShapeHelp.get_strides(out.shape) if out.shape else []
  return out