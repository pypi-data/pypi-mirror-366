from ctypes import c_float, c_size_t, c_int, c_bool
from typing import *

from ._cbase import CArray, lib, DType
from ._helpers import ShapeHelp, DtypeHelp, _get_item_array, _set_item_array, _iter_item_array
from .ops.binary import *
from .ops.unary import *
from .ops.shape import transpose_array_ops, flatten_array_ops, contiguous_array_ops, view_array_ops, reshape_array_ops, expand_dims_ops, make_contiguous_array_ops, squeeze_array_ops, to_list_array
from .ops.redux import sum_array_ops, mean_array_ops, max_array_ops, var_array_ops, min_array_ops, std_array_ops

int8, int16, int32, int64, long = "int8", "int16", "int32", "int64", "long"
float32, float64, double = "float32", "float64", "double"
uint8, uint16, uint32, uint64 = "uint8", "uint16", "uint32", "uint64"
boolean = "bool"

class array:
  int8, int16, int32, int64, long, float32, float64, double, uint8, uint16, uint32, uint64, boolean = int8, int16, int32, int64, long, float32, float64, double, uint8, uint16, uint32, uint64, boolean
  def __init__(self, data: Union[List[Any], int, float], dtype: str=float32):
    if isinstance(data, CArray): self.data, self.shape, self.size, self.ndim, self.strides, self.dtype = data, (), 0, 0, [], dtype or "float32"
    elif isinstance(data, array): self.data, self.shape, self.dtype, self.size, self.ndim, self.strides = data.data, data.shape, dtype or data.dtype, data.size, data.ndim, data.strides
    else:
      data, shape = ShapeHelp.flatten([data] if isinstance(data, (int, float)) else data), tuple(ShapeHelp.get_shape(data))
      self.size, self.ndim, self.dtype, self.shape, self.strides = len(data), len(shape), dtype or "float32", shape, ShapeHelp.get_strides(shape)
      self._data_ctypes, self._shape_ctypes = (c_float * self.size)(*data.copy()), (c_int * self.ndim)(*shape)
      self.data = lib.create_array(self._data_ctypes, c_size_t(self.ndim), self._shape_ctypes, c_size_t(self.size), c_int(DtypeHelp._parse_dtype(self.dtype)))
  def astype(self, dtype: str) -> "array":
    out = array(lib.cast_array(self.data, c_int(DtypeHelp._parse_dtype(dtype))).contents, dtype)
    out.shape, out.size, out.ndim, out.strides = self.shape, self.size, self.ndim, self.strides
    return out
  def __repr__(self) -> str: return f"array({self.tolist()}, dtype={self.dtype})"
  def __str__(self) -> str: return (lib.print_array(self.data), "")[1]
  def is_contiguous(self) -> bool: return bool(lib.is_contiguous_array(self.data))
  def is_view(self) -> bool:  return bool(lib.is_view_array(self.data))
  def __hash__(self): return id(self)
  def __getitem__(self, key): return _get_item_array(self, key)
  def __setitem__(self, key, value): return _set_item_array(self, key, value)
  def __iter__(self): return _iter_item_array(self)
  def contiguous(self) -> "array": return contiguous_array_ops(self)
  def make_contiguous(self) -> None: make_contiguous_array_ops(self)
  def view(self) -> "array": return view_array_ops(self)
  def tolist(self) -> List[Any]: return to_list_array(self)
  def __add__(self, other) -> "array": return add_array_ops(self, other)
  def __sub__(self, other) -> "array": return sub_array_ops(self, other)
  def __mul__(self, other) -> "array": return mul_array_ops(self, other)
  def __truediv__(self, other) -> "array": return div_array_ops(self, other)
  def __neg__(self) -> "array": return neg_array_ops(self)
  def __radd__(self, other): return radd_array_ops(self, other)
  def __rsub__(self, other): return rsub_array_ops(self, other)
  def __rmul__(self, other): return rmul_array_ops(self, other)
  def __rtruediv__(self, other): return rdiv_array_ops(self, other)
  def __pow__(self, exp) -> "array":  return pow_array_ops(self, exp)
  def __rpow__(self, base) -> "array": return rpow_array_ops(self, base)
  def __matmul__(self, other): return matmul_array_ops(self, other)
  def dot(self, other): return dot_array_ops(self, other)
  def log(self) -> "array": return log_array_ops(self)
  def sqrt(self) -> "array": return sqrt_array_ops(self)
  def exp(self) -> "array": return exp_array_ops(self)
  def abs(self) -> "array": return abs_array_ops(self)
  def sign(self) -> "array": return sign_array_ops(self)
  def sin(self) -> "array": return sin_array_ops(self)
  def cos(self) -> "array": return cos_array_ops(self)
  def tan(self) -> "array": return tan_array_ops(self)
  def sinh(self) -> "array": return sinh_array_ops(self)
  def cosh(self) -> "array": return cosh_array_ops(self)
  def tanh(self) -> "array": return tanh_array_ops(self)
  def transpose(self) -> "array": return transpose_array_ops(self)
  def reshape(self, new_shape: Union[List[int], Tuple[int]]) -> "array": return reshape_array_ops(self, new_shape)
  def squeeze(self, axis: int = -1) -> "array": return squeeze_array_ops(self, axis)
  def expand_dims(self, axis: int) -> "array": return expand_dims_ops(self, axis)
  def flatten(self) -> "array": return flatten_array_ops(self)
  def clip(self, max: float): return clip_norm_ops(self, max)
  def clamp(self, max: float, min: float): return clamp_norm_ops(self, max, min)
  def sum(self, axis: int = -1, keepdims: bool = False) -> "array": return sum_array_ops(self, axis, keepdims)
  def mean(self, axis: int = -1, keepdims: bool = False) -> "array": return mean_array_ops(self, axis, keepdims)
  def max(self, axis: int = -1, keepdims: bool = False) -> "array": return max_array_ops(self, axis, keepdims)
  def min(self, axis: int = -1, keepdims: bool = False) -> "array": return min_array_ops(self, axis, keepdims)
  def var(self, axis: int = -1, ddof: int = 0) -> "array": return var_array_ops(self, axis, ddof)
  def std(self, axis: int = -1, ddof: int = 0) -> "array": return std_array_ops(self, axis, ddof)
  def __eq__(self, other) -> "array":
    other = other if isinstance(other, (CArray, array)) or isinstance(other, (int, float)) else array(other)
    if isinstance(other, (int, float)): out = array(lib.equal_scalar(self.data, c_float(other)).contents, DType.BOOL)
    else: out = array(lib.equal_array(self.data, other.data).contents, DType.BOOL)
    return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]
  def __ne__(self, other) -> "array":
    other = other if isinstance(other, (CArray, array)) or isinstance(other, (int, float)) else array(other)
    if isinstance(other, (int, float)): out = array(lib.not_equal_scalar(self.data, c_float(other)).contents, DType.BOOL)
    else: out = array(lib.not_equal_array(self.data, other.data).contents, DType.BOOL)
    return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]
  def __gt__(self, other) -> "array":
    other = other if isinstance(other, (CArray, array)) or isinstance(other, (int, float)) else array(other)
    if isinstance(other, (int, float)): out = array(lib.greater_scalar(self.data, c_float(other)).contents, DType.BOOL)
    else: out = array(lib.greater_array(self.data, other.data).contents, DType.BOOL)
    return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]
  def __lt__(self, other) -> "array":
    other = other if isinstance(other, (CArray, array)) or isinstance(other, (int, float)) else array(other)
    if isinstance(other, (int, float)): out = array(lib.smaller_scalar(self.data, c_float(other)).contents, DType.BOOL)
    else: out = array(lib.smaller_array(self.data, other.data).contents, DType.BOOL)
    return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]
  def __ge__(self, other) -> "array":
    other = other if isinstance(other, (CArray, array)) or isinstance(other, (int, float)) else array(other)
    if isinstance(other, (int, float)): out = array(lib.greater_equal_scalar(self.data, c_float(other)).contents, DType.BOOL)
    else: out = array(lib.greater_equal_array(self.data, other.data).contents, DType.BOOL)
    return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]
  def __le__(self, other) -> "array":
    other = other if isinstance(other, (CArray, array)) or isinstance(other, (int, float)) else array(other)
    if isinstance(other, (int, float)): out = array(lib.smaller_equal_scalar(self.data, c_float(other)).contents, DType.BOOL)
    else: out = array(lib.smaller_equal_array(self.data, other.data).contents, DType.BOOL)
    return (setattr(out, "shape", self.shape), setattr(out, "size", self.size), setattr(out, "ndim", self.ndim), setattr(out, "strides", self.strides), out)[4]