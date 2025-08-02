from .._cbase import CArray, lib, DType
from .._helpers import ShapeHelp, DtypeHelp
from ctypes import c_float

def sin_array_ops(self):
  from .._core import array
  result_ptr = lib.sin_array(self.data).contents
  out = array(result_ptr, self.dtype)
  return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]

def cos_array_ops(self):
  from .._core import array
  result_ptr = lib.cos_array(self.data).contents
  out = array(result_ptr, self.dtype)
  return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]

def tan_array_ops(self):
  from .._core import array
  result_ptr = lib.tan_array(self.data).contents
  out = array(result_ptr, self.dtype)
  return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]

def sinh_array_ops(self):
  from .._core import array
  result_ptr = lib.sinh_array(self.data).contents
  out = array(result_ptr, self.dtype)
  return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]

def cosh_array_ops(self):
  from .._core import array
  result_ptr = lib.cosh_array(self.data).contents
  out = array(result_ptr, self.dtype)
  return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]

def tanh_array_ops(self):
  from .._core import array
  result_ptr = lib.tanh_array(self.data).contents
  out = array(result_ptr, self.dtype)
  return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]

def log_array_ops(self):
  from .._core import array
  result_ptr = lib.log_array(self.data).contents
  out = array(result_ptr, self.dtype)
  return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]

def exp_array_ops(self):
  from .._core import array
  result_ptr = lib.exp_array(self.data).contents
  out = array(result_ptr, self.dtype)
  return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]

def abs_array_ops(self):
  from .._core import array
  result_ptr = lib.abs_array(self.data).contents
  out = array(result_ptr, self.dtype)
  return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]

def sqrt_array_ops(self):
  from .._core import array
  result_ptr = lib.sqrt_array(self.data).contents
  out = array(result_ptr, self.dtype)
  return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]

def sign_array_ops(self):
  from .._core import array
  result_ptr = lib.sign_array(self.data).contents
  out = array(result_ptr, self.dtype)
  return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]

def neg_array_ops(self):
  from .._core import array
  result_ptr = lib.neg_array(self.data).contents
  out = array(result_ptr, self.dtype)
  return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]

def clip_norm_ops(self, max: float):
  from .._core import array
  out = array(lib.clip_array(self.data, c_float(max)).contents, self.dtype)
  out.shape, out.size, out.ndim, out.strides = self.shape, self.size, self.ndim, self.strides
  return out

def clamp_norm_ops(self, max: float, min: float):
  from .._core import array
  out = array(lib.clamp_array(self.data, c_float(min), c_float(max)).contents, self.dtype)
  out.shape, out.size, out.ndim, out.strides = self.shape, self.size, self.ndim, self.strides
  return out