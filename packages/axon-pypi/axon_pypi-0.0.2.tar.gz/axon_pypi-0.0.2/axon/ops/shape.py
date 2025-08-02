from .._cbase import CArray, lib, DType
from .._helpers import ShapeHelp, DtypeHelp
from ctypes import c_int

def transpose_array_ops(self):
  from .._core import array
  assert self.ndim <= 3, ".transpose() only supported till 3-d arrays"
  out = array(lib.transpose_array(self.data).contents, self.dtype)
  out.shape, out.size, out.ndim = tuple(ShapeHelp.transpose_shape(self.shape)), self.size, self.ndim
  out.strides = ShapeHelp.get_strides(out.shape)
  return out

def flatten_array_ops(self):
  from .._core import array
  out = array(lib.flatten_array(self.data).contents, self.dtype)
  out.shape = (self.size,)
  out.size, out.ndim, out.strides = self.size, 1, ShapeHelp.get_strides(out.shape)
  return out

def expand_dims_ops(self, axis):
  from .._core import array
  result_ptr = lib.expand_dims_array(self.data, c_int(axis)).contents
  out = array(result_ptr, self.dtype)
  new_shape = list(self.shape)
  if axis < 0: axis = len(new_shape) + axis + 1
  new_shape.insert(axis, 1)
  out.shape = tuple(new_shape)
  out.size, out.ndim, out.strides = self.size, len(out.shape), ShapeHelp.get_strides(out.shape)
  return out

def squeeze_array_ops(self, axis):
  from .._core import array
  result_ptr = lib.squeeze_array(self.data, c_int(axis)).contents
  out = array(result_ptr, self.dtype)
  if axis == -1: new_shape = [dim for dim in self.shape if dim != 1]      # Remove all dimensions of size 1
  else: # Remove specific axis if it has size 1
    if self.shape[axis] != 1: raise ValueError(f"Cannot squeeze axis {axis} with size {self.shape[axis]}")
    new_shape = list(self.shape); new_shape.pop(axis)
  out.shape = tuple(new_shape) if new_shape else (1,)
  out.size, out.ndim, out.strides = self.size, len(out.shape), ShapeHelp.get_strides(out.shape)
  return out

def reshape_array_ops(self, new_shape):
  from .._core import array
  if isinstance(new_shape, tuple): new_shape = list(new_shape)
  new_size, ndim = 1, len(new_shape)
  for dim in new_shape: new_size *= dim
  if new_size != self.size: raise ValueError(f"Cannot reshape array of size {self.size} into shape {new_shape}")
  result_ptr = lib.reshape_array(self.data, (c_int * ndim)(*new_shape), c_int(ndim)).contents
  out = array(result_ptr, self.dtype)
  out.shape, out.size, out.ndim = tuple(new_shape), self.size, ndim; out.strides = ShapeHelp.get_strides(new_shape)
  return out

def to_list_array(self):
  data_ptr = lib.out_data(self.data)
  data_array = [data_ptr[i] for i in range(self.size)]
  if self.ndim == 0: return data_array[0]
  elif self.ndim == 1: return data_array
  else: return ShapeHelp.reshape_list(data_array, self.shape)

def contiguous_array_ops(self):
  from .._core import array
  out = array(lib.contiguous_array(self.data).contents, self.dtype)
  out.shape, out.size, out.ndim, out.strides = self.shape, self.size, self.ndim, self.strides
  return out

def make_contiguous_array_ops(self) -> None:
  lib.make_contiguous_inplace_array(self.data)
  self.strides = ShapeHelp.get_strides(self.shape)  # updating strides since they may have changed

def view_array_ops(self):
  from .._core import array
  out = array(lib.view_array(self.data).contents, self.dtype)
  out.shape, out.size, out.ndim, out.strides = self.shape, self.size, self.ndim, self.strides
  return out