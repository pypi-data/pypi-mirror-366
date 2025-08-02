from .._cbase import CArray, lib, DType
from .._helpers import ShapeHelp, DtypeHelp
from ctypes import c_float

def add_array_ops(self, other):
  from .._core import array
  other = other if isinstance(other, array) or isinstance(other, (int, float)) else array(other, self.dtype)
  if isinstance(other, (int, float)): result_ptr = lib.add_scalar_array(self.data, c_float(other)).contents
  else:
    if self.shape == other.shape: result_ptr = lib.add_array(self.data, other.data).contents
    else:
      if ShapeHelp.is_broadcastable(self.shape, other.shape): result_ptr = lib.add_broadcasted_array(self.data, other.data).contents
      else: raise ValueError(f"Shapes {self.shape} & {other.shape} are incompatible for broadcasting")
  out = array(result_ptr, self.dtype)
  out.shape, out.ndim, out.size, out.strides = self.shape, self.ndim, self.size, self.strides
  return out

def sub_array_ops(self, other):
  from .._core import array
  other = other if isinstance(other, array) or isinstance(other, (int, float)) else array(other, self.dtype)
  if isinstance(other, (int, float)): result_ptr = lib.sub_scalar_array(self.data, c_float(other)).contents
  else:
    if self.shape == other.shape: result_ptr = lib.sub_array(self.data, other.data).contents
    else:
      if ShapeHelp.is_broadcastable(self.shape, other.shape): result_ptr = lib.sub_broadcasted_array(self.data, other.data).contents
      else: raise ValueError(f"Shapes {self.shape} & {other.shape} are incompatible for broadcasting")
  out = array(result_ptr, self.dtype)
  out.shape, out.ndim, out.size, out.strides = self.shape, self.ndim, self.size, self.strides
  return out

def mul_array_ops(self, other):
  from .._core import array
  other = other if isinstance(other, array) or isinstance(other, (int, float)) else array(other, self.dtype)
  if isinstance(other, (int, float)): result_ptr = lib.mul_scalar_array(self.data, c_float(other)).contents
  else:
    if self.shape == other.shape: result_ptr = lib.mul_array(self.data, other.data).contents
    else:
      if ShapeHelp.is_broadcastable(self.shape, other.shape): result_ptr = lib.sub_broadcasted_array(self.data, other.data).contents
      else: raise ValueError(f"Shapes {self.shape} & {other.shape} are incompatible for broadcasting")
  out = array(result_ptr, self.dtype)
  out.shape, out.ndim, out.size, out.strides = self.shape, self.ndim, self.size, self.strides
  return out

def div_array_ops(self, other):
  from .._core import array
  other = other if isinstance(other, array) or isinstance(other, (int, float)) else array(other, self.dtype)
  if isinstance(other, (int, float)): result_ptr = lib.div_scalar_array(self.data, c_float(other)).contents
  else:
    if self.shape == other.shape: result_ptr = lib.div_array(self.data, other.data).contents
    else:
      if ShapeHelp.is_broadcastable(self.shape, other.shape): result_ptr = lib.sub_broadcasted_array(self.data, other.data).contents
      else: raise ValueError(f"Shapes {self.shape} & {other.shape} are incompatible for broadcasting")
  out = array(result_ptr, self.dtype)
  out.shape, out.ndim, out.size, out.strides = self.shape, self.ndim, self.size, self.strides
  return out

def pow_array_ops(self, exp):
  from .._core import array
  if isinstance(exp, (int, float)): restult_ptr = lib.pow_array(self.data, c_float(exp)).contents
  out = array(restult_ptr, self.dtype)
  out.shape, out.ndim, out.size, out.strides = self.shape, self.ndim, self.size, self.strides
  return out

def rpow_array_ops(self, base):
  from .._core import array
  if isinstance(base, (int, float)): restult_ptr = lib.pow_scalar(c_float(base), self.data).contents
  else: raise NotImplementedError("__rpow__ with Array base not implemented yet")
  out = array(restult_ptr, self.dtype)
  out.shape, out.ndim, out.size, out.strides = self.shape, self.ndim, self.size, self.strides
  return out

def matmul_array_ops(self, other):
  from .._core import array
  other = other if isinstance(other, (CArray, array)) else array(other, self.dtype)
  if self.ndim <= 2 and other.ndim <= 2: result_ptr = lib.matmul_array(self.data, other.data).contents
  elif self.ndim == 3 and other.ndim == 3: result_ptr = lib.batch_matmul_arry(self.data, other.data).contents
  else: result_ptr = lib.broadcasted_matmul_array(self.data, other.data).contents
  out = array(result_ptr, self.dtype)
  shape, ndim, size = lib.out_shape(result_ptr), out.data.ndim, lib.out_size(result_ptr)
  out.shape, out.ndim, out.size = tuple([shape[i] for i in range(ndim)]), ndim, size
  out.strides = ShapeHelp.get_strides(out.shape)
  return out

def dot_array_ops(self, other):
  from .._core import array
  other = other if isinstance(other, (CArray, array)) else array(other, self.dtype)
  if self.ndim <= 2 and other.ndim <= 2: result_ptr = lib.dot_array(self.data, other.data).contents
  elif self.ndim == 3 and other.ndim == 3: result_ptr = lib.batch_dot_arry(self.data, other.data).contents
  out = array(result_ptr, self.dtype)
  shape, ndim, size = lib.out_shape(result_ptr), out.data.ndim, lib.out_size(result_ptr)
  out.shape, out.ndim, out.size = tuple([shape[i] for i in range(ndim)]), ndim, size
  out.strides = ShapeHelp.get_strides(out.shape)
  return out

def radd_array_ops(self, other): return self + other
def rmul_array_ops(self, other): return self * other
def rsub_array_ops(self, other):
  from .._core import array
  return -(self - other)
def rdiv_array_ops(self, other):
  from .._core import array
  return (self / other) ** -1